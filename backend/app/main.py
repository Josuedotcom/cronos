from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


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


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "environment": settings.environment_label,
    }
