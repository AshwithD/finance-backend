"""
Integration tests using an in-memory SQLite database so no Postgres is needed.
Run with:  pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import Base, get_db
from app.db.init_db import seed_admin

SQLITE_URL = "sqlite:///./test.db"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_admin(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app, raise_server_exceptions=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def admin_token():
    resp = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "Admin@123"})
    return resp.json()["access_token"]


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


# ── Auth Tests ────────────────────────────────────────────────────────────────

class TestAuth:
    def test_login_success(self):
        r = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "Admin@123"})
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["role"] == "admin"

    def test_login_wrong_password(self):
        r = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "wrong"})
        assert r.status_code == 401

    def test_login_unknown_email(self):
        r = client.post("/api/v1/auth/login", json={"email": "no@one.com", "password": "whatever"})
        assert r.status_code == 401

    def test_me(self):
        token = admin_token()
        r = client.get("/api/v1/auth/me", headers=auth_headers(token))
        assert r.status_code == 200
        assert r.json()["email"] == "admin@example.com"

    def test_me_no_token(self):
        r = client.get("/api/v1/auth/me")
        assert r.status_code == 403

    def test_refresh_token(self):
        r = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "Admin@123"})
        refresh = r.json()["refresh_token"]
        r2 = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
        assert r2.status_code == 200
        assert "access_token" in r2.json()


# ── User Management Tests ─────────────────────────────────────────────────────

class TestUsers:
    def test_create_viewer(self):
        token = admin_token()
        r = client.post(
            "/api/v1/users",
            json={"name": "Viewer User", "email": "viewer@test.com", "password": "Viewer@123", "role": "viewer"},
            headers=auth_headers(token),
        )
        assert r.status_code == 201
        assert r.json()["role"] == "viewer"

    def test_create_analyst(self):
        token = admin_token()
        r = client.post(
            "/api/v1/users",
            json={"name": "Analyst User", "email": "analyst@test.com", "password": "Analyst@123", "role": "analyst"},
            headers=auth_headers(token),
        )
        assert r.status_code == 201

    def test_create_duplicate_email(self):
        token = admin_token()
        client.post(
            "/api/v1/users",
            json={"name": "Dup", "email": "dup@test.com", "password": "Dup@12345", "role": "viewer"},
            headers=auth_headers(token),
        )
        r = client.post(
            "/api/v1/users",
            json={"name": "Dup2", "email": "dup@test.com", "password": "Dup@12345", "role": "viewer"},
            headers=auth_headers(token),
        )
        assert r.status_code == 409

    def test_viewer_cannot_create_user(self):
        # Login as viewer
        r = client.post("/api/v1/auth/login", json={"email": "viewer@test.com", "password": "Viewer@123"})
        token = r.json()["access_token"]
        r2 = client.post(
            "/api/v1/users",
            json={"name": "X", "email": "x@x.com", "password": "Xxxxx@123", "role": "viewer"},
            headers=auth_headers(token),
        )
        assert r2.status_code == 403

    def test_list_users(self):
        token = admin_token()
        r = client.get("/api/v1/users", headers=auth_headers(token))
        assert r.status_code == 200
        assert r.json()["total"] >= 1

    def test_weak_password_rejected(self):
        token = admin_token()
        r = client.post(
            "/api/v1/users",
            json={"name": "Weak", "email": "weak@test.com", "password": "simple"},
            headers=auth_headers(token),
        )
        assert r.status_code == 422


# ── Financial Records Tests ───────────────────────────────────────────────────

class TestRecords:
    def _create_record(self, token):
        return client.post(
            "/api/v1/records",
            json={"amount": 500.00, "type": "income", "category": "Salary", "date": "2024-03-15"},
            headers=auth_headers(token),
        )

    def test_admin_can_create_record(self):
        token = admin_token()
        r = self._create_record(token)
        assert r.status_code == 201
        data = r.json()
        assert data["category"] == "Salary"
        assert data["type"] == "income"

    def test_viewer_cannot_create_record(self):
        r = client.post("/api/v1/auth/login", json={"email": "viewer@test.com", "password": "Viewer@123"})
        token = r.json()["access_token"]
        r2 = self._create_record(token)
        assert r2.status_code == 403

    def test_viewer_can_read_records(self):
        r = client.post("/api/v1/auth/login", json={"email": "viewer@test.com", "password": "Viewer@123"})
        token = r.json()["access_token"]
        r2 = client.get("/api/v1/records", headers=auth_headers(token))
        assert r2.status_code == 200

    def test_filter_by_type(self):
        token = admin_token()
        r = client.get("/api/v1/records?type=income", headers=auth_headers(token))
        assert r.status_code == 200
        for item in r.json()["items"]:
            assert item["type"] == "income"

    def test_negative_amount_rejected(self):
        token = admin_token()
        r = client.post(
            "/api/v1/records",
            json={"amount": -100, "type": "expense", "category": "Food", "date": "2024-03-01"},
            headers=auth_headers(token),
        )
        assert r.status_code == 422

    def test_soft_delete(self):
        token = admin_token()
        r = self._create_record(token)
        record_id = r.json()["id"]
        del_r = client.delete(f"/api/v1/records/{record_id}", headers=auth_headers(token))
        assert del_r.status_code == 204
        # Verify it's gone from list
        get_r = client.get(f"/api/v1/records/{record_id}", headers=auth_headers(token))
        assert get_r.status_code == 404

    def test_update_record(self):
        token = admin_token()
        r = self._create_record(token)
        record_id = r.json()["id"]
        up = client.patch(
            f"/api/v1/records/{record_id}",
            json={"category": "Freelance", "amount": 750.00},
            headers=auth_headers(token),
        )
        assert up.status_code == 200
        assert up.json()["category"] == "Freelance"


# ── Dashboard Tests ───────────────────────────────────────────────────────────

class TestDashboard:
    def test_summary_viewer(self):
        r = client.post("/api/v1/auth/login", json={"email": "viewer@test.com", "password": "Viewer@123"})
        token = r.json()["access_token"]
        r2 = client.get("/api/v1/dashboard/summary", headers=auth_headers(token))
        assert r2.status_code == 200
        data = r2.json()
        assert "total_income" in data
        assert "net_balance" in data

    def test_insights_viewer_forbidden(self):
        r = client.post("/api/v1/auth/login", json={"email": "viewer@test.com", "password": "Viewer@123"})
        token = r.json()["access_token"]
        r2 = client.get("/api/v1/dashboard/insights", headers=auth_headers(token))
        assert r2.status_code == 403

    def test_insights_analyst(self):
        r = client.post("/api/v1/auth/login", json={"email": "analyst@test.com", "password": "Analyst@123"})
        token = r.json()["access_token"]
        r2 = client.get("/api/v1/dashboard/insights", headers=auth_headers(token))
        assert r2.status_code == 200
        data = r2.json()
        assert "monthly_trends" in data
        assert "category_totals_income" in data

    def test_insights_admin(self):
        token = admin_token()
        r = client.get("/api/v1/dashboard/insights", headers=auth_headers(token))
        assert r.status_code == 200
