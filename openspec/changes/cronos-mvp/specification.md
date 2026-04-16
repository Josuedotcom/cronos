# Cronos MVP - Specification Document

**Project:** Cronos - Colombian Labor Law-Compliant Shift Management System  
**Change ID:** cronos-mvp  
**Phase:** Specification  
**Status:** DRAFT  
**Created:** 2026-04-16  
**Author:** SDD Specification Phase  

---

## Table of Contents

1. [Requirements Overview](#1-requirements-overview)
2. [Functional Requirements by User Role](#2-functional-requirements-by-user-role)
3. [Colombian Labor Law Requirements](#3-colombian-labor-law-requirements)
4. [Data Model Specification](#4-data-model-specification)
5. [API Specifications](#5-api-specifications)
6. [Workflow Specifications](#6-workflow-specifications)
7. [UI/UX Requirements](#7-uiux-requirements)
8. [Non-Functional Requirements](#8-non-functional-requirements)
9. [Testing Requirements](#9-testing-requirements)
10. [Constraints & Assumptions](#10-constraints--assumptions)

---

## 1. Requirements Overview

### Project Goal
Build a web application where Colombian organizations can:
- **Workers** view their shift schedules and payroll breakdown
- **Managers** assign shifts, manage constraints, approve shift swaps
- **HR Teams** export accurate payroll data (cedula + hour categories) for their nómina software
- All while maintaining strict compliance with Colombian labor law (CST + Ley 2101/2021)

### Scope (MVP - Phases 1-3)
- Shift scheduling (CRUD templates + assignments)
- Multi-tenant data isolation (Company → SubOrganization → Area)
- Colombian payroll calculations (surcharges, overtime, holidays)
- Payroll export (CSV/XML with cedula + rubros)
- Shift swap requests (worker → manager approval workflow)
- Basic analytics (hours summary, overtime alerts)
- Comprehensive test coverage (100+ test cases for payroll edge cases)

### Out of Scope (Post-MVP)
- Sunday compensatory day auto-generation (requires stakeholder decision)
- Biometric/GPS clock-in
- Custom union agreement surcharges (CST standard only for MVP)
- Advanced analytics/reporting
- Mobile native app (PWA responsive web sufficient)
- Real-time WebSocket notifications (email sufficient)
- Two-factor authentication
- Audit logs (basic DB timestamps only)

---

## 2. Functional Requirements by User Role

### 2.1 Worker Requirements

**WR-1: View My Schedule**
- **Description:** Worker can view their assigned shifts for a given date range
- **Input:** Date range (e.g., current week, current month)
- **Output:** List of shifts with:
  - Date, start time, end time, shift template name
  - Recalculated hours (ordinarias, nocturnas, extras, recargos)
  - Total gross amount for the shift
- **Constraints:** Only own shifts visible (multi-tenant isolation)
- **UI:** Shift calendar view (weekly grid or list)

**WR-2: View My Payroll Breakdown**
- **Description:** Worker sees detailed payroll for a specific day or period
- **Input:** Date (or date range)
- **Output:**
  - Ordinarias: X hours @ $Y rate
  - Nocturnas: X hours @ ($Y × 1.35) rate
  - Extras ordinarias: X hours @ ($Y × 1.25) rate
  - Extras nocturnas: X hours @ ($Y × 1.75) rate
  - Recargo dominical: X hours @ ($Y × 1.75) rate
  - Total gross for period
- **Constraints:** Only own payroll visible
- **UI:** Payroll detail table per day, or aggregated per week/month

**WR-3: Request Shift Swap**
- **Description:** Worker initiates a shift swap request with another worker
- **Input:**
  - My shift to offer (ShiftAssignment ID)
  - Target worker to swap with (Worker ID)
- **Output:**
  - SwapRequest created with status `pending`
  - Notification sent to manager
- **Constraints:**
  - Can't swap with self
  - Can't swap shifts in the past
  - Both workers must exist in same Organization
- **Workflow:** WR-3 → MR-3 (manager approval) → WR-3 (notification of result)

**WR-4: View Swap Request Status**
- **Description:** Worker sees status of their pending swap requests
- **Input:** None (auto-filtered to current worker)
- **Output:** List of SwapRequests with status (pending, approved, rejected)
- **UI:** Simple list or notification center

---

### 2.2 Manager Requirements

**MR-1: Create Shift Templates**
- **Description:** Manager defines recurring shift patterns (e.g., "T" for tarde, "M" for mañana)
- **Input:**
  - Shift code (e.g., "T")
  - Shift name (e.g., "Tarde")
  - Start time (e.g., 14:00)
  - End time (e.g., 22:00)
  - Description (optional)
- **Output:** ShiftTemplate created
- **Constraints:** Code must be unique per Area
- **Permissions:** Manager role, scoped to own Organization/Area

**MR-2: Assign Shifts to Workers**
- **Description:** Manager assigns a shift template to a worker on a specific date
- **Input:**
  - Worker ID
  - Shift Template ID
  - Assignment Date
- **Output:** ShiftAssignment created
- **Constraints:**
  - Validate no duplicate shifts same day (one shift per worker per day)
  - Warn if assignment would exceed weekly hour limit (2 hrs/day or 12 hrs/week overtime max)
  - Prevent assigning shifts in the past (unless approved by HR)
- **Side Effect:** Auto-calculate TimesheetDay for that worker/date
- **Permissions:** Manager role
- **UI:** Shift scheduler UI (drag-drop calendar or form)

**MR-3: Approve/Reject Shift Swaps**
- **Description:** Manager reviews and approves/rejects worker shift swap requests
- **Input:**
  - SwapRequest ID
  - Action: approve or reject
  - Rejection reason (if reject)
- **Output:** SwapRequest status updated
- **Constraints:**
  - Validate both workers won't exceed limits after swap
  - Only manager can approve
- **Side Effect:** If approved, swap the two ShiftAssignments (worker A gets worker B's shift, vice versa)
- **Workflow:** Approval → Email notification to both workers
- **UI:** Swap request queue with approve/reject buttons

**MR-4: Update/Delete Shift Assignments**
- **Description:** Manager can modify or cancel shift assignments
- **Input:**
  - ShiftAssignment ID
  - New details (optional): date, shift template, etc.
  - OR: Delete action
- **Output:** ShiftAssignment updated/deleted
- **Constraints:**
  - Can't modify shifts in the past (requires HR override)
- **Side Effect:** If modified, recalculate TimesheetDay
- **Permissions:** Manager role

**MR-5: View Team Schedule**
- **Description:** Manager sees all shifts for their team/area
- **Input:** Date range, Area filter (optional)
- **Output:** Grid/calendar view of all team shifts
- **Constraints:** Only own Organization/Area shifts visible
- **UI:** Team calendar view with worker names

**MR-6: View Team Payroll Summary**
- **Description:** Manager sees aggregated payroll data for their team
- **Input:** Date range, Area filter
- **Output:**
  - Per worker: ordinarias, nocturnas, extras, recargos, total gross
  - Team totals
  - Overtime alerts (workers exceeding limits)
- **UI:** Summary table with drill-down to worker detail

---

### 2.3 HR Requirements

**HR-1: Manage Organizations & Hierarchy**
- **Description:** HR admin creates and manages Company → SubOrganization → Area hierarchy
- **Input:**
  - Company name, subdomain (for multi-tenant isolation)
  - SubOrganization name, parent company
  - Area name, parent sub-org, manager assignment
- **Output:** Hierarchy nodes created
- **Permissions:** HR admin role

**HR-2: Manage Users & Roles**
- **Description:** HR admin creates workers, managers, and assigns roles
- **Input:**
  - Name, email, phone, cedula
  - Role: worker, manager, hr_admin
  - Contract type: standard (8-9h/day), shift_36h (6h/day)
  - Hourly rate
  - Hire date
- **Output:** Worker created with role + permissions
- **Permissions:** HR admin role

**HR-3: Manage Holiday Calendar**
- **Description:** HR admin defines Colombian public holidays and company-specific holidays
- **Input:**
  - Holiday date, name, is_public_holiday (boolean)
- **Output:** Holiday entry created
- **Constraints:**
  - Pre-populate with official Colombian holidays (18+ festivos)
  - Allow custom company holidays
- **Side Effect:** Any shift on holiday date auto-triggers 75% surcharge + 110% if night shift
- **Permissions:** HR admin role

**HR-4: Configure Surcharge Rules** (Optional for MVP)
- **Description:** HR can adjust surcharge percentages (for future: custom union agreements)
- **Input:**
  - Surcharge type (night, sunday, sunday_night, overtime_day, etc.)
  - Percentage override (e.g., 35% → 50% for custom agreement)
  - Effective date range
- **Output:** SurchargeRule created/updated
- **Constraints:** Default CST percentages; allow override with audit trail
- **Permissions:** HR admin role

**HR-5: Export Payroll Data**
- **Description:** HR exports shift data in CSV/XML format for nómina integration
- **Input:**
  - Date range (e.g., bi-weekly payroll period)
  - Format: CSV or XML
  - Filter: All workers, or specific Area/SubOrg
- **Output:** File download (CSV or XML) with columns:
  - cedula, nombre, date, ordinarias, nocturnas, extras_dia, extras_noche, recargo_domingo, recargo_noche, total_valor
- **Constraints:** Only HR can export
- **Performance:** Streaming response for large exports (1000+ workers)
- **Permissions:** HR admin role

**HR-6: View All Payroll Data**
- **Description:** HR views comprehensive payroll dashboard
- **Input:** Date range, Company/SubOrg/Area filters
- **Output:**
  - Aggregated hours by type (per worker, per team, per company)
  - Total payroll cost
  - Overtime violations (workers exceeding limits)
  - Dominical work summary
- **Permissions:** HR admin role (scoped to own company)

**HR-7: Generate Reports**
- **Description:** HR generates compliance and analytics reports
- **Input:** Date range, metrics (hours, cost, violations, etc.)
- **Output:** PDF or downloadable spreadsheet
- **Permissions:** HR admin role
- **Note:** MVP = basic reports; Phase 4 = advanced analytics

---

## 3. Colombian Labor Law Requirements

### 3.1 Hour Classification Rules

**Standard Daytime:** 6:00 AM - 9:00 PM (no surcharge)  
**Standard Nighttime:** 9:00 PM - 6:00 AM (35% surcharge)

**Surcharge Percentages (CST):**
- Ordinary hours: 0% (base rate)
- Night hours: +35%
- Sunday day hours: +75%
- Sunday night hours: +110% (35% + 75%)
- Overtime day: +25%
- Overtime night: +75%
- Overtime Sunday day: +100%
- Overtime Sunday night: +150%

### 3.2 Workweek Hour Limits (Transitional)

- **2024:** Max 46 hours/week (from 48)
- **July 2025:** Max 44 hours/week
- **2026:** Max 42 hours/week (final)

**System behavior:**
- Auto-detect current year
- Apply correct limit based on date
- Warn/block if assignment would exceed limit

### 3.3 Overtime Rules

- **Definition:** Hours worked beyond standard daily limit (typically 8-9 hours)
- **Max daily:** 2 hours/day
- **Max weekly:** 12 hours/week
- **Surcharges:** Apply per type (day, night, Sunday)
- **Enforcement:** System must warn/block if limits exceeded

### 3.4 Midnight Rule

**Rule:** A shift crossing midnight changes hour type at exactly 00:00

**Example:**
```
Shift: Saturday 8:00 PM → Sunday 4:00 AM

Saturday 8:00 PM - 9:00 PM  (1h)  = Ordinary hours
Saturday 9:00 PM - 12:00 AM (3h)  = Night hours (35% surcharge)
Sunday 12:00 AM - 4:00 AM   (4h)  = Sunday night (110% surcharge)
```

**Implementation:** Split shift at midnight, classify each portion separately.

### 3.5 Habitual Dominical Work

**Definition:** If a worker works 3 or more Sundays in a calendar month, it's "habitual."

**Consequence:**
- Worker entitled to: 75% surcharge (payment) + paid compensatory day off
- If 1-2 Sundays (occasional): 75% surcharge OR compensatory day (worker's choice)

**MVP:** Calculate habitual status, flag for HR decision (don't auto-generate days)  
**Phase 4:** Auto-generate compensatory day entries

### 3.6 Holiday Surcharges

**Public Holidays:** 18+ official Colombian holidays (Año Nuevo, Epifanía, San Valentín, etc.)

**Surcharge:**
- Holiday day: +75% surcharge
- Holiday night: +110% surcharge (35% + 75%)

**Implementation:**
- Maintain HolidayCalendar table with all holidays
- On shift calculation, check if assignment date is holiday
- Apply appropriate surcharge

### 3.7 Rest Period Enforcement

**Rule:** Minimum 11 hours rest between shifts

**Implementation:**
- Warn if new shift assigned within 11 hours of previous shift's end
- Allow override by manager (with audit trail)

---

## 4. Data Model Specification

### 4.1 Core Entities

#### Company
```
id: UUID (PK)
name: String (required)
subdomain: String (unique, for multi-tenant routing)
timezone: String (default: America/Bogota)
created_at: Timestamp
updated_at: Timestamp
```

#### SubOrganization
```
id: UUID (PK)
company_id: UUID (FK → Company, required)
name: String (required)
description: String (optional)
parent_suborganization_id: UUID (FK → SubOrganization, optional - for hierarchy)
created_at: Timestamp
updated_at: Timestamp
```

#### Area
```
id: UUID (PK)
company_id: UUID (FK → Company, required)
suborganization_id: UUID (FK → SubOrganization, required)
name: String (required)
description: String (optional)
manager_id: UUID (FK → Worker, optional - manager assigned to area)
created_at: Timestamp
updated_at: Timestamp
```

#### Worker
```
id: UUID (PK)
company_id: UUID (FK → Company, required)
suborganization_id: UUID (FK → SubOrganization, required)
area_id: UUID (FK → Area, required)
cedula: String (required, unique per company)
first_name: String (required)
last_name: String (required)
email: String (unique per company, optional)
phone: String (optional)
contract_type: Enum (standard, shift_36h) - default: standard
hourly_rate: Decimal(10,2) (required, in COP or base currency)
hire_date: Date (required)
status: Enum (active, inactive, on_leave) - default: active
role: Enum (worker, manager, hr_admin) - default: worker
password_hash: String (for local auth, required)
created_at: Timestamp
updated_at: Timestamp
```

#### ShiftTemplate
```
id: UUID (PK)
company_id: UUID (FK → Company, required)
suborganization_id: UUID (FK → SubOrganization, required)
area_id: UUID (FK → Area, required)
code: String (e.g., "T", "M", "N") - required
name: String (e.g., "Tarde", "Mañana") - required
start_time: Time (e.g., 14:00) - required
end_time: Time (e.g., 22:00) - required
description: String (optional)
is_active: Boolean - default: true
created_at: Timestamp
updated_at: Timestamp
```

#### ShiftAssignment
```
id: UUID (PK)
company_id: UUID (FK → Company, required)
worker_id: UUID (FK → Worker, required)
shift_template_id: UUID (FK → ShiftTemplate, required)
assignment_date: Date (required)
status: Enum (scheduled, completed, absent, swapped) - default: scheduled
is_overtime_shift: Boolean - default: false
notes: String (optional)
created_by_worker_id: UUID (FK → Worker, optional - who created this)
created_at: Timestamp
updated_at: Timestamp
UNIQUE(worker_id, assignment_date)  -- One shift per worker per day
```

#### TimesheetDay
```
id: UUID (PK)
company_id: UUID (FK → Company, required)
worker_id: UUID (FK → Worker, required)
timesheet_date: Date (required)
ordinary_hours: Decimal(5,2) - default: 0
night_hours: Decimal(5,2) - default: 0
sunday_day_hours: Decimal(5,2) - default: 0
sunday_night_hours: Decimal(5,2) - default: 0
overtime_day: Decimal(5,2) - default: 0
overtime_night: Decimal(5,2) - default: 0
overtime_sunday_day: Decimal(5,2) - default: 0
overtime_sunday_night: Decimal(5,2) - default: 0
total_regular_amount: Decimal(12,2) - calculated
total_surcharge_amount: Decimal(12,2) - calculated
total_gross_amount: Decimal(12,2) - calculated
created_at: Timestamp
updated_at: Timestamp
UNIQUE(worker_id, timesheet_date)
```

#### ShiftSwapRequest
```
id: UUID (PK)
company_id: UUID (FK → Company, required)
requester_worker_id: UUID (FK → Worker, required)
target_worker_id: UUID (FK → Worker, required)
shift_assignment_id: UUID (FK → ShiftAssignment, required - the shift being offered)
status: Enum (pending, approved, rejected) - default: pending
manager_approved_by: UUID (FK → Worker, optional)
rejection_reason: String (optional)
created_at: Timestamp
resolved_at: Timestamp (nullable, populated on approval/rejection)
updated_at: Timestamp
CHECK (requester_worker_id != target_worker_id)
```

#### HolidayCalendar
```
id: UUID (PK)
company_id: UUID (FK → Company, required)
holiday_date: Date (required)
holiday_name: String (required)
is_public_holiday: Boolean - default: true
notes: String (optional)
created_at: Timestamp
UNIQUE(company_id, holiday_date)
```

#### SurchargeRule
```
id: UUID (PK)
company_id: UUID (FK → Company, required)
surcharge_type: Enum (night, sunday_day, sunday_night, overtime_day, overtime_night, overtime_sunday_day, overtime_sunday_night) - required
percentage: Decimal(5,2) (e.g., 35.00 for 35%) - required
effective_from: Date (required)
effective_to: Date (nullable, ongoing if null)
description: String (optional)
created_at: Timestamp
updated_at: Timestamp
```

---

## 5. API Specifications

### 5.1 Authentication Endpoints

#### POST /auth/login
```
Request:
  {
    "email": "juan@company.com",
    "password": "securepassword"
  }

Response (200 OK):
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": "uuid",
      "name": "Juan Pérez",
      "role": "manager",
      "company_id": "uuid",
      "area_id": "uuid"
    }
  }

Errors:
  401 Unauthorized - Invalid credentials
```

#### POST /auth/logout
```
Request: (requires Authorization header)
Response (200 OK): { "message": "Logged out successfully" }
```

#### POST /auth/refresh-token
```
Request: (requires Authorization header with refresh token)
Response (200 OK): { "access_token": "new_token", "expires_in": 3600 }
```

---

### 5.2 Shift Template Endpoints

#### GET /api/shift-templates
```
Query Params:
  area_id: UUID (required)
  is_active: Boolean (optional, default: true)
  limit: Int (default: 50)
  offset: Int (default: 0)

Response (200 OK):
  {
    "data": [
      {
        "id": "uuid",
        "code": "T",
        "name": "Tarde",
        "start_time": "14:00",
        "end_time": "22:00",
        "description": "Turno de tarde"
      }
    ],
    "total": 10,
    "limit": 50,
    "offset": 0
  }

Permissions: Worker (own area only), Manager, HR
```

#### POST /api/shift-templates
```
Request:
  {
    "area_id": "uuid",
    "code": "T",
    "name": "Tarde",
    "start_time": "14:00",
    "end_time": "22:00",
    "description": "Turno de tarde"
  }

Response (201 Created):
  {
    "id": "uuid",
    "code": "T",
    "name": "Tarde",
    ...
  }

Errors:
  400 Bad Request - Invalid data
  409 Conflict - Code already exists for this area
  403 Forbidden - User not authorized

Permissions: Manager, HR
```

#### PUT /api/shift-templates/{id}
```
Request: (partial update)
  {
    "name": "Tarde (Modificado)",
    "start_time": "15:00"
  }

Response (200 OK): Updated ShiftTemplate

Permissions: Manager, HR
```

#### DELETE /api/shift-templates/{id}
```
Response (204 No Content)

Permissions: Manager, HR
```

---

### 5.3 Shift Assignment Endpoints

#### GET /api/shifts/me
```
Query Params:
  from_date: Date (required, ISO format: 2026-04-16)
  to_date: Date (required)
  status: Enum (scheduled, completed, absent, swapped) (optional)

Response (200 OK):
  {
    "data": [
      {
        "id": "uuid",
        "assignment_date": "2026-04-20",
        "shift_template": {
          "code": "T",
          "name": "Tarde",
          "start_time": "14:00",
          "end_time": "22:00"
        },
        "status": "scheduled",
        "timesheet": {
          "ordinary_hours": 8.0,
          "night_hours": 0.0,
          "extras": 0.0,
          "total_gross": 150000
        }
      }
    ],
    "total": 5
  }

Permissions: Worker (own shifts only)
```

#### GET /api/shifts
```
Query Params:
  area_id: UUID (required for manager, optional for HR)
  worker_id: UUID (optional)
  from_date: Date (required)
  to_date: Date (required)
  status: Enum (optional)
  limit: Int (default: 100)
  offset: Int (default: 0)

Response (200 OK): List of ShiftAssignments (paginated)

Permissions: Manager (own area), HR (any area in company)
```

#### POST /api/shifts
```
Request:
  {
    "worker_id": "uuid",
    "shift_template_id": "uuid",
    "assignment_date": "2026-04-20"
  }

Response (201 Created): ShiftAssignment

Validations:
  - Check: worker exists and is in same company/area
  - Check: shift template exists in same area
  - Check: no duplicate shift same day (UNIQUE constraint)
  - Warn: if would exceed weekly hour limit
  - Warn: if assigned within 11 hours of previous shift
  - Side effect: Auto-calculate TimesheetDay

Errors:
  400 Bad Request - Validation failed
  409 Conflict - Duplicate shift same day
  403 Forbidden - Not authorized

Permissions: Manager, HR
```

#### PUT /api/shifts/{id}
```
Request: (partial update)
  {
    "assignment_date": "2026-04-21",
    "shift_template_id": "uuid"
  }

Response (200 OK): Updated ShiftAssignment

Side effect: Recalculate TimesheetDay

Constraints:
  - Cannot modify shifts in past (unless HR override)

Permissions: Manager, HR
```

#### DELETE /api/shifts/{id}
```
Response (204 No Content)

Side effect: Delete associated TimesheetDay

Permissions: Manager, HR
```

---

### 5.4 Payroll Endpoints

#### GET /api/timesheets/me
```
Query Params:
  from_date: Date (required)
  to_date: Date (required)
  group_by: Enum (day, week, month) (default: day)

Response (200 OK):
  {
    "data": [
      {
        "date": "2026-04-16",
        "ordinary_hours": 8.0,
        "night_hours": 2.0,
        "sunday_day_hours": 0.0,
        "sunday_night_hours": 0.0,
        "overtime_day": 0.0,
        "overtime_night": 0.0,
        "overtime_sunday_day": 0.0,
        "overtime_sunday_night": 0.0,
        "total_regular_amount": 120000,
        "total_surcharge_amount": 51000,
        "total_gross_amount": 171000
      }
    ],
    "period_total": {
      "ordinary_hours": 160.0,
      "total_gross_amount": 3420000
    }
  }

Permissions: Worker (own payroll)
```

#### GET /api/timesheets/{worker_id}
```
Query Params: (same as /timesheets/me)

Response (200 OK): Worker's payroll data

Permissions: Manager (own area workers), HR (any worker)
```

#### GET /api/timesheets
```
Query Params:
  area_id: UUID (required for manager)
  from_date: Date (required)
  to_date: Date (required)
  limit: Int (default: 100)
  offset: Int (default: 0)

Response (200 OK): List of workers' timesheet aggregates

Permissions: Manager (own area), HR (any area)
```

---

### 5.5 Export Endpoints

#### POST /api/exports/payroll
```
Request:
  {
    "from_date": "2026-04-01",
    "to_date": "2026-04-15",
    "format": "csv", // or "xml"
    "area_id": "uuid" (optional, filter)
  }

Response (200 OK): File download (streaming)
  Content-Type: text/csv (or application/xml)
  Content-Disposition: attachment; filename="payroll_2026-04-01_to_2026-04-15.csv"

CSV Format:
  cedula,nombre,ordinarias,nocturnas,extras_dia,extras_noche,recargo_domingo,recargo_noche,total_valor
  1234567890,Juan Pérez,160.0,20.0,0.0,0.0,8.0,0.0,2400000
  ...

XML Format:
  <?xml version="1.0" encoding="UTF-8"?>
  <payroll>
    <period>
      <from_date>2026-04-01</from_date>
      <to_date>2026-04-15</to_date>
    </period>
    <workers>
      <worker>
        <cedula>1234567890</cedula>
        <nombre>Juan Pérez</nombre>
        <ordinarias>160.0</ordinarias>
        ...
      </worker>
    </workers>
  </payroll>

Performance:
  - Streaming response for large exports
  - Background task for exports > 10MB
  - Email notification when ready

Permissions: HR only
```

---

### 5.6 Shift Swap Endpoints

#### POST /api/shift-swaps
```
Request:
  {
    "target_worker_id": "uuid",
    "shift_assignment_id": "uuid"  // My shift to offer
  }

Response (201 Created):
  {
    "id": "uuid",
    "requester_worker_id": "uuid",
    "target_worker_id": "uuid",
    "shift_assignment_id": "uuid",
    "status": "pending",
    "created_at": "2026-04-16T10:00:00Z"
  }

Validations:
  - Both workers in same company/area
  - Can't swap with self
  - Shift not in past
  - Not already pending for same pair

Side effect:
  - Send notification to manager

Permissions: Worker
```

#### GET /api/shift-swaps
```
Query Params:
  status: Enum (pending, approved, rejected) (optional)
  as_requester: Boolean (default: false - show swaps I initiated)
  as_target: Boolean (default: true - show swaps requested from me)
  limit: Int (default: 50)
  offset: Int (default: 0)

Response (200 OK): List of SwapRequests

Permissions: Worker (own swaps), Manager (all swaps in area)
```

#### PUT /api/shift-swaps/{id}/approve
```
Request: (empty body)

Response (200 OK):
  {
    "id": "uuid",
    "status": "approved",
    "manager_approved_by": "uuid",
    "resolved_at": "2026-04-16T10:30:00Z"
  }

Side effects:
  - Swap the two ShiftAssignments
  - Recalculate both workers' TimesheetDay
  - Send notifications to both workers
  - Validate constraints still met after swap

Constraints:
  - Must validate neither worker exceeds limits after swap
  - If violation detected, return 400 with reason

Permissions: Manager
```

#### PUT /api/shift-swaps/{id}/reject
```
Request:
  {
    "rejection_reason": "Worker A doesn't have time constraints met"
  }

Response (200 OK):
  {
    "id": "uuid",
    "status": "rejected",
    "rejection_reason": "...",
    "resolved_at": "2026-04-16T10:30:00Z"
  }

Side effects:
  - Send notification to requester

Permissions: Manager
```

---

### 5.7 Holiday Calendar Endpoints

#### GET /api/holidays
```
Query Params:
  year: Int (required, e.g., 2026)
  include_company_holidays: Boolean (default: true)

Response (200 OK):
  {
    "data": [
      {
        "id": "uuid",
        "holiday_date": "2026-01-01",
        "holiday_name": "Año Nuevo",
        "is_public_holiday": true
      },
      {
        "id": "uuid",
        "holiday_date": "2026-06-01",
        "holiday_name": "Corpus Christi",
        "is_public_holiday": true
      }
    ]
  }

Permissions: All roles
```

#### POST /api/holidays
```
Request:
  {
    "holiday_date": "2026-12-25",
    "holiday_name": "Navidad",
    "is_public_holiday": true
  }

Response (201 Created): Holiday entry

Permissions: HR only
```

---

## 6. Workflow Specifications

### 6.1 Shift Assignment Workflow

```
Manager → Create Shift Template (once per area)
            ↓
Manager → Assign Shift Template to Worker + Date
            ↓
System → Validate:
         - Worker exists
         - No duplicate same day
         - Check weekly limits (warn if exceed)
         - Check 11-hour rest period (warn)
            ↓
System → Auto-Calculate TimesheetDay:
         - Classify hours (ordinarias, nocturnas, etc.)
         - Apply surcharges
         - Calculate gross amount
            ↓
Worker → View shift in calendar
Manager → View shift in team schedule
HR → See payroll line item
```

### 6.2 Shift Swap Workflow

```
Worker A → Request Swap
             (My Shift A ↔ Worker B's Shift B)
             ↓
System → Validate:
         - Both workers exist + same area
         - Shifts not in past
         - No pending swap already
             ↓
Manager → Receive Notification
           Review Swap Request
             ↓
Manager → Approve/Reject
             ↓
           IF APPROVED:
             System → Swap assignments:
                      ShiftAssignment A → Worker B
                      ShiftAssignment B → Worker A
             System → Validate:
                      - Neither worker exceeds limits
                      - Both TimesheetDays recalculated
             ↓
           Workers → Receive notification
                     Confirm new shifts
           
           IF REJECTED:
             Worker A → Receive rejection reason
```

### 6.3 Payroll Export Workflow

```
HR → Request Export
     (Date range, format: CSV/XML)
     ↓
System → Query all workers in company/area
         For each worker:
         - Fetch TimesheetDay for date range
         - Sum ordinarias, nocturnas, extras, recargos
         ↓
System → Generate file (CSV or XML)
         ↓
IF file < 10MB:
         Streaming download response (immediate)
ELSE:
         Background task:
         - Generate file
         - Store in temp storage
         - Email download link to HR
         ↓
HR → Download payroll file
     Import into nómina software (Siigo, Novasoft, etc.)
```

---

## 7. UI/UX Requirements

### 7.1 Common UI Elements

**Navigation:**
- Top bar with: Cronos logo, user profile menu, logout
- Sidebar menu with: My Shifts, Payroll, Swaps, etc. (role-based)

**Authentication:**
- Login page (email + password)
- JWT token stored in localStorage
- Auto-logout on token expiration

**Multi-Tenancy:**
- Tenant context (Company/SubOrg/Area) visible in header
- Allow tenant switching if user has access to multiple

### 7.2 Worker UI Screens

**Dashboard:**
- Current week shifts (calendar view)
- Payroll summary (this week, this month)
- Pending swap requests (notifications)

**My Shifts:**
- Calendar grid (Mon-Sun, multiple weeks)
- Shift details on click: date, time, hours, gross amount
- "Request Swap" button per shift
- Filter by status (scheduled, completed, absent, swapped)

**My Payroll:**
- Date range selector (week, month, custom)
- Breakdown table:
  - Date | Ordinarias | Nocturnas | Extras | Recargos | Total
- Export as PDF (optional)

**Swap Requests:**
- List of my pending swaps (I initiated)
- Status: pending, approved, rejected
- List of swaps requested from me (pending)
- Accept/decline buttons (for swaps from others - future feature)

### 7.3 Manager UI Screens

**Dashboard:**
- Team shifts (calendar, next 2 weeks)
- Team payroll summary (totals, overtime alerts)
- Pending swaps (approval queue)

**Manage Shifts:**
- Area + team selector
- Shift calendar (drag-drop or modal form)
- Create shift: Date, Worker, Shift Template dropdown
- Edit/delete shift (modal or inline)
- Warnings: If would exceed limits, show banner with details

**Manage Shift Swaps:**
- Queue of pending swaps (requester → target → date)
- Details: both workers, shift details, reason (optional)
- Approve button: If valid, swap; if invalid, show error
- Reject button: Modal for rejection reason

**Team Payroll:**
- Table: Worker Name, Ordinarias, Nocturnas, Extras, Recargos, Total
- Drill down to worker detail (full period breakdown)
- Overtime alerts (badge if exceed 12h/week)

### 7.4 HR UI Screens

**Dashboard:**
- Company-wide payroll summary
- Recent exports
- System health (shifts scheduled, workers, etc.)

**Manage Organization:**
- Hierarchy tree: Company → SubOrgs → Areas
- Create/edit/delete nodes
- Assign managers to areas

**Manage Users:**
- Worker list (table)
- Create worker: Name, Cedula, Email, Phone, Role, Contract Type, Hourly Rate
- Edit worker details
- Change role/status

**Manage Holidays:**
- Calendar view (full year)
- Mark holidays (public vs company-specific)
- Pre-populated with Colombian holidays
- Add/edit/delete custom holidays

**Export Payroll:**
- Date range selector
- Format selector (CSV or XML)
- Area filter (optional)
- Download button
- Export history (recent exports)

**Payroll Dashboard:**
- Summary: Total workers, total ordinarias, total recargos, total payroll cost
- Breakdowns by area/sub-org
- Overtime violations (workers exceeding limits)
- Dominical work summary (who worked 3+ Sundays)

---

## 8. Non-Functional Requirements

### 8.1 Performance

| Metric | Target | Justification |
|--------|--------|---|
| API Response Time (p95) | < 500ms | Natural for web app |
| Page Load Time (first paint) | < 2s | MVP standard |
| Shift Calendar Render | < 1s | 100 shifts |
| Export Generation | < 10s | 1000 workers |
| Database Query Latency | < 100ms | Neon SSD |

### 8.2 Availability & Reliability

- **Uptime:** 99% (MVP acceptable)
- **RTO:** 4 hours (recovery time if failure)
- **RPO:** 1 hour (data loss acceptable: hourly backups via Neon)
- **Graceful Degradation:** If export fails, user can retry

### 8.3 Security

- **Authentication:** JWT with 1-hour expiration + refresh tokens
- **Authorization:** Role-based (worker, manager, hr_admin) + tenant scoping
- **Data Encryption:** HTTPS only, AES-256 for sensitive fields (password)
- **Password:** bcrypt hashing, min 12 characters
- **CORS:** Configured explicitly for Vercel frontend domain
- **Rate Limiting:** 100 requests/minute per IP (to prevent brute force)
- **Audit Trail:** Log all payroll exports (who, when, what)

### 8.4 Scalability

- **MVP (Phase 1-3):** Support up to 1000 workers, 500 shifts/day
- **Phase 4:** Support up to 10,000 workers via connection pooling + caching
- **Database Scaling:** Neon handles auto-scaling; if needed, add read replicas post-MVP
- **API Scaling:** Render/Vercel handle horizontal scaling

### 8.5 Compliance

- **Data Residency:** Neon (US-East) acceptable for LatAm (no special requirements)
- **Audit Trail:** All payroll exports logged (who, when, date range, format)
- **Retention:** Keep audit logs for 7 years (Colombian tax requirement)
- **Backup:** Neon auto-backups (7-day retention)

---

## 9. Testing Requirements

### 9.1 Unit Testing (Backend)

**Payroll Engine Tests (Highest Priority):**
- Test every surcharge type (night, sunday, combinations)
- Test midnight rule (shift crossing 00:00)
- Test overtime limits (max 2h/day, 12h/week)
- Test workweek reductions (46h → 44h → 42h)
- Test habitual Sunday detection
- Test holiday surcharges
- Test edge cases:
  - Shift exactly at day/night boundary (6am, 9pm)
  - Shift on holiday midnight boundary
  - Leap year handling
  - Year-end hour carryover (if any)

**Target:** 100+ test cases, 100% coverage of payroll module

**Example Test:**
```python
def test_midnight_rule_saturday_to_sunday():
    """Shift crossing midnight should classify hours correctly"""
    shift = Shift(
        start=datetime(2026, 4, 18, 20, 0),  # Sat 8pm
        end=datetime(2026, 4, 19, 4, 0)      # Sun 4am
    )
    result = payroll_engine.classify_hours(shift)
    
    assert result['ordinary_hours'] == 1.0  # Sat 8-9pm
    assert result['night_hours'] == 3.0     # Sat 9pm-12am
    assert result['sunday_night_hours'] == 4.0  # Sun 12am-4am
```

**Other Backend Tests:**
- Multi-tenancy isolation: queries respect tenant_id
- Auth: JWT validation, token expiration
- Validation: Worker exists, shift not duplicate, limits checked
- Database: Foreign key constraints, cascading deletes

### 9.2 Integration Testing (Backend)

- API endpoint tests (CRUD operations)
- Payroll calculation end-to-end (shift → timesheet → export)
- Shift swap workflow (validate → approve → swap)
- Export generation (query → format → download)
- Multi-tenant data isolation (user in Company A can't see Company B data)

### 9.3 Frontend Testing

- Component rendering tests (React Testing Library)
- User interactions (click, form submit)
- API integration (mock backend responses)
- Responsive design (mobile, tablet, desktop)

### 9.4 End-to-End Testing (E2E)

- Worker: Login → View shifts → Request swap → Logout
- Manager: Login → Create template → Assign shift → Approve swap → Logout
- HR: Login → Export payroll → Download file → Verify format

### 9.5 Manual Testing

- Payment calculation accuracy (spot-check timesheets)
- Colombian law compliance (verify surcharges, limits)
- Export file import into real nómina software (Siigo, Novasoft)
- Multi-user concurrent shifts (race conditions)

---

## 10. Constraints & Assumptions

### 10.1 Constraints

- **MVP Timeline:** 3-4 months (3 phases)
- **Team Size:** 1 backend + 1 frontend + 0.5 QA
- **Budget:** $0-50/month (Vercel free + Render free + Neon free)
- **Users:** MVP target ≤ 1000 workers
- **Data Retention:** Shifts/payroll data kept for 7 years min (Colombian tax)

### 10.2 Assumptions

- ✅ Workers accurately report hours (honor system, no biometric)
- ✅ Managers operate in good faith (no malicious shift assignment)
- ✅ HR has domain expertise (understands payroll, Colombian law)
- ✅ Internet connectivity available (no offline mode)
- ✅ Browsers support ES2020+ (no IE11 support)
- ✅ Pilot company has <500 workers (for load testing MVP)
- ✅ Colombian holidays can be pre-loaded (don't change year-to-year)

### 10.3 Dependencies

- **External:** Neon for database, Render for backend, Vercel for frontend
- **Libraries:** FastAPI, SQLAlchemy, React, Zustand, Tailwind CSS, pytest
- **Third-party Integrations:** None required for MVP (but future: Stripe for subscriptions)

### 10.4 Open Questions / Future Decisions

- **Q1:** Should MVP support multiple hourly rates per worker (e.g., higher rate for night shifts)?
  - **A (MVP):** No, single hourly rate only. Surcharges are %, not separate rates.
  
- **Q2:** How to handle workers transferring between areas mid-period?
  - **A (MVP):** Not supported. Worker bound to one area per period. Change area in next period.
  
- **Q3:** Should system warn managers about workers near limit, or auto-block?
  - **A (MVP):** Warn only (advisory). Allow managers to override with audit trail. Auto-block post-MVP if strict enforcement needed.

- **Q4:** What if Colombian law changes mid-month (e.g., day hours change from 9pm to 7pm)?
  - **A (MVP):** Require HR to manually recalculate and export. Phase 4: auto-recalculate with effective date.

---

## Summary

**Cronos MVP Specifications deliver:**
- ✅ Complete functional requirements (worker, manager, HR workflows)
- ✅ Colombian labor law compliance (surcharges, overtime, holidays, midnight rule)
- ✅ Data model (7 core entities, relationships, constraints)
- ✅ API specifications (27 endpoints, request/response formats, validations)
- ✅ Workflow specifications (shift assignment, swap, payroll export)
- ✅ UI/UX requirements (4 screens per role, responsive design)
- ✅ Non-functional requirements (performance, security, scalability)
- ✅ Testing strategy (100+ payroll test cases, E2E coverage)
- ✅ Constraints & assumptions documented

**Ready to proceed to Design Phase ✅**

---

**Created:** 2026-04-16  
**Phase:** SDD Specification  
**Status:** DRAFT - Ready for Review
