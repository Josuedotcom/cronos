# Cronos Backend

FastAPI backend for Cronos MVP.

## Requirements

- Python 3.11+
- PostgreSQL 14+

## Setup (Poetry)

```bash
cd backend
poetry install
copy .env.example .env
poetry run uvicorn app.main:app --reload
```

## Setup (pip)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e .
copy .env.example .env
uvicorn app.main:app --reload
```

## Health Check

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "environment": "development"
}
```
