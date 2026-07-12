# AssetFlow — Full Database Schema

Version 1.0 | PostgreSQL 15 | Companion to TRD v1.0

All tables use `UUID DEFAULT gen_random_uuid()` as PK unless noted. Timestamps are `TIMESTAMPTZ`.

## 0. Extensions & Enums

```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "btree_gist"; -- booking overlap exclusion constraint

CREATE TYPE user_role AS ENUM ('admin','asset_manager','dept_head','employee');
CREATE TYPE status_active_inactive AS ENUM ('active','inactive');
CREATE TYPE asset_status AS ENUM ('available','allocated','reserved','under_maintenance','lost','retired','disposed');
CREATE TYPE holder_type AS ENUM ('employee','department');
CREATE TYPE allocation_status AS ENUM ('active','returned','overdue');
CREATE TYPE transfer_status AS ENUM ('pending','approved','rejected');
CREATE TYPE booking_status AS ENUM ('upcoming','ongoing','completed','cancelled');
CREATE TYPE maintenance_priority AS ENUM ('low','medium','high','critical');
CREATE TYPE maintenance_status AS ENUM ('pending','approved','rejected','technician_assigned','in_progress','resolved');
CREATE TYPE audit_cycle_status AS ENUM ('open','closed');
CREATE TYPE audit_verification AS ENUM ('pending','verified','missing','damaged');
CREATE TYPE attachment_entity AS ENUM ('asset','maintenance_request','audit_item');
CREATE TYPE report_type AS ENUM ('utilization','maintenance_frequency','idle_assets','retirement_watch','allocation_summary','booking_heatmap');
```

## 1. Identity & Organization

```sql
CREATE TABLE departments (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name            TEXT NOT NULL,
  head_id         UUID REFERENCES users(id),         -- FK added after users table (circular)
  parent_dept_id  UUID REFERENCES departments(id),
  status          status_active_inactive NOT NULL DEFAULT 'active',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE users (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name            TEXT NOT NULL,
  email           TEXT NOT NULL UNIQUE,
  password_hash   TEXT NOT NULL,
  role            user_role NOT NULL DEFAULT 'employee',
  department_id   UUID REFERENCES departments(id),
  status          status_active_inactive NOT NULL DEFAULT 'active',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE departments ADD CONSTRAINT fk_dept_head FOREIGN KEY (head_id) REFERENCES users(id);

CREATE TABLE asset_categories (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name            TEXT NOT NULL UNIQUE,
  custom_fields   JSONB NOT NULL DEFAULT '[]',  -- schema: [{key, label, type, required}]
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## 2. Auth Support

```sql
CREATE TABLE refresh_tokens (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash      TEXT NOT NULL,
  expires_at      TIMESTAMPTZ NOT NULL,
  revoked         BOOLEAN NOT NULL DEFAULT false,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE password_reset_tokens (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash      TEXT NOT NULL,
  expires_at      TIMESTAMPTZ NOT NULL,
  used            BOOLEAN NOT NULL DEFAULT false,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## 3. Assets

```sql
CREATE TABLE assets (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tag                 TEXT NOT NULL UNIQUE,          -- auto-generated AF-0001
  name                TEXT NOT NULL,
  category_id         UUID NOT NULL REFERENCES asset_categories(id),
  serial_number       TEXT,
  qr_code             TEXT UNIQUE,
  acquisition_date    DATE,
  acquisition_cost    NUMERIC(12,2),
  condition           TEXT,                          -- e.g. good/fair/poor
  location            TEXT,
  status              asset_status NOT NULL DEFAULT 'available',
  is_bookable         BOOLEAN NOT NULL DEFAULT false,
  department_id       UUID REFERENCES departments(id),
  custom_field_values JSONB NOT NULL DEFAULT '{}',   -- instance values matching category.custom_fields
  photo_url           TEXT,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_assets_status ON assets(status);
CREATE INDEX idx_assets_category ON assets(category_id);
CREATE INDEX idx_assets_department ON assets(department_id);
CREATE INDEX idx_assets_location ON assets(location);
CREATE INDEX idx_assets_serial ON assets(serial_number);
```

## 4. Allocation & Transfer

```sql
CREATE TABLE allocations (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id              UUID NOT NULL REFERENCES assets(id),
  holder_type           holder_type NOT NULL,
  holder_id             UUID NOT NULL,               -- users.id or departments.id depending on holder_type
  allocated_date        DATE NOT NULL DEFAULT CURRENT_DATE,
  expected_return_date  DATE,
  actual_return_date    DATE,
  status                allocation_status NOT NULL DEFAULT 'active',
  checkin_notes         TEXT,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enforces the double-allocation block at DB level
CREATE UNIQUE INDEX one_active_allocation_per_asset
  ON allocations(asset_id) WHERE status = 'active';

CREATE INDEX idx_allocations_holder ON allocations(holder_type, holder_id);
CREATE INDEX idx_allocations_overdue ON allocations(expected_return_date) WHERE status = 'active';

CREATE TABLE transfer_requests (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id        UUID NOT NULL REFERENCES assets(id),
  from_holder_id  UUID NOT NULL,
  to_holder_id    UUID NOT NULL,
  requested_by    UUID NOT NULL REFERENCES users(id),
  reason          TEXT,
  status          transfer_status NOT NULL DEFAULT 'pending',
  approved_by     UUID REFERENCES users(id),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  resolved_at     TIMESTAMPTZ
);

CREATE INDEX idx_transfer_asset ON transfer_requests(asset_id);
CREATE INDEX idx_transfer_status ON transfer_requests(status);
```

## 5. Resource Booking

```sql
CREATE TABLE bookings (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resource_asset_id   UUID NOT NULL REFERENCES assets(id),
  booked_by           UUID NOT NULL REFERENCES users(id),
  start_time          TIMESTAMPTZ NOT NULL,
  end_time            TIMESTAMPTZ NOT NULL,
  status              booking_status NOT NULL DEFAULT 'upcoming',
  purpose             TEXT,
  reminder_sent       BOOLEAN NOT NULL DEFAULT false,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT valid_range CHECK (end_time > start_time)
);

-- Prevents overlapping bookings on the same resource
ALTER TABLE bookings ADD CONSTRAINT no_overlap
  EXCLUDE USING gist (
    resource_asset_id WITH =,
    tstzrange(start_time, end_time) WITH &&
  ) WHERE (status IN ('upcoming','ongoing'));

CREATE INDEX idx_bookings_resource_time ON bookings(resource_asset_id, start_time, end_time);
CREATE INDEX idx_bookings_status ON bookings(status);
```

## 6. Maintenance

```sql
CREATE TABLE maintenance_requests (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id        UUID NOT NULL REFERENCES assets(id),
  raised_by       UUID NOT NULL REFERENCES users(id),
  issue           TEXT NOT NULL,
  priority        maintenance_priority NOT NULL DEFAULT 'medium',
  status          maintenance_status NOT NULL DEFAULT 'pending',
  approved_by     UUID REFERENCES users(id),
  technician_name TEXT,
  resolved_at     TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_maintenance_asset ON maintenance_requests(asset_id);
CREATE INDEX idx_maintenance_status ON maintenance_requests(status);
```

## 7. Audit

```sql
CREATE TABLE audit_cycles (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name                  TEXT NOT NULL,
  scope_department_id   UUID REFERENCES departments(id),
  scope_location        TEXT,
  start_date            DATE NOT NULL,
  end_date              DATE NOT NULL,
  status                audit_cycle_status NOT NULL DEFAULT 'open',
  created_by            UUID NOT NULL REFERENCES users(id),
  closed_at             TIMESTAMPTZ,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE audit_auditors (
  audit_cycle_id  UUID NOT NULL REFERENCES audit_cycles(id) ON DELETE CASCADE,
  user_id         UUID NOT NULL REFERENCES users(id),
  PRIMARY KEY (audit_cycle_id, user_id)
);

CREATE TABLE audit_items (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  audit_cycle_id  UUID NOT NULL REFERENCES audit_cycles(id) ON DELETE CASCADE,
  asset_id        UUID NOT NULL REFERENCES assets(id),
  verification    audit_verification NOT NULL DEFAULT 'pending',
  notes           TEXT,
  verified_by     UUID REFERENCES users(id),
  verified_at     TIMESTAMPTZ,
  UNIQUE (audit_cycle_id, asset_id)
);

CREATE INDEX idx_audit_items_cycle ON audit_items(audit_cycle_id);
CREATE INDEX idx_audit_items_flagged ON audit_items(verification) WHERE verification IN ('missing','damaged');

CREATE TABLE audit_discrepancy_reports (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  audit_cycle_id  UUID NOT NULL REFERENCES audit_cycles(id),
  generated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  report_json     JSONB NOT NULL   -- snapshot of flagged audit_items at close time
);
```

## 8. Attachments (generic file storage)

```sql
CREATE TABLE attachments (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  entity_type     attachment_entity NOT NULL,
  entity_id       UUID NOT NULL,
  url             TEXT NOT NULL,
  file_type       TEXT,           -- image/pdf/etc
  uploaded_by     UUID NOT NULL REFERENCES users(id),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_attachments_entity ON attachments(entity_type, entity_id);
```

## 9. Notifications & Activity Log

```sql
CREATE TABLE notifications (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES users(id),
  type            TEXT NOT NULL,   -- e.g. 'asset_assigned','maintenance_approved','booking_reminder', etc.
  message         TEXT NOT NULL,
  entity_type     TEXT,
  entity_id       UUID,
  read            BOOLEAN NOT NULL DEFAULT false,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_notifications_user_unread ON notifications(user_id) WHERE read = false;

CREATE TABLE activity_logs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID REFERENCES users(id),
  action          TEXT NOT NULL,     -- e.g. 'asset.allocate','booking.cancel'
  entity_type     TEXT NOT NULL,
  entity_id       UUID,
  metadata        JSONB DEFAULT '{}',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_activity_entity ON activity_logs(entity_type, entity_id);
CREATE INDEX idx_activity_user ON activity_logs(user_id);
```

## 10. Reports (export tracking)

```sql
CREATE TABLE report_exports (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  report_type     report_type NOT NULL,
  generated_by    UUID NOT NULL REFERENCES users(id),
  file_url        TEXT NOT NULL,
  filters         JSONB DEFAULT '{}',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## 11. Entity Relationship Summary

```
departments 1---N users (department_id)
departments 1---1 users (head_id)
departments 1---N departments (parent_dept_id, self-ref)

asset_categories 1---N assets

assets 1---N allocations
assets 1---N transfer_requests
assets 1---N bookings (where is_bookable = true)
assets 1---N maintenance_requests
assets 1---N audit_items
assets 1---N attachments (entity_type='asset')
assets N---1 departments

users 1---N allocations (as holder, when holder_type='employee')
users 1---N transfer_requests (requested_by / approved_by)
users 1---N bookings (booked_by)
users 1---N maintenance_requests (raised_by / approved_by)
users N---N audit_cycles (via audit_auditors)
users 1---N audit_items (verified_by)
users 1---N notifications
users 1---N activity_logs
users 1---N refresh_tokens / password_reset_tokens

audit_cycles 1---N audit_items
audit_cycles 1---N audit_discrepancy_reports
audit_cycles N---1 departments (scope_department_id)
```

## 12. Notes
- `custom_fields` on `asset_categories` defines the schema (key/label/type/required); `custom_field_values` on `assets` stores the actual per-asset values — validated at API layer against the category's field definitions.
- `holder_id` on `allocations`/`transfer_requests` is polymorphic (references either `users.id` or `departments.id` based on `holder_type`) — no DB-level FK; enforced in application layer.
- All state transition tables (`asset_status`, `maintenance_status`, `booking_status`, `transfer_status`, `audit_verification`) are enforced as Postgres enums; illegal transitions are additionally guarded in the service layer (see TRD §4).
- `report_exports` and `audit_discrepancy_reports` are append-only; no update/delete endpoints.

## 13. References
- Architecture: `AssetFlow_Architecture.md`
- Product requirements: `AssetFlow_PRD.md`
- Technical requirements: `AssetFlow_TRD.md`
