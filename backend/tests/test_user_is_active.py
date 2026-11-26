"""Tests for the user is_active flag (deactivated accounts)."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User

pytestmark = pytest.mark.asyncio


async def test_new_users_default_to_active(test_admin_user: User):
    assert test_admin_user.is_active is True


async def test_active_user_can_log_in(async_client: AsyncClient, test_admin_user: User):
    response = await async_client.post(
        "/auth/token",
        data={"username": "admin@test.com", "password": "adminpassword"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_inactive_user_cannot_log_in(async_client: AsyncClient, async_session: AsyncSession, test_admin_user: User):
    test_admin_user.is_active = False
    await async_session.flush()

    response = await async_client.post(
        "/auth/token",
        data={"username": "admin@test.com", "password": "adminpassword"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Your account has been deactivated."


async def test_inactive_user_with_wrong_password_gets_generic_401(async_client: AsyncClient, async_session: AsyncSession, test_admin_user: User):
    """The deactivated status is only revealed after the password is verified."""
    test_admin_user.is_active = False
    await async_session.flush()

    response = await async_client.post(
        "/auth/token",
        data={"username": "admin@test.com", "password": "not-the-password"},
    )
    assert response.status_code == 401


async def test_existing_token_stops_working_after_deactivation(async_client: AsyncClient, async_session: AsyncSession, test_admin_user: User, admin_auth_headers: dict):
    before = await async_client.get("/auth/users/me", headers=admin_auth_headers)
    assert before.status_code == 200

    test_admin_user.is_active = False
    await async_session.flush()

    after = await async_client.get("/auth/users/me", headers=admin_auth_headers)
    assert after.status_code == 401


async def test_reactivated_user_token_works_again(async_client: AsyncClient, async_session: AsyncSession, test_admin_user: User, admin_auth_headers: dict):
    test_admin_user.is_active = False
    await async_session.flush()
    assert (await async_client.get("/auth/users/me", headers=admin_auth_headers)).status_code == 401

    test_admin_user.is_active = True
    await async_session.flush()
    assert (await async_client.get("/auth/users/me", headers=admin_auth_headers)).status_code == 200


async def test_users_me_exposes_is_active(async_client: AsyncClient, admin_auth_headers: dict):
    response = await async_client.get("/auth/users/me", headers=admin_auth_headers)
    assert response.status_code == 200
    assert response.json()["is_active"] is True
