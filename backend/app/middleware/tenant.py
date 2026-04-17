from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.auth.jwt import verify_token


class TenantMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self._excluded_prefixes = (
            "/auth/login",
            "/auth/refresh",
            "/auth/logout",
            "/docs",
            "/openapi.json",
            "/health",
        )

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        if request.url.path.startswith(self._excluded_prefixes):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "", 1).strip()

        if not token:
            return JSONResponse(status_code=401, content={"detail": "Missing token"})

        try:
            payload = verify_token(token)
        except Exception as exc:  # noqa: BLE001
            detail = getattr(exc, "detail", "Invalid token")
            status_code = getattr(exc, "status_code", 401)
            return JSONResponse(status_code=status_code, content={"detail": detail})

        request.state.company_id = payload.get("company_id")
        request.state.user_id = payload.get("sub")
        request.state.user_role = payload.get("role")

        if request.state.company_id is None or request.state.user_id is None:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})

        return await call_next(request)
