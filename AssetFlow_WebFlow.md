# AssetFlow — Web Flow

Version 1.0 | Maps every screen, component, and navigation path from the problem statement + mockup.

## 1. Global Shell
Persistent left sidebar (Screens 2–10), same order everywhere:
`Dashboard | Organization Setup* | Assets | Allocation & Transfer | Resource Booking | Maintenance | Audit | Reports | Notifications`
`*Organization Setup` visible/enabled to **Admin only**; other roles see remaining items, scoped by RBAC (see PRD §5, TRD §6).

Top-level unauthenticated route: **Screen 1 (Login/Signup)**. All other screens require a valid session; expired/invalid session → redirect to Screen 1.

## 2. Screen Inventory (component-level)

### Screen 1 — Login / Signup
- Email field, Password field, "Forgot password" link
- "Create Account" (signup) → creates **Employee** account only, no role picker ("admin roles assigned later")
- On success → Screen 2 (Dashboard)

### Screen 2 — Dashboard
- KPI cards: Available, Allocated, Active Bookings, Pending Transfers, Upcoming Returns
- Overdue banner: "N assets overdue for return – flagged for follow-up" (distinct styling, red)
- Quick actions: `+ Register Asset` → Screen 4, `Book Resource` → Screen 6, `Raise Requests` → Screen 7
- Recent Activity feed (latest events, same data source as Screen 10)

### Screen 3 — Organization Setup (Admin only)
- Tabs: Departments / Categories / Employee, `+ Add`
- Departments table: Head, Parent Dept, Status (Active/Inactive)
- Note: edits here drive picklists on Screen 4 (category/dept filters) and Screen 5 (allocation dept picker)
- Employee tab is the **only** place roles are promoted (Employee → Dept Head / Asset Manager)

### Screen 4 — Asset Registration & Directory
- Search bar (tag / serial / QR code) + `+ Register Asset`
- Filters: Category, Status, Department
- Table: Tag, Name, Category, Status, Location
- Row click → asset detail (history: allocation + maintenance)

### Screen 5 — Asset Allocation & Transfer
- Asset selector
- **Block state**: red banner "Already Allocated to {holder} ({dept}) – Direct re-allocation is blocked – submit a transfer request below"
- Transfer Request form: From (current holder, read-only) / To (employee picker) / Reason / `Submit Request`
- Allocation history log (chronological, allocate/return entries)

### Screen 6 — Resource Booking
- Resource + date selector
- Time-slot calendar (hourly rows)
- Existing booking shown solid (e.g. "Booked – Procurement Team – 9 to 10")
- Conflicting request shown dashed/red: "Requested 9:30 to 10:30 – conflict – slot is unavailable"
- `Book a Slot` (only enabled for non-overlapping ranges)

### Screen 7 — Maintenance Management
- Kanban board, columns = workflow states: **Pending → Approved → Technician Assigned → In Progress → Resolved**
- Each card: asset tag, issue summary, technician (once assigned)
- Footnote: "Approving a card moves the asset to Under Maintenance, resolving returns it to Available"

### Screen 8 — Asset Audit
- Cycle banner: scope (dept/date range), assigned auditors
- Checklist table: Asset, Expected Location, Verification (Verified / Missing / Damaged — tri-state selector)
- Flag banner: "N assets flagged – discrepancy report generated automatically"
- `Close Audit Cycle` (locks cycle, bulk-updates flagged-missing assets to Lost)

### Screen 9 — Reports & Analytics
- Charts: Utilization by department (bar), Maintenance Frequency (line)
- Lists: Most Used Assets, Idle Assets, Assets Due for Maintenance / Nearing Retirement
- `Export Report`

### Screen 10 — Activity Logs & Notifications
- Filter tabs: All / Alerts / Approvals / Bookings
- Feed rows: message + relative timestamp (e.g. "Overdue return: AF-0021 was due 3 days ago – 1d ago")

## 3. Navigation Map

```mermaid
flowchart LR
  Login[Screen 1: Login/Signup] -->|auth success| Dash[Screen 2: Dashboard]
  Dash --> Org[Screen 3: Org Setup *Admin*]
  Dash --> Assets[Screen 4: Assets]
  Dash --> Alloc[Screen 5: Allocation & Transfer]
  Dash --> Booking[Screen 6: Resource Booking]
  Dash --> Maint[Screen 7: Maintenance]
  Dash --> Audit[Screen 8: Audit]
  Dash --> Reports[Screen 9: Reports]
  Dash --> Notif[Screen 10: Notifications]
  Assets -->|register/select asset| Alloc
  Assets -->|select bookable asset| Booking
  Dash -->|quick action| Assets
  Dash -->|quick action| Booking
  Dash -->|quick action| Maint
  Org -->|edits picklists used by| Assets
  Org -->|edits picklists used by| Alloc
```

## 4. Key User Flows

### 4.1 Signup / Login
```mermaid
flowchart TD
  A[Visit app] --> B{Have account?}
  B -->|No| C[Create Account: email+password]
  C --> D[Account created as role=Employee]
  D --> E[Login]
  B -->|Yes| E
  E --> F{Credentials valid?}
  F -->|No| E
  F -->|Yes| G[Dashboard]
  E --> H[Forgot password] --> I[Reset link] --> E
```

### 4.2 Role Promotion (Admin path)
```mermaid
flowchart TD
  A[Admin: Org Setup > Employee tab] --> B[Select employee]
  B --> C[Promote to Dept Head or Asset Manager]
  C --> D[Role updated; user re-authenticates or token refreshes]
```

### 4.3 Asset Registration → Allocation
```mermaid
flowchart TD
  A[Asset Manager: Assets > + Register Asset] --> B[Fill details, save]
  B --> C[Asset status = Available]
  C --> D[Allocation & Transfer: select asset]
  D --> E{Already allocated?}
  E -->|No| F[Allocate to employee/dept]
  F --> G[Asset status = Allocated]
  E -->|Yes| H[Blocked: show current holder]
  H --> I[Submit Transfer Request]
  I --> J{Approved by Asset Mgr/Dept Head?}
  J -->|Yes| K[Re-allocated, history updated]
  J -->|No| L[Stays with current holder]
```

### 4.4 Return Flow
```mermaid
flowchart TD
  A[Holder or Asset Mgr: mark returned] --> B[Capture condition check-in notes]
  B --> C[Asset status -> Available]
  C --> D[Allocation status -> returned]
```

### 4.5 Resource Booking
```mermaid
flowchart TD
  A[Any role: Resource Booking > select resource+date] --> B[Pick time slot]
  B --> C{Overlaps existing Upcoming/Ongoing booking?}
  C -->|Yes| D[Reject: slot unavailable]
  C -->|No| E[Booking created: status=Upcoming]
  E --> F[Reminder sent before start]
  F --> G[Auto-transitions: Upcoming -> Ongoing -> Completed]
  E --> H[Optional: Cancel/Reschedule]
```

### 4.6 Maintenance Workflow
```mermaid
flowchart TD
  A[Employee: Raise maintenance request] --> B[Pending]
  B --> C{Asset Manager decision}
  C -->|Approve| D[Approved; Asset -> Under Maintenance]
  C -->|Reject| E[Rejected; asset unchanged]
  D --> F[Technician Assigned]
  F --> G[In Progress]
  G --> H[Resolved; Asset -> Available]
```

### 4.7 Audit Cycle
```mermaid
flowchart TD
  A[Admin/Asset Mgr: create Audit Cycle] --> B[Set scope: dept/location + date range]
  B --> C[Assign auditor(s)]
  C --> D[Auditors verify each in-scope asset]
  D --> E{Verification}
  E -->|Verified| F[No action]
  E -->|Missing or Damaged| G[Flagged for discrepancy report]
  G --> H[Report auto-generated]
  H --> I[Close Audit Cycle]
  I --> J[Cycle locked; confirmed-missing assets -> Lost]
```

### 4.8 Notifications Trigger Map
```mermaid
flowchart LR
  Alloc[Allocation created] --> N1[Asset Assigned]
  Transfer[Transfer approved] --> N2[Transfer Approved]
  Booking[Booking created/cancelled] --> N3[Booking Confirmed/Cancelled]
  Reminder[Cron: booking soon] --> N4[Booking Reminder]
  MaintApprove[Maintenance approved/rejected] --> N5[Maintenance Approved/Rejected]
  Overdue[Cron: past expected_return_date] --> N6[Overdue Return Alert]
  AuditFlag[Audit item = missing/damaged] --> N7[Audit Discrepancy Flagged]
  N1 & N2 & N3 & N4 & N5 & N6 & N7 --> Feed[Screen 10: Notifications feed]
  N1 & N2 & N3 & N4 & N5 & N6 & N7 --> Log[activity_logs]
```

## 5. End-to-End Organizational Flow (matches problem statement "Basic Workflow")
```mermaid
flowchart TD
  A[Admin: setup departments, categories, promote roles] --> B[Asset Manager: register asset -> Available]
  B --> C{Allocate or mark bookable?}
  C -->|Allocate| D[Allocation flow - 4.3]
  C -->|Bookable resource| E[Booking flow - 4.5]
  D --> F[Overdue returns auto-flagged]
  D --> G{Needs repair?}
  G -->|Yes| H[Maintenance flow - 4.6]
  H --> I[Asset back to Available on resolve]
  A --> J[Periodic Audit Cycle - 4.7]
  J --> K[Discrepancy report + Lost status updates]
  F & H & J & E --> L[Notifications + Activity Logs + Dashboard KPIs]
```

## 6. Role-Scoped Navigation Differences
| Screen | Admin | Asset Manager | Dept Head | Employee |
|---|---|---|---|---|
| Dashboard | full org KPIs | full org KPIs | dept-scoped KPIs | own-item KPIs |
| Org Setup | full access | ❌ hidden | ❌ hidden | ❌ hidden |
| Assets | full | register/edit | view dept assets | view own/dept assets |
| Allocation & Transfer | full | allocate + approve transfer | approve dept transfers | request transfer/return only |
| Resource Booking | full | full | full | book/cancel own |
| Maintenance | full | approve/assign | raise + view dept | raise + view own |
| Audit | create/close cycles | create/close cycles, verify if assigned | view if in scope | verify only if assigned as auditor |
| Reports | org-wide | org-wide | dept-scoped | own-only (limited) |
| Notifications | all org events | all org events | dept-scoped | own-scoped |

## 7. References
- Architecture: `AssetFlow_Architecture.md`
- Product requirements: `AssetFlow_PRD.md`
- Technical requirements: `AssetFlow_TRD.md`
- Schema: `AssetFlow_Schema.md`
