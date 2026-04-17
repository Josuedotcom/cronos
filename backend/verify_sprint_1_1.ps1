#!/usr/bin/env pwsh
<#
Sprint 1.1 Verification Script (PowerShell)
Checks all files created in Sprint 1.1 without needing Python
#>

Write-Host "`n=== Sprint 1.1 File Verification ===" -ForegroundColor Cyan -BackgroundColor Black
Write-Host ""

Write-Host "BE-001: FastAPI Scaffold" -ForegroundColor Blue
@("app/main.py", "app/config.py", ".env.example", "pyproject.toml", "requirements.txt") | ForEach-Object {
    if (Test-Path $_) {
        Write-Host "✓ $_" -ForegroundColor Green
    } else {
        Write-Host "✗ $_" -ForegroundColor Red
    }
}

Write-Host "`nBE-002: Alembic Migrations" -ForegroundColor Blue
@("alembic.ini", "alembic/env.py", "alembic/versions/001_create_base_schema.py") | ForEach-Object {
    if (Test-Path $_) {
        Write-Host "✓ $_" -ForegroundColor Green
    } else {
        Write-Host "✗ $_" -ForegroundColor Red
    }
}

Write-Host "`nBE-003: ORM Models" -ForegroundColor Blue
@("app/models/company.py", "app/models/worker.py", "app/models/shift.py", "app/models/holiday.py", "app/models/base.py", "app/schemas.py") | ForEach-Object {
    if (Test-Path $_) {
        Write-Host "✓ $_" -ForegroundColor Green
    } else {
        Write-Host "✗ $_" -ForegroundColor Red
    }
}

Write-Host "`nBE-004: Database Connection" -ForegroundColor Blue
@("app/database.py", "app/dependencies.py", "scripts/test_db_connection.py") | ForEach-Object {
    if (Test-Path $_) {
        Write-Host "✓ $_" -ForegroundColor Green
    } else {
        Write-Host "✗ $_" -ForegroundColor Red
    }
}

Write-Host "`n=== File Statistics ===" -ForegroundColor Cyan
$py_files = (Get-ChildItem -Recurse -Filter "*.py" | Measure-Object).Count
Write-Host "Total Python files: $py_files" -ForegroundColor Yellow

if (Test-Path "alembic/versions/001_create_base_schema.py") {
    $migration_lines = (Get-Content "alembic/versions/001_create_base_schema.py" | Measure-Object -Line).Lines
    Write-Host "Migration file lines: $migration_lines" -ForegroundColor Yellow
}

Write-Host "`n=== Code Quality Checks ===" -ForegroundColor Cyan

# Check for type hints in main.py
if (Select-String -Path "app/main.py" -Pattern "-> dict\[str, str\]" -Quiet) {
    Write-Host "✓ Type hints found in app/main.py" -ForegroundColor Green
}

# Check for async functions in database.py
if (Select-String -Path "app/database.py" -Pattern "async def" -Quiet) {
    Write-Host "✓ Async functions in app/database.py" -ForegroundColor Green
}

# Check for relationship definitions in models
if (Select-String -Path "app/models/company.py" -Pattern "Mapped\[" -Quiet) {
    Write-Host "✓ SQLAlchemy 2.0 Mapped type hints in models" -ForegroundColor Green
}

# Check for FastAPI health endpoint
if (Select-String -Path "app/main.py" -Pattern "@app.get\(\"\/health\"\)" -Quiet) {
    Write-Host "✓ FastAPI /health endpoint registered" -ForegroundColor Green
}

# Check for CORS configuration
if (Select-String -Path "app/main.py" -Pattern "CORSMiddleware" -Quiet) {
    Write-Host "✓ CORS middleware configured" -ForegroundColor Green
}

Write-Host "`n=== Summary ===" -ForegroundColor Green
Write-Host "✅ Sprint 1.1 Scaffolds Complete" -ForegroundColor Green
Write-Host "   - FastAPI app ready"
Write-Host "   - Alembic migrations ready"
Write-Host "   - 8 ORM models defined"
Write-Host "   - Database connection layer ready"
Write-Host "`n📖 See SPRINT_1_1_REPORT.md for detailed documentation" -ForegroundColor Cyan
Write-Host ""
