# Cronos MVP - Design Document

**Project:** Cronos - Colombian Labor Law-Compliant Shift Management System  
**Change ID:** cronos-mvp  
**Phase:** Design  
**Status:** DRAFT  
**Created:** 2026-04-16  
**Author:** SDD Design Phase  

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Database Design](#2-database-design)
3. [Payroll Engine Design](#3-payroll-engine-design)
4. [API Implementation Strategy](#4-api-implementation-strategy)
5. [Frontend Architecture](#5-frontend-architecture)
6. [Authentication & Security](#6-authentication--security)
7. [Data Flow Diagrams](#7-data-flow-diagrams)
8. [Error Handling Strategy](#8-error-handling-strategy)
9. [Caching & Performance](#9-caching--performance)
10. [Deployment & CI/CD](#10-deployment--cicd)

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                        │
│  Components: Shift Calendar, Payroll Dashboard, Forms           │
│  State: Zustand + Context API                                   │
│  Build: Vite                                                    │
│  Deploy: Vercel (free tier)                                     │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS/JSON (CORS configured)
┌────────────────────────▼────────────────────────────────────────┐
│                     BACKEND (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ API Layer (FastAPI Routers)                             │  │
│  │ ├─ /auth → Authentication endpoints                     │  │
│  │ ├─ /shifts → Shift management                           │  │
│  │ ├─ /timesheets → Payroll calculation & views            │  │
│  │ ├─ /exports → CSV/XML generation                        │  │
│  │ └─ /swaps, /holidays → Support endpoints                │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Business Logic Layer (Services)                         │  │
│  │ ├─ PayrollService → Payroll calculations                │  │
│  │ ├─ ShiftService → Shift validation & assignment         │  │
│  │ ├─ SwapService → Swap workflow & constraints            │  │
│  │ ├─ ExportService → CSV/XML generation                   │  │
│  │ └─ AuthService → JWT & tenant context                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Data Access Layer (SQLAlchemy ORM)                      │  │
│  │ ├─ Multi-tenant query injection (company_id)            │  │
│  │ ├─ Lazy loading relationships                           │  │
│  │ └─ Connection pooling via SQLAlchemy Pool               │  │
│  └──────────────────────────────────────────────────────────┘  │
│  Deploy: Render.com (free tier with sleep, $7/mo no-sleep)    │
└────────────────────────┬────────────────────────────────────────┘
                         │ PostgreSQL wire protocol
┌────────────────────────▼────────────────────────────────────────┐
│               DATABASE (PostgreSQL via Neon)                    │
│  ├─ Company hierarchy (tenant isolation)                        │
│  ├─ Workers, Shifts, Payroll tables                             │
│  ├─ Audit trail (payroll exports, changes)                      │
│  └─ Connection pooling (PgBouncer via Neon)                     │
│  Deploy: Neon serverless (free tier, $19/mo Launch tier)        │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Technology Stack Decisions

| Layer | Technology | Justification |
|-------|-----------|---|
| **Frontend** | React 18 + TypeScript | Industry standard, strong ecosystem, team familiar |
| **Frontend Build** | Vite | Fast bundler, ES modules, <1s dev reload |
| **Frontend State** | Zustand | Lightweight, minimal boilerplate vs Redux |
| **Frontend Styling** | Tailwind CSS + shadcn/ui | Rapid development, accessible components |
| **Backend** | FastAPI | Python ecosystem (Pandas, payroll logic), async support |
| **Backend ORM** | SQLAlchemy 2.0 | Async support, multi-tenant queries, mature |
| **Database** | PostgreSQL 14+ via Neon | ACID, JSON support, connection pooling included |
| **Auth** | JWT (HS256) | Stateless, scalable, simple for MVP |
| **Testing** | pytest (backend), Vitest (frontend) | Native async support, fast execution |
| **API Documentation** | OpenAPI/Swagger (FastAPI built-in) | Auto-generated from code |
| **Deployment** | Vercel (frontend) + Render (backend) + Neon (DB) | Cost-effective, auto-scaling, managed services |

---

## 2. Database Design

### 2.1 Entity Relationship Diagram (ERD)

```
┌─────────────────────────────────────────────────────────────┐
│                         COMPANY                             │
│ (PK) id: UUID                                               │
│      name: VARCHAR(255)                                     │
│      subdomain: VARCHAR(100) UNIQUE                         │
│      timezone: VARCHAR(50) DEFAULT 'America/Bogota'         │
├─ INDEXES: subdomain (for routing), name                     │
└─────────────────────────────────────────────────────────────┘
           │ 1:M
           │
┌──────────▼──────────────────────────────────────────────────┐
│                    SUBORGANIZATION                          │
│ (PK) id: UUID                                               │
│ (FK) company_id: UUID                                       │
│      name: VARCHAR(255)                                     │
│      parent_suborganization_id: UUID (nullable, for nesting)│
├─ INDEXES: company_id, parent_suborganization_id             │
└──────────────────────────────────────────────────────────────┘
           │ 1:M
           │
┌──────────▼──────────────────────────────────────────────────┐
│                        AREA                                 │
│ (PK) id: UUID                                               │
│ (FK) company_id: UUID                                       │
│ (FK) suborganization_id: UUID                               │
│ (FK) manager_id: UUID (nullable, → WORKER)                  │
│      name: VARCHAR(255)                                     │
├─ INDEXES: company_id, suborganization_id, manager_id        │
└──────────────────────────────────────────────────────────────┘
           │ 1:M
           │
     ┌─────┴──────┬──────────────┐
     │            │              │
     ▼            ▼              ▼
┌────────────┐ ┌──────────┐ ┌──────────────┐
│  WORKER    │ │ SHIFT    │ │ SHIFT        │
│            │ │TEMPLATE  │ │ ASSIGNMENT   │
│(PK) id     │ │          │ │              │
│(FK) area_id│ │(PK) id   │ │(PK) id       │
│ cedula     │ │(FK) area_id│ │(FK) worker_id
│ name       │ │ code     │ │(FK) template_id
│ email      │ │ name     │ │ date         │
│ hourly_rate│ │start_time│ │ status       │
│ role       │ │end_time  │ │              │
└────────────┘ └──────────┘ └──────┬───────┘
                                    │ 1:1
                                    │
                              ┌─────▼───────┐
                              │ TIMESHEET   │
                              │ DAY         │
                              │             │
                              │ ordinarias  │
                              │ nocturnas   │
                              │ extras      │
                              │ recargos    │
                              │ total_gross │
                              └─────────────┘

ADDITIONAL TABLES:
├─ SHIFT_SWAP_REQUEST (workflow)
│  (FK) requester_id, target_id, shift_assignment_id
│  status, manager_approved_by, rejection_reason
│
├─ HOLIDAY_CALENDAR
│  (FK) company_id
│  holiday_date, holiday_name, is_public_holiday
│
└─ SURCHARGE_RULE (future: custom % per company)
   (FK) company_id
   surcharge_type, percentage, effective_from, effective_to
```

### 2.2 SQL Schema (PostgreSQL)

```sql
-- COMPANIES (Root tenant)
CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  subdomain VARCHAR(100) UNIQUE NOT NULL,
  timezone VARCHAR(50) DEFAULT 'America/Bogota',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_companies_subdomain ON companies(subdomain);

-- SUBORGANIZATIONS (Department/division level)
CREATE TABLE suborganizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  parent_suborganization_id UUID REFERENCES suborganizations(id) ON DELETE SET NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_suborganizations_company ON suborganizations(company_id);
CREATE INDEX idx_suborganizations_parent ON suborganizations(parent_suborganization_id);

-- AREAS (Operational teams - where shifts are managed)
CREATE TABLE areas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  suborganization_id UUID NOT NULL REFERENCES suborganizations(id) ON DELETE CASCADE,
  manager_id UUID REFERENCES workers(id) ON DELETE SET NULL,  -- Defer FK, will add later
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_areas_company ON areas(company_id);
CREATE INDEX idx_areas_suborganization ON areas(suborganization_id);

-- WORKERS (Employees)
CREATE TABLE workers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  suborganization_id UUID NOT NULL REFERENCES suborganizations(id) ON DELETE CASCADE,
  area_id UUID NOT NULL REFERENCES areas(id) ON DELETE CASCADE,
  cedula VARCHAR(20) NOT NULL,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  email VARCHAR(100),
  phone VARCHAR(20),
  contract_type VARCHAR(20) DEFAULT 'standard' CHECK (contract_type IN ('standard', 'shift_36h')),
  hourly_rate DECIMAL(10, 2) NOT NULL,
  hire_date DATE NOT NULL,
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'on_leave')),
  role VARCHAR(20) DEFAULT 'worker' CHECK (role IN ('worker', 'manager', 'hr_admin', 'system_admin')),
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(company_id, cedula)
);
CREATE INDEX idx_workers_company ON workers(company_id);
CREATE INDEX idx_workers_area ON workers(area_id);
CREATE INDEX idx_workers_email ON workers(email);

-- Add FK constraint from areas to workers (after workers table created)
ALTER TABLE areas ADD CONSTRAINT fk_areas_manager_id 
  FOREIGN KEY (manager_id) REFERENCES workers(id) ON DELETE SET NULL;

-- SHIFT_TEMPLATES (Recurring shift patterns)
CREATE TABLE shift_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  suborganization_id UUID NOT NULL REFERENCES suborganizations(id) ON DELETE CASCADE,
  area_id UUID NOT NULL REFERENCES areas(id) ON DELETE CASCADE,
  code VARCHAR(10) NOT NULL,  -- e.g., "T", "M", "N"
  name VARCHAR(100) NOT NULL,  -- e.g., "Tarde", "Mañana", "Noche"
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(area_id, code)
);
CREATE INDEX idx_shift_templates_area ON shift_templates(area_id);

-- SHIFT_ASSIGNMENTS (Shifts assigned to workers)
CREATE TABLE shift_assignments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  worker_id UUID NOT NULL REFERENCES workers(id) ON DELETE CASCADE,
  shift_template_id UUID NOT NULL REFERENCES shift_templates(id) ON DELETE CASCADE,
  assignment_date DATE NOT NULL,
  status VARCHAR(20) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'absent', 'swapped')),
  is_overtime_shift BOOLEAN DEFAULT FALSE,
  notes TEXT,
  created_by_worker_id UUID REFERENCES workers(id) ON DELETE SET NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(worker_id, assignment_date)
);
CREATE INDEX idx_shift_assignments_worker ON shift_assignments(worker_id);
CREATE INDEX idx_shift_assignments_date ON shift_assignments(assignment_date);
CREATE INDEX idx_shift_assignments_company ON shift_assignments(company_id);

-- TIMESHEET_DAYS (Payroll calculation output)
CREATE TABLE timesheet_days (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  worker_id UUID NOT NULL REFERENCES workers(id) ON DELETE CASCADE,
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
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(worker_id, timesheet_date)
);
CREATE INDEX idx_timesheet_days_worker ON timesheet_days(worker_id);
CREATE INDEX idx_timesheet_days_date ON timesheet_days(timesheet_date);

-- SHIFT_SWAP_REQUESTS (Workflow for shift swaps)
CREATE TABLE shift_swap_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  requester_worker_id UUID NOT NULL REFERENCES workers(id) ON DELETE CASCADE,
  target_worker_id UUID NOT NULL REFERENCES workers(id) ON DELETE CASCADE,
  shift_assignment_id UUID NOT NULL REFERENCES shift_assignments(id) ON DELETE CASCADE,
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
  manager_approved_by UUID REFERENCES workers(id) ON DELETE SET NULL,
  rejection_reason TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  resolved_at TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CHECK (requester_worker_id != target_worker_id)
);
CREATE INDEX idx_swap_requests_requester ON shift_swap_requests(requester_worker_id);
CREATE INDEX idx_swap_requests_target ON shift_swap_requests(target_worker_id);
CREATE INDEX idx_swap_requests_status ON shift_swap_requests(status);

-- HOLIDAY_CALENDAR (Colombian holidays + custom)
CREATE TABLE holiday_calendar (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  holiday_date DATE NOT NULL,
  holiday_name VARCHAR(100) NOT NULL,
  is_public_holiday BOOLEAN DEFAULT TRUE,
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(company_id, holiday_date)
);
CREATE INDEX idx_holiday_calendar_company ON holiday_calendar(company_id);
CREATE INDEX idx_holiday_calendar_date ON holiday_calendar(holiday_date);

-- SURCHARGE_RULES (Configurable surcharges for future: custom agreements)
CREATE TABLE surcharge_rules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  surcharge_type VARCHAR(50) NOT NULL,
  percentage DECIMAL(5, 2) NOT NULL,
  effective_from DATE NOT NULL,
  effective_to DATE,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(company_id, surcharge_type, effective_from)
);
CREATE INDEX idx_surcharge_rules_company ON surcharge_rules(company_id);

-- AUDIT_LOG (Track all payroll exports for compliance)
CREATE TABLE audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  actor_worker_id UUID NOT NULL REFERENCES workers(id) ON DELETE SET NULL,
  action VARCHAR(50) NOT NULL,  -- 'export_payroll', 'update_shift', etc.
  entity_type VARCHAR(50),  -- 'shift_assignment', 'timesheet_day', etc.
  entity_id UUID,
  details JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_audit_log_company ON audit_log(company_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
```

### 2.3 Multi-Tenancy Enforcement

**Strategy:** ORM-level query injection with tenant_id

```python
# In SQLAlchemy ORM layer:
class TenantAwareMixin:
    company_id = Column(UUID, ForeignKey('companies.id'))

# Every query includes:
session.query(Worker).filter(Worker.company_id == current_tenant_id)

# FastAPI middleware injects tenant context:
@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    token = request.headers.get("Authorization")
    tenant_id = extract_tenant_from_token(token)
    request.state.tenant_id = tenant_id
    return await call_next(request)
```

---

## 3. Payroll Engine Design

### 3.1 Payroll Calculation Algorithm

**File:** `backend/app/services/payroll_engine.py`

```python
class PayrollEngine:
    """
    Colombian Labor Law payroll calculator.
    
    Rules implemented:
    - Hour classification (day/night/Sunday/holiday)
    - Surcharge percentages (35%, 75%, 110%, etc.)
    - Overtime limits & calculation
    - Midnight rule (shift crossing 00:00)
    - Habitual Sunday detection
    """
    
    def __init__(self, company_id: UUID, effective_date: Date):
        self.company_id = company_id
        self.effective_date = effective_date
        self.surcharge_rules = self._load_surcharge_rules()
        self.holidays = self._load_holidays()
        self.workweek_limit = self._get_workweek_limit()
    
    def calculate_timesheet(self, shift_assignment: ShiftAssignment) -> TimesheetDay:
        """
        Main entry point: Calculate payroll for a shift assignment.
        
        Process:
        1. Get shift details (start, end, template)
        2. Classify hours (day/night/sunday/holiday)
        3. Calculate surcharges
        4. Validate overtime limits
        5. Create TimesheetDay record
        """
        shift = shift_assignment.shift_template
        date = shift_assignment.assignment_date
        worker = shift_assignment.worker
        
        # Get shift times in worker's timezone
        start_local = self._to_local_time(shift.start_time, date)
        end_local = self._to_local_time(shift.end_time, date)
        
        # Handle midnight crossing
        if self._crosses_midnight(start_local, end_local):
            hours_before_midnight = self._classify_hours(start_local, datetime(date, 23, 59, 59))
            hours_after_midnight = self._classify_hours(datetime(date + 1, 0, 0, 0), end_local)
            hours = self._merge_hour_categories(hours_before_midnight, hours_after_midnight)
        else:
            hours = self._classify_hours(start_local, end_local)
        
        # Apply surcharges
        amounts = self._calculate_surcharges(hours, worker.hourly_rate)
        
        # Validate overtime limits
        self._validate_overtime_limits(worker, date, hours)
        
        # Detect habitual Sunday work
        is_habitual_sunday = self._is_habitual_sunday(worker, date)
        
        return TimesheetDay(
            worker_id=worker.id,
            timesheet_date=date,
            **hours,
            **amounts,
            is_habitual_sunday=is_habitual_sunday
        )
    
    def _classify_hours(self, start: datetime, end: datetime) -> Dict[str, float]:
        """
        Classify hours into categories based on Colombian law.
        
        Categories:
        - ordinary_hours: Daytime (6am-9pm) on weekday
        - night_hours: Nighttime (9pm-6am) on weekday
        - sunday_day_hours: Daytime on Sunday
        - sunday_night_hours: Nighttime on Sunday
        """
        hours = {
            'ordinary_hours': 0.0,
            'night_hours': 0.0,
            'sunday_day_hours': 0.0,
            'sunday_night_hours': 0.0,
            'overtime_day': 0.0,
            'overtime_night': 0.0,
            'overtime_sunday_day': 0.0,
            'overtime_sunday_night': 0.0,
        }
        
        # Iterate through each hour in shift
        current = start
        while current < end:
            next_hour = current + timedelta(hours=1)
            hour_duration = min((next_hour - current).total_seconds() / 3600, 1.0)
            
            is_sunday = current.weekday() == 6 or self._is_holiday(current.date())
            is_night = current.hour >= 21 or current.hour < 6  # 9pm-6am
            
            if is_sunday:
                if is_night:
                    hours['sunday_night_hours'] += hour_duration
                else:
                    hours['sunday_day_hours'] += hour_duration
            else:
                if is_night:
                    hours['night_hours'] += hour_duration
                else:
                    hours['ordinary_hours'] += hour_duration
            
            current = next_hour
        
        # Determine if overtime (daily or weekly)
        daily_total = sum([hours[k] for k in ['ordinary_hours', 'night_hours', 'sunday_day_hours', 'sunday_night_hours']])
        if daily_total > 9:  # Assuming 9h standard (typical Colombian daily limit)
            excess = daily_total - 9
            # Reclassify excess as overtime (simplified; real impl. would move by category)
            if hours['ordinary_hours'] > 9:
                excess_ordinary = hours['ordinary_hours'] - 9
                hours['ordinary_hours'] -= excess_ordinary
                hours['overtime_day'] += excess_ordinary
        
        return hours
    
    def _calculate_surcharges(self, hours: Dict[str, float], hourly_rate: Decimal) -> Dict[str, Decimal]:
        """Calculate gross amounts with surcharges applied."""
        surcharges = {
            'ordinary_hours': Decimal('1.00'),      # 0% surcharge
            'night_hours': Decimal('1.35'),         # 35% surcharge
            'sunday_day_hours': Decimal('1.75'),    # 75% surcharge
            'sunday_night_hours': Decimal('2.10'),  # 110% surcharge
            'overtime_day': Decimal('1.25'),        # 25% surcharge
            'overtime_night': Decimal('1.75'),      # 75% surcharge
            'overtime_sunday_day': Decimal('2.00'), # 100% surcharge
            'overtime_sunday_night': Decimal('2.50'),  # 150% surcharge
        }
        
        total_regular = Decimal('0')
        total_surcharge = Decimal('0')
        
        for category, hour_count in hours.items():
            if hour_count > 0:
                multiplier = surcharges[category]
                amount = Decimal(str(hour_count)) * hourly_rate * multiplier
                if multiplier == Decimal('1.00'):
                    total_regular += amount
                else:
                    total_surcharge += amount - (Decimal(str(hour_count)) * hourly_rate)
        
        return {
            'total_regular_amount': total_regular,
            'total_surcharge_amount': total_surcharge,
            'total_gross_amount': total_regular + total_surcharge
        }
    
    def _validate_overtime_limits(self, worker: Worker, date: Date, hours: Dict):
        """Check Colombian law overtime limits and warn/block."""
        daily_overtime = hours['overtime_day'] + hours['overtime_night'] + hours['overtime_sunday_day'] + hours['overtime_sunday_night']
        
        if daily_overtime > 2.0:
            raise OverTimeException(f"Daily overtime {daily_overtime}h exceeds 2h limit")
        
        # Check weekly limit (requires querying past 6 days)
        weekly_overtime = self._calculate_weekly_overtime(worker, date)
        if weekly_overtime > 12.0:
            raise OverTimeException(f"Weekly overtime {weekly_overtime}h exceeds 12h limit")
    
    def _is_holiday(self, date: Date) -> bool:
        """Check if date is a holiday (public or company-specific)."""
        return date in self.holidays
    
    def _is_habitual_sunday(self, worker: Worker, date: Date) -> bool:
        """Check if worker has 3+ Sundays in current month."""
        month_start = date.replace(day=1)
        month_end = (date.replace(day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        
        sunday_count = session.query(ShiftAssignment).filter(
            ShiftAssignment.worker_id == worker.id,
            ShiftAssignment.assignment_date >= month_start,
            ShiftAssignment.assignment_date <= month_end,
            extract(dow, ShiftAssignment.assignment_date) == 0  # Sunday
        ).count()
        
        return sunday_count >= 3
    
    def _get_workweek_limit(self) -> int:
        """Get current workweek limit based on year (2024-2026 transition)."""
        year = self.effective_date.year
        if year <= 2024:
            return 46
        elif year <= 2025:
            return 44
        else:
            return 42
```

### 3.2 Payroll Service (API Layer)

```python
class PayrollService:
    """High-level payroll operations."""
    
    def create_or_update_timesheet(self, shift_assignment: ShiftAssignment) -> TimesheetDay:
        """
        Trigger payroll calculation when shift is assigned/modified.
        
        Called from:
        - POST /api/shifts (new shift)
        - PUT /api/shifts/{id} (modified shift)
        """
        engine = PayrollEngine(
            company_id=shift_assignment.company_id,
            effective_date=shift_assignment.assignment_date
        )
        timesheet = engine.calculate_timesheet(shift_assignment)
        
        # Upsert timesheet
        existing = db.query(TimesheetDay).filter(
            TimesheetDay.worker_id == shift_assignment.worker_id,
            TimesheetDay.timesheet_date == shift_assignment.assignment_date
        ).first()
        
        if existing:
            existing.update(timesheet)
        else:
            db.add(timesheet)
        
        db.commit()
        return timesheet
    
    def generate_payroll_export(self, 
                               company_id: UUID, 
                               from_date: Date, 
                               to_date: Date, 
                               area_id: UUID = None,
                               format: str = 'csv') -> BytesIO:
        """
        Generate CSV/XML export with cedula + rubros.
        
        Query:
        1. Get all workers in company (or area)
        2. For each worker, fetch timesheets in date range
        3. Aggregate by category (ordinarias, nocturnas, etc.)
        4. Format as CSV/XML
        5. Return streaming response
        """
        workers = db.query(Worker).filter(Worker.company_id == company_id)
        if area_id:
            workers = workers.filter(Worker.area_id == area_id)
        
        rows = []
        for worker in workers:
            timesheets = db.query(TimesheetDay).filter(
                TimesheetDay.worker_id == worker.id,
                TimesheetDay.timesheet_date.between(from_date, to_date)
            ).all()
            
            # Aggregate
            total_ordinarias = sum(ts.ordinary_hours for ts in timesheets)
            total_nocturnas = sum(ts.night_hours for ts in timesheets)
            # ... etc
            
            rows.append({
                'cedula': worker.cedula,
                'nombre': f"{worker.first_name} {worker.last_name}",
                'ordinarias': total_ordinarias,
                'nocturnas': total_nocturnas,
                # ... rubros
            })
        
        if format == 'csv':
            return self._generate_csv(rows)
        elif format == 'xml':
            return self._generate_xml(rows)
    
    def _generate_csv(self, rows: List[Dict]) -> BytesIO:
        """Generate CSV with Pandas (efficient for large datasets)."""
        df = pd.DataFrame(rows)
        output = BytesIO()
        df.to_csv(output, index=False, encoding='utf-8')
        output.seek(0)
        return output
```

### 3.3 Test Suite Structure

```python
# backend/tests/test_payroll_engine.py

class TestPayrollEngineHourClassification:
    def test_daytime_hours_no_surcharge(self):
        """Daytime shift 8am-4pm = 8 ordinary hours."""
        shift = ShiftAssignment(start_time=time(8, 0), end_time=time(16, 0), date=date(2026, 4, 15))  # Wednesday
        result = engine.classify_hours(...)
        assert result['ordinary_hours'] == 8.0
        assert result['night_hours'] == 0.0
    
    def test_midnight_rule_saturday_to_sunday(self):
        """Saturday 8pm → Sunday 4am crosses midnight."""
        # Shift: Sat 8pm (1h) + Sat 9pm-12am (3h night) + Sun 12am-4am (4h sunday night)
        result = engine.classify_hours(...)
        assert result['ordinary_hours'] == 1.0
        assert result['night_hours'] == 3.0
        assert result['sunday_night_hours'] == 4.0
    
    def test_holiday_surcharge(self):
        """Shift on holiday applies 75% surcharge."""
        shift = ShiftAssignment(date=date(2026, 1, 1))  # New Year
        result = engine.classify_hours(...)
        assert result['holiday_day_hours'] > 0 or result['holiday_night_hours'] > 0
    
    def test_overtime_excess_daily(self):
        """Shift > 9h triggers overtime classification."""
        shift = ShiftAssignment(start_time=time(6, 0), end_time=time(17, 0))  # 11h
        result = engine.classify_hours(...)
        assert result['overtime_day'] == 2.0
    
    def test_habitual_sunday_detection(self):
        """3+ Sundays in month = habitual."""
        # Assign shifts on Sun 1st, Sun 8th, Sun 15th
        is_habitual = engine._is_habitual_sunday(worker, date(2026, 4, 15))
        assert is_habitual == True
    
    def test_workweek_limit_2024(self):
        """2024: workweek limit is 46h."""
        engine = PayrollEngine(company_id, date(2024, 6, 15))
        assert engine.workweek_limit == 46
    
    def test_workweek_limit_2026(self):
        """2026: workweek limit is 42h."""
        engine = PayrollEngine(company_id, date(2026, 6, 15))
        assert engine.workweek_limit == 42
    
    def test_surcharge_calculation(self):
        """Night hours (35%) calculation is correct."""
        hours = {'night_hours': 2.0}
        hourly_rate = Decimal('100000')
        amounts = engine._calculate_surcharges(hours, hourly_rate)
        expected_night_amount = 2 * 100000 * 1.35  # 270000
        assert amounts['total_gross_amount'] == Decimal('270000')

class TestPayrollEngineConstraints:
    def test_overtime_limit_per_day_block(self):
        """Max 2h/day overtime should block."""
        hours = {'overtime_day': 3.0}
        with pytest.raises(OverTimeException):
            engine._validate_overtime_limits(worker, date, hours)
    
    def test_overtime_limit_per_week_block(self):
        """Max 12h/week overtime should block."""
        # Setup: Worker has 10h overtime already this week
        # New shift would add 3h = 13h total → block
        with pytest.raises(OverTimeException):
            engine._validate_overtime_limits(worker, date, hours)

# ... 80+ more test cases covering all edge cases
```

---

## 4. API Implementation Strategy

### 4.1 FastAPI Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Configuration (DB URL, secrets, etc.)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── company.py          # SQLAlchemy models
│   │   ├── worker.py
│   │   ├── shift.py
│   │   ├── timesheet.py
│   │   └── ...
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── worker.py           # Pydantic request/response schemas
│   │   ├── shift.py
│   │   ├── payroll.py
│   │   └── ...
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py             # /auth endpoints
│   │   ├── shifts.py           # /api/shifts endpoints
│   │   ├── payroll.py          # /api/timesheets, /api/exports
│   │   ├── swaps.py            # /api/shift-swaps
│   │   └── ...
│   ├── services/
│   │   ├── __init__.py
│   │   ├── payroll_engine.py   # Payroll calculation logic
│   │   ├── shift_service.py    # Shift validation & assignment
│   │   ├── export_service.py   # CSV/XML generation
│   │   ├── auth_service.py     # JWT & tenant context
│   │   └── ...
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── tenant_middleware.py  # Multi-tenant context injection
│   │   ├── error_handler.py      # Global error handling
│   │   └── ...
│   └── utils/
│       ├── __init__.py
│       ├── db.py               # Database session management
│       ├── security.py         # Password hashing, JWT
│       └── ...
├── tests/
│   ├── __init__.py
│   ├── test_payroll_engine.py  # 100+ payroll tests
│   ├── test_api_shifts.py      # API endpoint tests
│   ├── test_api_payroll.py
│   └── ...
├── requirements.txt
├── Dockerfile
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
└── README.md
```

### 4.2 FastAPI Main App Setup

```python
# backend/app/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.middleware.tenant_middleware import TenantMiddleware
from app.routes import auth, shifts, payroll, swaps, holidays
from app.config import settings

app = FastAPI(
    title="Cronos API",
    description="Colombian Labor Law Shift Management",
    version="1.0.0"
)

# Security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],  # https://cronos.vercel.app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[settings.ALLOWED_HOSTS]
)

# Custom tenant middleware (inject context)
app.add_middleware(TenantMiddleware)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(shifts.router, prefix="/api/shifts", tags=["shifts"])
app.include_router(payroll.router, prefix="/api/timesheets", tags=["payroll"])
app.include_router(payroll.router, prefix="/api/exports", tags=["exports"])
app.include_router(swaps.router, prefix="/api/shift-swaps", tags=["swaps"])
app.include_router(holidays.router, prefix="/api/holidays", tags=["holidays"])

@app.on_event("startup")
async def startup_event():
    """Initialize DB connection pool, load config."""
    logger.info("Cronos API starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup."""
    logger.info("Cronos API shutting down...")

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
```

---

## 5. Frontend Architecture

### 5.1 React + Zustand State Structure

```
frontend/src/
├── components/
│   ├── Layout/
│   │   ├── Navbar.tsx
│   │   ├── Sidebar.tsx
│   │   └── MainLayout.tsx
│   ├── Shifts/
│   │   ├── ShiftCalendar.tsx
│   │   ├── ShiftForm.tsx
│   │   └── ShiftDetails.tsx
│   ├── Payroll/
│   │   ├── PayrollDashboard.tsx
│   │   ├── PayrollTable.tsx
│   │   └── ExportButton.tsx
│   ├── Admin/
│   │   ├── UserManagement.tsx
│   │   ├── HolidayCalendar.tsx
│   │   └── OrgHierarchy.tsx
│   └── Common/
│       ├── Modal.tsx
│       ├── Toast.tsx
│       └── LoadingSpinner.tsx
├── pages/
│   ├── LoginPage.tsx
│   ├── DashboardPage.tsx
│   ├── ShiftsPage.tsx
│   ├── PayrollPage.tsx
│   ├── AdminPage.tsx
│   └── NotFoundPage.tsx
├── stores/
│   ├── authStore.ts         # Auth state + JWT token
│   ├── userStore.ts         # Current user context + tenant
│   ├── shiftStore.ts        # Shift CRUD state
│   ├── payrollStore.ts      # Payroll view state
│   └── uiStore.ts           # Toast, modal, loading states
├── api/
│   ├── client.ts            # Axios client with CORS + auth header injection
│   ├── shifts.ts            # Shift API calls
│   ├── payroll.ts           # Payroll API calls
│   └── auth.ts              # Auth API calls
├── hooks/
│   ├── useAuth.ts
│   ├── useFetch.ts
│   ├── usePermissions.ts    # Role-based access
│   └── useTenant.ts         # Tenant context
├── utils/
│   ├── dateFormat.ts
│   ├── currency.ts          # COP formatting
│   └── validators.ts
├── styles/
│   ├── globals.css          # Tailwind config
│   └── variables.css        # CSS variables
├── App.tsx
├── main.tsx
├── vite-env.d.ts
└── index.html
```

### 5.2 Zustand Store Example

```typescript
// frontend/src/stores/shiftStore.ts

import { create } from 'zustand';
import { ShiftAssignment, ShiftTemplate } from '../types';
import * as shiftsApi from '../api/shifts';

interface ShiftState {
  shifts: ShiftAssignment[];
  templates: ShiftTemplate[];
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchShifts: (params: FetchParams) => Promise<void>;
  createShift: (data: CreateShiftInput) => Promise<void>;
  updateShift: (id: string, data: UpdateShiftInput) => Promise<void>;
  deleteShift: (id: string) => Promise<void>;
  fetchTemplates: (areaId: string) => Promise<void>;
}

export const useShiftStore = create<ShiftState>((set) => ({
  shifts: [],
  templates: [],
  loading: false,
  error: null,
  
  fetchShifts: async (params) => {
    set({ loading: true, error: null });
    try {
      const data = await shiftsApi.getShifts(params);
      set({ shifts: data });
    } catch (error) {
      set({ error: error.message });
    } finally {
      set({ loading: false });
    }
  },
  
  createShift: async (data) => {
    set({ loading: true });
    try {
      const newShift = await shiftsApi.createShift(data);
      set((state) => ({ shifts: [...state.shifts, newShift] }));
    } catch (error) {
      set({ error: error.message });
    } finally {
      set({ loading: false });
    }
  },
  
  // ... other actions
}));
```

---

## 6. Authentication & Security

### 6.1 JWT Implementation

```python
# backend/app/utils/security.py

from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt

class SecurityService:
    def __init__(self, settings):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.JWT_EXPIRE_MINUTES
    
    def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
        """Create JWT token with tenant_id embedded."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> dict:
        """Verify JWT and extract claims (including tenant_id)."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise UnauthorizedException("Invalid token")
    
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

# JWT payload structure:
# {
#   "sub": "user_id_uuid",
#   "company_id": "company_uuid",
#   "role": "manager",
#   "exp": 1682000000,
#   "iat": 1681996400
# }
```

### 6.2 CORS Configuration

```python
# backend/app/main.py

CORS_ORIGINS = [
    "https://cronos.vercel.app",      # Production frontend (Vercel)
    "http://localhost:5173",           # Development frontend (Vite)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## 7. Data Flow Diagrams

### 7.1 Shift Assignment Flow

```
┌──────────┐
│ Manager  │
└─────┬────┘
      │ 1. Create Shift Template (once)
      │    POST /api/shift-templates
      ▼
┌──────────────────────────────┐
│ Backend: Validate template   │
│ - Area exists                │
│ - Code unique per area       │
└─────────┬────────────────────┘
          │
          ▼
  ┌───────────────────┐
  │ DB: Save template │
  └────────┬──────────┘
           │
           │ 2. Assign Shift (repeatable)
           │    POST /api/shifts
           │
      ┌────▼─────────────────┐
      │ Manager              │
      │ - Worker            │
      │ - Template          │
      │ - Date              │
      └─────┬────────────────┘
            │
            ▼
  ┌──────────────────────────────┐
  │ Backend Validation:          │
  │ ✓ Worker in same area        │
  │ ✓ No duplicate same day      │
  │ ⚠ Check weekly limits        │
  │ ⚠ Check 11h rest period      │
  └─────┬────────────────────────┘
        │
        ├─ Valid ─────────────────────────┐
        │                                 │
        ▼                                 ▼
   ┌─────────────┐           ┌──────────────────────┐
   │ DB: Create  │           │ Backend: PayrollEngine
   │ Assignment  │           │ - Classify hours     │
   └────┬────────┘           │ - Calculate surcharge│
        │                     │ - Check overtime     │
        │                     └──────┬───────────────┘
        │                            │
        │                            ▼
        │                    ┌─────────────────┐
        │                    │ DB: Create      │
        │                    │ TimesheetDay    │
        │                    └────┬────────────┘
        │                         │
        ▼                         ▼
   ┌────────────────────────────────────────┐
   │ Shift visible to:                      │
   │ - Worker: /api/shifts/me               │
   │ - Manager: /api/shifts?area_id=X       │
   │ - HR: /api/shifts (all)                │
   └────────────────────────────────────────┘
```

### 7.2 Payroll Export Flow

```
┌──────┐
│ HR   │
└─┬────┘
  │ 1. Request Export
  │    POST /api/exports/payroll
  │    {from_date, to_date, format: "csv"}
  │
  ▼
┌──────────────────────────────┐
│ Backend: ExportService       │
│ 1. Query all workers + filters
│ 2. For each worker:          │
│    - Fetch timesheets        │
│    - Aggregate rubros        │
│    - Build row               │
└─────┬──────────────────────────┘
      │
      ├─ If file < 10MB:
      │  ▼
      │  ┌──────────────────────┐
      │  │ Generate CSV/XML     │
      │  │ (Streaming response) │
      │  └────┬─────────────────┘
      │       │
      │       ▼
      │    ┌─────────────────┐
      │    │ HR downloads    │
      │    │ cronos_export.csv
      │    └─────────────────┘
      │
      └─ Else (file > 10MB):
         ▼
         ┌─────────────────────────────┐
         │ Backend: Background Task    │
         │ 1. Generate large file      │
         │ 2. Store in temp storage    │
         │ 3. Email link to HR         │
         └─────────────────────────────┘
```

---

## 8. Error Handling Strategy

### 8.1 API Error Responses

```python
# Standard error format (RFC 7807)

class APIError(Exception):
    def __init__(self, status_code: int, error_code: str, message: str, details: dict = None):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details or {}

# Example error responses:

# 400 Bad Request
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "hourly_rate": "Must be positive number"
    }
  }
}

# 401 Unauthorized
{
  "error": {
    "code": "INVALID_TOKEN",
    "message": "JWT token expired"
  }
}

# 409 Conflict
{
  "error": {
    "code": "DUPLICATE_SHIFT",
    "message": "Worker already has shift on this date",
    "details": {
      "worker_id": "uuid-123",
      "date": "2026-04-20"
    }
  }
}

# 422 Unprocessable Entity (validation failure)
{
  "error": {
    "code": "OVERTIME_LIMIT_EXCEEDED",
    "message": "Assignment would exceed weekly overtime limit",
    "details": {
      "current_weekly_overtime": 10,
      "new_shift_overtime": 3,
      "limit": 12
    }
  }
}
```

### 8.2 Global Error Handler

```python
# backend/app/middleware/error_handler.py

@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    audit_log(request, exc)  # Log all errors
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    audit_log(request, exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred"
            }
        }
    )
```

---

## 9. Caching & Performance

### 9.1 Query Optimization

```sql
-- Essential indexes for query performance:

CREATE INDEX idx_shift_assignments_worker_date ON shift_assignments(worker_id, assignment_date);
CREATE INDEX idx_timesheet_days_worker_date ON timesheet_days(worker_id, timesheet_date);
CREATE INDEX idx_holiday_calendar_date ON holiday_calendar(holiday_date);

-- Example: Fast payroll export query
SELECT 
    w.cedula,
    w.first_name,
    w.last_name,
    SUM(td.ordinary_hours) as ordinarias,
    SUM(td.night_hours) as nocturnas,
    SUM(td.overtime_day) as extras_dia,
    SUM(td.total_gross_amount) as total_valor
FROM workers w
LEFT JOIN timesheet_days td ON w.id = td.worker_id
WHERE w.company_id = $1
  AND td.timesheet_date BETWEEN $2 AND $3
GROUP BY w.id, w.cedula, w.first_name, w.last_name
ORDER BY w.cedula;
```

### 9.2 Caching Strategy (Post-MVP)

```python
# Use Redis for caching expensive queries (Phase 4)

class CacheService:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def get_worker_payroll_summary(self, worker_id: UUID, month: str) -> dict:
        """
        Cache worker payroll for month (e.g., '2026-04').
        Invalidate on:
        - New shift assignment
        - TimesheetDay update
        - Holiday calendar update
        """
        cache_key = f"payroll:{worker_id}:{month}"
        cached = self.redis.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        # Calculate
        result = self._calculate_payroll(worker_id, month)
        
        # Cache for 24 hours
        self.redis.setex(cache_key, 86400, json.dumps(result))
        
        return result
    
    def invalidate_worker_payroll(self, worker_id: UUID):
        """Invalidate all cached payroll for worker."""
        pattern = f"payroll:{worker_id}:*"
        for key in self.redis.scan_iter(pattern):
            self.redis.delete(key)
```

---

## 10. Deployment & CI/CD

### 10.1 Vercel Deployment (Frontend)

```yaml
# vercel.json (Vercel config)
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "env": {
    "VITE_API_URL": "@cronos_api_url"
  },
  "functions": {
    "api/**/*.ts": {
      "memory": 512,
      "maxDuration": 30
    }
  }
}

# GitHub Actions (auto-deploy on push to main)
name: Deploy Frontend
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: vercel/action@master
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
```

### 10.2 Render Deployment (Backend)

```yaml
# render.yaml (Render config)
services:
  - type: web
    name: cronos-backend
    env: python
    plan: free
    buildCommand: "pip install -r requirements.txt && alembic upgrade head"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DATABASE_URL
        scope: build,runtime
        sync: false
      - key: FRONTEND_URL
        value: "https://cronos.vercel.app"

# GitHub Actions (auto-deploy on push to main)
name: Deploy Backend
on:
  push:
    branches: [main]
    paths:
      - 'backend/**'
      - '.github/workflows/deploy-backend.yml'
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Render
        uses: renderio/render-action@v0
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
```

### 10.3 Testing & Quality Gates

```yaml
# GitHub Actions: Run tests before merge
name: CI
on: [pull_request]
jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/ --cov=backend/app --cov-fail-under=80
      - run: black --check backend/
      - run: flake8 backend/
      - run: mypy backend/
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd frontend && npm install && npm run lint && npm run test
```

---

## Summary

**Cronos MVP Design delivers:**
- ✅ Complete database schema (8 entities, multi-tenant isolation)
- ✅ Payroll engine architecture (Colombian law compliance, 100+ test cases)
- ✅ FastAPI backend structure (7 resource groups, 27 endpoints, streaming exports)
- ✅ React frontend architecture (Zustand state, role-based components)
- ✅ JWT authentication & CORS security
- ✅ Error handling strategy (RFC 7807 errors)
- ✅ Caching & performance optimization
- ✅ CI/CD pipelines (Vercel + Render + GitHub Actions)

**Ready to proceed to Tasks Phase ✅**

---

**Created:** 2026-04-16  
**Phase:** SDD Design  
**Status:** DRAFT - Ready for Review
