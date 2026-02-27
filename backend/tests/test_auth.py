import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.user import User

pytestmark = pytest.mark.asyncio


async def test_register_user(async_client: AsyncClient, async_session: AsyncSession):
    """
    Test user registration via /auth/register endpoint.

    Verifies that:
    - A new user can be created through the registration endpoint
    - The response includes user data without the password
    - The user is persisted in the database
    """
    response = await async_client.post(
        "/auth/register",
        json={
            "email": "registration_test_user@test.com",
            "name": "Registration Test User",
            "password": "newpassword",
            "role": "officer",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "registration_test_user@test.com"
    assert data["name"] == "Registration Test User"
    assert "id" in data
    assert "password" not in data  # Password should never be returned
    assert data["role"] == "officer"

    # Verify the user was actually created in the database
    result = await async_session.execute(
        select(User).filter(User.email == "registration_test_user@test.com")
    )
    db_user = result.scalar_one_or_none()
    assert db_user is not None
    assert db_user.name == "Registration Test User"


async def test_login_for_access_token(async_client: AsyncClient, test_admin_user: User):
    """
    Test successful login via /auth/token endpoint.

    Verifies that:
    - Valid credentials return a JWT access token
    - Token type is "bearer"
    - Response follows OAuth2 token format
    """
    response = await async_client.post(
        "/auth/token",
        data={"username": "admin@test.com", "password": "adminpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(async_client: AsyncClient, test_admin_user: User):
    """
    Test login failure with incorrect password.

    Verifies that authentication fails (401 Unauthorized) when
    the email is correct but the password is wrong.
    """
    response = await async_client.post(
        "/auth/token",
        data={"username": "admin@test.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


async def test_login_wrong_username(async_client: AsyncClient, test_admin_user: User):
    """
    Test login failure with non-existent user.

    Verifies that authentication fails (401 Unauthorized) when
    attempting to login with an email that doesn't exist.
    """
    response = await async_client.post(
        "/auth/token",
        data={"username": "wronguser@test.com", "password": "adminpassword"},
    )
    assert response.status_code == 401


async def test_get_current_user(async_client: AsyncClient, admin_auth_headers: dict):
    """
    Test retrieving current user information via /auth/users/me.

    Verifies that:
    - An authenticated user can retrieve their own information
    - The correct user data is returned based on the JWT token
    - Password is not included in the response
    """
    response = await async_client.get("/auth/users/me", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@test.com"
    assert "password" not in data  # Password should never be returned


# ============================================================================
# DUPLICATE USER TESTS
# ============================================================================


async def test_register_duplicate_email_fails(
    async_client: AsyncClient, async_session: AsyncSession
):
    """
    Test that registering a user with an existing email fails.

    Verifies that:
    - First registration succeeds
    - Second registration with same email fails with 400
    - Error message indicates email is already registered
    """
    # First registration - should succeed
    response1 = await async_client.post(
        "/auth/register",
        json={
            "email": "duplicate_test_user@test.com",
            "name": "Duplicate Test First User",
            "password": "password123",
            "role": "officer",
        },
    )
    assert response1.status_code == 200

    # Second registration with same email - should fail
    response2 = await async_client.post(
        "/auth/register",
        json={
            "email": "duplicate_test_user@test.com",
            "name": "Duplicate Test Second User",
            "password": "password456",
            "role": "officer",
        },
    )
    assert response2.status_code == 400
    assert "already registered" in response2.json()["detail"].lower()


# ============================================================================
# PASSWORD VALIDATION TESTS
# ============================================================================


async def test_register_password_too_short(async_client: AsyncClient):
    """
    Test that registration fails with password shorter than 8 characters.

    Verifies that:
    - Password must be at least 8 characters
    - Returns 422 validation error
    """
    response = await async_client.post(
        "/auth/register",
        json={
            "email": "short_password_test@test.com",
            "name": "Short Password Test User",
            "password": "pass",  # Only 4 characters
            "role": "officer",
        },
    )
    assert response.status_code == 422
    errors = response.json()["detail"]
    # Check that there's a validation error for password field
    assert any("password" in str(error).lower() for error in errors)


async def test_register_password_minimum_length(async_client: AsyncClient):
    """
    Test that password with exactly 8 characters is accepted.

    Verifies that:
    - Minimum password length of 8 characters is enforced
    - Registration succeeds with valid 8-character password
    """
    response = await async_client.post(
        "/auth/register",
        json={
            "email": "min_password_test@test.com",
            "name": "Minimum Password Test User",
            "password": "pass1234",  # Exactly 8 characters
            "role": "officer",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "min_password_test@test.com"


# ============================================================================
# AUTHENTICATION FAILURE TESTS
# ============================================================================


async def test_access_protected_endpoint_without_token(async_client: AsyncClient):
    """
    Test that accessing protected endpoint without token fails.

    Verifies that:
    - Protected endpoints require authentication
    - Returns 401 Unauthorized without valid token
    """
    response = await async_client.get("/users/")
    assert response.status_code == 401


async def test_access_protected_endpoint_with_invalid_token(async_client: AsyncClient):
    """
    Test that accessing protected endpoint with invalid token fails.

    Verifies that:
    - Invalid JWT tokens are rejected
    - Returns 401 Unauthorized
    """
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = await async_client.get("/users/", headers=headers)
    assert response.status_code == 401
