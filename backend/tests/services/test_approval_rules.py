import pytest

from src.schemas.constants import ApprovalAction, Role
from src.services.approval_rules import (
    LAST_ADMIN,
    ApprovalDecision,
    Outcome,
    decide,
    is_active_admin,
    is_own_request,
    needs_second_admin,
)

APPROVE = ApprovalAction.APPROVE_USER
CHANGE_ROLE = ApprovalAction.CHANGE_ROLE
DEACTIVATE = ApprovalAction.DEACTIVATE_USER


# needs_second_admin


@pytest.mark.parametrize(
    ("action", "new_role", "expected"),
    [
        (APPROVE, Role.OFFICER, False),
        (APPROVE, Role.SUPERVISOR, True),
        (APPROVE, Role.ADMIN, True),
        (CHANGE_ROLE, Role.OFFICER, True),
        (CHANGE_ROLE, Role.SUPERVISOR, True),
        (CHANGE_ROLE, Role.ADMIN, True),
        (DEACTIVATE, None, True),
        (DEACTIVATE, Role.OFFICER, True),
    ],
)
def test_needs_second_admin(action, new_role, expected):
    assert needs_second_admin(action, new_role) is expected


def test_needs_second_admin_accepts_plain_role_strings():
    assert needs_second_admin(APPROVE, "officer") is False
    assert needs_second_admin(APPROVE, "supervisor") is True


@pytest.mark.parametrize("action", [APPROVE, CHANGE_ROLE])
def test_needs_second_admin_requires_a_role(action):
    with pytest.raises(ValueError, match="new_role is required"):
        needs_second_admin(action)


def test_needs_second_admin_rejects_an_invalid_role():
    with pytest.raises(ValueError):
        needs_second_admin(APPROVE, "superuser")


# is_active_admin


def test_is_active_admin_true_when_every_condition_holds():
    assert is_active_admin("admin", is_approved=True, is_verified=True, is_active=True) is True


@pytest.mark.parametrize(
    ("role", "is_approved", "is_verified", "is_active"),
    [
        ("officer", True, True, True),
        ("supervisor", True, True, True),
        ("admin", False, True, True),
        ("admin", True, False, True),
        ("admin", True, True, False),
    ],
)
def test_is_active_admin_false_when_any_condition_fails(role, is_approved, is_verified, is_active):
    assert is_active_admin(role, is_approved=is_approved, is_verified=is_verified, is_active=is_active) is False


# decide: one admin is enough


@pytest.mark.parametrize("admin_count", [1, 2, 5])
def test_approving_an_officer_executes_for_any_admin_count(admin_count):
    decision = decide(APPROVE, new_role=Role.OFFICER, target_is_active_admin=False, active_admin_count=admin_count)
    assert decision == ApprovalDecision(Outcome.EXECUTE)


# decide: second admin needed


@pytest.mark.parametrize(
    ("action", "new_role"),
    [
        (APPROVE, Role.SUPERVISOR),
        (APPROVE, Role.ADMIN),
        (CHANGE_ROLE, Role.OFFICER),
        (CHANGE_ROLE, Role.SUPERVISOR),
        (DEACTIVATE, None),
    ],
)
def test_second_admin_actions_create_a_request_when_two_or_more_admins_exist(action, new_role):
    for admin_count in (2, 3):
        decision = decide(action, new_role=new_role, target_is_active_admin=False, active_admin_count=admin_count)
        assert decision == ApprovalDecision(Outcome.REQUEST)


# decide: bypass for the sole active admin


@pytest.mark.parametrize(
    ("action", "new_role"),
    [
        (APPROVE, Role.SUPERVISOR),
        (APPROVE, Role.ADMIN),
        (CHANGE_ROLE, Role.SUPERVISOR),
        (DEACTIVATE, None),
    ],
)
def test_sole_admin_bypasses_second_admin_actions_on_other_users(action, new_role):
    decision = decide(action, new_role=new_role, target_is_active_admin=False, active_admin_count=1)
    assert decision == ApprovalDecision(Outcome.BYPASS)


def test_sole_admin_approving_an_officer_is_not_a_bypass():
    decision = decide(APPROVE, new_role=Role.OFFICER, target_is_active_admin=False, active_admin_count=1)
    assert decision.outcome is Outcome.EXECUTE


# decide: the last active admin is protected


def test_last_admin_cannot_be_deactivated():
    decision = decide(DEACTIVATE, target_is_active_admin=True, active_admin_count=1)
    assert decision == ApprovalDecision(Outcome.DENIED, LAST_ADMIN)


@pytest.mark.parametrize("new_role", [Role.OFFICER, Role.SUPERVISOR])
def test_last_admin_cannot_be_demoted(new_role):
    decision = decide(CHANGE_ROLE, new_role=new_role, target_is_active_admin=True, active_admin_count=1)
    assert decision == ApprovalDecision(Outcome.DENIED, LAST_ADMIN)


def test_an_admin_can_be_deactivated_when_another_active_admin_exists():
    decision = decide(DEACTIVATE, target_is_active_admin=True, active_admin_count=2)
    assert decision == ApprovalDecision(Outcome.REQUEST)


def test_deactivating_a_non_admin_is_not_blocked_by_the_last_admin_rule():
    decision = decide(DEACTIVATE, target_is_active_admin=False, active_admin_count=1)
    assert decision == ApprovalDecision(Outcome.BYPASS)


# decide: edge cases


def test_zero_active_admins_never_bypasses():
    decision = decide(DEACTIVATE, target_is_active_admin=False, active_admin_count=0)
    assert decision == ApprovalDecision(Outcome.REQUEST)


def test_negative_admin_count_is_rejected():
    with pytest.raises(ValueError, match="cannot be negative"):
        decide(DEACTIVATE, target_is_active_admin=False, active_admin_count=-1)


def test_decision_has_no_error_code_unless_denied():
    assert decide(APPROVE, new_role=Role.OFFICER, target_is_active_admin=False, active_admin_count=2).error_code is None


# is_own_request


def test_is_own_request():
    assert is_own_request(7, 7) is True
    assert is_own_request(7, 8) is False
