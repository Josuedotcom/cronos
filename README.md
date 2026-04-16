# Cronos - Shift Management System

Sistema web para la gestión de turnos de trabajo conforme a la legislación laboral colombiana.

## Descripción del Proyecto

**Cronos** es una aplicación integral para:
- **Trabajadores:** Visualizar sus turnos, horas extras, recargos, solicitar cambios
- **Gestores:** Asignar turnos, aprobar cambios, validar límites de horas
- **Recursos Humanos:** Exportar información de horas para nómina, generar reportes, auditoría

### Decisiones Arquitectónicas Clave

### 1. Backend: Neon + FastAPI (No Supabase)

**¿Por qué Neon en lugar de Supabase?**
- Supabase es excelente para apps CRUD, pero NO para lógica de nómina compleja
- La ley laboral colombiana requiere cálculos complejos en Python (testeable, auditable)
- PL/pgSQL o TypeScript Edge Functions se vuelven unmaintainables
- Python + pytest es superior para cambios de ley frecuentes (2024-2026)

**Ventajas:**
- ✅ Neon es solo PostgreSQL → cero vendor lock-in
- ✅ Auto-scaling + branching para staging seguro
- ✅ Puedes auto-hospedar cuando quieras (Docker o AWS RDS)

Ver `.atl/backend-decision.md` para análisis completo.

### 2. Multi-Tenancy: Company → SubOrganization → Area

```
Company (Empresa)
├── SubOrganization (Sucursal/División)
│   ├── Area 1 (Recursos, Operaciones)
│   │   ├── Shift Template: "T" (Tarde 2pm-10pm)
│   │   ├── Shift Template: "N" (Noche 10pm-6am)
│   │   └── Workers + Assignments
│   └── Area 2 (Logística)
│       ├── Shift Template: "M" (Mañana 6am-2pm)
│       └── Workers + Assignments
```

**Implementación MVP:** ORM layer (simple)  
**Post-MVP:** PostgreSQL RLS (seguridad de base de datos)

### 3. Motor de Nómina: Python (No SQL)

**Ubicación:** `backend/app/services/payroll_engine.py`

**Lógica** (Código Sustantivo del Trabajo colombiano):
- Clasificación de horas (ordinarias, nocturnas, dominicales, festivas)
- Recargos: Noche 35%, Domingo 75%, Noche+Domingo 110%
- Horas extras: Día 25%, Noche 75%, Domingo Día 100%, Domingo Noche 150%
- Límites: Max 2h/día, 12h/semana
- Regla de medianoche (turnos que cruzan 00:00)
- Dominical habitual (3+ domingos/mes)
- Workweek variable (48h→46h→44h→42h, 2024-2026)

**Testing:** Cobertura exhaustiva de edge cases con pytest

### 4. Exportes: CSV/XML con cedula + rubros

**No generamos nómina final**, solo categorías de horas:
- Worker cedula + name
- Horas ordinarias, nocturnas, extras, recargos (por tipo)
- Importables a Siigo, Novasoft, SAP, etc.

**Formato MVP:** CSV  
**Post-MVP:** XML, reportes avanzados, descarga programada



## Tecnología

### Backend
- **Python 3.11+** con FastAPI
- **PostgreSQL 14+** via **Neon** (serverless, auto-scaling)
  - Opción de auto-hospedar: Docker o AWS RDS (cero vendor lock-in)
- **SQLAlchemy 2.0** (ORM) con soporte multi-tenant
- **pytest** para testing (casos borde de ley laboral colombiana)
- **Pandas + csv/xml** para generación de exportes

### Frontend
- **TypeScript + React 18+**
- **Vite** como bundler
- **Tailwind CSS + shadcn/ui**
- **Zustand** para state management
- **Vitest + React Testing Library**

### DevOps & Deployment
- **Neon CLI** para gestión de base de datos (cloud)
- **Docker & Docker Compose** para desarrollo local
- **Alembic** para migraciones de BD
- **Git** + GitHub para versionamiento
- **Deployment:** ECS, Render, o Cloud Run (contenedores auto-escalables)

## Estructura del Proyecto

```
cronos/
├── .atl/                    # SDD artifacts
│   ├── sdd-context.md       # Project overview
│   ├── domain-model.md      # Data model & schema
│   └── clarification-questions.md
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routes/          # API endpoints
│   │   └── services/        # Business logic
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── stores/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Inicio Rápido

### Requisitos
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (recomendado)
- PostgreSQL 14+ (o usar docker-compose)

### Setup Local (Sin Docker)

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m alembic upgrade head  # Migraciones
python -m uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Setup con Docker
```bash
docker-compose up -d
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

## Fases de Desarrollo (SDD)

- [ ] **Exploration** ✅ - Dominio colombiano, requisitos legales
- [ ] **Proposal** - MVP scope y fases
- [ ] **Specification** - Requerimientos detallados
- [ ] **Design** - Arquitectura y decisiones clave
- [ ] **Tasks** - Desglose de implementación
- [ ] **Apply** - Desarrollo
- [ ] **Verify** - Validación y testing
- [ ] **Archive** - Documentación final

## Preguntas Pendientes

Ver `.atl/clarification-questions.md` para detalles. Se necesita clarificación en:

1. Integración de nómina (archivo vs solo horas)
2. Mecanismo de reloj (biométrico, GPS, manual)
3. Tolerancia de entrada/salida
4. Pactos colectivos
5. Turnos sucesivos (36h)
6. Dominical compensatorio vs surcharge
7. Multi-tenancy
8. Reportes específicos
9. Autenticación (local vs SSO)
10. Movilidad (web vs app)
11. Notificaciones (real-time)
12. Migración de históricos

## Contribución

1. Crear rama feature: `git checkout -b feature/nombre-feature`
2. Commit con mensaje convencional: `git commit -m "feat: descripción"`
3. Push: `git push origin feature/nombre-feature`
4. Abrir PR
5. Esperar code review y tests

## Licencia

Pendiente (definir con stakeholders)

## Contacto

Para preguntas sobre el proyecto, contactar al equipo de desarrollo.

---

**Proyecto Iniciado:** 2026-04-16  
**Stack:** Python + TypeScript  
**Compliance:** Colombian Labor Law (CST + Ley 2101/2021)
