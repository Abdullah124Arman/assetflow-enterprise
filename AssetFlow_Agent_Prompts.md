# AssetFlow — Agent Prompt Templates

## How to Use This File
1. Copy the prompt for the phase + agent (Backend = Member A, Frontend = Member B) you're working on
2. Attach the listed SOT files to the agent session
3. Paste the prompt at the start of the session
4. Never open a blank session and just start asking

---

## Universal Session Opener
Paste this at the TOP of EVERY agent session before anything else:

```
You are building AssetFlow — an Enterprise Asset & Resource Management System.
Single-org (no multi-tenancy). Backend: Python/Django/DRF. API: XML only. DB: PostgreSQL.

HARD RULES (never violate):
- PostgreSQL is the ONLY source of truth.
- API is XML ONLY — never emit or accept JSON. Every request/response uses
  Content-Type/Accept: application/xml.
- Every request AND response body must validate against its XSD (in /schemas)
  before it touches business logic.
- XML parser MUST be XXE-safe: resolve_entities=False, no_network=True, DTD and
  entity expansion disabled. This is non-negotiable given XML is the entire input surface.
- Signup ALWAYS hardcodes role=employee. Strip/ignore any client-supplied <role>.
  Roles are only ever changed via Org Setup > Employee Directory, by Admin.
- Every list/detail query for dept_head or employee roles MUST scope by department_id.
  No exceptions.
- Double-allocation block is DB-enforced via the `one_active_allocation_per_asset`
  partial unique index on allocations. Never rely on an app-level check alone —
  catch the IntegrityError and map it to 409 ALREADY_ALLOCATED.
- Booking overlap block is DB-enforced via the `no_overlap` GiST exclusion
  constraint on bookings (btree_gist). Never rely on an app-level check alone —
  catch the constraint violation and map it to 409 SLOT_UNAVAILABLE.
- Money fields (acquisition_cost) always NUMERIC/Decimal — never float.
- All timestamps TIMESTAMPTZ in DB.
- activity_logs is immutable — never expose an update or delete endpoint for it.
- Standard XML envelope:
  success: <response><data>...</data><meta>...</meta></response>
  error:   <response><error><code/><message/><details/></error></response>
- Server validates ALL critical rules regardless of what the client already checked.

I have attached the SOT documents. Read them before generating anything.
Current phase: [PHASE NUMBER AND NAME]
Current task: [EXACT TASK]
```

---

## PHASE 0 — Infrastructure & Setup

### Backend Agent — Member A
Attach: `AssetFlow_TRD.md`, `AssetFlow_Schema.md`

```
[Universal opener]

Task: Initialize the Django backend for AssetFlow.

Build exactly:
1. Django 5 project `assetflow` with DRF installed
2. Custom XMLParser + XMLRenderer registered as the ONLY parser/renderer
   (djangorestframework-xml as base, wrapped to run xmlschema validation
   against /schemas/*.xsd before returning parsed data to the view)
3. GET /health → 200, no auth required, returns <response><data><status>ok</status></data></response>
4. Global exception handler mapping DRF/DB exceptions to the standard XML error envelope
   (IntegrityError on the two named constraints → 409 with the correct code)
5. Folder structure:
   /backend
     /assetflow (settings.py, urls.py, celery.py)
     /apps
       auth/ org/ assets/ allocations/ bookings/ maintenance/ audit/ reports/ notifications/
     /schemas (empty .xsd placeholders for: user, department, category, asset)
     /common (parsers.py, renderers.py, permissions.py, xml_utils.py)
     manage.py
6. Env var loading via django-environ or python-dotenv — zero hardcoded secrets
7. Postgres connection via DATABASE_URL env var, psycopg driver

Do not build any auth or business logic yet. Infrastructure only.
```

### Frontend Agent — Member B
Attach: `AssetFlow_WebFlow.md`, `AssetFlow_Architecture.md`

```
[Universal opener]

Task: Initialize the AssetFlow React project.

Build exactly:
1. Vite + React 18 + Tailwind CSS scaffold
2. React Router routes (placeholder pages) for all 10 screens:
   /login, /dashboard, /org-setup, /assets, /allocation, /booking,
   /maintenance, /audit, /reports, /notifications
3. Sidebar nav component matching Screen 2–10 layout (Dashboard, Organization
   Setup*, Assets, Allocation & Transfer, Resource Booking, Maintenance, Audit,
   Reports, Notifications) — *Organization Setup hidden unless role=admin
4. XML API client wrapper in /src/api:
   - request(method, path, xmlBody?) → sends Content-Type/Accept: application/xml
   - parses response via DOMParser (or fast-xml-parser), throws a typed error on
     <error> envelope
5. Auth context/store: holds JWT, current role, department_id from token claims
6. .env with VITE_API_BASE_URL

Do not wire real data yet. Shell + navigation + XML client only.
```

### Database Setup Commands (run in order)
```
1. Create database `assetflow` on Postgres 15 instance (local docker or managed).
2. Enable extensions:
   CREATE EXTENSION IF NOT EXISTS pgcrypto;
   CREATE EXTENSION IF NOT EXISTS btree_gist;
3. Apply full schema from AssetFlow_Schema.md (enums, tables, indexes,
   the `one_active_allocation_per_asset` unique index, the `no_overlap`
   exclusion constraint) — via Django migrations once models exist, or
   directly via psql for the initial bootstrap.
4. Verify: \dt to list all tables; \d allocations and \d bookings to confirm
   the two critical constraints are present.
```

### Deployment / Local Run Commands
```
1. docker-compose up -d db redis
2. docker-compose up -d api worker beat
3. docker-compose up -d web
4. curl http://localhost:8000/health — confirm XML <status>ok</status> response
```

---

## PHASE 1 — Auth & Org Setup

### Backend Agent — Member A
Attach: `AssetFlow_TRD.md` §4–6, `AssetFlow_Schema.md` (users, departments, asset_categories tables)

```
[Universal opener]

Task: Build auth + organization setup endpoints.

Build exactly:
1. POST /auth/signup
   - Creates a `users` row with role HARDCODED to 'employee'
   - Reject/strip any <role> element present in the request XML
   - Returns JWT access + refresh inside <auth> envelope
2. POST /auth/login — phone/email + password, returns <auth> envelope
3. POST /auth/forgot-password — issues reset token (email/log stub is fine for hackathon)
4. POST /auth/refresh — rotates access token from refresh token
5. Departments: GET/POST /departments, PUT /departments/:id (create/edit/deactivate,
   head_id, parent_dept_id, status)
6. Categories: GET/POST /categories, PUT /categories/:id (custom_fields as XML
   list of <field key= label= type= required=/> elements, validated against XSD)
7. Employees: GET /employees, PATCH /employees/:id/role (ADMIN ONLY — the only
   endpoint in the whole system that can change a user's role)
8. Every mutating endpoint here writes an activity_logs row

XSDs to produce in /schemas: auth_request.xsd, auth_response.xsd, department.xsd,
category.xsd, employee.xsd

Permission: /employees/:id/role requires role=admin, enforced server-side via
DRF permission_classes — never trust a client-side "admin mode" flag.
```

### Frontend Agent — Member B
Attach: `AssetFlow_WebFlow.md` (Screens 1–3), `AssetFlow_PRD.md` §7.1–7.3

```
[Universal opener]

Task: Build Screen 1 (login/signup), Screen 2 shell, Screen 3 (org setup).

Build exactly:
1. LoginPage — email + password fields, "Forgot password" link, inline error state
2. SignupPage — email + password + name only, NO role field anywhere in the UI
   (confirms server-side hardcoding — don't even offer the illusion of choice)
3. DashboardPage shell — KPI cards with static/mock values for now
   (Available, Allocated, Active Bookings, Pending Transfers, Upcoming Returns),
   overdue banner placeholder, quick action buttons (non-functional stubs)
4. OrgSetupPage (admin-only route guard) — 3 tabs: Departments / Categories / Employee,
   `+ Add` button, tables matching the mockup columns (Head, Parent Dept, Status)
5. Employee tab: role-promotion action (dropdown: Employee → Dept Head / Asset Manager),
   calls PATCH /employees/:id/role

Wire all of the above to the real auth + org endpoints from Member A this phase.
Do not build Assets/Allocation/Booking screens yet.
```

### ⚠️ Verify Manually (do not trust agent output blindly)
```
XXE protection on the XML parser:
- resolve_entities=False
- no_network=True
- forbid_dtd=True (or equivalent)
Test with a crafted XML payload containing an external entity reference and
confirm the request is rejected, not resolved. This is the single highest-risk
item given XML is the entire input surface — check it before moving to Phase 2.
```

---

## PHASE 2 — Assets & Allocation/Transfer

### Backend Agent — Member A
Attach: `AssetFlow_TRD.md` §5.1, `AssetFlow_Schema.md` (assets, allocations, transfer_requests tables)

```
[Universal opener]

Task: Build asset registration/directory + allocation/transfer endpoints.

Build exactly:
1. POST /assets — register asset, server-generates tag as AF-%04d (immutable,
   reject if <tag> present in request), fields per Schema.md `assets` table
2. GET /assets?tag=&serial=&qr=&category=&status=&department=&location=
3. GET /assets/:id/history — allocation history + maintenance history, merged
   and sorted by date
4. POST /allocations
   - SELECT asset FOR UPDATE inside transaction
   - if not available → catch IntegrityError from the partial unique index,
     return 409 ALREADY_ALLOCATED with <current_holder> block
   - else create allocation, set asset.status='allocated', write activity_log
     + notification
5. POST /allocations/:id/return — capture checkin_notes, asset.status='available',
   allocation.status='returned'
6. POST /transfer-requests — from/to/reason
7. PATCH /transfer-requests/:id — approve (re-allocate + update history) / reject,
   role-gated to asset_manager/admin or scoped dept_head

XSDs: asset.xsd, allocation_request.xsd, transfer_request.xsd
```

### Frontend Agent — Member B
Attach: `AssetFlow_WebFlow.md` (Screens 4–5), `AssetFlow_PRD.md` §7.4–7.5

```
[Universal opener]

Task: Build Screen 4 (Assets) and Screen 5 (Allocation & Transfer).

Build exactly:
1. AssetsPage — search bar (tag/serial/QR), filters (Category/Status/Department),
   table (Tag/Name/Category/Status/Location), `+ Register Asset` form
2. AssetDetailPage — history timeline (allocation + maintenance)
3. AllocationPage — asset selector, on select:
   - if available: allocate form (holder, expected return date)
   - if already allocated: RED block banner "Already Allocated to {holder}
     ({dept}) — Direct re-allocation is blocked" + Transfer Request form
     (From read-only, To picker, Reason, Submit)
4. Allocation history log rendered below the form

Wire fully to the real endpoints. This screen's block-and-transfer behavior is
the #1 demo scenario — test it live with two different users before moving on.
```

### ⚠️ Verify Manually
```
Confirm `one_active_allocation_per_asset` exists in the DB (\d allocations)
and that a second allocation attempt on the same asset returns 409, not a
silent overwrite. Never ship this on an app-level-only check.
```

---

## PHASE 3 — Resource Booking

### Backend Agent — Member A
Attach: `AssetFlow_TRD.md` §5.2, `AssetFlow_Schema.md` (bookings table)

```
[Universal opener]

Task: Build resource booking endpoints.

Build exactly:
1. GET /bookings?resource_id=&date= — calendar view data for a resource
2. POST /bookings — resource_asset_id, start_time, end_time, purpose
   - Validate end_time > start_time in serializer
   - Insert inside transaction; on GiST exclusion constraint violation
     (IntegrityError), return 409 SLOT_UNAVAILABLE
   - On success, schedule a Celery reminder task 15 min before start_time
3. PATCH /bookings/:id — cancel / reschedule (reschedule re-runs the same
   overlap-constraint path)
4. Booking status auto-sync (upcoming→ongoing→completed) — write as a Celery
   Beat task stub now, wired fully in Phase 6

XSD: booking_request.xsd, booking.xsd
```

### Frontend Agent — Member B
Attach: `AssetFlow_WebFlow.md` (Screen 6), `AssetFlow_PRD.md` §7.6

```
[Universal opener]

Task: Build Screen 6 (Resource Booking).

Build exactly:
1. ResourceBookingPage — resource + date selector, hourly time-slot calendar
2. Existing bookings rendered solid ("Booked – {team} – {start} to {end}")
3. On conflicting request: dashed/red slot state ("Requested {start} to {end}
   – conflict – slot is unavailable"), `Book a Slot` disabled for that range
4. `Book a Slot` button — calls POST /bookings, shows the 409 SLOT_UNAVAILABLE
   error inline as the conflict state if it happens server-side too (don't
   only rely on client-side prediction)

This screen's overlap-block behavior is the #2 demo scenario — test overlapping
AND back-to-back (should succeed) bookings live before moving on.
```

### ⚠️ Verify Manually
```
Confirm the `no_overlap` GiST exclusion constraint is present on `bookings`
(\d bookings) and btree_gist extension is enabled. Fire two overlapping
requests concurrently (e.g. via a quick script) and confirm exactly one succeeds.
```

---

## PHASE 4 — Maintenance Management

### Backend Agent — Member A
Attach: `AssetFlow_TRD.md` §5.3, `AssetFlow_Schema.md` (maintenance_requests table)

```
[Universal opener]

Task: Build maintenance request workflow endpoints.

Build exactly:
1. POST /maintenance-requests — asset_id, issue, priority (enum: low/medium/
   high/critical), photo_url
2. PATCH /maintenance-requests/:id  with <action>approve|reject|assign|resolve</action>
   - approve: status=approved, approved_by=user, asset.status='under_maintenance'
     (single transaction)
   - reject: status=rejected
   - assign: status=technician_assigned, technician_name=<value>
   - resolve: status=resolved, resolved_at=now(), asset.status='available'
   Guard: approve/reject restricted to asset_manager/admin role
3. GET /maintenance-requests?asset_id=&status= — for kanban board data
4. Every transition writes activity_log + notification

XSD: maintenance_request.xsd
```

### Frontend Agent — Member B
Attach: `AssetFlow_WebFlow.md` (Screen 7), `AssetFlow_PRD.md` §7.7

```
[Universal opener]

Task: Build Screen 7 (Maintenance Management) as a kanban board.

Build exactly:
1. MaintenancePage — 5 columns: Pending, Approved, Technician Assigned,
   In Progress, Resolved
2. Cards show: asset tag, issue summary, technician (once assigned)
3. Column-appropriate action buttons per card (Approve/Reject on Pending,
   Assign Technician on Approved, Mark In Progress, Mark Resolved) — call
   PATCH /maintenance-requests/:id with the right <action>
4. Raise Request form (from Dashboard quick action or this screen directly)
5. Footnote text matching mockup: "Approving a card moves the asset to Under
   Maintenance, resolving returns it to Available"

Wire fully to real endpoints; confirm asset status flips are visible on
Screen 4 after approve/resolve.
```

---

## PHASE 5 — Asset Audit

### Backend Agent — Member A
Attach: `AssetFlow_TRD.md` §5.4, `AssetFlow_Schema.md` (audit_cycles, audit_auditors, audit_items, audit_discrepancy_reports tables)

```
[Universal opener]

Task: Build audit cycle endpoints.

Build exactly:
1. POST /audit-cycles — name, scope_department_id, scope_location, start_date,
   end_date; auto-creates audit_items for every asset in scope (status=pending)
2. POST /audit-cycles/:id/auditors — assign one or more users
3. PATCH /audit-items/:id — verification=verified|missing|damaged, notes
   - PERMISSION: only allowed if request.user is in audit_auditors for that
     cycle — check membership, don't just check role
   - PERMISSION: reject with 409 if the parent cycle.status='closed'
4. POST /audit-cycles/:id/close
   - Transaction: select all audit_items with verification='missing' for this
     cycle → bulk update assets.status='lost'
   - Build discrepancy report (missing + damaged items) → insert into
     audit_discrepancy_reports as XML (build via lxml.etree, store as text/XML
     in report_json-equivalent column, or store the raw XML string)
   - cycle.status='closed', closed_at=now()
   - Reject further audit_item PATCHes on this cycle from this point on

XSD: audit_cycle.xsd, audit_item.xsd, discrepancy_report.xsd
```

### Frontend Agent — Member B
Attach: `AssetFlow_WebFlow.md` (Screen 8), `AssetFlow_PRD.md` §7.8

```
[Universal opener]

Task: Build Screen 8 (Asset Audit).

Build exactly:
1. AuditPage — cycle banner (scope, date range, assigned auditors)
2. Checklist table: Asset / Expected Location / Verification (tri-state
   selector: Verified / Missing / Damaged) — only editable if current user is
   an assigned auditor for this cycle
3. Flag banner: "N assets flagged – discrepancy report generated automatically"
   (computed from missing+damaged count client-side, confirmed by server response)
4. `Close Audit Cycle` button — calls POST /audit-cycles/:id/close, then
   disables further edits on this cycle's checklist

Wire fully to real endpoints; confirm closing a cycle with a "missing" item
flips that asset's status to Lost (checkable on Screen 4).
```

---

## PHASE 6 — Dashboard, Reports & Notifications

### Backend Agent — Member A
Attach: `AssetFlow_TRD.md` §5, §7; `AssetFlow_PRD.md` §7.2, §7.9, §7.10

```
[Universal opener]

Task: Build dashboard KPIs, reports, notifications, and wire up Celery Beat.

Build exactly:
1. GET /dashboard/kpis — Available, Allocated, Active Bookings, Pending
   Transfers, Upcoming Returns, Maintenance Today (all scoped by role/dept
   per RBAC rules), plus overdue-returns list and recent activity feed
2. GET /reports/utilization, /reports/maintenance-frequency, /reports/idle-assets,
   /reports/retirement-watch, /reports/allocation-summary, /reports/booking-heatmap
3. GET /notifications?type=alerts|approvals|bookings|all, PATCH /notifications/:id/read
4. Celery Beat schedule (celery.py):
   - check_overdue_allocations — daily 00:05
   - sync_booking_status — every 5 min
   - send_booking_reminders — every 5 min
   - check_maintenance_sla — daily
5. Every notification-triggering event (asset assigned, transfer approved,
   booking confirmed/cancelled/reminder, maintenance approved/rejected,
   overdue return, audit discrepancy) must already be writing to
   notifications + activity_logs from earlier phases — this phase just
   surfaces them via the endpoints above, it doesn't re-implement the writes

XSD: kpi_summary.xsd, notification.xsd, report_*.xsd (one per report type)
```

### Frontend Agent — Member B
Attach: `AssetFlow_WebFlow.md` (Screens 2, 9, 10), `AssetFlow_PRD.md` §7.9–7.10

```
[Universal opener]

Task: Wire Screen 2 to live data, build Screen 9 (Reports) and Screen 10 (Notifications).

Build exactly:
1. DashboardPage — replace mock KPI values with GET /dashboard/kpis, overdue
   banner from real data, recent activity feed
2. ReportsPage — bar chart (utilization by department), line chart (maintenance
   frequency), most-used/idle-asset lists, maintenance/retirement watch list,
   `Export Report` button (CSV/PDF download)
3. NotificationsPage — filter tabs (All/Alerts/Approvals/Bookings), feed rows
   with relative timestamps, mark-as-read on click

Confirm actions from Phases 2–5 (allocate, book, maintenance approve, audit
flag) actually produce visible notifications here.
```

### ⚠️ Verify Manually
```
Celery Beat tasks are a common silent-failure point. After deploying, check
worker + beat logs directly and confirm each scheduled task has fired at least
once (don't just trust that the schedule config "looks right").
```

---

## PHASE 7 — Integration, Bug Bash & Demo Rehearsal

### Combined Prompt — Member A + Member B (pair/rotate)
Attach: ALL SOT docs

```
[Universal opener]

Task: Seed demo data and run a full cross-role smoke test.

Do exactly:
1. Write a seed script (Django management command or fixture) creating:
   - 1 admin, 1 asset manager, 1 dept head, 2 employees across 2 departments
   - ~15 assets across 3 categories, a mix of statuses including a few
     already-allocated and a few bookable resources
   - 1 active booking on a bookable resource (to demonstrate the overlap block)
   - 1 open maintenance request in each kanban column
   - 1 open audit cycle with a couple of items pre-verified
2. Walk through the "Basic Workflow" end-to-end story (AssetFlow_WebFlow.md §5)
   logged in as each of the 4 roles in turn — confirm nav visibility and data
   scoping match the RBAC matrix (AssetFlow_PRD.md §5 / Architecture.md §7)
3. Explicitly re-test the two hard-blocked scenarios live:
   - allocate an already-allocated asset → 409 + transfer request path
   - book an overlapping slot → 409 + valid back-to-back slot succeeds
4. Fix any last-mile XML/XSD mismatches between frontend and backend found
   during the walkthrough
5. Time the full demo script and trim to fit the presentation slot

Report back: list of bugs found + fixed, and confirm both hard-blocked
scenarios are demo-ready.
```

---

## PHASE 8 — Hardening Audit (if time remains)

### Security Audit — Member A (or whichever agent session is freshest)
Attach: ALL SOT docs

```
[Universal opener]

Task: Security audit of the AssetFlow backend.

Review every route and verify:

1. XML SAFETY
   Every parser instance (lxml/xmlschema) has resolve_entities=False,
   no_network=True, DTD/entity expansion disabled. Show me every place
   XML is parsed and confirm each one.

2. RBAC & DEPT SCOPING
   Every dept_head/employee-facing list/detail query filters by department_id.
   Org Setup routes are admin-only. Maintenance approve/reject and Audit
   cycle create/close are asset_manager/admin-only. Show me the permission
   classes on each route.

3. THE TWO HARD-BLOCKED CONSTRAINTS
   Confirm `one_active_allocation_per_asset` and `no_overlap` still exist in
   the DB and that both API paths catch the resulting IntegrityError rather
   than only checking application-side.

4. ROLE INTEGRITY
   Confirm signup can never set role to anything but employee, and that
   PATCH /employees/:id/role is the ONLY route in the codebase that writes
   to users.role.

5. SENSITIVE DATA IN LOGS
   Scan for any log statement that might contain: password, password_hash,
   JWT tokens, refresh tokens. Flag any found.

6. IMMUTABLE AUDIT TRAIL
   Confirm activity_logs has no update/delete endpoint anywhere.

Report: list of issues found, severity (critical/high/medium), and fix for each.
```

### Database Performance Check
```
Run EXPLAIN ANALYZE on these queries and report slow ones:
1. SELECT * FROM assets WHERE status = ? AND department_id = ? ORDER BY created_at DESC LIMIT 20
2. SELECT * FROM allocations WHERE asset_id = ? AND status = 'active'
3. SELECT * FROM bookings WHERE resource_asset_id = ? AND tstzrange(start_time, end_time) && tstzrange(?, ?)
4. SELECT * FROM audit_items WHERE audit_cycle_id = ? AND verification IN ('missing','damaged')
5. SELECT * FROM notifications WHERE user_id = ? AND read = false ORDER BY created_at DESC LIMIT 20
```

---

## References
- Architecture: `AssetFlow_Architecture.md`
- PRD: `AssetFlow_PRD.md`
- TRD: `AssetFlow_TRD.md`
- Schema: `AssetFlow_Schema.md`
- Web flow: `AssetFlow_WebFlow.md`
- Timeline: `AssetFlow_Timeline.md`
