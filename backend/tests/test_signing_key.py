import os
import secrets
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import jwt
import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from starlette.requests import Request

from src.config import Settings, settings
from src.database import get_db_session
from src.dependencies import create_access_token, get_user_id
from src.main import app
from src.models.user import User


@pytest.mark.parametrize("key", ["", "SECRET_KEY", "x" * 31, " " * 32, " " + "x" * 32, "x" * 32, "your-secure-secret-key-here-replace-this"])
def test_rejects_invalid_signing_keys(monkeypatch, key):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(ValidationError) as error:
        Settings(SECRET_KEY=key, _env_file=None)
    if key and key != "SECRET_KEY":
        assert key not in str(error.value)


def test_signing_key_loaded_from_environment(monkeypatch):
    key = secrets.token_urlsafe(32)
    monkeypatch.setenv("SECRET_KEY", key)
    assert Settings(_env_file=None).SECRET_KEY == key


def test_accepts_32_byte_signing_key(monkeypatch):
    key = secrets.token_urlsafe(24)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    assert len(key.encode("utf-8")) == 32
    assert Settings(SECRET_KEY=key, _env_file=None).SECRET_KEY == key


def test_signing_key_loaded_from_dotenv(monkeypatch, tmp_path):
    key = secrets.token_urlsafe(32)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(f"SECRET_KEY={key}\n")
    assert Settings(_env_file=env_file).SECRET_KEY == key


def test_missing_signing_key_prevents_startup(tmp_path):
    env = os.environ.copy()
    env.pop("SECRET_KEY", None)
    env["PYTHONPATH"] = os.getcwd()
    result = subprocess.run(
        [sys.executable, "-c", "import src.config"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "SECRET_KEY" in result.stderr


def test_signing_key_is_not_in_settings_repr():
    key = secrets.token_urlsafe(32)
    assert key not in repr(Settings(SECRET_KEY=key, _env_file=None))


def test_access_token_default_lifetime_is_30_minutes(monkeypatch):
    monkeypatch.delenv("ACCESS_TOKEN_EXPIRE_MINUTES", raising=False)
    assert Settings(_env_file=None).ACCESS_TOKEN_EXPIRE_MINUTES == 30
    monkeypatch.setattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    before = datetime.now(timezone.utc).timestamp()
    token = create_access_token({"sub": "123"})
    after = datetime.now(timezone.utc).timestamp()
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert before + 1799 <= payload["exp"] <= after + 1800


@pytest.mark.parametrize("minutes", [0, -1, 31])
def test_rejects_invalid_access_token_lifetimes(monkeypatch, minutes):
    monkeypatch.delenv("ACCESS_TOKEN_EXPIRE_MINUTES", raising=False)
    with pytest.raises(ValidationError):
        Settings(ACCESS_TOKEN_EXPIRE_MINUTES=minutes, _env_file=None)


@pytest.mark.parametrize("minutes", [0, -1, 31])
def test_rejects_invalid_custom_token_lifetimes(monkeypatch, minutes):
    monkeypatch.setattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    with pytest.raises(ValueError):
        create_access_token({"sub": "123"}, expires_delta=timedelta(minutes=minutes))


def test_accepts_shorter_custom_token_lifetime(monkeypatch):
    monkeypatch.setattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    before = datetime.now(timezone.utc).timestamp()
    token = create_access_token({"sub": "123"}, expires_delta=timedelta(minutes=5))
    after = datetime.now(timezone.utc).timestamp()
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert before + 299 <= payload["exp"] <= after + 300


def test_rate_limit_identity_rejects_token_without_expiry():
    token = jwt.encode({"sub": "123"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    request = Request({"type": "http", "headers": [(b"authorization", f"Bearer {token}".encode())], "client": ("192.0.2.1", 1234)})
    assert get_user_id(request) == "192.0.2.1"


async def test_placeholder_signed_token_cannot_impersonate_admin(monkeypatch):
    admin = User(id=123, name="Test Admin", email="admin@example.com", role="admin", hashed_password="unused", is_approved=True)
    result = MagicMock()
    result.scalar_one_or_none.return_value = admin
    db = AsyncMock()
    db.execute.return_value = result

    async def override_db():
        yield db

    monkeypatch.setattr("src.routers.user.user_service.list_pending_users", AsyncMock(return_value=[]))
    monkeypatch.setattr("src.routers.auth.authentication_service.authenticate_user", AsyncMock(return_value=admin))
    app.dependency_overrides[get_db_session] = override_db
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            forged = jwt.encode(
                {"sub": str(admin.id), "exp": datetime.now(timezone.utc) + timedelta(minutes=10)},
                "SECRET_KEY",
                algorithm="HS256",
            )
            response = await client.get("/users/pending", headers={"Authorization": f"Bearer {forged}"})
            assert response.status_code == 401
            db.execute.assert_not_awaited()

            login = await client.post("/auth/token", data={"username": admin.email, "password": "test-password"})
            assert login.status_code == 200
            valid = login.json()["access_token"]
            response = await client.get("/users/pending", headers={"Authorization": f"Bearer {valid}"})
            assert response.status_code == 200
    finally:
        app.dependency_overrides.pop(get_db_session, None)


async def test_key_rotation_and_invalid_expiry_reject_admin_tokens(monkeypatch):
    old_key = secrets.token_urlsafe(32)
    new_key = secrets.token_urlsafe(32)
    wrong_key = secrets.token_urlsafe(32)
    admin = User(id=123, name="Test Admin", email="admin@example.com", role="admin", hashed_password="unused")
    result = MagicMock()
    result.scalar_one_or_none.return_value = admin
    db = AsyncMock()
    db.execute.return_value = result

    async def override_db():
        yield db

    monkeypatch.setattr("src.routers.user.user_service.list_pending_users", AsyncMock(return_value=[]))
    monkeypatch.setattr(settings, "SECRET_KEY", old_key)
    old_token = create_access_token({"sub": str(admin.id)})
    monkeypatch.setattr(settings, "SECRET_KEY", new_key)
    expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
    wrong_token = jwt.encode({"sub": str(admin.id), "exp": expiry}, wrong_key, algorithm=settings.ALGORITHM)
    no_expiry = jwt.encode({"sub": str(admin.id)}, new_key, algorithm=settings.ALGORITHM)
    expired = jwt.encode({"sub": str(admin.id), "exp": datetime.now(timezone.utc) - timedelta(seconds=1)}, new_key, algorithm=settings.ALGORITHM)
    current_token = create_access_token({"sub": str(admin.id)})
    app.dependency_overrides[get_db_session] = override_db
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            for token in (old_token, wrong_token, no_expiry, expired):
                response = await client.get("/users/pending", headers={"Authorization": f"Bearer {token}"})
                assert response.status_code == 401
            db.execute.assert_not_awaited()
            response = await client.get("/users/pending", headers={"Authorization": f"Bearer {current_token}"})
            assert response.status_code == 200
    finally:
        app.dependency_overrides.pop(get_db_session, None)
