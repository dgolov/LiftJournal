"""Tests for /api/auth router."""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException


async def test_register_success(client):
    token_out = {"access_token": "tok", "token_type": "bearer", "user_id": 1, "name": "Alice"}

    with patch("app.api.routers.auth.AuthService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.register.return_value = type("T", (), token_out)()

        resp = await client.post("/api/auth/register", json={
            "email": "alice@test.com", "password": "pass123", "name": "Alice"
        })

    assert resp.status_code == 201
    svc.register.assert_called_once_with("alice@test.com", "pass123", "Alice")


async def test_register_duplicate_email_returns_400(client):
    with patch("app.api.routers.auth.AuthService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.register.side_effect = HTTPException(status_code=400, detail="Email уже зарегистрирован")

        resp = await client.post("/api/auth/register", json={
            "email": "dup@test.com", "password": "pass", "name": "User"
        })

    assert resp.status_code == 400


async def test_login_success(client):
    token_out = {"access_token": "tok", "token_type": "bearer", "user_id": 1, "name": "Alice"}

    with patch("app.api.routers.auth.AuthService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.login.return_value = type("T", (), token_out)()

        resp = await client.post("/api/auth/login", json={
            "email": "alice@test.com", "password": "pass123"
        })

    assert resp.status_code == 200
    svc.login.assert_called_once_with("alice@test.com", "pass123")


async def test_login_wrong_credentials_returns_401(client):
    with patch("app.api.routers.auth.AuthService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.login.side_effect = HTTPException(status_code=401, detail="Неверный email или пароль")

        resp = await client.post("/api/auth/login", json={
            "email": "x@x.com", "password": "wrong"
        })

    assert resp.status_code == 401


async def test_register_missing_fields_returns_422(client):
    resp = await client.post("/api/auth/register", json={"email": "x@x.com"})
    assert resp.status_code == 422


async def test_login_missing_fields_returns_422(client):
    resp = await client.post("/api/auth/login", json={"email": "x@x.com"})
    assert resp.status_code == 422


async def test_health_endpoint(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
