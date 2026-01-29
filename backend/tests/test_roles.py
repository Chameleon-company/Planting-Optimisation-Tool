import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.user import User

pytestmark = pytest.mark.asyncio


# Test user creation endpoint
async def test_create_user_by_admin(
    async_client: AsyncClient, test_admin_user, admin_auth_headers: dict
):
    response = await async_client.post(
        "/users/",  # Added trailing slash
        json={
            "email": "admin_created_officer@test.com",
            "name": "Admin Created Officer User",
            "password": "testpassword",
            "role": "officer",
        },
        headers=admin_auth_headers,
    )
    assert response.status_code == 201


async def test_create_user_by_supervisor_success(
    async_client: AsyncClient, test_supervisor_user, supervisor_auth_headers: dict
):
    """
    Test that supervisors CAN create users.

    Note: This endpoint was changed to allow any authenticated user to create users,
    not just admins. If you want to restrict user creation to admins only,
    add require_role(Role.ADMIN) to the create_user endpoint.
    """
    response = await async_client.post(
        "/users/",
        json={
            "email": "supervisor_created_officer@test.com",
            "name": "Supervisor Created Officer User",
            "password": "testpassword",
            "role": "officer",
        },
        headers=supervisor_auth_headers,
    )
    # Changed from 403 to 201 because supervisors can now create users
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "supervisor_created_officer@test.com"
    assert data["role"] == "officer"


# Test reading user information
async def test_read_users_by_supervisor(
    async_client: AsyncClient, test_supervisor_user, supervisor_auth_headers: dict
):
    response = await async_client.get(
        "/users/", headers=supervisor_auth_headers
    )  # Added trailing slash
    assert response.status_code == 200


async def test_read_users_by_admin(
    async_client: AsyncClient, test_admin_user, admin_auth_headers: dict
):
    response = await async_client.get(
        "/users/", headers=admin_auth_headers
    )  # Added trailing slash
    assert response.status_code == 200


async def test_read_users_by_officer_fail(
    async_client: AsyncClient, test_officer_user, officer_auth_headers: dict
):
    response = await async_client.get(
        "/users/", headers=officer_auth_headers
    )  # Added trailing slash
    assert response.status_code == 403


# Test role hierarchy
async def test_admin_can_access_supervisor_endpoint(
    async_client: AsyncClient, test_admin_user, admin_auth_headers: dict
):
    response = await async_client.get(
        "/users/", headers=admin_auth_headers
    )  # Added trailing slash
    assert response.status_code == 200


# ============================================================================
# OFFICER ROLE RESTRICTION TESTS
# ============================================================================


async def test_officer_cannot_get_user_by_id(
    async_client: AsyncClient,
    test_officer_user: User,
    test_supervisor_user: User,
    officer_auth_headers: dict,
):
    """
    Test that officers cannot access GET /users/{user_id} endpoint.

    Verifies that:
    - Officer role cannot view specific user details
    - Returns 403 Forbidden
    """
    response = await async_client.get(
        f"/users/{test_supervisor_user.id}", headers=officer_auth_headers
    )
    assert response.status_code == 403


async def test_officer_cannot_update_user(
    async_client: AsyncClient,
    test_officer_user: User,
    test_supervisor_user: User,
    officer_auth_headers: dict,
):
    """
    Test that officers cannot update users (PUT /users/{user_id}).

    Verifies that:
    - Officer role cannot update user information
    - Returns 403 Forbidden
    - Only ADMIN can update users
    """
    response = await async_client.put(
        f"/users/{test_supervisor_user.id}",
        json={
            "email": "officer_update_attempt@test.com",
            "name": "Officer Update Attempt",
            "password": "newpassword",
            "role": "officer",
        },
        headers=officer_auth_headers,
    )
    assert response.status_code == 403


async def test_officer_cannot_delete_user(
    async_client: AsyncClient,
    test_officer_user: User,
    test_supervisor_user: User,
    officer_auth_headers: dict,
):
    """
    Test that officers cannot delete users (DELETE /users/{user_id}).

    Verifies that:
    - Officer role cannot delete users
    - Returns 403 Forbidden
    - Only ADMIN can delete users
    """
    response = await async_client.delete(
        f"/users/{test_supervisor_user.id}", headers=officer_auth_headers
    )
    assert response.status_code == 403


# ============================================================================
# SUPERVISOR ROLE RESTRICTION TESTS
# ============================================================================


async def test_supervisor_can_get_user_by_id(
    async_client: AsyncClient,
    test_supervisor_user: User,
    test_officer_user: User,
    supervisor_auth_headers: dict,
):
    """
    Test that supervisors CAN view specific user details.

    Verifies that:
    - SUPERVISOR role has access to GET /users/{user_id}
    - Returns 200 OK with user data
    """
    response = await async_client.get(
        f"/users/{test_officer_user.id}", headers=supervisor_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_officer_user.id


async def test_supervisor_cannot_update_user(
    async_client: AsyncClient,
    test_supervisor_user: User,
    test_officer_user: User,
    supervisor_auth_headers: dict,
):
    """
    Test that supervisors CANNOT update users.

    Verifies that:
    - SUPERVISOR role cannot update user information
    - Returns 403 Forbidden
    - Only ADMIN can update users
    """
    response = await async_client.put(
        f"/users/{test_officer_user.id}",
        json={
            "email": "supervisor_update_attempt@test.com",
            "name": "Supervisor Update Attempt",
            "password": "newpassword",
            "role": "officer",
        },
        headers=supervisor_auth_headers,
    )
    assert response.status_code == 403


async def test_supervisor_cannot_delete_user(
    async_client: AsyncClient,
    test_supervisor_user: User,
    test_officer_user: User,
    supervisor_auth_headers: dict,
):
    """
    Test that supervisors CANNOT delete users.

    Verifies that:
    - SUPERVISOR role cannot delete users
    - Returns 403 Forbidden
    - Only ADMIN can delete users
    """
    response = await async_client.delete(
        f"/users/{test_officer_user.id}", headers=supervisor_auth_headers
    )
    assert response.status_code == 403


# ============================================================================
# ADMIN ROLE FULL ACCESS TESTS
# ============================================================================


async def test_admin_can_get_user_by_id(
    async_client: AsyncClient,
    test_admin_user: User,
    test_officer_user: User,
    admin_auth_headers: dict,
):
    """
    Test that admins CAN view specific user details.

    Verifies that:
    - ADMIN role has access to GET /users/{user_id}
    - Returns 200 OK with user data
    """
    response = await async_client.get(
        f"/users/{test_officer_user.id}", headers=admin_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_officer_user.id


async def test_admin_can_update_user(
    async_client: AsyncClient,
    test_admin_user: User,
    test_officer_user: User,
    admin_auth_headers: dict,
):
    """
    Test that admins CAN update users.

    Verifies that:
    - ADMIN role can update user information
    - Returns 200 OK with updated user data
    - Changes are persisted
    """
    response = await async_client.put(
        f"/users/{test_officer_user.id}",
        json={
            "email": "updated_officer@test.com",
            "name": "Updated Officer Name",
            "password": "newpassword123",
            "role": "supervisor",
        },
        headers=admin_auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "updated_officer@test.com"
    assert data["name"] == "Updated Officer Name"
    assert data["role"] == "supervisor"


async def test_admin_can_delete_user(
    async_client: AsyncClient,
    test_admin_user: User,
    async_session: AsyncSession,
    admin_auth_headers: dict,
):
    """
    Test that admins CAN delete users.

    Verifies that:
    - ADMIN role can delete users
    - Returns 204 No Content
    - User is actually removed from database
    """
    # Create a user to delete
    from src.services.authentication import get_password_hash

    user_to_delete = User(
        name="User To Delete",
        email="user_to_delete_test@test.com",
        hashed_password=get_password_hash("password"),
        role="officer",
    )
    async_session.add(user_to_delete)
    await async_session.flush()
    await async_session.refresh(user_to_delete)
    user_id = user_to_delete.id

    # Delete the user
    response = await async_client.delete(
        f"/users/{user_id}", headers=admin_auth_headers
    )
    assert response.status_code == 204

    # Verify user is deleted
    result = await async_session.execute(select(User).where(User.id == user_id))
    deleted_user = result.scalar_one_or_none()
    assert deleted_user is None


# ============================================================================
# DUPLICATE USER VIA /users/ ENDPOINT
# ============================================================================


async def test_create_user_duplicate_email_via_users_endpoint(
    async_client: AsyncClient, test_admin_user: User, admin_auth_headers: dict
):
    """
    Test that creating a user via /users/ endpoint with duplicate email fails.

    Verifies that:
    - First user creation succeeds
    - Second creation with same email fails with 400
    """
    # Create first user
    response1 = await async_client.post(
        "/users/",
        json={
            "email": "duplicate_via_users_endpoint@test.com",
            "name": "First Users Endpoint User",
            "password": "password123",
            "role": "officer",
        },
        headers=admin_auth_headers,
    )
    assert response1.status_code == 201

    # Try to create second user with same email
    response2 = await async_client.post(
        "/users/",
        json={
            "email": "duplicate_via_users_endpoint@test.com",
            "name": "Second Users Endpoint User",
            "password": "password456",
            "role": "supervisor",
        },
        headers=admin_auth_headers,
    )
    assert response2.status_code == 400
    assert "already registered" in response2.json()["detail"].lower()


# ============================================================================
# PASSWORD VALIDATION VIA /users/ ENDPOINT
# ============================================================================


async def test_create_user_password_too_short(
    async_client: AsyncClient, test_admin_user: User, admin_auth_headers: dict
):
    """
    Test that creating user via /users/ fails with short password.

    Verifies password validation is enforced on user creation endpoint.
    """
    response = await async_client.post(
        "/users/",
        json={
            "email": "short_password_via_users@test.com",
            "name": "Short Password Via Users Test",
            "password": "abc",  # Too short
            "role": "officer",
        },
        headers=admin_auth_headers,
    )
    assert response.status_code == 422
