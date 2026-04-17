from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from app.auth.password import verify_password
from app.dependencies import get_db
from app.models.worker import Worker, WorkerRole

router = APIRouter()


def _problem_response(
    status_code: int,
    title: str,
    detail: str,
    instance: str,
    type_url: str = "about:blank",
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        media_type="application/problem+json",
        content={
            "type": type_url,
            "title": title,
            "status": status_code,
            "detail": detail,
            "instance": instance,
        },
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginUser(BaseModel):
    id: UUID
    email: EmailStr | None
    role: str
    company_id: UUID


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: LoginUser


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=16)


class RefreshResponse(BaseModel):
    access_token: str
    user_id: UUID


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_db)) -> Any:
    result = await session.execute(
        select(Worker).where(Worker.email == str(payload.email))
    )
    worker = result.scalars().first()

    if worker is None:
        return _problem_response(
            status_code=401,
            title="Unauthorized",
            detail="Invalid credentials",
            instance="/auth/login",
        )

    if not verify_password(payload.password, worker.password_hash):
        return _problem_response(
            status_code=401,
            title="Unauthorized",
            detail="Invalid credentials",
            instance="/auth/login",
        )

    role = (
        worker.role.value if isinstance(worker.role, WorkerRole) else str(worker.role)
    )
    access_token = create_access_token(
        user_id=worker.id,
        company_id=worker.company_id,
        role=role,
    )
    refresh_token = create_refresh_token(user_id=worker.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": worker.id,
            "email": worker.email,
            "role": role,
            "company_id": worker.company_id,
        },
    }


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    payload: RefreshRequest,
    session: AsyncSession = Depends(get_db),
) -> Any:
    decoded = verify_refresh_token(payload.refresh_token)
    try:
        user_id = UUID(str(decoded["sub"]))
    except (KeyError, ValueError):
        return _problem_response(
            status_code=401,
            title="Unauthorized",
            detail="Invalid refresh token",
            instance="/auth/refresh",
        )

    result = await session.execute(select(Worker).where(Worker.id == user_id))
    worker = result.scalars().first()
    if worker is None:
        return _problem_response(
            status_code=401,
            title="Unauthorized",
            detail="Invalid refresh token",
            instance="/auth/refresh",
        )

    role = (
        worker.role.value if isinstance(worker.role, WorkerRole) else str(worker.role)
    )
    access_token = create_access_token(worker.id, worker.company_id, role)
    return {"access_token": access_token, "user_id": worker.id}


@router.post("/logout")
async def logout() -> dict[str, str]:
    return {"message": "Logged out successfully"}
