from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends

from app.auth.rbac import require_role
from app.config import settings
from app.middleware.tenant import TenantMiddleware
from app.routers import auth, shifts, holidays, payroll


app = FastAPI(
    title="Cronos API",
    description="Colombian labor law-compliant shift and payroll backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.CORS_LOCAL_ORIGIN,
        settings.CORS_DEV_ORIGIN,
        settings.BACKEND_URL,
    ],
    allow_origin_regex=settings.CORS_VERCEL_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TenantMiddleware)

app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(shifts.router)
app.include_router(holidays.router)
app.include_router(payroll.router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "environment": settings.environment_label,
    }


@app.get("/auth/rbac-example")
async def rbac_example(
    _: str = Depends(require_role("manager", "hr_admin")),
) -> dict[str, str]:
    return {"message": "You have sufficient permissions."}
