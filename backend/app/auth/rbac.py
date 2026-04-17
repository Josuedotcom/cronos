from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status


def get_user_role(request: Request) -> str:
    role = getattr(request.state, "user_role", None)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User role not available",
        )
    return str(role)


def require_role(*roles: str) -> Callable[[str], str]:
    allowed_roles = {role.lower() for role in roles}

    def role_checker(user_role: str = Depends(get_user_role)) -> str:
        if user_role.lower() not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user_role

    return role_checker
