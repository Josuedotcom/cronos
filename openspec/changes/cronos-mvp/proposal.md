# Cronos MVP - Change Proposal

**Project:** Cronos - Colombian Labor Law-Compliant Shift Management System  
**Change ID:** cronos-mvp  
**Status:** PROPOSED  
**Created:** 2026-04-16  
**Author:** SDD Proposal Phase  

---

## 1. Problem Statement

**Current State:**
Many Colombian organizations manage worker shifts using spreadsheets, manual processes, or outdated systems that don't correctly calculate payroll according to the Código Sustantivo del Trabajo (CST). This leads to:
- Manual errors in shift schedules
- Incorrect payroll calculations (missing surcharges, overtime miscalculations)
- No transparency for workers (unclear hours, earnings)
- HR struggling to track surcharges, overtime limits, dominical work
- Compliance risk (labor law violations)
- Difficulty scaling to multiple sub-organizations and areas

**Goal:**
Build an integrated web platform where:
- **Workers** see their schedules clearly and understand their payroll breakdown
- **Managers** assign shifts efficiently, manage swaps, validate labor law constraints
- **HR** exports accurate payroll data (cedula + rubros) for their accounting software
- **Multi-tenant organizations** can manage multiple sub-organizations and areas with different shift grids

**Success = Workers trust the system, HR exports clean data, zero labor law violations.**

---

## 2. MVP Scope

### Must-Have Features (MVP - Phases 1-3)

| Feature | Priority | Phase | Effort | Rationale |
|---------|----------|-------|--------|-----------|
| **Shift Templates (CRUD)** | P0 | 1 | M | HR defines shift patterns (T, M, N, etc.) with hours |
| **Shift Assignment (CRUD)** | P0 | 1 | M | Managers assign shifts to workers + dates |
| **Worker Shift View** | P0 | 1 | M | Workers see their schedule |
| **Company/Sub-Org/Area Hierarchy** | P0 | 1 | L | Foundation for multi-tenancy |
| **Multi-Tenant Isolation** | P0 | 1 | L | Data isolation per company/sub-org |
| **User Roles** | P0 | 1 | S | Worker, Manager, HR roles + permissions |
| **Authentication (JWT)** | P0 | 1 | M | Login + token-based auth |
| **Colombian Payroll Engine** | P0 | 2 | XL | Hour classification, surcharges, overtime, midnight rule, workweek limits |
| **Payroll Calculation** | P0 | 2 | L | Auto-calculate TimesheetDay per assignment |
| **CSV Export (Payroll)** | P0 | 2 | M | Export: cedula + ordinarias + nocturnas + extras + recargos |
| **Payroll View (Worker)** | P0 | 2 | M | Workers see hours breakdown per day/week |
| **Payroll View (HR)** | P0 | 2 | M | HR views aggregated payroll data |
| **Colombian Holiday Calendar** | P0 | 2 | S | Manage holidays (18+ festivos) |
| **Holiday Surcharge Trigger** | P0 | 2 | M | Apply 75% surcharge on holidays |
| **Shift Swap Request (Basic)** | P1 | 3 | M | Workers request swap, managers approve |
| **Analytics Dashboard (Simple)** | P1 | 3 | M | Hours summary, overtime alerts per worker/team |
| **XML Export (Optional)** | P2 | 3 | M | Export for accounting software (Siigo, Novasoft) |
| **Extensive Test Suite** | P0 | 1-3 | XL | Unit + integration tests, payroll edge cases |

### Out of Scope (Post-MVP)

| Feature | Reason | Timeline |
|---------|--------|----------|
| Sunday Compensatory Days (automatic generation) | Requires stakeholder clarification | Post-MVP / Phase 4 |
| Biometric/GPS Clock-In | Honor system MVP + extra complexity | Phase 4+ |
| Custom Union Agreements (% surcharges) | CST standard only for MVP | Phase 4+ |
| Advanced Reporting (complex aggregations) | Basic dashboard sufficient | Phase 4+ |
| Mobile App (iOS/Android) | Web responsive + PWA sufficient | Phase 4+ |
| Real-Time WebSocket Notifications | Email notifications sufficient | Phase 4+ |
| Audit Logs (detailed) | Basic audit via DB timestamps | Phase 4+ |
| Two-Factor Auth | JWT + basic auth sufficient | Phase 4+ |
| Advanced Multi-Tenancy (strict RLS)** | ORM-level isolation sufficient (MVP) | Phase 4+ |

---

## 3. Intent & High-Level Approach

### Architecture

```
Frontend (React + TypeScript + Vite)
         │
         ├─→ HTTPS/JSON API
         │
Backend (FastAPI + Python 3.11+)
         │
         ├─→ SQLAlchemy ORM (multi-tenant queries)
         ├─→ Payroll Engine Module (complex calculations)
         ├─→ Export Service (CSV/XML generation)
         └─→ Auth Middleware (JWT + tenant_id injection)
         │
         └─→ PostgreSQL (Neon serverless)
               ├─ Company / SubOrganization / Area hierarchy
               ├─ Worker + ShiftTemplate + ShiftAssignment
               ├─ TimesheetDay (payroll output)
               └─ HolidayCalendar + SurchargeRules
```

### Multi-Tenancy Strategy

**MVP (Phase 1-3):** ORM-level isolation
- Inject `tenant_id` (company_id) into all SQLAlchemy queries
- `Company`, `SubOrganization`, `Area` model the hierarchy
- Each endpoint validates user's tenant access

**Post-MVP (Phase 4):** PostgreSQL RLS
- Enable strict row-level security at the DB
- FastAPI middleware sets `app.current_tenant` Postgres variable
- DB enforces isolation automatically

### Payroll Engine Approach

**Location:** `backend/app/services/payroll_engine.py`

**Why Python (not SQL)?**
- Law changes frequently (workweek reductions 2024-2026)
- Requires rigorous unit testing of edge cases
- Easy to version control and audit
- Supports Pandas for complex data transformations

**Logic:**
- Hour classification (ordinarias, nocturnas, dominicales, festivas)
- Surcharge calculation (night 35%, Sunday 75%, night+Sunday 110%, overtime 25-150%)
- Overtime limits validation (max 2h/day, 12h/week)
- Midnight rule (shifts crossing 00:00 change type)
- Habitual Sunday detection (3+ domingos/mes)
- Workweek variable (48h→46h→44h→42h, 2024-2026)

**Testing:**
- pytest with 100+ test cases for edge cases
- Regression tests for every law change
- CI/CD validation before any deployment

### Export Strategy

**MVP (CSV):**
```
cedula, nombre, ordinarias, nocturnas, extras_dia, extras_noche, recargo_domingo, recargo_noche, total_horas, total_valor
1234567890, Juan Pérez, 160.0, 20.0, 2.0, 0.0, 4.0, 0.0, 186.0, $2,345,600
```

**Post-MVP (XML, advanced):**
- Format for Siigo, Novasoft, SAP
- Large-file streaming (memory efficient)
- Scheduled batch exports

---

## 4. Phased Rollout

### Phase 1: Foundation & Basic Shift Management (Weeks 1-4)

**Goal:** Get basic shift scheduling working

**Deliverables:**
- [ ] Project setup: FastAPI scaffold, SQLAlchemy models, Alembic migrations
- [ ] Database schema: Company, SubOrganization, Area, Worker, ShiftTemplate, ShiftAssignment
- [ ] Multi-tenancy ORM layer (tenant_id injection)
- [ ] Authentication: JWT login/logout
- [ ] Shift CRUD endpoints (create/list/update/delete templates and assignments)
- [ ] Worker shift view (my schedule)
- [ ] Manager shift view (assign shifts to workers)
- [ ] HR admin interface (manage workers, organizations)
- [ ] React UI: Shift calendar view, CRUD forms
- [ ] Docker setup (local Postgres, FastAPI, React dev stack)
- [ ] Initial pytest suite (ORM models, auth)

**Effort:** 4 weeks (1 backend, 1 frontend, part-time QA)  
**Testing:** Basic CRUD, auth, tenant isolation

---

### Phase 2: Payroll Engine & Exports (Weeks 5-8)

**Goal:** Implement complex Colombian payroll calculations and enable HR exports

**Deliverables:**
- [ ] Payroll Engine Module (Python):
  - [ ] Hour classification algorithm
  - [ ] Surcharge calculation logic
  - [ ] Overtime validation
  - [ ] Midnight rule handling
  - [ ] Habitual Sunday detection
- [ ] Extensive pytest coverage (100+ test cases):
  - [ ] Every surcharge type
  - [ ] Edge cases (midnight, holidays, workweek reductions)
  - [ ] Law change scenarios
- [ ] TimesheetDay auto-calculation (trigger on shift assignment)
- [ ] Payroll View (worker sees: ordinarias, nocturnas, extras, recargos per day)
- [ ] Payroll View (HR sees: all workers aggregated)
- [ ] CSV Export endpoint (cedula + rubros)
- [ ] Holiday Calendar CRUD (manage festivos colombianos)
- [ ] Holiday surcharge trigger logic
- [ ] React UI: Payroll breakdown, export button
- [ ] Background task: Generate/email exports

**Effort:** 4 weeks (payroll complexity is XL)  
**Testing:** Comprehensive payroll test suite (critical for compliance)

---

### Phase 3: Advanced Features (Weeks 9-12)

**Goal:** Enable shift swaps, analytics, improve UX

**Deliverables:**
- [ ] Shift Swap Request workflow:
  - [ ] Worker requests swap
  - [ ] System validates constraints (no overtime breach)
  - [ ] Manager approves/rejects
  - [ ] On approval, swap assignments
- [ ] Analytics Dashboard (simple):
  - [ ] Hours by type (pie chart)
  - [ ] Overtime alerts
  - [ ] Team summary
- [ ] XML Export (optional, for Siigo/Novasoft compatibility)
- [ ] Improved error handling + user feedback
- [ ] Performance optimization (queries, caching)
- [ ] Documentation (API docs, user guide)
- [ ] End-to-end testing (user workflows)

**Effort:** 4 weeks  
**Testing:** Workflow validation, E2E scenarios

---

### Phase 4: Cloud & Scale (Post-MVP, Timeline TBD)

**Goal:** Production deployment, multi-tenant subscriptions, compliance

**Deliverables:**
- [ ] Migrate PostgreSQL to Neon Cloud
- [ ] Deploy FastAPI to ECS / Render / Cloud Run (auto-scaling)
- [ ] Enable PostgreSQL RLS (strict multi-tenant isolation)
- [ ] Subscription system (Stripe/PayU):
  - [ ] Org size-based tiers
  - [ ] Usage tracking
  - [ ] Billing
- [ ] Advanced features:
  - [ ] Sunday compensatory auto-generation
  - [ ] Custom union agreement surcharges
  - [ ] Real-time WebSocket notifications
  - [ ] Mobile app (PWA or native)
  - [ ] Advanced reporting
- [ ] Security hardening (audit logs, 2FA, DLP)
- [ ] Performance tuning (query optimization, caching, CDN)
- [ ] Legal review (DIAN compliance for payroll export)

**Effort:** 4-6 weeks (deployment + subscriptions)  
**Timeline:** 1-2 months post-MVP launch

---

## 5. Success Criteria

### MVP Launch Criteria

| Criterion | Measurable | Owner |
|-----------|-----------|-------|
| **Shift Management Works** | Workers can see schedules; managers can assign shifts | QA |
| **Payroll Accurate** | Surcharges correctly calculated per CST; test suite 100+ cases pass | QA + Engineering |
| **Export Works** | HR exports CSV with cedula + rubros; data matches payroll engine calculations | QA + HR |
| **Multi-Tenant Isolation** | Data properly isolated per company/sub-org; no data leakage | QA + Security |
| **Performance** | Page load <2s, export <10s for 1000 workers | QA |
| **Compliance** | All Colombian labor law rules implemented; audit trail exists | Legal + Eng |
| **Tests Pass** | 100+ pytest cases pass, CI/CD green on every merge | QA |
| **User Acceptance** | Internal stakeholders (HR, managers, 5 pilot workers) approve MVP | Product |

---

## 6. Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|-----------|
| **Payroll logic bugs** | Incorrect worker pay (legal + financial risk) | Medium | Extensive pytest (100+ cases), code review by payroll expert, staged rollout (1 company first) |
| **Multi-tenant data leakage** | GDPR/LSFO violation, legal liability | Low | ORM-level isolation MVP, RLS post-MVP, penetration testing |
| **Colombian law changes** | System non-compliant, payroll errors | High | Modular Python engine, version control, feature flags for law changes |
| **Export format incompatibility** | HR cannot import to nómina software | Medium | Test with actual Siigo/Novasoft instances, validate formats |
| **Performance with large teams** | Export slow for 1000+ workers | Low | Streaming responses, query optimization, PostgreSQL indexing |
| **Database downtime (Neon)** | System unavailable, shift schedules lost | Very Low | Neon has 99.95% SLA; backup plan: self-host Postgres on AWS RDS |
| **Scope creep** | MVP delays, budget overruns | Medium | Strict phase gates, defer Phase 4 features, user acceptance sign-off |

---

## 7. Effort Estimate

### MVP (Phases 1-3): ~3-4 months

**Team:**
- 1 Backend Engineer (Python/FastAPI) - 100% → 3 months
- 1 Frontend Engineer (React/TypeScript) - 100% → 3 months
- 1 QA Engineer - 50% → 3 months (payroll validation critical)
- 1 Product Manager - 50% (requirements, scope management)

**Breakdown (Man-Months):**
- Phase 1 (Foundation): 3 weeks × 2.5 people = ~1.8 MM
- Phase 2 (Payroll): 4 weeks × 2.5 people = ~2.5 MM (payroll is complex)
- Phase 3 (Advanced): 3 weeks × 2.5 people = ~1.9 MM
- **Total MVP: ~6-6.5 MM (feasible in 3-4 months with team of 2.5)**

### Phase 4 (Cloud & Scale): +2-4 weeks additional

### Contingency: +20% (1 month buffer)

---

## 8. Assumptions & Open Questions

### Assumptions
- ✅ Payroll export only (not final nómina file generation)
- ✅ Honor system clock-in (no biometric/GPS)
- ✅ CST standard surcharges (no custom union agreements for MVP)
- ✅ Neon Cloud available / or can self-host Postgres
- ✅ Team has Python + React + SQL experience

### Open Questions to Confirm

1. **Pilot Organization:** Which real company will be the first MVP user? (Helps validate payroll accuracy)
2. **Export Format:** CSV sufficient for MVP, or must support XML from day 1?
3. **Historical Data:** Is there legacy shift/payroll data to migrate?
4. **Timeline Pressure:** Fixed 3-month deadline or flexible?
5. **Legal Review:** Will DIAN or labor lawyer review payroll calculations?
6. **Go-Live Date:** Target launch date? (Affects resource planning)

---

## 9. Next Steps

### If This Proposal is APPROVED:

1. **Get Stakeholder Sign-Off** on scope, phases, and timeline
2. **Move to SDD Spec Phase** → Write detailed requirements
3. **Move to SDD Design Phase** → Database schema, API contracts
4. **Move to SDD Tasks Phase** → Sprint breakdown
5. **Begin Implementation (SDD Apply)** → Code!

### If Changes Needed:

1. Specify which features to move between phases
2. Clarify timeline constraints
3. Adjust team size / effort
4. We'll update proposal and re-review

---

## Summary

**Cronos MVP delivers:**
- ✅ Shift management for workers, managers, HR
- ✅ Accurate Colombian payroll calculations (CST compliance)
- ✅ CSV/XML export for HR nómina integration
- ✅ Multi-tenant foundation for future SaaS subscriptions
- ✅ Extensible architecture (Neon + FastAPI) for scaling

**Timeline:** 3-4 months (MVP)  
**Effort:** ~6-6.5 man-months  
**Go-Live Impact:** Eliminates manual shift scheduling, ensures labor law compliance, improves worker transparency

**Ready to proceed to Specification phase? ✅**

---

**Prepared by:** SDD Proposal Phase  
**Date:** 2026-04-16  
**Status:** Ready for Review
