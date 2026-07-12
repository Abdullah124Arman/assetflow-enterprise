# 🚀 AssetFlow Enterprise

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Version](https://img.shields.io/badge/Version-v2.0.1-blue)
![License](https://img.shields.io/badge/License-MIT-blue)

AssetFlow Enterprise is a comprehensive, modern, and highly scalable **Asset Management System** tailored for large organizations. Built with a robust Django backend and a lightning-fast React frontend, it empowers teams to meticulously track, allocate, maintain, and audit organizational assets with ease.

AssetFlow provides a **single source of truth** for asset states and prevents issues like double-allocations and booking overlaps through strict database-level constraints.

---

## 🛠 Tech Stack

### Frontend
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=FFD62E)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![React Router](https://img.shields.io/badge/React_Router-CA4245?style=for-the-badge&logo=react-router&logoColor=white)

- **Framework**: React 18 + Vite (SPA) + Tailwind CSS
- **Data Layer**: Custom XML parsing (`DOMParser` / `fast-xml-parser`) for all API fetch operations.

### Backend
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)
![Django REST](https://img.shields.io/badge/Django_REST-ff1709?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![XML API](https://img.shields.io/badge/XML_API-F37626?style=for-the-badge)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=JSON%20web%20tokens&logoColor=white)

- **Language & Framework**: Python 3.12, Django 5 + Django REST Framework (DRF)
- **API Paradigm**: **XML-only REST API** (JSON is explicitly disabled). Every request and response uses XML payloads.
- **Validation**: Payload validation against predefined **XSD schemas** using `lxml` and `xmlschema` before reaching business logic.
- **Database**: PostgreSQL (via Django ORM) hosted on Neon. Uses advanced constraints like partial unique indexes and GiST exclusion constraints.
- **Authentication**: JWT (Access & Refresh) via `djangorestframework-simplejwt`, token delivered inside an XML `<auth>` envelope.
- **Background Jobs**: Celery + Celery Beat / Custom Django scheduler for overdue checks and booking reminders.
- **Real-time**: WebSocket (Django Channels) for real-time notifications.
- **Security**: XXE protection (entities/network disabled in `lxml`), rate limiting, parameterised queries.

---

## 🚀 Key Modules & Workflows

### 1. Asset Lifecycle & Directory
- Maintain a single source of truth for asset state: `Available`, `Allocated`, `Reserved`, `Under Maintenance`, `Lost`, `Retired`, or `Disposed`.
- Robust search and filter by tag, serial, category, and department.
- Maintains comprehensive allocation and maintenance history.

### 2. Allocation & Transfer
- **Double-Allocation Block**: Prevented at the DB level via `one_active_allocation_per_asset` partial unique index.
- If an asset is already allocated, users can submit a **Transfer Request** that requires approval from an Asset Manager or Department Head.

### 3. Resource Booking
- Calendar view for booking shared bookable resources (e.g., projectors, meeting rooms).
- **Overlap Validation**: Enforced at the DB level using PostgreSQL's GiST exclusion constraints. Overlapping requests are automatically rejected.

### 4. Maintenance Kanban
- Report issues for assets to enter the maintenance kanban workflow.
- **States**: `Pending` → `Approved` (asset automatically flipped to `Under Maintenance`) → `Technician Assigned` → `In Progress` → `Resolved` (asset back to `Available`).

### 5. Audit Cycles
- Create scoped audits (by department/location and date range).
- Auditors verify each asset as `Verified`, `Missing`, or `Damaged`.
- Closing an audit cycle generates an automatic **Discrepancy Report** and bulk updates missing assets to `Lost` status.

### 6. Reports & Dashboard
- Visual KPI cards on the dashboard (Available, Allocated, Pending Transfers, Upcoming Returns).
- Dynamic reports for departmental utilization, maintenance frequency, and most-used vs. idle assets.
- Activity feeds for a full system audit trail.

---

## 🖥 Frontend Web Flow (Screens)

AssetFlow is organized into a robust left-sidebar navigation layout containing 10 core screens:

1. **Login/Signup**: Standard Auth. Sign-up creates standard Employee roles (elevated roles granted by Admins).
2. **Dashboard**: KPI cards, overdue asset banners, and recent activity feed.
3. **Organization Setup (Admin Only)**: Manage Departments, Categories (with custom fields), and Employee roles.
4. **Assets**: Central directory for all assets with filtering and registration capabilities.
5. **Allocation & Transfer**: Direct allocation or transfer request flows.
6. **Resource Booking**: Calendar slot booking with visual conflict indicators.
7. **Maintenance**: Kanban board for asset repair and upkeep.
8. **Audit**: Scope definition and verification checklist for auditors.
9. **Reports**: System utilization analytics and export functionalities.
10. **Notifications**: Full activity log and real-time event feed (Alerts, Approvals, Bookings).

---

## 🔐 User Roles (RBAC)

Role-Based Access Control is enforced server-side using middleware and row-level scoping (`department_id` filtering).

- **Admin**: Full access. Manage org setup, promote employee roles, manage audit cycles, and view org-wide analytics.
- **Asset Manager**: Register and allocate assets. Approve transfers, maintenance requests, and audit discrepancies.
- **Department Head**: Manage their own department's assets, approve department-scoped allocations/transfers, book resources.
- **Employee**: Base role. Can view assigned assets, book resources, raise maintenance requests, and initiate returns/transfers.

---

## 📂 Project Structure

```text
assetflow-enterprise/
├── backend/
│   ├── assetflow/            # Django root (settings, urls, celery config)
│   ├── apps/                 # Modular Django apps (auth, org, assets, allocations, bookings, maintenance, audit, reports, notifications)
│   ├── common/               # Custom DRF XML parsers, renderers, XSD validation utilities
│   ├── manage.py             # Django entry point
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── pages/            # 10 core React screens
│   │   ├── components/       # Shared UI components
│   │   ├── api/              # XML-based API client wrappers
│   │   └── store/            # State management (auth, notification feed)
│   ├── package.json          # Node dependencies
│   └── vite.config.js        # Vite bundler config
├── schemas/                  # XML Schema Definitions (XSDs) used for API payload validation
└── docs/                     # Product, Technical, Web Flow, and Schema reference documents
```

---

## ⚙️ Getting Started (Local Development)

### Prerequisites
- Python 3.12+
- Node.js (v18+)
- PostgreSQL (with `btree_gist` extension enabled for booking overlaps)
- Redis (optional, for Celery and Django Channels)

### 1. Backend Setup
```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables (Create a .env file with DB credentials)
# Ensure your PostgreSQL instance has the btree_gist extension created.

# Run migrations
python manage.py migrate

# Start Django development server
python manage.py runserver
```

### 2. Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

---

## 📚 Documentation Reference

For more deep-dive technical and product requirements, refer to the `docs/` directory:
- **`AssetFlow_PRD.md`**: Product Requirements Document (Metrics, Roles, Scope).
- **`AssetFlow_TRD.md`**: Technical Requirements (XML API contract, Constraints, Job triggers).
- **`AssetFlow_Architecture.md`**: High-level system architecture and data pipelines.
- **`AssetFlow_Schema.md`**: Complete PostgreSQL Database Schema DDL.
- **`AssetFlow_WebFlow.md`**: Screen-by-screen frontend logic and user flows.
