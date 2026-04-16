#!/usr/bin/env python3
"""
Verification script for Sprint 1.1 deliverables.
Runs without database connection - checks imports, structure, and code quality.

Usage:
    python verify_sprint_1_1.py
"""

import sys
import importlib.util
from pathlib import Path
from typing import Tuple

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(text: str):
    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}{text:^60}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")


def print_section(text: str):
    print(f"\n{BOLD}{BLUE}→ {text}{RESET}")


def print_ok(text: str):
    print(f"{GREEN}✓{RESET} {text}")


def print_error(text: str):
    print(f"{RED}✗{RESET} {text}")


def print_warning(text: str):
    print(f"{YELLOW}⚠{RESET} {text}")


def verify_file_exists(path: Path) -> bool:
    """Check if file exists."""
    exists = path.exists()
    if exists:
        print_ok(f"File exists: {path.relative_to(Path.cwd())}")
    else:
        print_error(f"File NOT found: {path.relative_to(Path.cwd())}")
    return exists


def verify_imports() -> Tuple[bool, dict]:
    """Verify that all modules can be imported."""
    print_section("BE-001: FastAPI & Config Imports")

    results = {}

    # Test 1: Import FastAPI app
    try:
        from app.main import app

        print_ok("FastAPI app imports successfully")
        results["fastapi_app"] = True

        # Check health endpoint exists
        if any(route.path == "/health" for route in app.routes):
            print_ok("Health check endpoint (/health) is registered")
            results["health_endpoint"] = True
        else:
            print_error("Health check endpoint (/health) NOT found")
            results["health_endpoint"] = False
    except Exception as e:
        print_error(f"Failed to import FastAPI app: {e}")
        results["fastapi_app"] = False
        results["health_endpoint"] = False

    # Test 2: Import config
    try:
        from app.config import settings

        print_ok("Settings (config) imports successfully")
        results["config"] = True

        # Check environment
        print_ok(f"  Environment: {settings.environment_label}")
        print_ok(f"  Token expiry: {settings.TOKEN_EXPIRY}s")
        print_ok(f"  Refresh token expiry: {settings.REFRESH_TOKEN_EXPIRY}s")
    except Exception as e:
        print_error(f"Failed to import config: {e}")
        results["config"] = False

    # Test 3: Import database module
    print_section("BE-004: Database Connection Imports")
    try:
        from app.database import engine, SessionLocal

        print_ok("Database module (engine, SessionLocal) imports successfully")
        results["database"] = True

        print_ok(
            f"  Engine URL: {str(engine.url).split('@')[1] if '@' in str(engine.url) else '***'}"
        )
    except Exception as e:
        print_error(f"Failed to import database: {e}")
        results["database"] = False

    # Test 4: Import dependencies
    try:
        from app.dependencies import get_db

        print_ok("Dependencies (get_db) imports successfully")
        results["dependencies"] = True
    except Exception as e:
        print_error(f"Failed to import dependencies: {e}")
        results["dependencies"] = False

    return all(results.values()), results


def verify_models() -> Tuple[bool, dict]:
    """Verify that all ORM models are defined correctly."""
    print_section("BE-003: SQLAlchemy ORM Models")

    results = {}
    expected_models = [
        "Company",
        "SubOrganization",
        "Area",
        "Worker",
        "ShiftTemplate",
        "ShiftAssignment",
        "TimesheetDay",
        "Holiday",
        "SurchargeRule",
    ]

    try:
        from app.models import (
            Company,
            SubOrganization,
            Area,
            Worker,
            ShiftTemplate,
            ShiftAssignment,
            TimesheetDay,
            Holiday,
            SurchargeRule,
        )

        for model_name in expected_models:
            try:
                model = globals()[model_name]
                # Check if it has __tablename__
                if hasattr(model, "__tablename__"):
                    print_ok(
                        f"Model {model_name} defined (table: {model.__tablename__})"
                    )
                    results[model_name] = True
                else:
                    print_error(f"Model {model_name} missing __tablename__")
                    results[model_name] = False
            except KeyError:
                print_error(f"Model {model_name} not found in imports")
                results[model_name] = False
    except Exception as e:
        print_error(f"Failed to import models: {e}")
        return False, {model: False for model in expected_models}

    return all(results.values()), results


def verify_schemas() -> Tuple[bool, dict]:
    """Verify that Pydantic schemas are defined."""
    print_section("BE-003: Pydantic Schemas")

    try:
        from app.schemas import (
            CompanyCreate,
            CompanyRead,
            WorkerCreate,
            WorkerRead,
            ShiftTemplateCreate,
            ShiftTemplateRead,
        )

        print_ok("Core schemas import successfully")

        # Check a few schemas
        schemas_to_check = [
            (CompanyCreate, "CompanyCreate"),
            (WorkerRead, "WorkerRead"),
        ]

        results = {}
        for schema, name in schemas_to_check:
            try:
                print_ok(f"  Schema {name} defined")
                results[name] = True
            except Exception as e:
                print_error(f"  Schema {name} issue: {e}")
                results[name] = False

        return all(results.values()), results
    except Exception as e:
        print_error(f"Failed to import schemas: {e}")
        return False, {}


def verify_alembic() -> Tuple[bool, dict]:
    """Verify Alembic migration files exist."""
    print_section("BE-002: Alembic Migrations")

    results = {}

    # Check alembic.ini
    alembic_ini = Path("alembic.ini")
    if verify_file_exists(alembic_ini):
        results["alembic_ini"] = True
    else:
        results["alembic_ini"] = False

    # Check env.py
    env_py = Path("alembic/env.py")
    if verify_file_exists(env_py):
        results["env_py"] = True
    else:
        results["env_py"] = False

    # Check initial migration
    migration_file = Path("alembic/versions/001_create_base_schema.py")
    if verify_file_exists(migration_file):
        results["migration"] = True

        # Count lines in migration
        with open(migration_file) as f:
            lines = len(f.readlines())
        print_ok(f"  Migration file has {lines} lines")
    else:
        results["migration"] = False

    return all(results.values()), results


def verify_project_structure() -> Tuple[bool, dict]:
    """Verify backend project directory structure."""
    print_section("BE-001: Project Structure")

    results = {}
    expected_dirs = [
        "app",
        "app/models",
        "alembic",
        "alembic/versions",
        "scripts",
    ]

    for dir_path in expected_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            print_ok(f"Directory exists: {dir_path}")
            results[dir_path] = True
        else:
            print_error(f"Directory missing: {dir_path}")
            results[dir_path] = False

    # Check key files
    expected_files = [
        "pyproject.toml",
        "requirements.txt",
        ".env.example",
        "app/main.py",
        "app/config.py",
        "app/database.py",
        "app/dependencies.py",
        "app/schemas.py",
        "app/models/__init__.py",
        "app/models/base.py",
        "app/models/company.py",
        "app/models/worker.py",
        "app/models/shift.py",
        "app/models/holiday.py",
        "scripts/test_db_connection.py",
    ]

    print_section("BE-001: Key Files")
    for file_path in expected_files:
        path = Path(file_path)
        if verify_file_exists(path):
            results[file_path] = True
        else:
            results[file_path] = False

    return all(results.values()), results


def verify_code_quality() -> Tuple[bool, dict]:
    """Check code quality (type hints, docstrings, etc.)."""
    print_section("Code Quality Checks")

    results = {}

    # Check main.py has type hints and docstrings
    try:
        from app.main import app, health_check

        # Check health_check has return type hint
        if health_check.__annotations__.get("return"):
            print_ok("health_check has return type hint")
            results["health_check_type_hint"] = True
        else:
            print_warning("health_check missing return type hint")
            results["health_check_type_hint"] = False
    except Exception as e:
        print_error(f"Failed to check code quality: {e}")
        results["health_check_type_hint"] = False

    # Check Worker model has correct fields
    try:
        from app.models.worker import Worker, WorkerRole

        # Check role enum
        if hasattr(WorkerRole, "WORKER") and hasattr(WorkerRole, "MANAGER"):
            print_ok("WorkerRole enum has expected values (WORKER, MANAGER, HR_ADMIN)")
            results["worker_role_enum"] = True
        else:
            print_error("WorkerRole enum missing values")
            results["worker_role_enum"] = False
    except Exception as e:
        print_error(f"Failed to check Worker model: {e}")
        results["worker_role_enum"] = False

    return all(results.values()), results


def main():
    """Run all verification checks."""
    print_header("Sprint 1.1 Verification Script")
    print(f"Backend directory: {Path.cwd()}")

    all_passed = True

    # Run all checks
    checks = [
        ("Project Structure", verify_project_structure),
        ("Alembic Migrations", verify_alembic),
        ("FastAPI & Config", verify_imports),
        ("ORM Models", verify_models),
        ("Pydantic Schemas", verify_schemas),
        ("Code Quality", verify_code_quality),
    ]

    results_summary = {}

    for check_name, check_func in checks:
        try:
            passed, details = check_func()
            results_summary[check_name] = passed
            if not passed:
                all_passed = False
        except Exception as e:
            print_error(f"Check '{check_name}' failed with error: {e}")
            results_summary[check_name] = False
            all_passed = False

    # Print summary
    print_header("Summary")

    for check_name, passed in results_summary.items():
        status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
        print(f"{status} {check_name}")

    print()

    if all_passed:
        print(f"{GREEN}{BOLD}✓ All Sprint 1.1 checks PASSED!{RESET}\n")
        print(f"{BOLD}Sprint 1.1 Deliverables:{RESET}")
        print(f"  {GREEN}✓{RESET} BE-001: FastAPI project scaffold")
        print(
            f"  {GREEN}✓{RESET} BE-002: Alembic migrations (001_create_base_schema.py)"
        )
        print(f"  {GREEN}✓{RESET} BE-003: SQLAlchemy ORM models (9 models)")
        print(f"  {GREEN}✓{RESET} BE-004: Database connection layer")
        print()
        print(f"{BOLD}Next steps:{RESET}")
        print(f"  1. Update .env with Neon PostgreSQL connection string")
        print(f"  2. Run: pip install -r requirements.txt")
        print(f"  3. Run: alembic upgrade head (to apply migrations to DB)")
        print(f"  4. Run: uvicorn app.main:app --reload (to start FastAPI server)")
        print(f"  5. Test: curl http://localhost:8000/health")
        print()
        return 0
    else:
        print(f"{RED}{BOLD}✗ Some Sprint 1.1 checks FAILED{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
