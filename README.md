# AssetFlow - Enterprise Asset & Resource Management System

## Overview
AssetFlow is a centralized ERP module for tracking, allocating, and maintaining physical assets and shared resources — industry-agnostic (offices, schools, hospitals, factories, agencies). It replaces spreadsheets/paper logs with structured lifecycles, booking, maintenance, and audit workflows.

## Key Features
- **Asset Registration & Directory**: Single source of truth for asset state with comprehensive search and filtering capabilities.
- **Allocation & Transfer**: Ensures zero double-allocation of a single asset. Manage asset transfers and returns seamlessly.
- **Resource Booking**: Calendar view for resource booking with built-in overlap validation to prevent double-booking.
- **Maintenance Management**: Kanban-style workflow (Pending → Approved → Technician Assigned → In Progress → Resolved) for maintenance requests.
- **Audit Cycles**: Create audit cycles, assign auditors, verify items, and auto-generate discrepancy reports.
- **Reports & Analytics**: Insights into utilization, maintenance frequency, idle assets, and booking heatmaps.
- **Notifications & Activity Logs**: Full audit trail of every state-changing action and real-time notifications for key events.

## Technology Stack
**Frontend:**
- React + Tailwind CSS (SPA)
- Custom XML Parsing (`DOMParser` / `fast-xml-parser`)

**Backend:**
- Python 3.12
- Django 5 + Django REST Framework (DRF)
- XML-only API (`djangorestframework-xml`), payload validation against XSD schemas (`lxml`, `xmlschema`)
- Auth: JWT (access + refresh) via `djangorestframework-simplejwt`
- Background Jobs: Celery + Celery Beat (overdue checks, reminders)
- Real-time/Notifications: WebSocket (Django Channels)

**Database:**
- PostgreSQL (via Django ORM)

## User Roles (RBAC)
- **Admin**: Full access. Manage org setup (departments, categories, role promotion), audit cycles, and org-wide analytics.
- **Asset Manager**: Register/allocate assets, approve transfers/maintenance/audit resolution, approve returns.
- **Department Head**: View department assets, approve department allocation/transfer requests, book resources.
- **Employee**: View own assets, book resources, raise maintenance requests, initiate return/transfer.

## Project Structure
```text
assetflow-enterprise/
├── backend/
│   ├── assetflow/            # Django project settings
│   ├── apps/                 # Django apps (auth, org, assets, allocations, bookings, maintenance, audit, reports, notifications)
│   ├── common/               # Custom DRF XML parsers, renderers, XSD validation, custom error handling
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/            # 10 core screens
│   │   ├── components/       # Reusable UI components
│   │   ├── api/              # API clients for XML communication
│   │   └── store/            # State management (auth, notifications)
│   ├── package.json
│   └── vite.config.js (or similar)
├── schemas/                  # XSD files for request/response validation
└── docs/                     # TRD, PRD, Architecture, and Schema documentation
```

## Getting Started
### Prerequisites
- Python 3.12+
- Node.js (v18+)
- PostgreSQL
- Redis (for Celery and Channels)

### Backend Setup
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the database and apply migrations:
   ```bash
   python manage.py migrate
   ```
5. Start the development server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## API Documentation
All API endpoints communicate exclusively via XML. Requests must have `Content-Type: application/xml` and `Accept: application/xml`. Every request and response is validated against the corresponding XSD schema located in the `/schemas` directory.

Please refer to the `docs/` folder for detailed PRD, Architecture, TRD, and Schema definitions.
