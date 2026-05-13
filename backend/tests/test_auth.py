from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.auth_token import AuthToken
from src.models.user import User
from src.services.authentication import create_auth_token, hash_token
from src.utils.security import get_password_hash, verify_password

pytestmark = pytest.mark.asyncio


async def test_register_user(async_client: AsyncClient, async_session: AsyncSession):
    """Test user registration via /auth/register endpoint.

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
            "password": "Password1!",
            "role": "officer",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User registered. Verification email sent."

    # Verify the user was actually created in the database
    result = await async_session.execute(select(User).filter(User.email == "registration_test_user@test.com"))
    db_user = result.scalar_one_or_none()
    assert db_user is not None
    assert db_user.name == "Registration Test User"
    assert db_user.email == "registration_test_user@test.com"
    assert db_user.is_verified is False


async def test_login_for_access_token(async_client: AsyncClient, test_admin_user: User):
    """Test successful login via /auth/token endpoint.

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
    """Test login failure with incorrect password.

    Verifies that authentication fails (401 Unauthorized) when
    the email is correct but the password is wrong.
    """
    response = await async_client.post(
        "/auth/token",
        data={"username": "admin@test.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


async def test_login_wrong_username(async_client: AsyncClient, test_admin_user: User):
    """Test login failure with non-existent user.

    Verifies that authentication fails (401 Unauthorized) when
    attempting to login with an email that doesn't exist.
    """
    response = await async_client.post(
        "/auth/token",
        data={"username": "wronguser@test.com", "password": "adminpassword"},
    )
    assert response.status_code == 401


async def test_login_unverified_correct_password_returns_403(
    async_client: AsyncClient,
    async_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
):
    sent_emails = []

    async def mock_send_email(
        recipient: str | None = None,
        subject: str = "",
        body: str | None = None,
        html_body: str | None = None,
        to_email: str | None = None,
        **kwargs,
    ):
        sent_emails.append(
            {
                "to_email": recipient or to_email,
                "subject": subject,
                "body": body or "",
                "html_body": html_body or "",
            }
        )

    monkeypatch.setattr(
        "src.routers.auth.send_email",
        mock_send_email,
    )

    response = await async_client.post(
        "/auth/register",
        json={
            "email": "unverified_login_test@test.com",
            "name": "Unverified Login Test",
            "password": "Password1!",
            "role": "officer",
        },
    )

    assert response.status_code == 200

    # Clear the registration email so the login resend is easier to assert.
    sent_emails.clear()

    login_response = await async_client.post(
        "/auth/token",
        data={
            "username": "unverified_login_test@test.com",
            "password": "Password1!",
        },
    )

    assert login_response.status_code == 403
    assert login_response.json()["detail"] == ("Email not verified. A new verification email has been sent.")

    email_body = sent_emails[0]["body"] + sent_emails[0]["html_body"]

    assert len(sent_emails) == 1
    assert sent_emails[0]["to_email"] == "unverified_login_test@test.com"
    assert "verify" in sent_emails[0]["subject"].lower()
    assert "/verify-email?token=" in email_body

    result = await async_session.execute(select(User).where(User.email == "unverified_login_test@test.com"))
    user = result.scalar_one()

    token_result = await async_session.execute(
        select(AuthToken).where(
            AuthToken.user_id == user.id,
            AuthToken.token_type == "email_verification",
            AuthToken.used_at.is_(None),
        )
    )
    tokens = token_result.scalars().all()

    assert len(tokens) == 1


async def test_login_unverified_wrong_password_returns_401(async_client: AsyncClient):
    """Test that login with wrong credentials on an unverified account returns 401.

    Verifies that:
    - Wrong password returns 401 regardless of verification status
    - The unverified error (403) is not leaked when the password is incorrect
    """
    await async_client.post(
        "/auth/register",
        json={
            "email": "unverified_wrong@test.com",
            "name": "Unverified Wrong Password",
            "password": "Password1!",
            "role": "officer",
        },
    )

    response = await async_client.post(
        "/auth/token",
        data={"username": "unverified_wrong@test.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


async def test_get_current_user(async_client: AsyncClient, admin_auth_headers: dict):
    """Test retrieving current user information via /auth/users/me.

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


async def test_register_duplicate_email_fails(async_client: AsyncClient, async_session: AsyncSession):
    """Test that registering a user with an existing email fails.

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
            "password": "Password1!",
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
            "password": "Password2!",
            "role": "officer",
        },
    )
    assert response2.status_code == 400
    assert "already registered" in response2.json()["detail"].lower()


async def test_register_duplicate_name_succeeds(async_client: AsyncClient):
    """Test that two users can register with the same name.

    Verifies that:
    - Name is not a unique identifier — email is
    - Duplicate names are permitted as long as emails differ
    """
    response1 = await async_client.post(
        "/auth/register",
        json={
            "email": "same_name_first@test.com",
            "name": "John Smith",
            "password": "Password1!",
            "role": "officer",
        },
    )
    assert response1.status_code == 200

    response2 = await async_client.post(
        "/auth/register",
        json={
            "email": "same_name_second@test.com",
            "name": "John Smith",
            "password": "Password1!",
            "role": "officer",
        },
    )
    assert response2.status_code == 200


async def test_register_email_is_normalized_to_lowercase(async_client: AsyncClient):
    response = await async_client.post(
        "/auth/register",
        json={
            "email": "CaseTest@Gmail.com",
            "name": "Email Test One",
            "password": "Password1!",
            "role": "officer",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User registered. Verification email sent."


async def test_register_duplicate_email_different_case_fails(async_client: AsyncClient):
    first_response = await async_client.post(
        "/auth/register",
        json={
            "email": "CaseTestDup@Gmail.com",
            "name": "Duplicate Email First User",
            "password": "Password1!",
            "role": "officer",
        },
    )
    assert first_response.status_code == 200

    second_response = await async_client.post(
        "/auth/register",
        json={
            "email": "casetestdup@gmail.com",
            "name": "Duplicate Email Second User",
            "password": "Password2!",
            "role": "officer",
        },
    )
    assert second_response.status_code == 400
    assert "already registered" in second_response.json()["detail"].lower()


async def test_register_unique_email_still_succeeds(async_client: AsyncClient):
    response = await async_client.post(
        "/auth/register",
        json={
            "email": "differentcasecheck@gmail.com",
            "name": "Email Test Four",
            "password": "Password1!",
            "role": "officer",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User registered. Verification email sent."


# ============================================================================
# PASSWORD VALIDATION TESTS
# ============================================================================


async def test_register_password_too_short(async_client: AsyncClient):
    """Test that registration fails with password shorter than 8 characters.

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
    errors = response.json()["errors"]
    assert any("password" in error["field"] for error in errors)


async def test_register_password_minimum_length(async_client: AsyncClient):
    """Test that password with exactly 8 characters is accepted.

    Verifies that:
    - Minimum password length of 8 characters is enforced
    - Registration succeeds with valid 8-character password
    """
    response = await async_client.post(
        "/auth/register",
        json={
            "email": "min_password_test@test.com",
            "name": "Minimum Password Test User",
            "password": "Password1!",  # Exactly 8 characters
            "role": "officer",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User registered. Verification email sent."


# ============================================================================
# AUTHENTICATION FAILURE TESTS
# ============================================================================


async def test_access_protected_endpoint_without_token(async_client: AsyncClient):
    """Test that accessing protected endpoint without token fails.

    Verifies that:
    - Protected endpoints require authentication
    - Returns 401 Unauthorized without valid token
    """
    response = await async_client.get("/users/")
    assert response.status_code == 401


async def test_access_protected_endpoint_with_invalid_token(async_client: AsyncClient):
    """Test that accessing protected endpoint with invalid token fails.

    Verifies that:
    - Invalid JWT tokens are rejected
    - Returns 401 Unauthorized
    """
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = await async_client.get("/users/", headers=headers)
    assert response.status_code == 401


# ============================================================================
# EMAIL VERIFICATION + PASSWORD RESET TESTS
# ============================================================================


async def test_verify_email_success(async_client: AsyncClient, async_session: AsyncSession):
    """Test successful email verification.

    Verifies that:
    - A valid verification token can verify the user
    - The user is marked as verified in the database
    - The verification token is marked as used
    """
    response = await async_client.post(
        "/auth/register",
        json={
            "email": "verify_me@test.com",
            "name": "Verify Me",
            "password": "Password1!",
            "role": "officer",
        },
    )
    assert response.status_code == 200

    result = await async_session.execute(select(User).filter(User.email == "verify_me@test.com"))
    user = result.scalar_one()
    assert user.is_verified is False

    raw_token = await create_auth_token(
        async_session,
        user_id=user.id,
        token_type="email_verification",
    )

    response = await async_client.post(
        "/auth/verify-email",
        json={"token": raw_token},
    )
    assert response.status_code == 200

    result = await async_session.execute(select(User).filter(User.id == user.id))
    verified_user = result.scalar_one()
    assert verified_user.is_verified is True

    result = await async_session.execute(
        select(AuthToken).filter(
            AuthToken.user_id == user.id,
            AuthToken.token_type == "email_verification",
            AuthToken.token_hash == hash_token(raw_token),
        )
    )
    token_obj = result.scalar_one()
    assert token_obj.used_at is not None


async def test_verify_email_invalid_token_fails(async_client: AsyncClient):
    """Test that email verification fails for an invalid token."""
    response = await async_client.post(
        "/auth/verify-email",
        json={"token": "invalid-token"},
    )
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


async def test_forgot_password_email_is_normalized(async_client: AsyncClient):
    """Test forgot-password accepts normalized email input."""
    response = await async_client.post(
        "/auth/forgot-password",
        json={"email": "  ADMIN@Test.com  "},
    )
    assert response.status_code == 200


async def test_validate_reset_password_token_success(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
):
    """Test that a valid reset token is accepted before form submission."""
    raw_token = await create_auth_token(
        async_session,
        user_id=test_admin_user.id,
        token_type="password_reset",
    )

    response = await async_client.get(
        "/auth/reset-password/validate",
        params={"token": raw_token},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Reset token is valid"


async def test_validate_reset_password_token_invalid_fails(async_client: AsyncClient):
    """Test that an invalid reset token is rejected on page load."""
    response = await async_client.get(
        "/auth/reset-password/validate",
        params={"token": "invalid-reset-token"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired token"


async def test_validate_reset_password_token_expired_fails(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
):
    """Test that an expired reset token is rejected on page load."""
    raw_token = "expired-reset-token-check"

    expired_token = AuthToken(
        user_id=test_admin_user.id,
        token_hash=hash_token(raw_token),
        token_type="password_reset",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    async_session.add(expired_token)
    await async_session.commit()

    response = await async_client.get(
        "/auth/reset-password/validate",
        params={"token": raw_token},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired token"


async def test_reset_password_success_and_token_single_use(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
):
    """Test successful password reset and single-use token behavior.

    Verifies that:
    - A valid reset token updates the user's password
    - The reset token is marked as used
    - The same token cannot be reused
    """
    raw_token = await create_auth_token(
        async_session,
        user_id=test_admin_user.id,
        token_type="password_reset",
    )

    response = await async_client.post(
        "/auth/reset-password",
        json={
            "token": raw_token,
            "new_password": "NewPassword1!",
        },
    )
    assert response.status_code == 200

    result = await async_session.execute(select(User).filter(User.id == test_admin_user.id))
    updated_user = result.scalar_one()
    assert verify_password("NewPassword1!", updated_user.hashed_password)

    result = await async_session.execute(
        select(AuthToken).filter(
            AuthToken.user_id == test_admin_user.id,
            AuthToken.token_type == "password_reset",
        )
    )
    token_obj = result.scalar_one()
    assert token_obj.used_at is not None

    reuse_response = await async_client.post(
        "/auth/reset-password",
        json={
            "token": raw_token,
            "new_password": "AnotherPass1!",
        },
    )
    assert reuse_response.status_code == 400
    assert "invalid" in reuse_response.json()["detail"].lower()


async def test_reset_password_rejects_same_current_password(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
):
    """Test that reset-password rejects the user's current password."""
    current_password = "SamePass1!"
    test_admin_user.hashed_password = get_password_hash(current_password)
    async_session.add(test_admin_user)
    await async_session.commit()

    raw_token = await create_auth_token(
        async_session,
        user_id=test_admin_user.id,
        token_type="password_reset",
    )

    response = await async_client.post(
        "/auth/reset-password",
        json={
            "token": raw_token,
            "new_password": current_password,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "New password must be different from the current password"


async def test_reset_password_expired_token_fails(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
):
    """Test that reset-password fails for an expired token."""
    raw_token = "expired-reset-token"

    expired_token = AuthToken(
        user_id=test_admin_user.id,
        token_hash=hash_token(raw_token),
        token_type="password_reset",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    async_session.add(expired_token)
    await async_session.commit()

    response = await async_client.post(
        "/auth/reset-password",
        json={
            "token": raw_token,
            "new_password": "ExpiredPass1!",
        },
    )
    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower() or "invalid" in response.json()["detail"].lower()


async def test_resend_verification_email_user_not_found(
    async_client: AsyncClient,
):
    response = await async_client.post(
        "/auth/resend-verification",
        json={"email": "missing@test.com"},
    )

    assert response.status_code == 200
    assert "verification link" in response.json()["message"]


async def test_resend_verification_email_already_verified(
    async_client: AsyncClient,
    async_session: AsyncSession,
):
    response = await async_client.post(
        "/auth/register",
        json={
            "email": "verified@test.com",
            "name": "Verified User",
            "password": "Password1!",
            "role": "officer",
        },
    )

    assert response.status_code == 200

    result = await async_session.execute(select(User).where(User.email == "verified@test.com"))
    user = result.scalar_one()
    user.is_verified = True
    await async_session.commit()

    resend_response = await async_client.post(
        "/auth/resend-verification",
        json={"email": "verified@test.com"},
    )

    assert resend_response.status_code == 400
    assert resend_response.json()["detail"] == "Account is already verified"


async def test_resend_verification_email_success(
    async_client: AsyncClient,
    async_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
):
    sent_emails = []

    async def mock_send_email(
        recipient: str,
        subject: str,
        body: str | None = None,
        html_body: str | None = None,
        **kwargs,
    ):
        sent_emails.append(
            {
                "recipient": recipient,
                "subject": subject,
                "body": body or "",
                "html_body": html_body or "",
            }
        )

    monkeypatch.setattr(
        "src.routers.auth.send_email",
        mock_send_email,
    )

    response = await async_client.post(
        "/auth/register",
        json={
            "email": "resend@test.com",
            "name": "Resend User",
            "password": "Password1!",
            "role": "officer",
        },
    )

    assert response.status_code == 200

    sent_emails.clear()

    resend_response = await async_client.post(
        "/auth/resend-verification",
        json={"email": "resend@test.com"},
    )

    assert resend_response.status_code == 200
    assert resend_response.json()["message"] == "Verification email sent"

    assert len(sent_emails) == 1
    assert sent_emails[0]["recipient"] == "resend@test.com"

    result = await async_session.execute(select(User).where(User.email == "resend@test.com"))
    user = result.scalar_one()

    token_result = await async_session.execute(
        select(AuthToken).where(
            AuthToken.user_id == user.id,
            AuthToken.token_type == "email_verification",
            AuthToken.used_at.is_(None),
        )
    )

    tokens = token_result.scalars().all()

    assert len(tokens) == 1
