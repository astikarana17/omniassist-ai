"""Unit tests for the RBAC permission matrix."""
from __future__ import annotations

from app.core.permissions import (
    Permission,
    Role,
    can_manage_role,
    has_permission,
    permission_matrix,
    permissions_for,
)


def test_super_admin_has_everything():
    perms = permissions_for(Role.SUPER_ADMIN)
    assert perms == set(Permission)


def test_viewer_is_read_only():
    assert has_permission(Role.VIEWER, Permission.TICKET_READ)
    assert not has_permission(Role.VIEWER, Permission.TICKET_WRITE)
    assert not has_permission(Role.VIEWER, Permission.MEMBER_MANAGE)


def test_support_agent_scope():
    assert has_permission(Role.SUPPORT_AGENT, Permission.CONVERSATION_WRITE)
    assert has_permission(Role.SUPPORT_AGENT, Permission.TICKET_RESOLVE)
    assert not has_permission(Role.SUPPORT_AGENT, Permission.LEAD_WRITE)
    assert not has_permission(Role.SUPPORT_AGENT, Permission.SETTINGS_WRITE)


def test_sales_agent_scope():
    assert has_permission(Role.SALES_AGENT, Permission.LEAD_WRITE)
    assert not has_permission(Role.SALES_AGENT, Permission.TICKET_DELETE)


def test_admin_cannot_manage_billing():
    assert not has_permission(Role.ADMIN, Permission.BILLING_MANAGE)
    assert has_permission(Role.ADMIN, Permission.MEMBER_MANAGE)


def test_role_hierarchy_prevents_escalation():
    assert can_manage_role(Role.ADMIN, Role.SUPPORT_AGENT)
    assert can_manage_role(Role.SUPPORT_MANAGER, Role.SUPPORT_AGENT)
    assert not can_manage_role(Role.SUPPORT_AGENT, Role.ADMIN)
    assert not can_manage_role(Role.ADMIN, Role.ADMIN)  # cannot manage equal rank


def test_matrix_is_serializable():
    matrix = permission_matrix()
    assert set(matrix.keys()) == {r.value for r in Role}
    assert all(isinstance(v, list) for v in matrix.values())
