# Test the permission logic directly, no HTTP needed
from app.core.permissions import has_permission, Role

def test_viewer_cannot_create():
    assert has_permission(Role.VIEWER, "records:create") == False

def test_admin_can_do_everything():
    assert has_permission(Role.ADMIN, "records:create") == True
    assert has_permission(Role.ADMIN, "users:delete") == True

def test_analyst_can_read_insights():
    assert has_permission(Role.ANALYST, "dashboard:insights") == True

def test_analyst_cannot_create_records():
    assert has_permission(Role.ANALYST, "records:create") == False