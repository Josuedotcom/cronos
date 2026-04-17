from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from fastapi import HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError

from app.config import settings

ALGORITHM = "HS256"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(user_id: UUID, company_id: UUID, role: str) -> str:
    issued_at = _now_utc()
    expires_at = issued_at + timedelta(seconds=settings.TOKEN_EXPIRY)

    payload = {
        "sub": str(user_id),
        "company_id": str(company_id),
        "role": role,
        "iat": issued_at,
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    issued_at = _now_utc()
    expires_at = issued_at + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRY)

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": issued_at,
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        ) from exc
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc


def verify_refresh_token(token: str) -> dict:
    payload = verify_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    return payload
