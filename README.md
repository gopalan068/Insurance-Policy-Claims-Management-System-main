# Insurance Policy & Claims Management System

> **Unified Enterprise Full-Stack Platform** featuring **Module 1 (Admin Management Portal)** and **Module 2 (Customer Policyholder Portal)** built with **FastAPI**, **SQLAlchemy ORM**, **SQLite (`insurance.db`)**, **Pydantic v2**, **PyJWT**, **Bcrypt**, **React 18**, **Vite**, **Material UI (MUI v5)**, and **Recharts**.

---

## 🏛️ System Architecture & Multi-Module Structure

This repository contains the unified codebase for the Insurance Policy & Claims Management System, backed by a shared SQLite database (`backend/insurance.db`) and unified REST APIs.

```text
┌────────────────────────────────────────────────────────────────────────┐
│               INSURANCE POLICY & CLAIMS MANAGEMENT SYSTEM               │
└────────────────────────────────────────────────────────────────────────┘
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
┌──────────────┐             ┌──────────────┐             ┌──────────────┐
│   CUSTOMER   │             │    ADMIN     │             │CLAIMS OFFICER│
│    MODULE    │             │    MODULE    │             │    MODULE    │
│  [MODULE 2]  │             │  [MODULE 1]  │             │              │
└──────────────┘             └──────────────┘             └──────────────┘
       ▲                            ▲                            ▲
       └────────────────────────────┼────────────────────────────┘
                                    │
                                    ▼
                      ┌───────────────────────────┐
                      │   FASTAPI + SQLALCHEMY    │
                      │       insurance.db        │
                      └───────────────────────────┘
```

---

## 🚀 Implemented Modules

### 1. Module 1: Admin Module
- **System Administration**: Full lifecycle management of users (`ADMIN`, `CUSTOMER`, `AGENT`, `CLAIMS_OFFICER`), active/inactive toggles, and delete protection.
- **Policy Catalog**: Creation, editing, activation, deactivation of plans (`HEALTH`, `LIFE`, `VEHICLE`, `TRAVEL`, `HOME`).
- **Monitoring Centers**: Policy subscription oversight, claims monitoring, and document repository.
- **Analytics & Reports**: 12 live KPI cards, 4 Recharts visual feeds, claims settlement metrics, and CSV export.
- **Compliance & Audit**: Immutable system audit logs tracking all administrative actions.

### 2. Module 2: Customer Module
- **Registration & Authentication**: Online account creation with email uniqueness checks, Bcrypt password hashing, and instant welcome notification.
- **Policyholder Dashboard**: 6 real-time KPI cards (Total Policies, Active Coverage, Expired Policies, Total Claims, Pending Claims, Approved Claims), recent subscriptions summary, and active claims tracking.
- **Policy Catalog & Purchase**: Searchable catalog with category filtering, detailed benefits breakdown, term selection, and instant online checkout with start/end date calculation.
- **My Subscriptions**: Detailed view of active/expired coverage plans, certificate numbers, and associated claims.
- **Claim Submission**: Filing claims against active policies with validation (positive amount, date checks) and immediate multi-file evidence attachment (PDF, PNG, JPG).
- **Claim Status Tracking**: Visual progress lifecycle (`Submitted` -> `Under Review` -> `Approved / Rejected`), officer adjudication remarks, and "Upload Additional Evidence" functionality.
- **Document Archive**: Central repository of all uploaded claim receipts and invoices with secure download links.
- **Notifications Center**: Real-time event notifications with unread badge counter, mark-as-read, and direct links.
- **Customer Profile**: Personal details management, contact information updates, and password reset.

---

## 🔒 Security, RBAC & IDOR Protections

1. **Role-Based Access Control (RBAC)**:
   - Evaluated on backend via FastAPI dependencies (`require_admin`, `require_customer`).
   - Evaluated on frontend via `ProtectedRoute` (`allowedRoles={['ADMIN']}` vs `allowedRoles={['CUSTOMER']}`).
   - Attempts by customers to access `/api/admin/*` return **403 Forbidden**.
   - Attempts by admins to access `/api/customer/*` return **403 Forbidden**.
2. **Insecure Direct Object Reference (IDOR) Isolation**:
   - Customer A can **only** view, query, or download documents for purchases and claims matching their own `customer_id`.
   - Any attempt to access another customer's resource returns **404 Not Found** or **403 Forbidden**.
3. **Password Security**:
   - Stored strictly as **Bcrypt hashes** (256-bit salt). No plaintext passwords or hashes are ever exposed in API responses.
4. **Path Traversal Protection**:
   - Document upload and download handlers strictly validate filesystem paths to prevent `../` attacks.

---

## 🔑 Default Test Credentials

| Role | Email | Password | Access Portal |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin@insurance.com` | `Admin@123` | Admin Portal (`/admin/*`) |
| **Customer Policyholder** | `john.vance@example.com` | `Customer@123` | Customer Portal (`/customer/*`) |
| **Insurance Agent** | `robert.agent@insurance.com` | `Agent@123` | Agent Records (Monitored by Admin) |
| **Claims Officer** | `frank.officer@insurance.com` | `Officer@123` | Officer Records (Monitored by Admin) |

*(Quick-fill demo buttons are provided directly on the login page)*

---

## 📁 Unified Directory Structure

```text
incursence/
├── backend/
│   ├── main.py                     # FastAPI app with CORS & lifespan seeder
│   ├── database.py                 # SQLAlchemy engine & SessionLocal
│   ├── models.py                   # Shared ORM models (User, Policy, Claim, Notification, etc.)
│   ├── schemas.py                  # Pydantic v2 schemas for Admin and Customer
│   ├── auth.py                     # Bcrypt hashing & PyJWT tokens
│   ├── dependencies.py             # RBAC (require_admin, require_customer) & audit/notifications
│   ├── insurance.db                # Shared SQLite database
│   ├── seed.py                     # Idempotent database seeder
│   ├── routers/
│   │   ├── auth.py                 # Login, Register (/api/auth/register), Me
│   │   ├── admin_*.py              # 11 Admin Module routers
│   │   ├── customer_dashboard.py   # /api/customer/dashboard
│   │   ├── customer_policies.py    # /api/customer/policies
│   │   ├── customer_purchases.py   # /api/customer/purchases
│   │   ├── customer_claims.py      # /api/customer/claims
│   │   ├── customer_documents.py   # /api/customer/documents
│   │   ├── customer_notifications.py# /api/customer/notifications
│   │   └── customer_profile.py     # /api/customer/profile
│   ├── uploads/                    # Secure file evidence storage
│   ├── test_api.py                 # Admin API integration test
│   ├── inspect_system.py           # Deep system inspection test
│   └── test_customer_module.py     # 21-scenario Customer Module test suite
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── src/
│   │   ├── theme.js                # Shared Material UI theme
│   │   ├── main.jsx
│   │   ├── App.jsx                 # React Router v6 configuring /admin/* & /customer/*
│   │   ├── context/
│   │   │   └── AuthContext.jsx     # Unified multi-role authentication context
│   │   ├── services/
│   │   │   ├── api.js              # Axios instance with Bearer interceptors
│   │   │   ├── authService.js
│   │   │   ├── adminService.js
│   │   │   └── customerService.js  # Customer API methods
│   │   ├── components/
│   │   │   ├── ProtectedRoute.jsx  # Configurable role-based route guard
│   │   │   ├── AdminLayout.jsx
│   │   │   ├── CustomerLayout.jsx  # Responsive customer drawer + navbar layout
│   │   │   ├── CustomerNavbar.jsx
│   │   │   ├── CustomerSidebar.jsx
│   │   │   ├── PolicyCard.jsx
│   │   │   ├── ClaimStatusChip.jsx
│   │   │   └── EmptyState.jsx
│   │   └── pages/
│   │       ├── Login.jsx           # Unified role-aware login with demo helpers
│   │       ├── Register.jsx        # Customer registration screen
│   │       ├── admin/              # 12 Admin portal pages
│   │       └── customer/           # 10 Customer portal pages
│   │           ├── Dashboard.jsx
│   │           ├── Policies.jsx
│   │           ├── PolicyDetails.jsx
│   │           ├── PurchasePolicy.jsx
│   │           ├── MyPolicies.jsx
│   │           ├── MyPolicyDetails.jsx
│   │           ├── Claims.jsx
│   │           ├── SubmitClaim.jsx
│   │           ├── ClaimDetails.jsx
│   │           ├── Documents.jsx
│   │           ├── Notifications.jsx
│   │           └── Profile.jsx
│
├── run_backend.bat                 # 1-Click startup script for Backend
└── run_frontend.bat                # 1-Click startup script for Frontend
```

---

## ⚡ Quick Start Instructions

### 1. Start the Backend API
```powershell
cd backend
python main.py
```
- FastAPI Unified Server: `http://127.0.0.1:8000`
- Swagger Interactive Docs: `http://127.0.0.1:8000/docs`

### 2. Start the Frontend Application
```powershell
cd frontend
npm run dev
```
- Web Application: `http://localhost:5173`

### 3. Run Automated Verification Tests
```powershell
# Test Customer Module (21 test cases)
python backend/test_customer_module.py

# Test Admin Module & System Integrity
python backend/inspect_system.py
```
