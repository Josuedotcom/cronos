# Cronos - Domain Model & Data Schema

## Entity Relationship Diagram (Conceptual)

```
┌─────────────────────────────────────────────────────────────┐
│                        COMPANY (Tenant)                      │
│ - id, name, timezone, default_surcharge_config              │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬────────────────┐
        │              │              │                │
        ▼              ▼              ▼                ▼
   WORKER        HOLIDAY_CALENDAR  SHIFT_TEMPLATE  SURCHARGE_RULE
   - id          - date             - id            - id
   - company_id  - name             - name          - company_id
   - name        - is_public_holiday - start_hour   - shift_type
   - contract_type                  - end_hour      - surcharge_type
   - hourly_rate                     - company_id    - percentage
   - status                                         - effective_from
                                                   - effective_to
        │
        ▼
   SHIFT_ASSIGNMENT (M2M between Worker & ShiftTemplate + date)
   - id
   - worker_id
   - shift_template_id
   - assignment_date
   - actual_start (nullable)
   - actual_end (nullable)
   - status (scheduled, completed, absent, swapped)
   - is_overtime_shift
   - created_by_manager_id
        │
        │ (derives) ▼
        │    TIMESHEET_DAY (Payroll output per worker per day)
        │    - id
        │    - worker_id
        │    - date
        │    - ordinary_hours
        │    - night_hours
        │    - sunday_day_hours
        │    - sunday_night_hours
        │    - overtime_day
        │    - overtime_night
        │    - overtime_sunday_day
        │    - overtime_sunday_night
        │    - total_gross_amount (calculated)
        │
        ▼
   SHIFT_SWAP_REQUEST (Workflow)
   - id
   - requester_worker_id
   - target_worker_id
   - shift_assignment_id (the shift being offered)
   - status (pending, approved, rejected)
   - manager_approved_by
   - created_at
   - resolved_at

```

## SQL Schema (PostgreSQL)

### companies
```sql
CREATE TABLE companies (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  timezone VARCHAR(50) DEFAULT 'America/Bogota',
  country_code VARCHAR(2) DEFAULT 'CO',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### workers
```sql
CREATE TABLE workers (
  id BIGSERIAL PRIMARY KEY,
  company_id BIGINT NOT NULL REFERENCES companies(id),
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE,
  phone VARCHAR(20),
  contract_type ENUM('standard', 'shift_36h') DEFAULT 'standard',
  hourly_rate DECIMAL(10, 2) NOT NULL,
  hire_date DATE NOT NULL,
  status ENUM('active', 'inactive', 'on_leave') DEFAULT 'active',
  role ENUM('worker', 'manager', 'hr_admin', 'system_admin') DEFAULT 'worker',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  CONSTRAINT fk_company FOREIGN KEY(company_id) REFERENCES companies(id)
);
```

### shift_templates
```sql
CREATE TABLE shift_templates (
  id BIGSERIAL PRIMARY KEY,
  company_id BIGINT NOT NULL REFERENCES companies(id),
  name VARCHAR(100) NOT NULL,
  start_hour TIME NOT NULL,
  end_hour TIME NOT NULL,
  description TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### shift_assignments
```sql
CREATE TABLE shift_assignments (
  id BIGSERIAL PRIMARY KEY,
  company_id BIGINT NOT NULL REFERENCES companies(id),
  worker_id BIGINT NOT NULL REFERENCES workers(id),
  shift_template_id BIGINT NOT NULL REFERENCES shift_templates(id),
  assignment_date DATE NOT NULL,
  actual_start TIMESTAMP,
  actual_end TIMESTAMP,
  status ENUM('scheduled', 'completed', 'absent', 'swapped') DEFAULT 'scheduled',
  is_overtime_shift BOOLEAN DEFAULT false,
  created_by_manager_id BIGINT REFERENCES workers(id),
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(worker_id, assignment_date),  -- One shift per worker per day
  CONSTRAINT fk_company FOREIGN KEY(company_id) REFERENCES companies(id)
);
```

### holiday_calendar
```sql
CREATE TABLE holiday_calendar (
  id BIGSERIAL PRIMARY KEY,
  company_id BIGINT NOT NULL REFERENCES companies(id),
  holiday_date DATE NOT NULL,
  holiday_name VARCHAR(100) NOT NULL,
  is_public_holiday BOOLEAN DEFAULT true,  -- If false, it's a company-specific holiday
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(company_id, holiday_date),
  CONSTRAINT fk_company FOREIGN KEY(company_id) REFERENCES companies(id)
);
```

### surcharge_rules
```sql
CREATE TABLE surcharge_rules (
  id BIGSERIAL PRIMARY KEY,
  company_id BIGINT NOT NULL REFERENCES companies(id),
  surcharge_type ENUM('night', 'sunday', 'sunday_night', 'overtime_day', 'overtime_night') NOT NULL,
  percentage DECIMAL(5, 2) NOT NULL,
  effective_from DATE NOT NULL,
  effective_to DATE,  -- NULL = ongoing
  description TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  CONSTRAINT fk_company FOREIGN KEY(company_id) REFERENCES companies(id)
);
```

### timesheet_days (Payroll view - calculated)
```sql
CREATE TABLE timesheet_days (
  id BIGSERIAL PRIMARY KEY,
  company_id BIGINT NOT NULL REFERENCES companies(id),
  worker_id BIGINT NOT NULL REFERENCES workers(id),
  timesheet_date DATE NOT NULL,
  ordinary_hours DECIMAL(5, 2) DEFAULT 0,
  night_hours DECIMAL(5, 2) DEFAULT 0,
  sunday_day_hours DECIMAL(5, 2) DEFAULT 0,
  sunday_night_hours DECIMAL(5, 2) DEFAULT 0,
  overtime_day DECIMAL(5, 2) DEFAULT 0,
  overtime_night DECIMAL(5, 2) DEFAULT 0,
  overtime_sunday_day DECIMAL(5, 2) DEFAULT 0,
  overtime_sunday_night DECIMAL(5, 2) DEFAULT 0,
  total_regular_amount DECIMAL(12, 2),
  total_surcharge_amount DECIMAL(12, 2),
  total_gross_amount DECIMAL(12, 2),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(worker_id, timesheet_date),
  CONSTRAINT fk_company FOREIGN KEY(company_id) REFERENCES companies(id)
);
```

### shift_swap_requests
```sql
CREATE TABLE shift_swap_requests (
  id BIGSERIAL PRIMARY KEY,
  company_id BIGINT NOT NULL REFERENCES companies(id),
  requester_worker_id BIGINT NOT NULL REFERENCES workers(id),
  target_worker_id BIGINT NOT NULL REFERENCES workers(id),
  shift_assignment_id BIGINT NOT NULL REFERENCES shift_assignments(id),
  status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
  manager_approved_by BIGINT REFERENCES workers(id),
  rejection_reason TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  resolved_at TIMESTAMP,
  updated_at TIMESTAMP DEFAULT NOW(),
  CONSTRAINT fk_company FOREIGN KEY(company_id) REFERENCES companies(id),
  CONSTRAINT check_different_workers CHECK (requester_worker_id != target_worker_id)
);
```

## Key Calculation Rules

### Hour Classification Algorithm

For each shift crossing midnight (the "Midnight Rule"):

```
Input: shift_start (local time), shift_end (local time), shift_date
Day boundaries: 6:00 AM = day_start, 9:00 PM = night_start, 12:00 AM (next day) = end

For each hour in [shift_start, shift_end]:
  if hour is on a Sunday or public holiday:
    if hour >= night_start (9 PM) OR hour < day_start (6 AM):
      → Sunday Night Hours (110% surcharge = 35% + 75%)
    else:
      → Sunday Day Hours (75% surcharge)
  elif hour >= night_start OR hour < day_start:
    → Night Hours (35% surcharge)
  else:
    → Ordinary Hours (no surcharge)

If total_daily_hours > contract_limit (8-9 hrs typically):
  excess_hours = total_daily_hours - contract_limit
  Apply overtime rules (25%-150% depending on time of day + day type)
```

### Surcharge Calculation

```python
gross_amount = sum(
  ordinary_hours * hourly_rate +
  night_hours * hourly_rate * (1 + 0.35) +
  sunday_day_hours * hourly_rate * (1 + 0.75) +
  sunday_night_hours * hourly_rate * (1 + 1.10) +
  overtime_day * hourly_rate * (1 + 0.25) +
  overtime_night * hourly_rate * (1 + 0.75) +
  overtime_sunday_day * hourly_rate * (1 + 1.00) +
  overtime_sunday_night * hourly_rate * (1 + 1.50)
)
```

## API Endpoints (High-Level)

### Authentication
- `POST /auth/login` - Worker/Manager login
- `POST /auth/logout`
- `POST /auth/refresh-token`

### Workers
- `GET /api/workers/me` - Current worker profile
- `GET /api/workers/{id}` - Worker details (manager/HR only)
- `GET /api/workers` - List workers (manager/HR only, paginated)
- `PUT /api/workers/{id}` - Update worker (HR only)

### Shift Templates
- `GET /api/shift-templates` - List active templates
- `POST /api/shift-templates` - Create template (HR/manager)
- `PUT /api/shift-templates/{id}` - Update template
- `DELETE /api/shift-templates/{id}` - Deactivate template

### Shift Assignments
- `GET /api/shifts/me` - My shift schedule (worker view, optionally filtered by date range)
- `GET /api/shifts?worker_id=X&from=DATE&to=DATE` - Manager view of a worker's shifts
- `GET /api/shifts?company_id=X&from=DATE&to=DATE` - HR view (all workers, all shifts)
- `POST /api/shifts` - Create shift assignment (manager/HR)
- `PUT /api/shifts/{id}` - Update shift assignment
- `DELETE /api/shifts/{id}` - Cancel shift assignment

### Shift Swaps
- `POST /api/shift-swaps` - Initiate swap request (worker)
- `GET /api/shift-swaps?status=pending` - List pending requests (manager)
- `PUT /api/shift-swaps/{id}/approve` - Approve swap (manager)
- `PUT /api/shift-swaps/{id}/reject` - Reject swap (manager)

### Timesheet & Payroll
- `GET /api/timesheets/me?from=DATE&to=DATE` - My hours summary (worker)
- `GET /api/timesheets/{worker_id}?from=DATE&to=DATE` - Worker's hours summary (manager/HR)
- `GET /api/timesheets?from=DATE&to=DATE` - All workers hours (HR, paginated)
- `POST /api/exports/payroll` - Generate payroll export (HR)

### Holiday Calendar
- `GET /api/holidays?year=2024` - List holidays
- `POST /api/holidays` - Add/update holiday (HR)

---

**Status:** Draft - For SDD Proposal Phase  
**Last Updated:** 2026-04-16
