# Cronos - Shift Management System

Sistema web para la gestión de turnos de trabajo conforme a la legislación laboral colombiana.

## Descripción del Proyecto

**Cronos** es una aplicación integral para:
- **Trabajadores:** Visualizar sus turnos, horas extras, recargos, solicitar cambios
- **Gestores:** Asignar turnos, aprobar cambios, validar límites de horas
- **Recursos Humanos:** Exportar información de horas para nómina, generar reportes, auditoría

### Cumplimiento Legal

Basado en:
- Código Sustantivo del Trabajo (CST) colombiano
- Ley 2101/2021 (reforma laboral)
- Regulación de jornadas (48h → 42h progresivo 2024-2026)
- Recargos nocturnos, dominicales, festivos
- Horas extras y límites

## Tecnología

### Backend
- **Python 3.11+** con FastAPI
- **PostgreSQL** para persistencia
- **SQLAlchemy 2.0** (ORM)
- **Celery + Redis** para tareas asincrónicas
- **pytest** para testing

### Frontend
- **TypeScript + React 18+**
- **Vite** como bundler
- **Tailwind CSS + shadcn/ui**
- **Zustand** para state management
- **Vitest + React Testing Library**

### DevOps
- **Docker & Docker Compose**
- **Alembic** para migraciones de BD
- **Git** + GitHub

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
