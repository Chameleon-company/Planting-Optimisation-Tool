import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.audit_log import AuditLog

pytestmark = pytest.mark.asyncio


async def test_audit_log_on_user_creation(
    async_client: AsyncClient,
    test_admin_user,
    admin_auth_headers: dict,
    async_session: AsyncSession,
):
    """
    Test that user creation generates an audit log entry.

    Verifies that when an admin creates a user, an audit log is recorded with:
    - The correct event type ("user_create")
    - The admin's user ID (the creator, not the created user)
    - Details about who created whom
    """
    # Action that should trigger an audit log
    response = await async_client.post(
        "/users/",
        json={
            "email": "audituser@example.com",
            "name": "Audit User",
            "password": "auditpassword",
            "role": "officer",
        },
        headers=admin_auth_headers,
    )
    assert response.status_code == 201

    # Check that the audit log was created
    # Query for audit logs with this specific email in the details
    # to avoid conflicts with other tests that also create users
    result = await async_session.execute(
        select(AuditLog)
        .filter(AuditLog.event_type == "user_create")
        .filter(AuditLog.details.contains("audituser@example.com"))
        .order_by(AuditLog.timestamp.desc())
    )
    log_entry = result.scalars().first()

    assert log_entry is not None, "Audit log entry should be created for user creation"
    # The user_id in the audit log should be the admin who created the user
    assert log_entry.user_id == test_admin_user.id, (
        f"Expected user_id {test_admin_user.id}, got {log_entry.user_id}"
    )
    # The details should mention both the creator and the created user
    assert "created user audituser@example.com" in log_entry.details
    assert "admin@test.com" in log_entry.details  # The admin's email appears in details
