"""Role-Based Access Control: roles, permissions and the permission matrix."""
from __future__ import annotations

from enum import StrEnum


class Role(StrEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    SUPPORT_MANAGER = "support_manager"
    SUPPORT_AGENT = "support_agent"
    SALES_MANAGER = "sales_manager"
    SALES_AGENT = "sales_agent"
    VIEWER = "viewer"


class Permission(StrEnum):
    # Conversations / Inbox
    CONVERSATION_READ = "conversation:read"
    CONVERSATION_WRITE = "conversation:write"
    CONVERSATION_HANDOFF = "conversation:handoff"
    CONVERSATION_DELETE = "conversation:delete"
    # Tickets
    TICKET_READ = "ticket:read"
    TICKET_WRITE = "ticket:write"
    TICKET_ASSIGN = "ticket:assign"
    TICKET_RESOLVE = "ticket:resolve"
    TICKET_DELETE = "ticket:delete"
    # Leads / CRM
    LEAD_READ = "lead:read"
    LEAD_WRITE = "lead:write"
    LEAD_DELETE = "lead:delete"
    # Knowledge base
    KB_READ = "kb:read"
    KB_WRITE = "kb:write"
    KB_DELETE = "kb:delete"
    # AI agents
    AGENT_READ = "agent:read"
    AGENT_WRITE = "agent:write"
    # Analytics
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_EXPORT = "analytics:export"
    # Team / members
    MEMBER_READ = "member:read"
    MEMBER_INVITE = "member:invite"
    MEMBER_MANAGE = "member:manage"  # change roles / remove
    # Settings / org
    SETTINGS_READ = "settings:read"
    SETTINGS_WRITE = "settings:write"
    BILLING_MANAGE = "billing:manage"
    # Security / audit
    AUDIT_READ = "audit:read"
    APIKEY_MANAGE = "apikey:manage"
    # Channels
    CHANNEL_MANAGE = "channel:manage"
    # --- Business Operations Platform expansion ---
    # Company knowledge (Product Expert agent)
    COMPANY_READ = "company:read"
    COMPANY_WRITE = "company:write"
    # Competitor intelligence
    COMPETITOR_READ = "competitor:read"
    COMPETITOR_WRITE = "competitor:write"
    # Onboarding
    ONBOARDING_READ = "onboarding:read"
    ONBOARDING_WRITE = "onboarding:write"
    # Customer success + health
    CUSTOMER_SUCCESS_READ = "customer_success:read"
    CUSTOMER_SUCCESS_WRITE = "customer_success:write"
    # Knowledge gaps
    KNOWLEDGE_GAP_READ = "knowledge_gap:read"
    KNOWLEDGE_GAP_WRITE = "knowledge_gap:write"
    # Executive insights
    INSIGHTS_READ = "insights:read"
    # Meetings / demos
    MEETING_READ = "meeting:read"
    MEETING_WRITE = "meeting:write"
    # Workflow automation
    WORKFLOW_READ = "workflow:read"
    WORKFLOW_WRITE = "workflow:write"
    # Employee assistant (internal docs / HR)
    EMPLOYEE_READ = "employee:read"
    EMPLOYEE_WRITE = "employee:write"
    # Business impact / ROI analytics
    IMPACT_READ = "impact:read"


_ALL: set[Permission] = set(Permission)

# Read-only slice of the new Business-Operations surface (for viewer/analyst roles).
_OPS_READ: set[Permission] = {
    Permission.COMPANY_READ,
    Permission.COMPETITOR_READ,
    Permission.ONBOARDING_READ,
    Permission.CUSTOMER_SUCCESS_READ,
    Permission.KNOWLEDGE_GAP_READ,
    Permission.INSIGHTS_READ,
    Permission.MEETING_READ,
    Permission.WORKFLOW_READ,
    Permission.IMPACT_READ,
}

_SUPPORT_BASE: set[Permission] = {
    Permission.CONVERSATION_READ,
    Permission.CONVERSATION_WRITE,
    Permission.CONVERSATION_HANDOFF,
    Permission.TICKET_READ,
    Permission.TICKET_WRITE,
    Permission.TICKET_RESOLVE,
    Permission.KB_READ,
    Permission.ANALYTICS_READ,
    # Ops surface a support agent needs day-to-day
    Permission.COMPANY_READ,
    Permission.COMPETITOR_READ,
    Permission.KNOWLEDGE_GAP_READ,
    Permission.KNOWLEDGE_GAP_WRITE,
    Permission.ONBOARDING_READ,
    Permission.MEETING_READ,
    Permission.EMPLOYEE_READ,
}

_SALES_BASE: set[Permission] = {
    Permission.CONVERSATION_READ,
    Permission.CONVERSATION_WRITE,
    Permission.LEAD_READ,
    Permission.LEAD_WRITE,
    Permission.KB_READ,
    Permission.ANALYTICS_READ,
    # Ops surface a sales agent needs day-to-day
    Permission.COMPANY_READ,
    Permission.COMPETITOR_READ,
    Permission.COMPETITOR_WRITE,
    Permission.MEETING_READ,
    Permission.MEETING_WRITE,
    Permission.CUSTOMER_SUCCESS_READ,
    Permission.EMPLOYEE_READ,
}

ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.SUPER_ADMIN: _ALL,
    Role.ADMIN: _ALL
    - {Permission.BILLING_MANAGE},  # admins manage everything except billing ownership
    Role.SUPPORT_MANAGER: _SUPPORT_BASE
    | {
        Permission.TICKET_ASSIGN,
        Permission.TICKET_DELETE,
        Permission.CONVERSATION_DELETE,
        Permission.KB_WRITE,
        Permission.MEMBER_READ,
        Permission.ANALYTICS_EXPORT,
        Permission.AGENT_READ,
        Permission.AUDIT_READ,
        # Manage the ops surface a support org owns
        Permission.COMPANY_WRITE,
        Permission.ONBOARDING_WRITE,
        Permission.CUSTOMER_SUCCESS_READ,
        Permission.CUSTOMER_SUCCESS_WRITE,
        Permission.WORKFLOW_READ,
        Permission.WORKFLOW_WRITE,
        Permission.INSIGHTS_READ,
        Permission.IMPACT_READ,
        Permission.EMPLOYEE_WRITE,
    },
    Role.SUPPORT_AGENT: _SUPPORT_BASE,
    Role.SALES_MANAGER: _SALES_BASE
    | {
        Permission.LEAD_DELETE,
        Permission.KB_WRITE,
        Permission.MEMBER_READ,
        Permission.ANALYTICS_EXPORT,
        Permission.AGENT_READ,
        # Manage the ops surface a sales org owns
        Permission.COMPANY_WRITE,
        Permission.CUSTOMER_SUCCESS_WRITE,
        Permission.WORKFLOW_READ,
        Permission.WORKFLOW_WRITE,
        Permission.INSIGHTS_READ,
        Permission.IMPACT_READ,
    },
    Role.SALES_AGENT: _SALES_BASE,
    Role.VIEWER: {
        Permission.CONVERSATION_READ,
        Permission.TICKET_READ,
        Permission.LEAD_READ,
        Permission.KB_READ,
        Permission.ANALYTICS_READ,
    }
    | _OPS_READ,
}

# Role hierarchy weight — used to prevent privilege escalation (you can only
# assign/modify members at or below your own level).
ROLE_RANK: dict[Role, int] = {
    Role.SUPER_ADMIN: 100,
    Role.ADMIN: 90,
    Role.SUPPORT_MANAGER: 70,
    Role.SALES_MANAGER: 70,
    Role.SUPPORT_AGENT: 50,
    Role.SALES_AGENT: 50,
    Role.VIEWER: 10,
}


def permissions_for(role: Role | str) -> set[Permission]:
    return ROLE_PERMISSIONS.get(Role(role), set())


def has_permission(role: Role | str, permission: Permission) -> bool:
    return permission in permissions_for(role)


def can_manage_role(actor: Role | str, target: Role | str) -> bool:
    """An actor may only manage members whose role rank is < their own."""
    return ROLE_RANK.get(Role(actor), 0) > ROLE_RANK.get(Role(target), 0)


def permission_matrix() -> dict[str, list[str]]:
    """Serializable matrix for the frontend / docs."""
    return {role.value: sorted(p.value for p in perms) for role, perms in ROLE_PERMISSIONS.items()}
