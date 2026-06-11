"""RBAC tests for the new Business-Operations permissions + route registration."""
from __future__ import annotations

import pytest

from app.core.permissions import Permission, Role, has_permission, permissions_for


def test_new_permissions_exist():
    for key in [
        "company:read", "company:write", "competitor:read", "competitor:write",
        "onboarding:read", "onboarding:write", "customer_success:read",
        "customer_success:write", "knowledge_gap:read", "knowledge_gap:write",
        "insights:read", "meeting:read", "meeting:write", "workflow:read",
        "workflow:write", "employee:read", "employee:write", "impact:read",
    ]:
        assert any(p.value == key for p in Permission), f"missing permission {key}"


def test_super_admin_still_has_everything():
    assert permissions_for(Role.SUPER_ADMIN) == set(Permission)


def test_admin_has_all_ops_except_none_special():
    # admin = everything except billing; should include every new ops permission.
    admin = permissions_for(Role.ADMIN)
    assert Permission.WORKFLOW_WRITE in admin
    assert Permission.COMPANY_WRITE in admin
    assert Permission.IMPACT_READ in admin


def test_support_agent_ops_scope():
    assert has_permission(Role.SUPPORT_AGENT, Permission.COMPANY_READ)
    assert has_permission(Role.SUPPORT_AGENT, Permission.KNOWLEDGE_GAP_WRITE)
    assert not has_permission(Role.SUPPORT_AGENT, Permission.COMPANY_WRITE)
    assert not has_permission(Role.SUPPORT_AGENT, Permission.WORKFLOW_WRITE)


def test_sales_agent_ops_scope():
    assert has_permission(Role.SALES_AGENT, Permission.MEETING_WRITE)
    assert has_permission(Role.SALES_AGENT, Permission.COMPETITOR_WRITE)
    assert not has_permission(Role.SALES_AGENT, Permission.EMPLOYEE_WRITE)


def test_viewer_ops_is_read_only():
    assert has_permission(Role.VIEWER, Permission.COMPANY_READ)
    assert has_permission(Role.VIEWER, Permission.INSIGHTS_READ)
    assert has_permission(Role.VIEWER, Permission.IMPACT_READ)
    assert not has_permission(Role.VIEWER, Permission.COMPANY_WRITE)
    # viewer should NOT see internal employee docs
    assert not has_permission(Role.VIEWER, Permission.EMPLOYEE_READ)


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/company/products",
        "/api/v1/onboarding/flows",
        "/api/v1/customer-success/accounts",
        "/api/v1/knowledge-gaps",
        "/api/v1/insights",
        "/api/v1/meetings",
        "/api/v1/workflows",
        "/api/v1/employee/documents",
    ],
)
def test_ops_routes_registered_and_require_auth(client, path):
    """Every new route is mounted and rejects unauthenticated access (401)."""
    resp = client.get(path)
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] in ("AUTH_REQUIRED",)
