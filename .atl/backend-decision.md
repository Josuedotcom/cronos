# Backend Architecture Decision: Neon + FastAPI

## Executive Summary

After evaluating **Supabase**, **Neon**, and **Traditional FastAPI + PostgreSQL**, we've selected:

### ✅ **Neon (Cloud DB) + FastAPI (Python Backend) + React (Frontend)**

**Why NOT Supabase?**
- Supabase is excellent for CRUD apps but is a "trap" for complex payroll domains
- Colombian labor law logic in PL/pgSQL or TypeScript Edge Functions becomes unmaintainable
- Payroll calculations require rigorous unit testing and frequent law updates (2024-2026 workweek reductions)
- Python is superior for mathematical/payroll modeling with full testing framework

**Why Neon + FastAPI?**
1. **Python for Complex Logic:** FastAPI allows testable, auditable payroll engine
2. **Neon for DB Peace of Mind:** Fully managed, auto-scaling PostgreSQL + branching for safe migrations
3. **Zero Vendor Lock-In:** Neon is just Postgres. Switch to Docker/AWS RDS anytime
4. **Self-Hosting Path:** Start with Neon Cloud, migrate to self-hosted infrastructure later
5. **Multi-Tenancy:** Implement in FastAPI ORM layer (MVP simple) or PostgreSQL RLS (post-MVP)

---

## Detailed Comparison

| Feature | Supabase | Neon + FastAPI | Traditional FastAPI |
|---------|----------|-----------------|-------------------|
| **Initial Setup** | Low (Auth/APIs out-of-box) | Medium (build FastAPI layer) | High (full stack) |
| **Operational Burden** | High (self-hosted 10+ containers) | Low (DB managed, app simple) | High (manage DB + app) |
| **Cost (MVP)** | Low/Free | Free/generous tier | Cheap VPS |
| **Cost (Scale)** | Expensive | Usage-based, predictable | Manual scaling needed |
| **Multi-Tenancy** | Excellent (native RLS) | Good (FastAPI + RLS) | Good (FastAPI + RLS) |
| **Payroll Logic** | ❌ Poor (PL/pgSQL complexity) | ✅ Excellent (Python) | ✅ Excellent (Python) |
| **CSV/XML Exports** | Medium (Edge Functions) | ✅ Excellent (Pandas) | ✅ Excellent (Pandas) |
| **Testability** | Hard (SQL/TS logic) | ✅ Easy (pytest) | ✅ Easy (pytest) |
| **Vendor Lock-In** | High (Auth, Functions, Storage) | None (standard Postgres) | None (standard Postgres) |
| **Portability** | Difficult migration | Easy (pg_dump/restore) | Easy (pg_dump/restore) |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React + TS)                    │
│  - TypeScript components (Shift calendar, exports, etc.)    │
│  - Zustand state management                                 │
│  - Vite build tool                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS/JSON
┌──────────────────────▼──────────────────────────────────────┐
│                  FastAPI Backend (Python)                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Core Logic Layers:                                  │   │
│  │ ├── API Routes (FastAPI routers)                    │   │
│  │ ├── Services (Business logic)                       │   │
│  │ ├── Payroll Engine (Colombian labor law)           │   │
│  │ ├── Multi-Tenancy Layer (ORM + RLS config)         │   │
│  │ ├── Export Service (CSV/XML generation)            │   │
│  │ └── Auth Middleware (JWT validation)               │   │
│  └─────────────────────────────────────────────────────┘   │
│  - SQLAlchemy ORM + Alembic migrations                     │
│  - pytest for testing (payroll edge cases)                 │
│  - Deployed: Docker container (ECS/Render/Cloud Run)       │
└──────────────────────┬──────────────────────────────────────┘
                       │ SQL
┌──────────────────────▼──────────────────────────────────────┐
│         PostgreSQL via Neon (Serverless DB)                 │
│  - Auto-scaling compute                                     │
│  - Database branching (dev/staging/prod)                    │
│  - RLS for multi-tenant row isolation                       │
│  - Optional: Self-host with Docker/AWS RDS                  │
└──────────────────────────────────────────────────────────────┘
```

---

## Implementation Roadmap

### Phase 1: MVP Setup (Weeks 1-4)
**Objective:** Get basic shift management working

- [ ] **Database:** PostgreSQL locally (Docker) or Neon dev tier
- [ ] **Backend:** FastAPI project scaffold with:
  - [ ] SQLAlchemy ORM models (Company, SubOrganization, Area, Worker, ShiftTemplate, ShiftAssignment)
  - [ ] Alembic migrations
  - [ ] Auth middleware (JWT)
  - [ ] Multi-tenancy ORM layer (inject `tenant_id` into queries)
- [ ] **Shift CRUD:** Endpoints for:
  - [ ] List/Create/Update/Delete shift templates
  - [ ] List/Create/Update/Delete shift assignments
- [ ] **Frontend:** React setup with Vite + basic UI for shift calendar view
- [ ] **Testing:** Initial pytest suite for ORM models

### Phase 2: Payroll Engine & Exports (Weeks 5-8)
**Objective:** Implement complex Colombian labor law calculations

- [ ] **Payroll Module (Python):**
  - [ ] Hour classification algorithm (day/night/Sunday/holiday/overtime)
  - [ ] Surcharge calculation per Colombian CST rules
  - [ ] Workweek hour calculation with 2024-2026 baseline adjustments
  - [ ] Habitual Sunday detection (3+ Sundays/month)
  - [ ] Midnight rule (shifts crossing midnight)
- [ ] **Extensive pytest Coverage:**
  - [ ] Unit tests for every surcharge type
  - [ ] Edge cases (midnight crossings, holidays, workweek transitions)
  - [ ] Regression tests for labor law changes
- [ ] **Export Service:**
  - [ ] CSV export (worker cedula + rubros)
  - [ ] XML export for accounting software
  - [ ] Streaming responses for large exports (memory efficiency)
- [ ] **Timesheet Calculation:**
  - [ ] Auto-calculate TimesheetDay records per shift
  - [ ] Aggregation by pay period (weekly, bi-weekly, monthly)

### Phase 3: Advanced Features (Weeks 9-12)
**Objective:** Shift swaps, notifications, analytics

- [ ] **Shift Swaps Workflow:**
  - [ ] ShiftSwapRequest CRUD
  - [ ] Manager approval logic
  - [ ] Constraint validation (no overtime limit breaches)
- [ ] **Analytics & Reporting:**
  - [ ] Hours summary per worker (by type)
  - [ ] Team-level reporting
  - [ ] Overtime alerts
- [ ] **Notifications:**
  - [ ] Email notifications (shift assignments, swap requests)
  - [ ] Optional: WebSocket real-time updates (post-MVP)

### Phase 4: Cloud Migration & Scale (Post-MVP)
**Objective:** Production-ready deployment with subscriptions

- [ ] **Database Migration:** Migrate to Neon Cloud tier (if started locally)
- [ ] **App Deployment:** Deploy FastAPI to ECS/Render/Cloud Run with auto-scaling
- [ ] **Production Database:** RLS enforcement at PostgreSQL level
- [ ] **Subscription System:** Integrate Stripe/PayU for org-size billing
- [ ] **Performance Tuning:** Query optimization, caching, connection pooling
- [ ] **Data Residency:** Ensure Neon region complies with LatAm data sovereignty

---

## Key Technical Decisions

### 1. Multi-Tenancy Implementation

**MVP Approach (Simple):**
- Inject `tenant_id` (company_id) into all SQLAlchemy queries
- ORM layer enforces tenant isolation at application level
- All tables have `company_id` foreign key

**Post-MVP Approach (Secure):**
- PostgreSQL Row-Level Security (RLS)
- FastAPI middleware sets `app.current_tenant` as Postgres local variable
- Database-level isolation of sensitive payroll data

### 2. Payroll Engine Location

**Decision:** Python module in FastAPI backend, NOT database stored procedures

**Rationale:**
- Law changes frequently (workweek reductions, new tax rules)
- Python allows rigorous unit testing of edge cases
- Easy versioning and rollback of calculation logic
- Auditable for compliance with DIAN requirements

**Structure:**
```
backend/app/services/
├── payroll_engine.py        # Core calculation logic
├── surcharge_calculator.py  # Recargo calculations
├── export_generator.py      # CSV/XML generation
└── tests/
    ├── test_payroll_edge_cases.py
    ├── test_midnight_rule.py
    ├── test_sunday_surcharge.py
    └── test_workweek_reductions.py
```

### 3. Export Strategy

**MVP:** Streaming CSV response with background task for email
**Post-MVP:** Scheduled batch exports, larger file storage (S3 bucket)

### 4. Self-Hosting Fallback

**Anytime you want to self-host:**
```bash
# Change DATABASE_URL to local or AWS RDS
export DATABASE_URL=postgresql://user:pass@localhost:5432/cronos

# Or use Docker Postgres
docker run -e POSTGRES_DB=cronos postgres:14

# Deploy FastAPI with Docker
docker build -t cronos-backend . && docker run -p 8000:8000 cronos-backend
```

No code changes needed. Zero vendor lock-in.

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| **Neon outage** | Self-host backup Postgres (just change DATABASE_URL) |
| **Data sovereignty** | Neon US-East region acceptable for LatAm; verify with clients |
| **Payroll law changes** | Version payroll engine, extensive testing, audit trail in code |
| **Export performance** | Streaming responses + background tasks for large datasets |
| **Security (multi-tenant)** | RLS post-MVP, audit logs for all payroll data access |

---

## Deployment Architecture (Cloud)

```
┌─────────────────────────────────────────────────────────┐
│              Load Balancer / CDN                         │
│           (CloudFlare / AWS CloudFront)                  │
└────────────────┬────────────────┬───────────────────────┘
                 │                │
        ┌────────▼────────┐  ┌────▼─────────────┐
        │  React Frontend │  │  FastAPI Backend │
        │   (S3 + CDN)    │  │ (ECS / Render)   │
        │    Vite build   │  │  Containers      │
        └─────────────────┘  └────┬─────────────┘
                                  │
                          ┌───────▼────────┐
                          │  Neon DB       │
                          │  PostgreSQL    │
                          │  (Serverless)  │
                          └────────────────┘
                          
Optional: AWS S3 for exports
```

---

## Next Steps

1. ✅ Architecture decided: **Neon + FastAPI + React**
2. ⏭️ Move to **SDD Proposal Phase** → Define MVP scope and features
3. ⏭️ Then **SDD Spec Phase** → Detailed API contracts and workflows
4. ⏭️ Then **SDD Design Phase** → Database schema and payroll engine design
5. ⏭️ Then **SDD Tasks Phase** → Implementation sprint breakdown
6. ⏭️ Begin **SDD Apply Phase** → Start coding!

---

**Decision Date:** 2026-04-16  
**Status:** APPROVED ✅  
**Prepared for:** SDD Proposal Phase
