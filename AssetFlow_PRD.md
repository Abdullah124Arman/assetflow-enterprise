# Product Requirements Document — AssetFlow

**Enterprise Asset & Resource Management System**
Version 1.0 | Hackathon build (8 hrs)

## 1. Overview
AssetFlow is a centralized ERP module for tracking, allocating, and maintaining physical assets and shared resources — industry-agnostic (offices, schools, hospitals, factories, agencies). Replaces spreadsheets/paper logs with structured lifecycles, booking, maintenance, and audit workflows. Excludes purchasing, invoicing, accounting.

## 2. Problem Statement
Organizations lack real-time visibility into who holds which asset, its condition, and its location. Manual tracking causes double-bookings, lost assets, untracked maintenance, and no audit trail.

## 3. Goals
- Single source of truth for asset state (Available, Allocated, Reserved, Under Maintenance, Lost, Retired, Disposed)
- Zero double-allocation of a single asset
- Zero overlapping resource bookings
- All maintenance work gated behind approval
- Every audit cycle produces a discrepancy report automatically
- Every state change is visible via dashboard/notifications without manual digging

## 4. Success Metrics
| Metric | Target |
|---|---|
| Double-allocation incidents | 0 |
| Booking overlap incidents | 0 |
| Maintenance requests with approval step skipped | 0 |
| Overdue returns surfaced automatically | 100% |
| Audit cycles producing auto-discrepancy report | 100% |

## 5. User Roles
| Role | Core Responsibilities |
|---|---|
| Admin | Departments, categories, audit cycles, role promotion, org-wide analytics |
| Asset Manager | Register/allocate assets, approve transfers/maintenance/audit resolution, approve returns |
| Department Head | View dept assets, approve dept allocation/transfer requests, book resources for dept |
| Employee | View own assets, book resources, raise maintenance requests, initiate return/transfer |

Role assignment happens only via Admin → Employee Directory. Signup never grants elevated roles.

## 6. Scope

**In scope**
- Auth (employee-only signup, admin-driven role promotion)
- Org setup: departments (with hierarchy), categories (custom fields), employee directory
- Asset registration, directory, search/filter, lifecycle, history
- Allocation with double-allocation block + transfer request flow
- Resource booking with overlap validation
- Maintenance approval workflow (kanban: Pending→Approved→Technician Assigned→In Progress→Resolved)
- Audit cycles: scope, auditors, per-item verification, auto discrepancy report, close/lock
- Reports: utilization, maintenance frequency, idle/most-used, retirement watch, booking heatmap, export
- Notifications + full activity log
- KPI dashboard

**Out of scope**
- Purchasing/procurement, invoicing, accounting integration
- Multi-tenant billing
- Mobile native apps (responsive web only)
- QR code hardware scanning (QR field supported, scanning device integration not required)

## 7. Functional Requirements

### 7.1 Auth (Screen 1)
- FR1.1 Signup creates Employee role only, no role field exposed
- FR1.2 Login via email/password, session token (JWT), "forgot password" flow
- FR1.3 Invalid/expired session redirects to login

### 7.2 Dashboard (Screen 2)
- FR2.1 KPI cards: Available, Allocated, Active Bookings, Pending Transfers, Upcoming Returns, Maintenance Today
- FR2.2 Overdue returns shown in a distinct (flagged) section, separate from upcoming
- FR2.3 Quick actions: Register Asset, Book Resource, Raise Maintenance Request
- FR2.4 Recent activity feed (latest N events)

### 7.3 Organization Setup — Admin only (Screen 3)
- FR3.1 Departments: create/edit/deactivate, assign head, optional parent department, status
- FR3.2 Categories: create/edit, optional custom fields (e.g. warranty period)
- FR3.3 Employee Directory: list with dept/role/status; promote Employee → Dept Head / Asset Manager (only entry point for role change)
- FR3.4 Department/category edits propagate to picklists used in Screens 4–8

### 7.4 Asset Registration & Directory (Screen 4)
- FR4.1 Register asset: name, category, auto-tag (AF-000x), serial number, acquisition date/cost, condition, location, photo/docs, bookable flag
- FR4.2 Search/filter by tag, serial, QR code, category, status, department, location
- FR4.3 Lifecycle status badge per asset (7 states)
- FR4.4 Per-asset history: allocation history + maintenance history

### 7.5 Allocation & Transfer (Screen 5)
- FR5.1 Allocate asset to employee/department with optional expected return date
- FR5.2 Block re-allocation of an already-allocated asset; show current holder; offer Transfer Request instead
- FR5.3 Transfer workflow: Requested → Approved (Asset Manager/Dept Head) → Re-allocated, history auto-updated
- FR5.4 Return flow: mark returned, capture condition check-in notes, asset → Available
- FR5.5 Overdue allocations (past expected return) auto-flagged to Dashboard + Notifications

### 7.6 Resource Booking (Screen 6)
- FR6.1 Calendar view of a resource's existing bookings
- FR6.2 Overlap validation: reject any request overlapping an existing Upcoming/Ongoing booking on same resource; back-to-back slots allowed
- FR6.3 Booking status: Upcoming, Ongoing, Completed, Cancelled
- FR6.4 Cancel/reschedule; reminder notification before slot start

### 7.7 Maintenance Management (Screen 7)
- FR7.1 Raise request: asset, issue description, priority, photo
- FR7.2 Kanban workflow: Pending → Approved/Rejected (Asset Manager) → Technician Assigned → In Progress → Resolved
- FR7.3 Asset auto-flips to Under Maintenance on approval, back to Available on resolution
- FR7.4 Maintenance history retained per asset

### 7.8 Asset Audit (Screen 8)
- FR8.1 Create audit cycle: scope (dept/location), date range, assign auditor(s)
- FR8.2 Auditor marks each in-scope asset: Verified / Missing / Damaged
- FR8.3 System auto-generates discrepancy report for flagged items
- FR8.4 Close cycle: locks cycle, bulk-updates asset status (e.g. confirmed-missing → Lost)
- FR8.5 Audit history retained per cycle

### 7.9 Reports & Analytics (Screen 9)
- FR9.1 Utilization by department (chart)
- FR9.2 Maintenance frequency (by asset/category, trend chart)
- FR9.3 Most-used vs idle assets lists
- FR9.4 Assets due for maintenance / nearing retirement
- FR9.5 Department-wise allocation summary
- FR9.6 Booking heatmap (peak usage windows)
- FR9.7 Export report (CSV/PDF)

### 7.10 Activity Logs & Notifications (Screen 10)
- FR10.1 Notification feed filterable by type (All/Alerts/Approvals/Bookings)
- FR10.2 Notification triggers: Asset Assigned, Maintenance Approved/Rejected, Booking Confirmed/Cancelled/Reminder, Transfer Approved, Overdue Return, Audit Discrepancy Flagged
- FR10.3 Full activity log: who did what, when, across all modules

## 8. Non-Functional Requirements
- **Security**: role-based access control enforced server-side on every endpoint, not just UI hiding; passwords hashed; JWT with expiry/refresh
- **Data integrity**: allocation, booking overlap, and audit-close operations must be transactional
- **Usability**: responsive layout, consistent nav across all 10 screens, status shown via color-coded badges
- **Performance**: search/filter results under 1s for typical dataset sizes
- **Auditability**: every state-changing action logged with actor + timestamp

## 9. Assumptions & Constraints
- Single organization per deployment (no multi-tenancy) for hackathon scope
- QR code field stored as data only, no scanner hardware integration required
- File uploads (photos/docs) stored in object storage, not DB
- 8-hour build window — see milestone plan below

## 10. Milestone Plan (8-hour build)
| Hrs | Deliverable |
|---|---|
| 0–1 | Auth + role model + DB schema scaffolded |
| 1–2.5 | Org Setup (departments, categories, employee directory) |
| 2.5–4 | Asset registration/directory + allocation/transfer with double-block |
| 4–5.5 | Resource booking with overlap validation |
| 5.5–6.5 | Maintenance kanban workflow |
| 6.5–7 | Audit cycles + discrepancy report |
| 7–7.5 | Dashboard KPIs + notifications/activity log |
| 7.5–8 | Reports & analytics, polish, demo run-through |

## 11. Open Questions
- Multi-department shared assets: allowed, or one department owner only?
- Retention policy for activity logs?
- Export format priority: CSV vs PDF for reports?

## 12. References
- Architecture: `AssetFlow_Architecture.md`
- Mockup: Excalidraw link in problem statement
