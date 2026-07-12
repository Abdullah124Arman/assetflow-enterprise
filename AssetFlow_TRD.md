# Technical Requirements Document — AssetFlow

Version 2.0 | Stack: Python + XML | Companion to PRD v1.0, Architecture doc, Schema doc

**Assumption (stated once, applied throughout):** backend fully rewritten in Python; all API request/response bodies use XML (replacing JSON) validated against XSD schemas. Frontend remains a browser SPA but its data layer now sends/parses XML instead of JSON. Database stays PostgreSQL (language-agnostic) — see `AssetFlow_Schema.md`, unchanged.

## 1. Tech Stack
| Layer | Choice | Notes |
|---|---|---|
| Backend language | Python 3.12 | |
| Web framework | Django 5 + Django REST Framework (DRF) | `djangorestframework-xml` for XML renderer/parser |
| API format | XML | every request/response body; XSD schemas per resource |
| XML tooling | `lxml`, `xmlschema` | parsing, XSD validation, XPath for querying payloads |
| ORM | Django ORM | maps 1:1 to tables in `AssetFlow_Schema.md` |
| DB | PostgreSQL 15 | via `psycopg` |
| Auth | `djangorestframework-simplejwt` | JWT access/refresh; claims serialized into XML `<auth>` response |
| Background jobs | Celery + Redis (broker) + Celery Beat | overdue checks, booking reminders, status sync |
| File storage | `django-storages` → S3-compatible bucket | signed URLs |
| Frontend | React 18 + Vite (unchanged UI layer) | fetch layer swapped: `DOMParser`/`fast-xml-parser` instead of `JSON.parse` |
| Web server | Gunicorn + Nginx | reverse proxy, static/media |
| Containerization | Docker Compose | api, worker (celery), beat, redis, db, web |

## 2. Environments
- `local`: docker-compose, seeded demo data via Django fixtures (XML fixture format supported natively by Django: `dumpdata --format=xml`)
- `staging`/`prod`: same images, env-driven config (`DATABASE_URL`, `JWT_SECRET`, `S3_*`, `REDIS_URL`)
- Secrets via platform secret store in prod, never committed

## 3. Data Model
Full DDL (enums, tables, indexes, constraints) lives in `AssetFlow_Schema.md` — unchanged by the language/format shift. Core tables carried over as-is from v1.0: `users`, `departments`, `asset_categories`, `assets`, `allocations`, `transfer_requests`, `bookings`, `maintenance_requests`, `audit_cycles`, `audit_auditors`, `audit_items`, `notifications`, `activity_logs`.

Django models map 1:1 via `Meta.db_table`; enums implemented as Django `TextChoices` backed by the existing Postgres `CHECK`/`ENUM` types (`db_type` override or `models.CharField(choices=...)` with a matching Postgres enum via `django.contrib.postgres.fields`).

Key constraints preserved at the DB layer regardless of app language:
- `one_active_allocation_per_asset` (partial unique index on `allocations`) — enforces the double-allocation block
- `no_overlap` (GiST exclusion constraint on `bookings`, requires `btree_gist`) — enforces booking overlap prevention
- `valid_range` check (`end_time > start_time`) on `bookings`

## 4. XML API Contract

### 4.1 Envelope & conventions
```xml
<!-- success -->
<response>
  <data>...</data>
  <meta><page>1</page><total>42</total></meta>
</response>

<!-- error -->
<response>
  <error>
    <code>ALREADY_ALLOCATED</code>
    <message>Asset is already allocated</message>
    <details>...</details>
  </error>
</response>
```
- HTTP status still conveys class of error: 400 validation, 401 auth, 403 rbac, 404, 409 conflict, 500
- Content negotiation: `Content-Type: application/xml`, `Accept: application/xml` required on every call; DRF's `XMLParser`/`XMLRenderer` registered as the **only** parser/renderer (JSON explicitly disabled)
- Every resource has a matching **XSD** under `/schemas/*.xsd`, served statically and referenced via `xsi:schemaLocation` in responses for client-side validation

### 4.2 Example XSD — Asset
```xml
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="asset">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="id" type="xs:string"/>
        <xs:element name="tag" type="xs:string"/>
        <xs:element name="name" type="xs:string"/>
        <xs:element name="category_id" type="xs:string"/>
        <xs:element name="status">
          <xs:simpleType>
            <xs:restriction base="xs:string">
              <xs:enumeration value="available"/>
              <xs:enumeration value="allocated"/>
              <xs:enumeration value="reserved"/>
              <xs:enumeration value="under_maintenance"/>
              <xs:enumeration value="lost"/>
              <xs:enumeration value="retired"/>
              <xs:enumeration value="disposed"/>
            </xs:restriction>
          </xs:simpleType>
        </xs:element>
        <xs:element name="is_bookable" type="xs:boolean"/>
        <xs:element name="department_id" type="xs:string" minOccurs="0"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>
```
Every request body is validated against its XSD in DRF's `parse()` step (custom `XMLParser` subclass calling `xmlschema.validate()`) before it reaches the view — malformed/non-conforming XML is rejected with 400 and never touches business logic.

### 4.3 Example request/response — Allocate Asset
```xml
POST /allocations
<allocation_request>
  <asset_id>b3f1...</asset_id>
  <holder_type>employee</holder_type>
  <holder_id>a91c...</holder_id>
  <expected_return_date>2026-08-01</expected_return_date>
</allocation_request>
```
Conflict response (double-allocation block):
```xml
409 Conflict
<response>
  <error>
    <code>ALREADY_ALLOCATED</code>
    <message>Asset is already allocated</message>
    <details>
      <current_holder>
        <name>Priya Shah</name>
        <department>Engineering</department>
      </current_holder>
    </details>
  </error>
</response>
```

### 4.4 Example — Booking overlap
```xml
POST /bookings
<booking_request>
  <resource_asset_id>c7e2...</resource_asset_id>
  <start_time>2026-07-15T09:30:00Z</start_time>
  <end_time>2026-07-15T10:30:00Z</end_time>
  <purpose>Procurement sync</purpose>
</booking_request>
```
```xml
409 Conflict
<response>
  <error>
    <code>SLOT_UNAVAILABLE</code>
    <message>Requested time overlaps an existing booking</message>
  </error>
</response>
```

### 4.5 Pagination, Filtering & Idempotency
- Pagination: query params `?page&limit`, response `<meta><page/><limit/><total/></meta>`
- Filtering: query params map directly to indexed columns (`status`, `category_id`, `department_id`, `location`) — same filterable fields as v1.0
- Idempotency: mutating endpoints (`POST /allocations`, `POST /bookings`) accept an optional `Idempotency-Key` header to guard against double-submit from the UI; server caches the XML response for a given key for 24h and replays it on retry instead of re-executing the write

## 5. Critical Flows (Django implementation)

### 5.1 Allocate Asset
```python
# views.py (DRF, XML in/out)
class AllocateAssetView(APIView):
    permission_classes = [IsAssetManagerOrAdmin]

    def post(self, request):
        data = request.data  # already XSD-validated dict via custom XMLParser
        with transaction.atomic():
            asset = Asset.objects.select_for_update().get(id=data["asset_id"])
            if asset.status != "available":
                current = Allocation.objects.get(asset=asset, status="active")
                return xml_error("ALREADY_ALLOCATED", current_holder=current.holder, status=409)
            try:
                allocation = Allocation.objects.create(
                    asset=asset, holder_type=data["holder_type"],
                    holder_id=data["holder_id"],
                    expected_return_date=data.get("expected_return_date"),
                )
            except IntegrityError:  # unique partial index race guard
                return xml_error("ALREADY_ALLOCATED", status=409)
            asset.status = "allocated"
            asset.save()
            ActivityLog.objects.create(user=request.user, action="asset.allocate", entity_id=asset.id)
            notify(asset_holder(allocation), "asset_assigned", asset)
        return xml_response(AllocationSerializer(allocation).data, status=201)
```
DB unique partial index remains the source of truth for concurrency correctness — the pre-check is UX-only.

### 5.2 Book Resource (overlap block)
```python
class BookResourceView(APIView):
    def post(self, request):
        data = request.data
        try:
            with transaction.atomic():
                booking = Booking.objects.create(
                    resource_asset_id=data["resource_asset_id"],
                    booked_by=request.user,
                    start_time=data["start_time"],
                    end_time=data["end_time"],
                    purpose=data.get("purpose"),
                )
        except IntegrityError:  # GiST exclusion constraint violation
            return xml_error("SLOT_UNAVAILABLE", status=409)
        schedule_reminder.delay(str(booking.id))  # Celery task
        ActivityLog.objects.create(user=request.user, action="booking.create", entity_id=booking.id)
        return xml_response(BookingSerializer(booking).data, status=201)
```

### 5.3 Maintenance Approval
```python
class MaintenanceActionView(APIView):
    permission_classes = [IsAssetManagerOrAdmin]

    def patch(self, request, pk):
        action = request.data["action"]  # approve | reject | resolve
        with transaction.atomic():
            mr = MaintenanceRequest.objects.select_related("asset").get(id=pk)
            if action == "approve":
                mr.status, mr.approved_by = "approved", request.user
                mr.asset.status = "under_maintenance"
                mr.asset.save()
            elif action == "reject":
                mr.status = "rejected"
            elif action == "resolve":
                mr.status, mr.resolved_at = "resolved", timezone.now()
                mr.asset.status = "available"
                mr.asset.save()
            mr.save()
        return xml_response(MaintenanceSerializer(mr).data)
```

### 5.4 Audit Close
```python
class CloseAuditCycleView(APIView):
    def post(self, request, pk):
        with transaction.atomic():
            cycle = AuditCycle.objects.select_for_update().get(id=pk, status="open")
            missing_ids = AuditItem.objects.filter(
                audit_cycle=cycle, verification="missing"
            ).values_list("asset_id", flat=True)
            Asset.objects.filter(id__in=missing_ids).update(status="lost")
            flagged = AuditItem.objects.filter(
                audit_cycle=cycle, verification__in=["missing", "damaged"]
            )
            report = AuditDiscrepancyReport.objects.create(
                audit_cycle=cycle,
                report_xml=render_discrepancy_xml(flagged),  # lxml.etree build
            )
            cycle.status, cycle.closed_at = "closed", timezone.now()
            cycle.save()
        return xml_response(AuditReportSerializer(report).data)
```
Further `PATCH` on `audit_items` of a closed cycle → 409 (guarded in `perform_update`).

## 6. Auth & RBAC
- JWT via `djangorestframework-simplejwt`; payload `{sub, role, department_id, exp}`
- Token delivered inside XML: `<auth><access_token/><refresh_token/><expires_in/></auth>`
- Custom DRF `authentication.BaseAuthentication` subclass extracts JWT from `Authorization: Bearer`, unchanged by XML shift
- `permission_classes` per view (`IsAdmin`, `IsAssetManagerOrAdmin`, `IsDeptScoped`) — `IsDeptScoped` injects `.filter(department_id=request.user.department_id)` for dept_head/employee querysets
- Signup view hardcodes `role="employee"`; if `<role>` present in request XML, it's stripped/ignored (never trusted from client)
- Role promotion invalidates existing refresh tokens (`OutstandingToken.objects.filter(user=...).delete()`) so the new role takes effect on next login

## 7. Background Jobs (Celery Beat schedule)
| Task | Schedule | Action |
|---|---|---|
| `check_overdue_allocations` | daily 00:05 | `active` allocations past `expected_return_date` → `overdue` + notification |
| `sync_booking_status` | every 5 min | flip upcoming→ongoing→completed vs `now()` |
| `send_booking_reminders` | every 5 min | notify 15 min before `start_time`, dedupe via `reminder_sent` |
| `check_maintenance_sla` | daily | flag `pending` requests open beyond SLA threshold |

All tasks defined in `tasks.py`, registered in `celery.py` beat schedule; idempotent (safe to re-run).

## 8. Validation Rules
- Enforced twice: XSD (structural — types, enums, required fields) then Django `clean()`/serializer `validate()` (business — cross-field rules)
- Asset tag: server-generated (`AF-%04d` sequence), immutable, rejected if present in create payload
- Booking: `start_time` ≥ now; max duration configurable (default 4h) checked in serializer
- Allocation: `expected_return_date` (if present) must be > `allocated_date`
- Maintenance priority: XSD enum `low|medium|high|critical`
- Audit verification: `PATCH audit_items/:id` permitted only if `request.user` is in `audit_auditors` for that cycle (DB membership check in `has_permission`)

## 9. Security
- Passwords: Django's default PBKDF2 (or Argon2 via `django.contrib.auth.hashers`), cost per Django defaults
- Rate limiting: `django-ratelimit` on login endpoint, 5 req/min/IP
- XXE protection: `lxml` parser configured with `resolve_entities=False`, `no_network=True`, DTD loading disabled — mandatory given XML input surface
- XML bomb protection: `xmlschema`/`lxml` entity expansion limits set; request body size capped (e.g. 1MB) at Nginx + DRF parser level
- SQL: Django ORM parameterized queries only, no raw SQL string interpolation
- File uploads: type/size validated server-side before signed-URL issuance (max 10MB, image/pdf only)
- CORS: `django-cors-headers` allowlist frontend origin only
- `activity_logs` immutable — no update/delete endpoint exposed

## 10. Testing Strategy
- Unit: `pytest-django` for business rule functions (overlap check, allocation guard, discrepancy XML generation)
- XSD conformance tests: every endpoint's sample response validated against its `.xsd` in CI
- Integration: `pytest` + `pytest-django`'s live DB (or `testcontainers-python` Postgres) for the 4 critical flows in §5
- Concurrency test: parallel allocation requests (via `concurrent.futures` / `pytest-xdist`) on same asset → assert exactly one succeeds, rest return `ALREADY_ALLOCATED`
- Concurrency test: overlapping booking requests fired simultaneously → assert exactly one succeeds
- E2E (smoke): Playwright script driving the React frontend through signup→login→register asset→allocate→block re-allocate→transfer→book→maintenance cycle→audit cycle

## 11. Observability
- Structured JSON **logs** (log lines themselves stay JSON — internal ops tooling, not part of the API contract) with request id, user id, route, latency
- Health endpoint `/healthz` (DB + Redis + S3 connectivity check)
- Celery task failures reported via Sentry-compatible hook
- `/schemas/` directory versioned alongside API version to avoid breaking XSD consumers

## 12. Non-Functional Targets
| Metric | Target |
|---|---|
| API p95 latency (read) | < 350ms (XML parse/serialize overhead vs JSON factored in) |
| API p95 latency (write) | < 650ms |
| Search/filter (Assets) | < 1s at 10k rows |
| Concurrent booking race correctness | 100% (DB-enforced) |
| XML payload size ceiling | 1MB per request (rejected above) |
| Uptime (demo/staging) | best-effort, no SLA for hackathon |

## 13. Migration Notes (from v1.0 Node/JSON stack)
- Database schema (`AssetFlow_Schema.md`) is unchanged — Django models generated via `inspectdb` or hand-written to match existing DDL exactly
- Prisma migrations replaced by Django migrations (`makemigrations`/`migrate`); same target tables/constraints
- All prior REST examples in the old TRD map 1:1 to the XML examples in §4 — same routes, same status codes, only content-type and body format changed
- Frontend fetch layer: replace `res.json()` with an XML parse step (`DOMParser` in-browser or `fast-xml-parser`); all `/api/*` calls now send `Content-Type: application/xml`

## 14. References
- Architecture: `AssetFlow_Architecture.md`
- Product requirements: `AssetFlow_PRD.md`
- Schema: `AssetFlow_Schema.md`
- Web flow: `AssetFlow_WebFlow.md`
