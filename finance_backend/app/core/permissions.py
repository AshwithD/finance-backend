from enum import Enum


class Role(str, Enum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"


# Permissions per role — single source of truth
ROLE_PERMISSIONS: dict[Role, set[str]] = {
    Role.VIEWER: {
        "records:read",
        "dashboard:read",
        "profile:read",
    },
    Role.ANALYST: {
        "records:read",
        "records:export",
        "dashboard:read",
        "dashboard:insights",
        "profile:read",
    },
    Role.ADMIN: {
        "records:read",
        "records:create",
        "records:update",
        "records:delete",
        "records:export",
        "dashboard:read",
        "dashboard:insights",
        "users:read",
        "users:create",
        "users:update",
        "users:delete",
        "profile:read",
    },
}


def has_permission(role: Role, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())
