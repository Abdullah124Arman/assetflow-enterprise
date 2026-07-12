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

CREATE TABLE departments (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name            TEXT NOT NULL,
  head_id         UUID, -- FK added after users table (circular)
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
  custom_fields   JSONB NOT NULL DEFAULT '[]',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

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

CREATE TABLE assets (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tag                 TEXT NOT NULL UNIQUE,
  name                TEXT NOT NULL,
  category_id         UUID NOT NULL REFERENCES asset_categories(id),
  serial_number       TEXT,
  qr_code             TEXT UNIQUE,
  acquisition_date    DATE,
  acquisition_cost    NUMERIC(12,2),
  condition           TEXT,
  location            TEXT,
  status              asset_status NOT NULL DEFAULT 'available',
  is_bookable         BOOLEAN NOT NULL DEFAULT false,
  department_id       UUID REFERENCES departments(id),
  custom_field_values JSONB NOT NULL DEFAULT '{}',
  photo_url           TEXT,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_assets_status ON assets(status);
CREATE INDEX idx_assets_category ON assets(category_id);
CREATE INDEX idx_assets_department ON assets(department_id);
CREATE INDEX idx_assets_location ON assets(location);
CREATE INDEX idx_assets_serial ON assets(serial_number);

CREATE TABLE allocations (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id              UUID NOT NULL REFERENCES assets(id),
  holder_type           holder_type NOT NULL,
  holder_id             UUID NOT NULL,
  allocated_date        DATE NOT NULL DEFAULT CURRENT_DATE,
  expected_return_date  DATE,
  actual_return_date    DATE,
  status                allocation_status NOT NULL DEFAULT 'active',
  checkin_notes         TEXT,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

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

ALTER TABLE bookings ADD CONSTRAINT no_overlap
  EXCLUDE USING gist (
    resource_asset_id WITH =,
    tstzrange(start_time, end_time) WITH &&
  ) WHERE (status IN ('upcoming','ongoing'));

CREATE INDEX idx_bookings_resource_time ON bookings(resource_asset_id, start_time, end_time);
CREATE INDEX idx_bookings_status ON bookings(status);

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
  report_json     JSONB NOT NULL
);

CREATE TABLE attachments (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  entity_type     attachment_entity NOT NULL,
  entity_id       UUID NOT NULL,
  url             TEXT NOT NULL,
  file_type       TEXT,
  uploaded_by     UUID NOT NULL REFERENCES users(id),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_attachments_entity ON attachments(entity_type, entity_id);

CREATE TABLE notifications (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES users(id),
  type            TEXT NOT NULL,
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
  action          TEXT NOT NULL,
  entity_type     TEXT NOT NULL,
  entity_id       UUID,
  metadata        JSONB DEFAULT '{}',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_activity_entity ON activity_logs(entity_type, entity_id);
CREATE INDEX idx_activity_user ON activity_logs(user_id);

CREATE TABLE report_exports (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  report_type     report_type NOT NULL,
  generated_by    UUID NOT NULL REFERENCES users(id),
  file_url        TEXT NOT NULL,
  filters         JSONB DEFAULT '{}',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
