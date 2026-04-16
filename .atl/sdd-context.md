# Cronos - SDD Context & Project Setup

## Project Overview
**Name:** Cronos  
**Goal:** Web application for Colombian labor law-compliant worker shift management  
**Primary Users:** Workers, Managers, HR Teams  
**Compliance:** Colombian Código Sustantivo del Trabajo (CST) & Ley 2101/2021  

## Tech Stack

### Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI (async, modern, good for real-time notifications)
- **Database:** PostgreSQL (JSON support for flexible configurations, compliance with Colombian law transitions)
- **ORM:** SQLAlchemy 2.0+
- **Testing:** pytest with pytest-asyncio
- **API Documentation:** OpenAPI/Swagger (built into FastAPI)

### Frontend
- **Language:** TypeScript
- **Framework:** React 18+ (component-based, strong ecosystem)
- **State Management:** Zustand (lightweight, complements Python backend)
- **Styling:** Tailwind CSS + shadcn/ui (accessible components)
- **Build Tool:** Vite (fast, modern bundler)
- **Testing:** Vitest + React Testing Library
- **HTTP Client:** axios or fetch API

### Infrastructure & DevOps
- **Database Migrations:** Alembic (Python)
- **Environment:** Docker & Docker Compose (for consistency)
- **Task Queue:** Celery + Redis (for async payroll calculations, notifications)
- **API Gateway:** nginx or uvicorn directly
- **Logging:** Python logging + structured logs (JSON)
- **Authentication:** JWT tokens (FastAPI middleware)

### Development Tools
- **Version Control:** Git + GitHub
- **Code Quality:** Black, flake8, mypy (Python); ESLint, Prettier (TypeScript)
- **Secrets Management:** python-dotenv (.env files for local dev)
- **Documentation:** MkDocs or Sphinx for API docs

## Domain Model (Colombian Labor Law Constraints)

### Core Entities
1. **Worker** - Individual employee with contract type (standard 48h/week or 36h shifts)
2. **ShiftTemplate** - Recurring shift patterns (e.g., "Morning 6am-2pm")
3. **ShiftAssignment** - Specific shift instance assigned to a worker on a date
4. **ShiftSwapRequest** - Workflow for workers to trade shifts (requires manager approval)
5. **TimesheetDay** - Calculated payroll line item per worker per day (regular hrs, night hrs, overtime, surcharges)
6. **HolidayCalendar** - Colombian public holidays (18+) triggering 75% surcharge
7. **Company** - Multi-tenant support (each company has its own workers, shifts, policies)
8. **SurchargeRule** - Configurable surcharge % by type (night 35%, Sunday 75%, etc.) to handle labor law changes

### Key Business Rules

| Rule | Details |
|------|---------|
| **Workweek Hours** | 46h in 2024, 44h in July 2025, 42h in 2026 (auto-adjusting baseline) |
| **Day Hours** | 6:00 AM - 9:00 PM (may change to 7:00 PM per pending reform) |
| **Night Hours** | 9:00 PM - 6:00 AM (35% surcharge, 75% on Sundays = 110% total) |
| **Overtime Limits** | Max 2 hrs/day, 12 hrs/week. System must block or warn. |
| **Sunday/Holiday** | 75% surcharge; if 3+ Sundays/month = habitual (entitled to compensatory day OFF + surcharge) |
| **Midnight Rule** | Shifts crossing midnight change hour type at 00:00 (e.g., Sat 8pm→Sun 4am = mixed surcharge types) |
| **Rest Periods** | Warn if < 11 hours rest between shifts (labor law minimum) |

## Development Phases (SDD-aligned)

1. **Exploration** ✅ - Understand Colombian labor domain, regulations, constraints
2. **Proposal** - Define feature MVP and phased rollout
3. **Specification** - Document requirements, API contracts, workflows
4. **Design** - Architecture decisions, payroll calculation engine, database schema
5. **Tasks** - Break into implementation sprints
6. **Apply** - Build backend, frontend, tests
7. **Verify** - Validate against specs and Colombian law compliance
8. **Archive** - Release & document decisions

## Critical Questions (To Be Clarified)

- [ ] **Payroll Integration:** Generate final payroll file or export categorized hours (Novedades) for external software?
- [ ] **Clock-In Mechanism:** Biometrics, GPS, mobile, or manual HR entry?
- [ ] **Grace Periods:** How to handle early/late arrivals (auto-overtime or manager approval)?
- [ ] **Union Agreements:** Custom surcharge % per company or standard CST only?
- [ ] **Multi-Tenancy:** Single company or SaaS for multiple organizations?

## Git & Development Workflow

- **Main Branch:** `main` - production-ready code
- **Feature Branches:** `feature/shift-assignment`, `feature/payroll-engine`, etc.
- **PR Requirements:** Code review + tests must pass before merge
- **Commit Style:** Conventional commits (`feat:`, `fix:`, `docs:`, etc.)

## Testing Strategy

- **Unit Tests:** Business logic (surcharge calculations, validations)
- **Integration Tests:** API endpoints + database interactions
- **E2E Tests:** User workflows (shift assignment, swap requests, analytics export)
- **Colombian Law Edge Cases:** Midnight crossings, habitual Sundays, workweek reductions, overtime limits

## Artifact Store
- **Mode:** engram (persistent memory across sessions)
- **Status:** Initialized for `cronos` project
- **Change Tracking:** Each feature/bug tracked via engram topic_key pattern

---

**Created:** 2026-04-16  
**Updated by SDD Init Phase**
