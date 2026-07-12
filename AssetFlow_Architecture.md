# AssetFlow — System Architecture

## 1. Stack
- Frontend: React + Tailwind (SPA) — fetch layer parses XML (`DOMParser`/`fast-xml-parser`) instead of JSON
- Backend: Python 3.12, Django 5 + Django REST Framework — XML-only API (`djangorestframework-xml`), all payloads validated against XSD schemas (`lxml`, `xmlschema`)
- DB: PostgreSQL (via Django ORM)
- Auth: JWT (access + refresh) via `djangorestframework-simplejwt`, Django password hasher (PBKDF2/Argon2); token delivered inside an XML `<auth>` envelope
- File storage: S3-compatible bucket (asset photos, maintenance photos, audit attachments) via `django-storages`
- Background jobs: Celery + Redis (broker) + Celery Beat (overdue checks, reminders) — replaces node-cron
- Realtime/notifications: WebSocket (Django Channels) or polling fallback
- Deployment: Docker Compose (api, worker, beat, redis, web, db)

## 2. High-Level Architecture
```
[React SPA] --XML/JWT--> [Django REST API] --SQL--> [PostgreSQL]
                               |--> [S3 storage]
                               |--> [Notification service] --WS(Channels)--> [React SPA]
                               |--> [Celery worker + Beat] (overdue checks, reminders)
                               |--> [XSD schema store] (/schemas/*.xsd, request/response validation)
```
Every request/response body is XML; XSD schemas gate both directions before payloads reach business logic (see TRD §4 for envelope format and validation pipeline).

## 3. Modules (map to screens)
1. Auth — signup(employee-only), login, forgot password, session/JWT refresh
2. Org Setup — Departments, Categories, Employee Directory, Role Promotion (admin-only)
3. Assets — registration, directory, search/filter, lifecycle status, history
4. Allocation & Transfer — allocate, block double-allocation, transfer requests, returns
5. Resource Booking — slot booking, overlap validation, cancel/reschedule
6. Maintenance — request → approval → technician → resolution, kanban states
7. Audit — cycles, auditor assignment, item verification, discrepancy report, close cycle
8. Reports — utilization, maintenance frequency, idle/most-used, heatmap, export
9. Notifications/Activity Log — event feed, full audit trail
10. Dashboard — aggregated KPIs from modules above

## 4. Database Schema (core tables)

**users**
id, name, email, password_hash, role[admin|asset_manager|dept_head|employee], department_id(FK), status[active|inactive], created_at

**departments**
id, name, head_id(FK users), parent_dept_id(FK self), status[active|inactive]

**asset_categories**
id, name, custom_fields(jsonb) — e.g. warranty_period

**assets**
id, tag(unique, auto AF-xxxx), name, category_id(FK), serial_number, acquisition_date, acquisition_cost, condition, location, status[available|allocated|reserved|under_maintenance|lost|retired|disposed], is_bookable(bool), department_id(FK), photo_url, created_at

**allocations**
id, asset_id(FK), holder_type[employee|department], holder_id, allocated_date, expected_return_date, actual_return_date, status[active|returned|overdue], checkin_notes

**transfer_requests**
id, asset_id(FK), from_holder_id, to_holder_id, requested_by(FK users), reason, status[pending|approved|rejected], approved_by, created_at

**bookings**
id, resource_asset_id(FK assets, is_bookable=true), booked_by(FK users), start_time, end_time, status[upcoming|ongoing|completed|cancelled], purpose

**maintenance_requests**
id, asset_id(FK), raised_by(FK users), issue, priority, photo_url, status[pending|approved|rejected|technician_assigned|in_progress|resolved], approved_by, technician_name, resolved_at

**audit_cycles**
id, name, scope_department_id, scope_location, start_date, end_date, status[open|closed]

**audit_auditors**
audit_cycle_id(FK), user_id(FK) — join table

**audit_items**
id, audit_cycle_id(FK), asset_id(FK), verification[verified|missing|damaged], notes, verified_by

**notifications**
id, user_id(FK), type, message, entity_type, entity_id, read(bool), created_at

**activity_logs**
id, user_id(FK), action, entity_type, entity_id, metadata(jsonb), created_at

## 5. State Machines

**Asset**
`Available ↔ Allocated`
`Available → Reserved → Allocated|Available`
`Available ↔ Under Maintenance`
`Any → Lost` (via audit close)
`Any → Retired → Disposed`

**Maintenance request**
`Pending → Approved (asset→Under Maintenance) → Technician Assigned → In Progress → Resolved (asset→Available)`
`Pending → Rejected`

**Booking**
`Upcoming → Ongoing → Completed`
`Upcoming → Cancelled`

**Transfer**
`Requested → Approved (reallocate, history updated) | Rejected`

**Audit cycle**
`Open (items get verified) → Closed (locks, missing→asset.status=Lost)`

## 6. Key Business Rules
- **Double-allocation block**: on allocate request, check for existing `allocations.status=active` on that asset. If found → reject, return current holder, expose "Transfer Request" action instead of raw allocate.
- **Booking overlap**: reject if `new.start < existing.end AND new.end > existing.start` for any `bookings.status in (upcoming, ongoing)` on same resource.
- **Overdue detection**: cron job daily — allocations past `expected_return_date` → status=overdue + notification; bookings/maintenance similarly checked for reminders.
- **Audit discrepancy report**: auto-generated from `audit_items` where verification in (missing, damaged) at cycle close; closing cycle is transactional (locks cycle + bulk asset status updates).
- **Role assignment**: only settable via Org Setup → Employee Directory by Admin. Signup endpoint hardcodes role=employee.

## 7. RBAC Matrix (summary)
| Action | Admin | Asset Mgr | Dept Head | Employee |
|---|---|---|---|---|
| Org setup (dept/category/roles) | ✅ | ❌ | ❌ | ❌ |
| Register/edit asset | ✅ | ✅ | ❌ | ❌ |
| Allocate asset | ✅ | ✅ | dept-scoped approve | ❌ |
| Approve transfer | ✅ | ✅ | dept-scoped | ❌ |
| Book resource | ✅ | ✅ | ✅ | ✅ |
| Raise maintenance | ✅ | ✅ | ✅ | ✅ |
| Approve maintenance | ✅ | ✅ | ❌ | ❌ |
| Create/close audit cycle | ✅ | ✅ | ❌ | ❌ |
| Verify audit item | auditor-assigned only (any role can be assigned as auditor) |
| View org-wide reports | ✅ | ✅ | dept-scoped | own-only |

Enforce via middleware: `requireRole([...])` + row-level scoping (`department_id` filter) for dept_head/employee queries.

## 8. API Structure (REST routes, XML bodies, JWT-protected except auth)
Same routes/status codes as before — only `Content-Type`/`Accept: application/xml` and body format changed (see TRD §4 for XML envelope, XSD, and example payloads).
```
POST   /auth/signup            /auth/login          /auth/forgot-password
GET    /departments             POST/PUT /departments/:id
GET    /categories               POST/PUT /categories/:id
GET    /employees                PATCH /employees/:id/role   (admin only)
GET    /assets   ?tag&status&category&dept&location
POST   /assets                   GET/PUT /assets/:id
GET    /assets/:id/history
POST   /allocations              POST /allocations/:id/return
POST   /transfer-requests        PATCH /transfer-requests/:id (approve/reject)
GET    /bookings?resource_id&date
POST   /bookings                 PATCH /bookings/:id (cancel/reschedule)
POST   /maintenance-requests     PATCH /maintenance-requests/:id (status transitions)
POST   /audit-cycles             POST /audit-cycles/:id/auditors
PATCH  /audit-items/:id          POST /audit-cycles/:id/close
GET    /reports/utilization      /reports/maintenance-frequency  /reports/idle-assets  /reports/booking-heatmap
GET    /notifications             PATCH /notifications/:id/read
GET    /activity-logs
GET    /dashboard/kpis
GET    /schemas/{resource}.xsd   (static XSD, one per resource, referenced via xsi:schemaLocation)
```

## 9. Notification Triggers
Asset Assigned, Transfer Approved, Booking Confirmed/Cancelled/Reminder, Maintenance Approved/Rejected/Resolved, Overdue Return Alert, Audit Discrepancy Flagged — each write to `notifications` + `activity_logs` in same transaction as the triggering action.

## 10. Suggested Folder Structure
```
/backend
  /assetflow            (Django project: settings, urls, celery.py)
  /apps
    auth/ org/ assets/ allocations/ bookings/ maintenance/ audit/ reports/ notifications/
      (each: models.py, serializers.py [XML], views.py, permissions.py, tasks.py, tests/)
  /schemas               (*.xsd, one per resource, versioned with API)
  /common
    parsers.py, renderers.py (custom DRF XMLParser/XMLRenderer + XSD validation)
    permissions.py (IsAdmin, IsAssetManagerOrAdmin, IsDeptScoped)
    xml_utils.py (lxml helpers, error envelope builders)
  manage.py
/frontend
  /src
    /pages (10 screens)
    /components
    /api (client per module — sends/parses XML)
    /store (auth, notifications)
```

## 11. References
- Product requirements: `AssetFlow_PRD.md`
- Technical requirements (Python/XML detail, XSD examples, flows): `AssetFlow_TRD.md`
- Schema: `AssetFlow_Schema.md`
- Web flow: `AssetFlow_WebFlow.md`
