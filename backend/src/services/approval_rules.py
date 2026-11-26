from dataclasses import dataclass
from enum import Enum

from src.schemas.constants import ApprovalAction, Role

# Error codes for the API contract
LAST_ADMIN = "last_admin"
OWN_REQUEST = "own_request"

# Roles that cannot be granted by a single admin
ELEVATED_ROLES = frozenset({Role.SUPERVISOR, Role.ADMIN})


class Outcome(str, Enum):
    """What the caller should do with the requested action."""

    EXECUTE = "execute"
    REQUEST = "request"
    BYPASS = "bypass"
    DENIED = "denied"


@dataclass(frozen=True)
class ApprovalDecision:
    outcome: Outcome
    error_code: str | None = None


def is_active_admin(role: str, *, is_approved: bool, is_verified: bool, is_active: bool) -> bool:
    """Returns True if the account counts as an active admin."""
    return role == Role.ADMIN and is_approved and is_verified and is_active


def needs_second_admin(action: ApprovalAction, new_role: Role | str | None = None) -> bool:
    """Returns True if the action needs a second admin's approval.

    Args:
        action: The user-management action being attempted.
        new_role: The role being granted. Required for APPROVE_USER and
            CHANGE_ROLE, ignored for DEACTIVATE_USER.

    Raises:
        ValueError: If new_role is missing when required, or is not a valid role.
    """
    if action == ApprovalAction.DEACTIVATE_USER:
        return True

    if new_role is None:
        raise ValueError(f"new_role is required for {action.value}")

    # Validate the role on every path, so an invalid role is always rejected
    role = Role(new_role)

    if action == ApprovalAction.CHANGE_ROLE:
        return True

    # APPROVE_USER: only granting supervisor or admin needs a second admin
    return role in ELEVATED_ROLES


def _removes_admin_access(action: ApprovalAction, new_role: Role | str | None) -> bool:
    """Returns True if the action would stop the target being an admin."""
    if action == ApprovalAction.DEACTIVATE_USER:
        return True
    if action == ApprovalAction.CHANGE_ROLE:
        return Role(new_role) != Role.ADMIN
    return False


def decide(
    action: ApprovalAction,
    *,
    new_role: Role | str | None = None,
    target_is_active_admin: bool,
    active_admin_count: int,
) -> ApprovalDecision:
    """Decides how an action should be handled.

    Args:
        action: The user-management action being attempted.
        new_role: The role being granted (APPROVE_USER and CHANGE_ROLE only).
        target_is_active_admin: Whether the user being acted on is an active admin now.
        active_admin_count: How many active admins exist right now.

    Returns:
        An ApprovalDecision. When the outcome is DENIED, error_code says why.
    """
    if active_admin_count < 0:
        raise ValueError("active_admin_count cannot be negative")

    if not needs_second_admin(action, new_role):
        return ApprovalDecision(Outcome.EXECUTE)

    # Never leave the system without an active admin, even with a bypass
    if target_is_active_admin and active_admin_count <= 1 and _removes_admin_access(action, new_role):
        return ApprovalDecision(Outcome.DENIED, LAST_ADMIN)

    if active_admin_count == 1:
        return ApprovalDecision(Outcome.BYPASS)

    return ApprovalDecision(Outcome.REQUEST)


def is_own_request(requested_by_id: int, approver_id: int) -> bool:
    """Returns True if the approver is the person who made the request."""
    return requested_by_id == approver_id
