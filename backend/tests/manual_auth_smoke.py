"""Manual smoke checks for Sprint 1.2 auth/middleware/RBAC.

Run manually once backend is up:
    uvicorn app.main:app --reload
    python tests/manual_auth_smoke.py
"""

from __future__ import annotations

import json

import httpx


BASE_URL = "http://localhost:8000"


def pretty(resp: httpx.Response) -> str:
    try:
        payload = resp.json()
    except Exception:  # noqa: BLE001
        payload = {"raw": resp.text}
    return json.dumps({"status": resp.status_code, "body": payload}, indent=2)


def run() -> None:
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        health = client.get("/health")
        print("Health:\n", pretty(health))

        unauthorized = client.get("/auth/rbac-example")
        print("RBAC without token (expect 401):\n", pretty(unauthorized))

        login = client.post(
            "/auth/login",
            json={"email": "admin@example.com", "password": "wrong-password"},
        )
        print("Login with wrong creds (expect 401/problem+json):\n", pretty(login))

        refresh = client.post("/auth/refresh", json={"refresh_token": "invalid-token"})
        print("Refresh with invalid token (expect 401):\n", pretty(refresh))

        logout = client.post("/auth/logout")
        print("Logout (expect 200):\n", pretty(logout))


if __name__ == "__main__":
    run()
