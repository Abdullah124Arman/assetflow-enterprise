# AssetFlow — Project Timeline (2-person team, 8-hour build)

Version 1.0 | Stack: Python/Django/XML backend + React frontend (per TRD v2.0)

**Split:** Member A = Backend (Django/DRF, XML API, DB, Celery). Member B = Frontend (React) + integration. Both work the same feature per phase in parallel so the API contract (XSD) is agreed before either starts, then they meet at each checkpoint to wire real endpoints in.

## 1. Timeline (Gantt)
```mermaid
gantt
    dateFormat  HH:mm
    axisFormat  %H:%M
    section Setup
    Repo/Docker/DB/XSD skeleton (both)       :s0, 00:00, 30m
    section Phase 1 - Auth & Org Setup
    Backend: auth, org endpoints (A)         :a1, 00:30, 60m
    Frontend: login/signup/dashboard shell, org setup UI (B) :b1, 00:30, 60m
    Wire + verify (both)                     :c1, after a1, 15m
    section Phase 2 - Assets & Allocation
    Backend: assets, allocation, transfer, double-block (A) :a2, 01:45, 90m
    Frontend: Screens 4 & 5 (B)              :b2, 01:45, 90m
    Wire + verify (both)                     :c2, after a2, 15m
    section Phase 3 - Resource Booking
    Backend: bookings, overlap constraint (A) :a3, 03:30, 60m
    Frontend: Screen 6 calendar (B)          :b3, 03:30, 60m
    Wire + verify (both)                     :c3, after a3, 15m
    section Phase 4 - Maintenance
    Backend: maintenance workflow (A)        :a4, 04:45, 60m
    Frontend: Screen 7 kanban (B)            :b4, 04:45, 60m
    Wire + verify (both)                     :c4, after a4, 15m
    section Phase 5 - Audit
    Backend: audit cycles, discrepancy report (A) :a5, 06:00, 60m
    Frontend: Screen 8 (B)                   :b5, 06:00, 60m
    Wire + verify (both)                     :c5, after a5, 10m
    section Phase 6 - Dashboard, Notifications, Reports
    Backend: KPI/report aggregation, Celery jobs, notifications (A) :a6, 07:10, 45m
    Frontend: Screens 2, 9, 10 wiring (B)    :b6, 07:10, 45m
    section Phase 7 - Integration & Demo
    Seed data, bug bash, demo rehearsal (both) :c7, 07:55, 30m
```

## 2. Phase-by-Phase Breakdown

### Phase 0 — Setup (00:00–00:30, both)
- Repo scaffold: `/backend` (Django project), `/frontend` (Vite React)
- `docker-compose.yml`: api, worker, beat, redis, db, web
- Apply DB schema (`AssetFlow_Schema.md`) via Django migrations
- Agree XSD skeletons for the first 3 resources (user, department, asset) so both sides code against the same contract
- **Checkpoint:** `docker-compose up` boots all services; empty login page loads

### Phase 1 — Auth & Org Setup (00:30–01:45)
- **A:** signup/login/forgot-password endpoints, JWT issuance, `role=employee` hardcoding, department/category/employee CRUD, role-promotion endpoint
- **B:** Screen 1 (login/signup), Screen 2 shell (static KPI cards), Screen 3 (org setup tabs) built against XSD stubs
- **Wire:** connect Screen 1 & 3 to real endpoints
- **Checkpoint:** can sign up, log in, admin can create a department and promote a user

### Phase 2 — Assets & Allocation/Transfer (01:45–03:30)
- **A:** asset registration/search endpoints, allocation endpoint + double-allocation block (partial unique index + 409 handling), transfer request workflow, return flow
- **B:** Screen 4 (directory, search/filter, register form), Screen 5 (allocate, block banner, transfer form, history)
- **Wire:** allocate an asset, attempt re-allocation, confirm block + transfer request path works end-to-end
- **Checkpoint:** the double-allocation demo scenario works live

### Phase 3 — Resource Booking (03:30–04:45)
- **A:** booking endpoint, GiST exclusion constraint, conflict response, cancel/reschedule
- **B:** Screen 6 calendar/slot UI, conflict state (dashed red slot)
- **Wire:** book overlapping slots, confirm rejection + valid back-to-back booking succeeds
- **Checkpoint:** overlap-block demo scenario works live

### Phase 4 — Maintenance (04:45–06:00)
- **A:** maintenance request endpoints, approval/reject/assign/resolve transitions, asset status side-effects
- **B:** Screen 7 kanban board, drag/action buttons per column
- **Wire:** raise → approve → assign → resolve, confirm asset status flips at approve/resolve
- **Checkpoint:** full maintenance lifecycle demoable

### Phase 5 — Audit (06:00–07:10)
- **A:** audit cycle CRUD, auditor assignment, item verification endpoint (auditor-scoped), close-cycle transaction (discrepancy report + bulk Lost update)
- **B:** Screen 8 (cycle banner, checklist, flagged banner, close button)
- **Wire:** create cycle, verify items, close cycle, confirm missing→Lost + report generated
- **Checkpoint:** audit demo scenario works live

### Phase 6 — Dashboard, Reports, Notifications (07:10–07:55)
- **A:** `/dashboard/kpis` aggregation, `/reports/*` endpoints, Celery Beat jobs (overdue, reminders, SLA), notification writes on every trigger event
- **B:** Screen 2 real KPI wiring + recent activity, Screen 9 charts/lists/export button, Screen 10 notification feed + filters
- **Checkpoint:** dashboard reflects live data; notifications populate from prior phases' actions

### Phase 7 — Integration, Bug Bash, Demo Rehearsal (07:55–08:00 buffer→wrap)
- Seed realistic demo data across all modules
- Both: cross-browser/role smoke pass (Admin, Asset Manager, Dept Head, Employee)
- Rehearse the "Basic Workflow" end-to-end story (see WebFlow §5) as the demo script
- Fix any last-mile UI/API mismatches

## 3. Ownership Summary
| Track | Owner | Scope |
|---|---|---|
| Backend (Django/DRF, XML, XSD, DB, Celery) | Member A | All modules' API + business rules + background jobs |
| Frontend (React) + integration | Member B | All 10 screens + wiring to live API each phase |
| Setup, demo data, rehearsal | Both | Phase 0 and Phase 7 |

## 4. Risk Buffer
No slack is built into phases 1–6 (60–90 min each, tight). If a phase overruns:
1. Cut Reports charts to static/mock data first (lowest demo risk)
2. Cut Notifications filters (All/Alerts/Approvals/Bookings) down to a single unfiltered feed
3. Never cut the double-allocation block or booking-overlap block — these are the two explicitly-graded conflict scenarios in the problem statement

## 5. References
- Architecture: `AssetFlow_Architecture.md`
- PRD: `AssetFlow_PRD.md`
- TRD: `AssetFlow_TRD.md`
- Schema: `AssetFlow_Schema.md`
- Web flow: `AssetFlow_WebFlow.md`
