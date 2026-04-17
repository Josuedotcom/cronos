# Cronos MVP — Task Breakdown (12 Weeks)

**Project:** Cronos - Colombian Labor Law-Compliant Shift Management System  
**Change ID:** cronos-mvp  
**Phase:** Task Breakdown  
**Status:** DRAFT  
**Created:** 2026-04-16  

---

## Overview

- **Total Tasks:** 48
- **Total Effort:** 142 story points
- **Duration:** 12 weeks (3 phases × 4 weeks)
- **Team:** 1 backend dev + 1 frontend dev + 0.5 QA
- **Velocity Target:** 12 SP/week (allows buffer for refinement)

---

## Phase 1: Backend Foundation & Core Payroll Engine (Weeks 1-4)

### Sprint 1.1: Project Setup & Database (Week 1)

| Task ID | Title | Effort | Dependencies | Status |
|---------|-------|--------|--------------|--------|
| **BE-001** | FastAPI Project Scaffold | 3 SP | None | Complete |
| **BE-002** | PostgreSQL Schema Migration (Alembic) | 5 SP | BE-001 | Complete |
| **BE-003** | SQLAlchemy ORM Models (8 entities) | 5 SP | BE-002 | Complete |
| **BE-004** | Database Connection & Configuration | 2 SP | BE-001 | Complete |

#### BE-001: FastAPI Project Scaffold
- **Description:** Create FastAPI project structure, Poetry/pip setup, environment configuration
- **Acceptance Criteria:**
  - FastAPI app runs on `localhost:8000` without errors
  - `poetry install` or `pip install -r requirements.txt` works
  - `.env.example` created with all required variables (DATABASE_URL, SECRET_KEY, etc.)
  - Main app file at `backend/app/main.py` with basic health check endpoint
  - CORS middleware configured for Vercel frontend
- **Files to Create/Modify:**
  - `backend/pyproject.toml` (Poetry config with FastAPI, SQLAlchemy, Pydantic, pytest)
  - `backend/app/__init__.py`
  - `backend/app/main.py` (FastAPI app creation, middleware setup)
  - `backend/app/config.py` (settings via Pydantic BaseSettings)
  - `backend/.env.example`
  - `backend/README.md` (setup instructions)
- **Notes:** Use Python 3.11+, FastAPI 0.104+, SQLAlchemy 2.0

#### BE-002: PostgreSQL Schema Migration (Alembic)
- **Description:** Set up Alembic migrations for the 8 core database entities
- **Acceptance Criteria:**
  - Alembic environment initialized at `backend/alembic/`
  - Initial migration (`001_create_base_schema.py`) created with all tables per design.md § 2.2
  - Tables: companies, sub_organizations, areas, workers, shift_templates, shift_assignments, timesheet_days, holidays, surcharge_rules
  - All indexes created as per design (compound indexes on (company_id, area_id), (worker_id, date), etc.)
  - Foreign keys + cascading deletes configured
  - `alembic upgrade head` successfully creates all tables
- **Files to Create/Modify:**
  - `backend/alembic/env.py` (auto-migration config)
  - `backend/alembic/versions/001_create_base_schema.py`
  - `backend/alembic.ini` (SQLAlchemy URL from .env)
- **Notes:** Migrations must be idempotent; test rollback works

#### BE-003: SQLAlchemy ORM Models (8 entities)
- **Description:** Create SQLAlchemy 2.0 async models for all entities
- **Acceptance Criteria:**
  - 8 models created: Company, SubOrganization, Area, Worker, ShiftTemplate, ShiftAssignment, TimesheetDay, Holiday
  - All relationships defined (1:N, M:N) with lazy loading strategy
  - Type hints and validators (Pydantic for request/response)
  - Multi-tenant context (all models have `company_id` or inheritance)
  - Soft deletes via `deleted_at` timestamp on Worker, ShiftTemplate
- **Files to Create/Modify:**
  - `backend/app/models/__init__.py`
  - `backend/app/models/company.py` (Company, SubOrganization, Area)
  - `backend/app/models/worker.py` (Worker)
  - `backend/app/models/shift.py` (ShiftTemplate, ShiftAssignment, TimesheetDay)
  - `backend/app/models/holiday.py` (Holiday, SurchargeRule)
  - `backend/app/schemas.py` (Pydantic schemas for requests/responses)
- **Notes:** Use `async_session` from SQLAlchemy; implement `__repr__` for debugging

#### BE-004: Database Connection & Configuration
- **Description:** Configure async database connection pooling and session management
- **Acceptance Criteria:**
  - Async engine created with connection pooling (pool_size=20, max_overflow=10)
  - SessionLocal factory configured for dependency injection in FastAPI
  - Test database connection script succeeds
  - Environment variables (DATABASE_URL, SQLALCHEMY_ECHO for dev)
  - Connection pool monitor implemented (optional: logs pool exhaustion)
- **Files to Create/Modify:**
  - `backend/app/database.py` (create_engine, SessionLocal, async context managers)
  - Update `backend/app/config.py` with DATABASE_URL parsing
- **Notes:** Test with Neon serverless connection string; monitor pool exhaustion in logs

---

### Sprint 1.2: Authentication & Authorization (Week 2)

| Task ID | Title | Effort | Dependencies | Status |
|---------|-------|--------|--------------|--------|
| **BE-005** | JWT Token Generation & Verification | 3 SP | BE-001 | Complete |
| **BE-006** | Authentication Endpoints (login, refresh, logout) | 3 SP | BE-005, BE-003 | Complete |
| **BE-007** | Multi-Tenant Middleware (inject company_id) | 3 SP | BE-006 | Complete |
| **BE-008** | Role-Based Access Control (RBAC) | 2 SP | BE-007 | Complete |

- [x] **BE-005** JWT Token Generation & Verification
- [x] **BE-006** Authentication Endpoints (login, refresh, logout)
- [x] **BE-007** Multi-Tenant Middleware (inject company_id)
- [x] **BE-008** Role-Based Access Control (RBAC)

#### BE-005: JWT Token Generation & Verification
- **Description:** Implement JWT token creation, validation, and refresh logic
- **Acceptance Criteria:**
  - JWT tokens created with: `sub` (user_id), `exp`, `iat`, `company_id`, `role`
  - Tokens signed with HS256 (SECRET_KEY from .env)
  - Token expiration: 1 hour access, 7 days refresh
  - Verify function decodes and validates token signature
  - Expired/invalid tokens raise `HTTPException(401)`
- **Files to Create/Modify:**
  - `backend/app/auth/jwt.py` (create_access_token, verify_token, create_refresh_token)
  - `backend/app/config.py` (TOKEN_EXPIRY, REFRESH_TOKEN_EXPIRY, SECRET_KEY)
- **Notes:** Use PyJWT library; use `datetime.utcnow()` (or `datetime.now(timezone.utc)`)

#### BE-006: Authentication Endpoints (login, refresh, logout)
- **Description:** Create FastAPI routes for user authentication
- **Acceptance Criteria:**
  - POST `/auth/login` → email + password → access_token + refresh_token
  - POST `/auth/refresh` → refresh_token → new access_token
  - POST `/auth/logout` → (optional: token blacklist; MVP can skip)
  - Workers table has password (hashed with bcrypt) + email fields
  - Login validates email exists + password matches (bcrypt.verify)
  - Routes return RFC 7807 error responses for invalid credentials
- **Files to Create/Modify:**
  - `backend/app/routers/auth.py` (FastAPI APIRouter with login, refresh)
  - `backend/app/auth/password.py` (hash_password, verify_password using bcrypt)
  - `backend/app/models/worker.py` (add email, hashed_password fields)
  - Update `backend/app/main.py` to include auth router
- **Notes:** Use bcrypt for password hashing; test with curl or Postman

#### BE-007: Multi-Tenant Middleware (inject company_id)
- **Description:** Middleware that extracts JWT token, validates tenant context, injects company_id into request state
- **Acceptance Criteria:**
  - Middleware runs on all non-auth routes
  - Extracts `company_id` from JWT token
  - Stores `company_id` in `request.state.company_id`
  - Stores `user_id` in `request.state.user_id`
  - Returns 401 if no valid token
  - All subsequent queries filtered by `company_id` (enforced in service layer)
- **Files to Create/Modify:**
  - `backend/app/middleware/tenant.py` (TenantMiddleware)
  - Update `backend/app/main.py` to add middleware
  - Create `backend/app/dependencies.py` (get_company_id, get_user_id dependency functions)
- **Notes:** Middleware runs AFTER auth; verify in logs that company_id is injected per request

#### BE-008: Role-Based Access Control (RBAC)
- **Description:** Decorator/dependency to check user role (worker, manager, hr_admin)
- **Acceptance Criteria:**
  - Roles defined: `WORKER`, `MANAGER`, `HR_ADMIN`
  - Decorator `@require_role("MANAGER")` restricts endpoint to that role
  - Role stored in JWT token + Worker model
  - Returns 403 Forbidden if user lacks required role
- **Files to Create/Modify:**
  - `backend/app/auth/rbac.py` (require_role decorator, get_user_role)
  - Update `backend/app/models/worker.py` (add role field, Enum)
  - Update auth router to set role in JWT
- **Notes:** Start with 3 roles; extensible design for future roles

---

### Sprint 1.3: Core Payroll Engine (Week 3)

| Task ID | Title | Effort | Dependencies | Status |
|---------|-------|--------|--------------|--------|
| **BE-009** | Payroll Engine: Hour Classification Algorithm | 8 SP | BE-003 | Pending |
| **BE-010** | Payroll Engine: Surcharge & Overtime Calculation | 8 SP | BE-009 | Pending |
| **BE-011** | Payroll Engine: Unit Tests (100+ cases) | 8 SP | BE-010 | Pending |

#### BE-009: Payroll Engine - Hour Classification Algorithm
- **Description:** Core algorithm to classify work hours (ordinarias, nocturnas, extras, recargos dominicales)
- **Acceptance Criteria:**
  - Classify each hour worked per Colombian CST rules:
    - Ordinarias (6am-9pm): Base rate
    - Nocturnas (9pm-6am): +35% surcharge
    - Midnight rule: Shift crossing 00:00 changes hour type at midnight
    - Sunday (00:00-23:59): +75% surcharge on all hours
    - Sunday night (9pm-6am on Sunday): +110% surcharge
    - Holiday (24-hour period): +75% surcharge
  - Function: `classify_hours(shift_date, start_time, end_time, worker_rate) → dict`
  - Return: `{ordinarias: X, nocturnas: Y, extras_ordinarias: Z, extras_nocturnas: W, recargo_dominical: V}`
  - Handle edge cases: Shifts starting in one day, ending next day; DST transitions
  - Workweek limit validation: Max 46h (2024), 44h (2025), 42h (2026)
- **Files to Create/Modify:**
  - `backend/app/services/payroll_engine.py` (HourClassifier class with classify_hours method)
  - `backend/app/services/constants.py` (rates, limits, thresholds)
- **Notes:** This is THE critical business logic; must be thoroughly tested and auditable

#### BE-010: Payroll Engine - Surcharge & Overtime Calculation
- **Description:** Calculate gross pay per shift, accounting for surcharges, overtime limits, and workweek transitions
- **Acceptance Criteria:**
  - Function: `calculate_shift_payroll(worker_id, shift_assignment, holiday_calendar) → dict`
  - Return: `{gross_pay: X, ordinarias_hours: Y, nocturnas_hours: Z, ...}`
  - Overtime calculation: Any hours beyond workweek limit get +25% surcharge (extra ordinaria/nocturna)
  - Overtime cap: Max 2h/day, 12h/week (per CST art 159)
  - Midnight rule: If shift crosses 00:00, recalculate surcharges for before/after midnight
  - Workweek transitions: If worker crosses into next week, cap at 46h (2024) and recalculate
  - Holiday detection: Check holiday_calendar for surcharges
  - Multi-tenant filter: Only calculate for given company
- **Files to Create/Modify:**
  - Update `backend/app/services/payroll_engine.py` (add SurchargeCalculator class)
  - Add queries to fetch workweek hours, holiday calendar per tenant
- **Notes:** Must handle Neon time zones correctly; consider storing shifts in UTC, displaying in local time

#### BE-011: Payroll Engine - Unit Tests (100+ cases)
- **Description:** Comprehensive pytest test suite for payroll engine
- **Acceptance Criteria:**
  - 100+ test cases covering:
    - Basic hours (6am-9pm = ordinarias)
    - Night hours (9pm-6am = nocturnas with 35% surcharge)
    - Midnight shift (8pm-4am crosses 00:00, recalculate at midnight)
    - Sunday ordinarias (75% surcharge)
    - Sunday night (110% surcharge)
    - Holiday hours (75% surcharge)
    - Overtime ordinarias (25% surcharge on hours > workweek limit)
    - Overtime nocturnas (35% + 25% = 60% surcharge)
    - Workweek limit transitions (46h 2024, 44h 2025, 42h 2026)
    - Overtime caps (2h/day, 12h/week)
    - Edge cases: Year-end transitions, DST, leap seconds, zero-hour assignments
  - All tests pass with 100% code coverage for payroll_engine.py
  - Test fixtures: sample workers, shifts, holiday calendars
- **Files to Create/Modify:**
  - `backend/tests/__init__.py`
  - `backend/tests/conftest.py` (pytest fixtures: workers, shifts, holidays)
  - `backend/tests/test_payroll_engine.py` (100+ test cases)
  - `backend/tests/test_payroll_edge_cases.py` (midnight rule, workweek limits, overtime)
- **Notes:** Run with `pytest --cov=app/services/payroll_engine --cov-report=html`; aim for 100% coverage

---

### Sprint 1.4: Basic API Endpoints & Integration (Week 4)

| Task ID | Title | Effort | Dependencies | Status |
|---------|-------|--------|--------------|--------|
| **BE-012** | Shift Template CRUD Endpoints | 5 SP | BE-008, BE-003 | Pending |
| **BE-013** | Shift Assignment CRUD & Validation | 5 SP | BE-012, BE-010 | Pending |
| **BE-014** | Payroll Query Endpoints (per worker/period) | 5 SP | BE-013 | Pending |
| **BE-015** | Holiday Management Endpoints | 3 SP | BE-008, BE-003 | Pending |
| **BE-016** | Integration Tests (API layer) | 5 SP | BE-014 | Pending |

#### BE-012: Shift Template CRUD Endpoints
- **Description:** REST endpoints to create, read, update, delete shift templates
- **Acceptance Criteria:**
  - POST `/shifts/templates` → create template (name, start_time, end_time, shift_code)
  - GET `/shifts/templates` → list all templates for company
  - GET `/shifts/templates/{id}` → fetch single template
  - PUT `/shifts/templates/{id}` → update template
  - DELETE `/shifts/templates/{id}` → soft-delete template
  - Multi-tenant: Only return templates for authenticated user's company
  - RBAC: Only MANAGER + HR_ADMIN can create/edit/delete
- **Files to Create/Modify:**
  - `backend/app/routers/shifts.py` (FastAPI APIRouter with template endpoints)
  - `backend/app/schemas.py` (ShiftTemplateCreate, ShiftTemplateRead Pydantic models)
  - Update `backend/app/main.py` to include shifts router
- **Notes:** Template names are user-customizable (e.g., "T" = Tarde, "M" = Mañana, "N" = Nocturna)

#### BE-013: Shift Assignment CRUD & Validation
- **Description:** Endpoints to assign shifts to workers, with conflict detection
- **Acceptance Criteria:**
  - POST `/shifts/assignments` → assign shift to worker (worker_id, template_id, date)
  - GET `/shifts/assignments` → list assignments for company/date range (with query filters)
  - GET `/shifts/assignments/{id}` → fetch assignment + calculated payroll preview
  - PUT `/shifts/assignments/{id}` → update assignment (reschedule/change template)
  - DELETE `/shifts/assignments/{id}` → soft-delete assignment
  - Validation: Check for conflicts (worker can't have 2 shifts same date), max 2h overtime/day
  - Multi-tenant: All assignments scoped to company
  - RBAC: MANAGER can assign; WORKER can view own assignments
- **Files to Create/Modify:**
  - Update `backend/app/routers/shifts.py` with assignment endpoints
  - Add validation logic: `validate_shift_assignment()` in ShiftService
  - Update `backend/app/schemas.py` with ShiftAssignmentCreate, ShiftAssignmentRead
- **Notes:** Assignment creation should trigger payroll recalculation (cached in timesheet_day)

#### BE-014: Payroll Query Endpoints (per worker/period)
- **Description:** Endpoints to query payroll for a worker or period
- **Acceptance Criteria:**
  - GET `/payroll/worker/{worker_id}?start_date=2026-01-01&end_date=2026-01-31` → aggregated payroll for period
  - GET `/payroll/daily/{worker_id}?date=2026-01-15` → payroll breakdown for single day
  - GET `/payroll/summary?start_date=...&end_date=...` → company-wide payroll summary (HR_ADMIN only)
  - Response includes: ordinarias, nocturnas, extras, recargos, total_gross, by-date breakdown
  - Multi-tenant: Filter by company
  - RBAC: WORKER sees only own payroll; MANAGER sees team; HR_ADMIN sees all
- **Files to Create/Modify:**
  - `backend/app/routers/payroll.py` (new APIRouter for payroll queries)
  - `backend/app/services/payroll_service.py` (query/aggregation logic)
  - Update `backend/app/main.py` to include payroll router
- **Notes:** Queries should be optimized (use GROUP BY, SUM in SQL to avoid loops)

#### BE-015: Holiday Management Endpoints
- **Description:** REST endpoints for company holidays
- **Acceptance Criteria:**
  - POST `/holidays` → create holiday (date, name, company_id)
  - GET `/holidays?start_date=...&end_date=...` → list holidays for period
  - DELETE `/holidays/{id}` → delete holiday
  - Multi-tenant: Only return holidays for company
  - RBAC: HR_ADMIN only
- **Files to Create/Modify:**
  - `backend/app/routers/holidays.py` (FastAPI APIRouter)
  - Update `backend/app/main.py` to include holidays router
- **Notes:** Holidays used by payroll engine to apply surcharge rules

#### BE-016: Integration Tests (API layer)
- **Description:** End-to-end API tests (fastapi TestClient)
- **Acceptance Criteria:**
  - Test flow: Create company → Create worker → Assign shift → Query payroll → Verify numbers
  - Test RBAC: Unauthorized users should get 403 on protected endpoints
  - Test multi-tenant: Worker in Company A can't see Company B's data
  - Test payroll calculations: Verify shift assignments generate correct payroll
  - All tests pass; coverage >80% for routers
- **Files to Create/Modify:**
  - `backend/tests/test_api_shifts.py` (test shift endpoints)
  - `backend/tests/test_api_payroll.py` (test payroll queries)
  - `backend/tests/test_api_auth.py` (test auth flow)
  - Update `backend/tests/conftest.py` with TestClient, auth fixtures
- **Notes:** Use pytest-asyncio for async tests; mock database in fixtures

---

## Phase 2: Frontend UI & API Integration (Weeks 5-8)

### Sprint 2.1: Frontend Setup & Authentication UI (Week 5)

| Task ID | Title | Effort | Dependencies | Status |
|---------|-------|--------|--------------|--------|
| **FE-001** | React + Vite + Zustand Setup | 3 SP | None | Pending |
| **FE-002** | API Client & HTTP Interceptor | 3 SP | FE-001, BE-006 | Pending |
| **FE-003** | Login & Session Management UI | 5 SP | FE-002 | Pending |
| **FE-004** | Authentication Store (Zustand) | 2 SP | FE-003 | Pending |

#### FE-001: React + Vite + Zustand Setup
- **Description:** Create Vite + React project scaffold with Zustand + Tailwind CSS
- **Acceptance Criteria:**
  - Vite dev server runs on localhost:5173
  - React 18 + TypeScript configured
  - Tailwind CSS + shadcn/ui components available
  - Zustand store setup + devtools for debugging
  - ESLint + Prettier configured
  - `.env.example` with VITE_API_URL (backend URL)
  - Git ignored: node_modules, .env, dist
- **Files to Create/Modify:**
  - `frontend/vite.config.ts` (Vite config, React plugin)
  - `frontend/package.json` (dependencies)
  - `frontend/tsconfig.json` (TypeScript config)
  - `frontend/src/main.tsx` (React root)
  - `frontend/src/App.tsx` (app root component)
  - `frontend/tailwind.config.js` + `frontend/src/index.css`
  - `frontend/.env.example`
- **Notes:** Use `npm create vite@latest` as starting point; add deps: zustand, axios, zod

#### FE-002: API Client & HTTP Interceptor
- **Description:** Axios instance with JWT token management, error handling
- **Acceptance Criteria:**
  - Axios instance created with base URL from env variable
  - Request interceptor: Attach JWT token (Authorization header)
  - Response interceptor: Handle 401 (refresh token, retry request)
  - Response interceptor: Handle 4xx/5xx errors with RFC 7807 error details
  - Token stored in localStorage (access_token, refresh_token)
  - Refresh token logic: If 401, use refresh_token to get new access_token
- **Files to Create/Modify:**
  - `frontend/src/api/client.ts` (axios config, interceptors)
  - `frontend/src/api/endpoints.ts` (API endpoint constants)
  - `frontend/src/stores/authStore.ts` (token storage via localStorage)
- **Notes:** Test token refresh flow manually; consider httpOnly cookies post-MVP

#### FE-003: Login & Session Management UI
- **Description:** Login form, error handling, session persist
- **Acceptance Criteria:**
  - Login page with email + password fields
  - Form validation: Email format, password min 8 chars
  - Submit: POST /auth/login with credentials
  - On success: Store tokens, redirect to dashboard
  - On error: Show error message (from API response)
  - Session persist: On page reload, auto-login if token valid
  - Logout button: Clear tokens, redirect to login
  - Loading state: Disable submit while request pending
- **Files to Create/Modify:**
  - `frontend/src/pages/LoginPage.tsx` (login form)
  - `frontend/src/components/AuthForm.tsx` (form component)
  - `frontend/src/hooks/useAuth.ts` (login/logout logic)
  - `frontend/src/utils/validation.ts` (email, password validation)
  - Update `frontend/src/App.tsx` with routing (protected routes)
- **Notes:** Use React Router for client-side routing; redirect unauthenticated users to /login

#### FE-004: Authentication Store (Zustand)
- **Description:** Zustand store for auth state (user, tokens, role)
- **Acceptance Criteria:**
  - Store properties: user (id, email, role, company_id), tokens (access, refresh), loading, error
  - Actions: login(), logout(), refreshToken(), setUser()
  - Computed: isAuthenticated, userRole, canAccess(role)
  - Persistence: Load tokens from localStorage on app init
  - Devtools: Use zustand devtools for debugging
- **Files to Create/Modify:**
  - `frontend/src/stores/authStore.ts` (Zustand auth store)
  - `frontend/src/hooks/useAuthStore.ts` (store hook wrapper)
- **Notes:** Keep store simple; don't store sensitive data (tokens, passwords)

---

### Sprint 2.2: Dashboard & Shift UI (Week 6)

| Task ID | Title | Effort | Dependencies | Status |
|---------|-------|--------|--------------|--------|
| **FE-005** | Dashboard Layout & Navigation | 3 SP | FE-004 | Pending |
| **FE-006** | Shift Calendar Component | 5 SP | FE-005, BE-013 | Pending |
| **FE-007** | Shift Assignment Form | 5 SP | FE-006, BE-012 | Pending |

#### FE-005: Dashboard Layout & Navigation
- **Description:** Main dashboard layout with sidebar navigation, user menu
- **Acceptance Criteria:**
  - Sidebar with navigation links: Home, Shifts, Payroll, Swaps, Admin (role-based)
  - User menu: Profile, Settings, Logout
  - Dark mode toggle (optional, store in localStorage)
  - Responsive: Mobile-friendly (hamburger menu on mobile)
  - Top bar: App logo, user name/email
  - Content area: Main outlet for page content
- **Files to Create/Modify:**
  - `frontend/src/layouts/DashboardLayout.tsx` (main layout component)
  - `frontend/src/components/Sidebar.tsx` (navigation sidebar)
  - `frontend/src/components/TopBar.tsx` (top bar with user menu)
  - Update `frontend/src/App.tsx` with routing (Home, Shifts, Payroll, Admin routes)
- **Notes:** Use Tailwind CSS; shadcn/ui for buttons, menus; ensure accessibility (ARIA labels)

#### FE-006: Shift Calendar Component
- **Description:** Interactive calendar showing worker's shifts
- **Acceptance Criteria:**
  - Calendar view: Weekly grid or monthly grid (user choice)
  - Display shifts: Show shift name (template code), start/end time
  - Color-coding: Different colors for day shifts, night shifts, overtime
  - Date navigation: Previous/next month/week
  - Click shift: Show shift details (payroll preview, edit option if manager)
  - Filters: By worker (managers only), by date range
  - API: Fetch shifts from GET `/shifts/assignments?start_date=...&end_date=...`
- **Files to Create/Modify:**
  - `frontend/src/components/ShiftCalendar.tsx` (calendar component)
  - `frontend/src/components/ShiftDay.tsx` (individual day cell)
  - `frontend/src/hooks/useShifts.ts` (fetch shifts logic)
  - `frontend/src/stores/shiftStore.ts` (Zustand shifts store)
- **Notes:** Consider using react-big-calendar or date-fns for calendar logic

#### FE-007: Shift Assignment Form
- **Description:** Form to create/edit shift assignments (managers only)
- **Acceptance Criteria:**
  - Form fields: Worker (dropdown), Template (dropdown), Date (date picker)
  - Validation: All fields required; date can't be in past (managers can override)
  - Submit: POST `/shifts/assignments` with data
  - On success: Show success toast, refresh calendar
  - On error: Show error details from API
  - Loading state: Disable submit while pending
  - Edit mode: Pre-fill form if editing existing assignment
  - RBAC: Only visible to MANAGER role
- **Files to Create/Modify:**
  - `frontend/src/components/ShiftAssignmentForm.tsx` (form component)
  - `frontend/src/hooks/useShiftAssignment.ts` (form logic)
  - `frontend/src/api/shifts.ts` (API calls for shifts)
- **Notes:** Use react-hook-form + zod for validation; handle API errors gracefully

---

### Sprint 2.3: Payroll UI & Exports (Week 7)

| Task ID | Title | Effort | Dependencies | Status |
|---------|-------|--------|--------------|--------|
| **FE-008** | Payroll Breakdown Table Component | 5 SP | FE-005, BE-014 | Pending |
| **FE-009** | CSV/XML Export Feature | 5 SP | FE-008 | Pending |
| **FE-010** | Payroll Summary (Manager/HR view) | 3 SP | FE-008 | Pending |

#### FE-008: Payroll Breakdown Table Component
- **Description:** Table showing payroll breakdown per day or period
- **Acceptance Criteria:**
  - Columns: Date, Ordinarias (hours + rate), Nocturnas, Extras, Recargos, Total Gross
  - Show per-day breakdown or aggregated by week/month (user choice)
  - Color-coding: Highlight overtime rows, recargos
  - Sortable: Click column headers to sort
  - Filterable: Date range picker (start_date, end_date)
  - API: Fetch from GET `/payroll/worker/{worker_id}?start_date=...&end_date=...`
  - Workers can see own payroll; managers see team; HR sees all
- **Files to Create/Modify:**
  - `frontend/src/components/PayrollTable.tsx` (table component)
  - `frontend/src/hooks/usePayroll.ts` (fetch payroll logic)
  - `frontend/src/stores/payrollStore.ts` (Zustand payroll store)
- **Notes:** Use react-table or tanstack/table for advanced table features

#### FE-009: CSV/XML Export Feature
- **Description:** Button to export payroll as CSV or XML
- **Acceptance Criteria:**
  - Export button on payroll page
  - Format options: CSV or XML (radio/dropdown)
  - Parameters: Start date, end date (defaults to current month)
  - API: GET `/payroll/export?format=csv&start_date=...&end_date=...`
  - Response: File download (Content-Disposition: attachment)
  - CSV format: cedula,ordinarias,nocturnas,extras,recargos,total_gross (per spec)
  - XML format: <payroll><worker>...</worker></payroll> (per spec)
  - Loading: Show progress/loading indicator
- **Files to Create/Modify:**
  - `frontend/src/components/PayrollExport.tsx` (export form)
  - `frontend/src/api/payroll.ts` (export API call)
  - `frontend/src/utils/download.ts` (file download utility)
- **Notes:** Trigger file download via blob URL; test with actual files

#### FE-010: Payroll Summary (Manager/HR view)
- **Description:** High-level payroll summary for managers/HR (team/company overview)
- **Acceptance Criteria:**
  - Shows: Total hours, total payroll, worker count, overtime hours
  - Charts: Hours by type (ordinarias, nocturnas, extras), payroll by worker (pie chart)
  - Filters: By date range, by area/sub-org, by worker
  - API: GET `/payroll/summary?start_date=...&end_date=...`
  - RBAC: MANAGER sees team summary; HR_ADMIN sees company summary
- **Files to Create/Modify:**
  - `frontend/src/components/PayrollSummary.tsx` (summary component)
  - `frontend/src/components/PayrollCharts.tsx` (chart components using recharts/visx)
- **Notes:** Use recharts or visx for charts; lazy-load charts for performance

---

### Sprint 2.4: Shift Swaps & Integration Tests (Week 8)

| Task ID | Title | Effort | Dependencies | Status |
|---------|-------|--------|--------------|--------|
| **FE-011** | Shift Swap Request UI | 5 SP | FE-006, BE-009 (shift swap endpoints) | Pending |
| **FE-012** | Frontend Unit Tests (Vitest) | 5 SP | All FE tasks | Pending |
| **FE-013** | Frontend E2E Tests (Cypress) | 5 SP | All FE tasks | Pending |

#### FE-011: Shift Swap Request UI
- **Description:** UI for workers to request shift swaps
- **Acceptance Criteria:**
  - Workers can view own shifts
  - Select a shift + target worker to swap with
  - Submit request: POST `/swaps` with (my_shift_id, target_worker_id)
  - View pending swap requests: GET `/swaps/pending`
  - Managers can approve/reject: PUT `/swaps/{id}?action=approve|reject`
  - Status: Pending, Approved, Rejected (with timestamp)
  - Notifications: Show success/error toast on action
- **Files to Create/Modify:**
  - `backend/app/routers/swaps.py` (shift swap API endpoints, CRUD + approval)
  - `frontend/src/components/ShiftSwapForm.tsx` (request form)
  - `frontend/src/components/ShiftSwapList.tsx` (pending requests list)
  - Update `backend/app/services/swap_service.py` (swap logic, conflict detection)
- **Notes:** Backend task BE-009 must be completed first; implement swap validation (both workers in same org, no conflicts)

#### FE-012: Frontend Unit Tests (Vitest)
- **Description:** Unit tests for React components, stores, hooks
- **Acceptance Criteria:**
  - Tests for: Auth store, shift store, payroll store
  - Tests for: Login form, shift calendar, payroll table
  - Tests for: API client, interceptors, error handling
  - Coverage: >80% of frontend code
  - All tests pass; no warnings
  - Use Mock Service Worker (MSW) for API mocking
- **Files to Create/Modify:**
  - `frontend/src/__tests__/stores/authStore.test.ts`
  - `frontend/src/__tests__/stores/shiftStore.test.ts`
  - `frontend/src/__tests__/components/LoginPage.test.tsx`
  - `frontend/src/__tests__/api/client.test.ts`
  - `frontend/vitest.config.ts` (Vitest config)
  - `frontend/src/mocks/handlers.ts` (MSW handlers)
- **Notes:** Use `@testing-library/react` for component testing; test user interactions

#### FE-013: Frontend E2E Tests (Cypress)
- **Description:** End-to-end tests simulating user workflows
- **Acceptance Criteria:**
  - Test flow: Login → View dashboard → Create shift → View payroll → Export → Logout
  - Test RBAC: Different roles see different pages
  - Test errors: Invalid login, API errors
  - All tests pass in headless mode
  - Coverage: Happy path + 2-3 error scenarios
- **Files to Create/Modify:**
  - `frontend/cypress/e2e/auth.cy.ts` (login/logout flow)
  - `frontend/cypress/e2e/shifts.cy.ts` (shift management flow)
  - `frontend/cypress/e2e/payroll.cy.ts` (payroll view/export flow)
  - `frontend/cypress.config.ts` (Cypress config)
- **Notes:** Run with `cypress open` for development, `cypress run` for CI

**NOTE:** Backend tasks for Shift Swap endpoints (not yet listed above) needed before FE-011 can be completed:
- **BE-009: Shift Swap Endpoints** (3 SP) — POST/GET/PUT `/swaps` endpoints
  - Acceptance: Create, list, approve/reject swap requests
  - Add to Sprint 1.4 or Sprint 2.1 (depends on resource allocation)

---

## Phase 3: Testing, Deployment & Refinement (Weeks 9-12)

### Sprint 3.1: Law Compliance Validation & UAT (Week 9)

| Task ID | Title | Effort | Dependencies | Status |
|---------|-------|--------|--------------|--------|
| **QA-001** | Manual Law Compliance Testing | 8 SP | All payroll tests | Pending |
| **QA-002** | UAT Script & Checklist | 5 SP | BE-014, FE-010 | Pending |

#### QA-001: Manual Law Compliance Testing
- **Description:** Manual tests verifying payroll against Colombian labor law (CST, Ley 2101/2021)
- **Acceptance Criteria:**
  - Test scenarios (manual + automated):
    - Daytime shift (6am-2pm) on Monday: Only ordinarias, no surcharge ✓
    - Night shift (10pm-6am) on Tuesday: Nocturnas with 35% surcharge ✓
    - Shift crossing midnight (10pm Mon → 4am Tue): Mixed ordinarias + nocturnas ✓
    - Sunday shift: 75% surcharge on all hours ✓
    - Holiday (e.g., Dec 25): 75% surcharge on all hours ✓
    - Overtime (50+ hours in week): Hours >46 get 25% surcharge ✓
    - Workweek transition (Dec 31 into Jan 1): Correctly reset workweek hours ✓
    - Habitual Sundays (if 3+ Sundays/month): Detect and flag for compensatory day logic (Phase 4) ✓
  - Document test results: Pass/fail per scenario
  - Document any deviations or bugs found
- **Files to Create/Modify:**
  - `docs/compliance-test-results.md` (test log)
  - `backend/tests/test_colombian_law_compliance.py` (automated compliance tests)
- **Notes:** Work with domain expert (user) to verify calculations; iterate if needed

#### QA-002: UAT Script & Checklist
- **Description:** Test checklist for business stakeholders (HR manager, worker)
- **Acceptance Criteria:**
  - User-friendly checklist (Google Sheets or Markdown)
  - Steps: Login as different roles, assign shift, view payroll, export CSV, etc.
  - Success criteria for each step (e.g., "CSV download completes within 2 seconds")
  - Sign-off: Stakeholder confirms all steps passed
  - Document findings: Any UX improvements, bugs, missing features
- **Files to Create/Modify:**
  - `docs/uat-checklist.md` (UAT checklist)
- **Notes:** Distribute to stakeholders; schedule UAT session (1-2 hours)

---

### Sprint 3.2: Load Testing & Performance Optimization (Week 10)

| Task ID | Title | Effort | Dependencies | Status |
|---------|-------|--------|--------------|--------|
| **QA-003** | Load Testing (1000+ workers) | 5 SP | BE-014, BE-016 | Pending |
| **QA-004** | Performance Optimization (DB indexes, caching) | 5 SP | QA-003 | Pending |
| **DEV-001** | Admin UI & System Health Dashboard | 3 SP | FE-005 | Pending |

#### QA-003: Load Testing (1000+ workers)
- **Description:** Performance testing with realistic data volume
- **Acceptance Criteria:**
  - Dataset: 1000 workers × 30 days = 30,000 shifts, 30,000+ payroll entries
  - Test queries: Payroll export for 1000 workers (should complete <30 seconds)
  - Test API: Concurrent requests (100 simultaneous login attempts)
  - Measure: Response times, database query times, memory usage, CPU
  - Tools: locust or k6 for load testing; pg_stat_statements for slow query logging
  - Results: Document response times, identify bottlenecks
- **Files to Create/Modify:**
  - `backend/load_tests/payroll_export_load_test.py` (locust script)
  - `docs/load-test-results.md` (results log)
- **Notes:** Run on staging (Render + Neon); iterate optimization if needed

#### QA-004: Performance Optimization (DB indexes, caching)
- **Description:** Apply optimizations based on load test findings
- **Acceptance Criteria:**
  - Add missing indexes (e.g., on (company_id, worker_id, date) for payroll queries)
  - Implement query caching (Redis) for frequently accessed data (holiday calendars, surcharge rules)
  - Lazy-load relationships in ORM (don't fetch all related objects by default)
  - Optimize N+1 queries: Use SQLAlchemy `selectinload` or `joinedload`
  - Result: Re-run load tests; should see <20% improvement in response times
- **Files to Create/Modify:**
  - `backend/app/models/` (add indexes to ORM models)
  - `backend/app/services/caching.py` (Redis caching logic)
  - Update SQL schema migration with new indexes
- **Notes:** Monitor Neon connection pool; increase pool if needed

#### DEV-001: Admin UI & System Health Dashboard
- **Description:** Admin-only page showing system health, metrics
- **Acceptance Criteria:**
  - Metrics: Total users, total shifts this month, avg payroll per worker, system uptime
  - Charts: Shifts trend (last 30 days), payroll by area, workers by role
  - Alerts: Any pending UAT findings, overdue approvals
  - RBAC: HR_ADMIN only
- **Files to Create/Modify:**
  - `frontend/src/pages/AdminDashboard.tsx`
  - `backend/app/routers/admin.py` (GET `/admin/metrics`, `/admin/health`)
- **Notes:** Keep UI simple; focus on actionable metrics

---

### Sprint 3.3: Deployment & CI/CD (Week 11)

| Task ID | Title | Effort | Dependencies | Status |
|---------|-------|--------|--------------|--------|
| **DEV-002** | GitHub Actions CI/CD Pipeline | 5 SP | All tests passing | Pending |
| **DEV-003** | Backend Deployment to Render | 3 SP | DEV-002 | Pending |
| **DEV-004** | Frontend Deployment to Vercel | 3 SP | DEV-002 | Pending |
| **DEV-005** | Database Schema on Neon (Production Setup) | 2 SP | BE-002 | Pending |

#### DEV-002: GitHub Actions CI/CD Pipeline
- **Description:** Automate tests, builds, and deployment
- **Acceptance Criteria:**
  - Triggers: On every push to main/develop
  - Jobs:
    - Backend: pytest run all tests, coverage check (>80%), linting (flake8)
    - Frontend: npm test (Vitest), E2E tests (Cypress), build check
    - On success: Trigger deployment jobs
  - Slack notifications: Build status, test failures
- **Files to Create/Modify:**
  - `.github/workflows/backend-test.yml`
  - `.github/workflows/frontend-test.yml`
  - `.github/workflows/deploy-backend.yml`
  - `.github/workflows/deploy-frontend.yml`
- **Notes:** Use secrets for credentials (NEON_DATABASE_URL, VERCEL_TOKEN, RENDER_API_KEY)

#### DEV-003: Backend Deployment to Render
- **Description:** Deploy FastAPI app to Render
- **Acceptance Criteria:**
  - Dockerfile created for FastAPI
  - Docker image builds and runs locally first (test with `docker build . && docker run`)
  - Render.com account set up; web service created
  - GitHub integration: Push to main triggers Render deploy
  - Environment variables set in Render (DATABASE_URL, SECRET_KEY, etc.)
  - Health check: GET /health returns 200
  - Deploy time: <5 minutes
- **Files to Create/Modify:**
  - `backend/Dockerfile`
  - `backend/.dockerignore`
  - `render.yaml` (Render deployment config)
- **Notes:** Use Render's free tier for MVP (can sleep); upgrade to $7/mo no-sleep for production

#### DEV-004: Frontend Deployment to Vercel
- **Description:** Deploy React app to Vercel
- **Acceptance Criteria:**
  - Vercel account set up; project linked to GitHub
  - Push to main triggers Vercel deploy
  - Environment variables set in Vercel (VITE_API_URL=https://api.cronos.example.com)
  - Build: `npm run build` succeeds, output in dist/
  - Deploy time: <2 minutes
  - Preview deployments: Create PR → automatic preview URL generated
- **Files to Create/Modify:**
  - `vercel.json` (Vercel config)
  - Update `frontend/.env.example` with production VITE_API_URL
- **Notes:** Use Vercel free tier; upgrade to Pro if needed for custom domains

#### DEV-005: Database Schema on Neon (Production Setup)
- **Description:** Set up production PostgreSQL database on Neon
- **Acceptance Criteria:**
  - Neon account created; project set up
  - Branching: Main branch for production, dev branch for testing
  - Connection string: DATABASE_URL stored in Render/Vercel secrets
  - Run migrations: `alembic upgrade head` on production database
  - Backups: Enable automatic daily backups (Neon default)
  - Connection pooling: PgBouncer enabled via Neon
- **Files to Create/Modify:**
  - `backend/.env.production` (template for production env vars)
- **Notes:** Neon free tier: 1 project, 3 branches, 1GB storage; sufficient for MVP

---

### Sprint 3.4: Documentation & Release (Week 12)

| Task ID | Title | Effort | Dependencies | Status |
|---------|-------|--------|--------------|--------|
| **DOCS-001** | API Documentation (OpenAPI/Swagger) | 3 SP | All API endpoints complete | Pending |
| **DOCS-002** | Deployment Guide & Runbook | 3 SP | DEV-003, DEV-004, DEV-005 | Pending |
| **DOCS-003** | User Guide (HR Manager, Worker) | 5 SP | FE-010, QA-002 | Pending |
| **REL-001** | Release & Soft Launch | 3 SP | All sprints complete | Pending |

#### DOCS-001: API Documentation (OpenAPI/Swagger)
- **Description:** Auto-generated API docs from FastAPI
- **Acceptance Criteria:**
  - Swagger UI at `/docs` with all 27 endpoints documented
  - Request/response schemas fully documented
  - Examples for each endpoint (e.g., sample request for POST /shifts/assignments)
  - Authentication documented (JWT bearer token)
  - Rate limiting noted (if any)
  - Errors documented (4xx, 5xx codes with descriptions)
- **Files to Create/Modify:**
  - Update all API endpoints with docstrings, examples
  - `backend/app/main.py` update FastAPI app config for Swagger title, version
- **Notes:** FastAPI auto-generates OpenAPI spec at /openapi.json; Swagger UI at /docs

#### DOCS-002: Deployment Guide & Runbook
- **Description:** Step-by-step guide for deploying Cronos to production
- **Acceptance Criteria:**
  - Prerequisites: GitHub account, Vercel account, Render account, Neon account
  - Steps to deploy:
    1. Fork/clone repo
    2. Set up Neon database (create project, get connection string)
    3. Create Render web service (link GitHub, set env vars)
    4. Create Vercel project (link GitHub, set env vars)
    5. Deploy and test
  - Troubleshooting: Common issues (connection pool exhausted, CORS errors, etc.)
  - Monitoring: How to check Render logs, Neon metrics, Vercel analytics
- **Files to Create/Modify:**
  - `docs/DEPLOYMENT.md` (deployment guide)
  - `docs/TROUBLESHOOTING.md` (common issues)
- **Notes:** Include screenshots/links; test guide with fresh deployment

#### DOCS-003: User Guide (HR Manager, Worker)
- **Description:** End-user documentation
- **Acceptance Criteria:**
  - Worker Guide: How to view shifts, payroll, request swaps
  - Manager Guide: How to create templates, assign shifts, approve swaps
  - HR Admin Guide: How to manage users, export payroll, generate reports
  - Screenshots: Step-by-step with UI screenshots
  - FAQs: Common questions (payroll calculations, export formats, etc.)
- **Files to Create/Modify:**
  - `docs/USER_GUIDE.md` (combined user guide)
  - `docs/ADMIN_GUIDE.md` (admin-only features)
- **Notes:** Write for non-technical audience; include examples

#### REL-001: Release & Soft Launch
- **Description:** Finalize release, conduct soft launch
- **Acceptance Criteria:**
  - Version bump: v1.0.0 in all files (package.json, pyproject.toml, etc.)
  - Git tag: `git tag -a v1.0.0 -m "MVP Release"`
  - Release notes: Document features, known limitations, roadmap
  - Soft launch: Deploy to staging, announce to beta users
  - Collect feedback: Monitor Slack/email for issues
  - Post-launch tasks: Log any issues for Phase 4, gather user feedback
- **Files to Create/Modify:**
  - `CHANGELOG.md` (release notes)
  - Update `README.md` with links to docs, demo, feedback form
- **Notes:** Don't push to production main branch yet; use staging for 1-2 weeks of testing

---

## Task Dependencies & Critical Path

```
Phase 1 (Weeks 1-4):
  BE-001 (FastAPI Setup) → BE-002 (DB Schema) → BE-003 (ORM Models) → BE-004 (DB Connection)
    ↓
  BE-005 (JWT) → BE-006 (Auth Endpoints) → BE-007 (Tenant Middleware) → BE-008 (RBAC)
    ↓
  BE-009 (Hour Classification) → BE-010 (Surcharge Calc) → BE-011 (100+ Unit Tests)
    ↓
  BE-012 (Template CRUD) → BE-013 (Assignment CRUD) → BE-014 (Payroll Queries) → BE-015 (Holidays) → BE-016 (Integration Tests)

Phase 2 (Weeks 5-8):
  FE-001 (Vite Setup) → FE-002 (API Client) → FE-003 (Login UI) → FE-004 (Auth Store)
    ↓
  FE-005 (Dashboard) → FE-006 (Shift Calendar) → FE-007 (Shift Form)
    ↓
  FE-008 (Payroll Table) → FE-009 (CSV/XML Export) → FE-010 (Summary)
    ↓
  FE-011 (Shift Swaps) → FE-012 (Unit Tests) → FE-013 (E2E Tests)

Phase 3 (Weeks 9-12):
  QA-001 (Law Compliance) → QA-002 (UAT)
  QA-003 (Load Testing) → QA-004 (Optimization)
  DEV-002 (CI/CD) → DEV-003 (Render Deploy) → DEV-004 (Vercel Deploy) → DEV-005 (Neon Setup)
  DOCS-001 (API Docs) → DOCS-002 (Deployment Guide) → DOCS-003 (User Guide) → REL-001 (Release)
```

---

## Effort Summary

| Phase | Tasks | Story Points | Weeks | Velocity |
|-------|-------|--------------|-------|----------|
| **Phase 1** | 16 | 48 SP | 4 | 12 SP/week |
| **Phase 2** | 13 | 54 SP | 4 | 13.5 SP/week |
| **Phase 3** | 19 | 40 SP | 4 | 10 SP/week |
| **Total** | 48 | 142 SP | 12 | 11.8 SP/week avg |

---

## Team Allocation

- **Backend Dev:** Phase 1 (full), Phase 2 (partial for BE-009 Shift Swaps), Phase 3 (support QA/deploy)
- **Frontend Dev:** Phase 2 (full), Phase 3 (support testing/deployment)
- **QA (0.5):** Phase 1 (light), Phase 2 (light), Phase 3 (full)

---

## Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|-----------|
| **Payroll logic bugs** | High | Medium | 100+ unit tests, law compliance validation, UAT with stakeholder |
| **Colombian law changes mid-2026** | Medium | Low | Version payroll engine, document law version, communicate with users |
| **DB performance (1000+ workers)** | High | Medium | Load testing Week 10, optimize queries & indexes, monitor Neon metrics |
| **API rate limiting (free tier)** | Medium | Low | Render free tier sleeps after 15 mins; upgrade to $7/mo no-sleep before production |
| **Frontend build size (Vercel limits)** | Low | Low | Monitor bundle size, lazy-load routes, use code splitting |
| **JWT token refresh failures** | Medium | Medium | Implement retry logic, test token refresh flow thoroughly, handle gracefully |
| **Multi-tenant data leak** | Critical | Low | Rigorous testing of company_id injection, audit SQL queries, conduct security review |
| **Export format incompatibility** | Medium | Low | Work with HR teams to validate CSV/XML formats, test with customer nómina software |

---

## Key Milestones

- **End of Week 4:** Core payroll engine working, 100+ tests passing, basic API functional
- **End of Week 8:** Full UI built, all workflows end-to-end testable
- **End of Week 10:** Load tests passed, performance optimized, UAT passed
- **End of Week 12:** Deployed to Vercel/Render/Neon, soft launch complete, beta feedback collected

---

## Next Steps (After Task Approval)

1. **User Reviews tasks.md**
   - Verify task breakdown makes sense
   - Confirm effort estimates are reasonable
   - Adjust dependencies or sprints if needed

2. **User Approves (or requests changes)**
   - If approved: Proceed to Phase 6 (SDD Apply)
   - If changes needed: Update tasks.md, re-review

3. **SDD Apply Phase (Week-by-week implementation)**
   - Generate code scaffolds (FastAPI boilerplate, React starter)
   - Check off tasks as completed
   - Run tests after each sprint
   - Track progress

4. **SDD Verify Phase**
   - Validate payroll calculations against spec
   - Run full test suite
   - UAT with stakeholders

5. **SDD Archive Phase**
   - Final release documentation
   - Prepare for Phase 4 (post-MVP roadmap)

---

**This task breakdown is flexible.** Tasks can be reordered, effort adjusted, or split across team members. The goal is to ship a working MVP in 12 weeks with 100% Colombian law compliance and sufficient test coverage for confidence in production use.
