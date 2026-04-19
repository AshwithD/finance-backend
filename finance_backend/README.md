# Finance Data Processing & Access Control Backend

A production-ready backend for a finance dashboard system built with **FastAPI**, **PostgreSQL**, **SQLAlchemy 2**, and **JWT authentication**.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.111 |
| Database | PostgreSQL (SQLite for tests) |
| ORM | SQLAlchemy 2 (mapped columns) |
| Auth | JWT via `python-jose` + `passlib[bcrypt]` |
| Validation | Pydantic v2 |
| Migrations | Alembic |
| Testing | Pytest + HTTPX TestClient |

---

## Project Structure

```
finance_backend/
├── app/
│   ├── main.py                  # FastAPI app, lifespan, CORS, error handlers
│   ├── api/v1/
│   │   ├── router.py            # Aggregates all routers under /api/v1
│   │   └── endpoints/
│   │       ├── auth.py          # /auth  — login, refresh, me
│   │       ├── users.py         # /users — CRUD (admin-gated)
│   │       ├── records.py       # /records — financial record CRUD + filter
│   │       └── dashboard.py     # /dashboard — summary + insights
│   ├── core/
│   │   ├── config.py            # Pydantic Settings (reads .env)
│   │   ├── security.py          # Password hashing, JWT encode/decode
│   │   └── permissions.py       # Role enum + permission map
│   ├── db/
│   │   ├── session.py           # SQLAlchemy engine + get_db dependency
│   │   └── init_db.py           # create_all + seed first admin
│   ├── middleware/
│   │   └── auth.py              # get_current_user, require_permission, require_admin
│   ├── models/
│   │   ├── user.py              # User ORM model
│   │   └── financial_record.py  # FinancialRecord ORM model
│   ├── schemas/
│   │   ├── auth.py              # Login/token schemas
│   │   ├── user.py              # UserCreate, UserUpdate, UserOut
│   │   ├── record.py            # RecordCreate, RecordUpdate, RecordOut, filters
│   │   └── dashboard.py         # Summary, insights, trend schemas
│   └── services/
│       ├── auth_service.py      # Login + refresh logic
│       ├── user_service.py      # User CRUD business logic
│       ├── record_service.py    # Record CRUD + soft delete
│       └── dashboard_service.py # Aggregation queries
├── tests/
│   └── test_api.py              # Integration tests (SQLite in-memory)
├── alembic/                     # DB migration scripts
├── alembic.ini
├── requirements.txt
└── .env.example
```

---

## Setup & Run

### 1. Clone and install

```bash
git clone <repo-url>
cd finance_backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — set DATABASE_URL and a strong SECRET_KEY
```


### 3. Start PostgreSQL

```bash
# Using Docker (recommended):
docker run -d \
  --name finance-pg \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=finance_db \
  -p 5432:5432 \
  postgres:16
```

### 4. Run migrations

```bash
alembic upgrade head
```

> On first startup, `init_db` also auto-creates tables and seeds the admin user defined in `.env`.

### 5. Start the server

```bash
uvicorn app.main:app --reload
```

API available at: http://localhost:8000  
Swagger UI: http://localhost:8000/docs  
ReDoc: http://localhost:8000/redoc

---

## Default Admin Credentials

```
Email:    admin@example.com
Password: Admin@123
```
Change these in `.env` before deploying.

---

## API Reference

### Authentication

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/v1/auth/login` | Login, get access + refresh tokens | Public |
| POST | `/api/v1/auth/refresh` | Exchange refresh token for new access token | Public |
| GET  | `/api/v1/auth/me` | Get current user profile | Any role |

**Login request:**
```json
POST /api/v1/auth/login
{ "email": "admin@example.com", "password": "Admin@123" }
```

**Login response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": { "id": "...", "name": "System Admin", "role": "admin", ... }
}
```

Use the `access_token` as `Authorization: Bearer <token>` on all protected routes.

---

### User Management

| Method | Path | Description | Role Required |
|--------|------|-------------|---------------|
| POST   | `/api/v1/users` | Create user | Admin |
| GET    | `/api/v1/users` | List users (paginated) | Admin |
| GET    | `/api/v1/users/{id}` | Get user by ID | Admin |
| PATCH  | `/api/v1/users/{id}` | Update user | Admin (full) / Self (name only) |
| DELETE | `/api/v1/users/{id}` | Delete user | Admin |

**Create user:**
```json
POST /api/v1/users
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "password": "Secure@123",
  "role": "analyst"
}
```
Password rules: min 8 chars, at least 1 uppercase, 1 digit.

---

### Financial Records

| Method | Path | Description | Role Required |
|--------|------|-------------|---------------|
| POST   | `/api/v1/records` | Create record | Admin |
| GET    | `/api/v1/records` | List records (filterable, paginated) | Viewer+ |
| GET    | `/api/v1/records/{id}` | Get single record | Viewer+ |
| PATCH  | `/api/v1/records/{id}` | Update record | Admin |
| DELETE | `/api/v1/records/{id}` | Soft-delete record | Admin |

**Create record:**
```json
POST /api/v1/records
{
  "amount": 5000.00,
  "type": "income",
  "category": "Salary",
  "date": "2024-03-15",
  "notes": "March salary"
}
```

**Filter records:**
```
GET /api/v1/records?type=expense&category=food&date_from=2024-01-01&date_to=2024-03-31&page=1&page_size=10
```

All query params are optional and combinable.

---

### Dashboard

| Method | Path | Description | Role Required |
|--------|------|-------------|---------------|
| GET | `/api/v1/dashboard/summary` | Basic totals + counts | Viewer+ |
| GET | `/api/v1/dashboard/insights` | Full analytics payload | Analyst+ |

**Summary response:**
```json
{
  "total_income": "15000.00",
  "total_expenses": "8400.00",
  "net_balance": "6600.00",
  "record_count": 24,
  "income_count": 10,
  "expense_count": 14
}
```

**Insights response includes:**
- `summary` — same as above
- `category_totals_income` — income broken down by category
- `category_totals_expense` — expenses broken down by category
- `monthly_trends` — last 12 months of income/expense/net per month
- `recent_records` — 10 most recent transactions

---

## Role Permission Matrix

| Permission | Viewer | Analyst | Admin |
|-----------|--------|---------|-------|
| `records:read` | ✅ | ✅ | ✅ |
| `records:create` | ❌ | ❌ | ✅ |
| `records:update` | ❌ | ❌ | ✅ |
| `records:delete` | ❌ | ❌ | ✅ |
| `records:export` | ❌ | ✅ | ✅ |
| `dashboard:read` | ✅ | ✅ | ✅ |
| `dashboard:insights` | ❌ | ✅ | ✅ |
| `users:*` | ❌ | ❌ | ✅ |

Permissions live in a single dictionary in `app/core/permissions.py` — easy to extend.

---

## Running Tests

Tests use **SQLite** in-memory — no Postgres needed.

```bash
pytest tests/ -v
```

Test coverage includes:
- Login success/failure, refresh tokens, bearer auth
- Admin-only user creation, duplicate email rejection, weak password rejection
- Viewer/analyst permission enforcement on records and dashboard
- Record filtering, soft delete, field updates
- Dashboard summary (all roles) and insights (analyst+ only)

---

## Design Decisions & Assumptions

### Soft Delete
Records are never hard-deleted. The `is_deleted` flag is set to `True` on DELETE. This preserves audit history. Deleted records are excluded from all queries and analytics.

### Atomic Permission System
Permissions are string constants (`"records:create"`) mapped per role in one place. The `require_permission("records:create")` FastAPI dependency enforces them at the route level — no scattered `if role == admin` checks.

### Token Pair Strategy
Login returns both an **access token** (short-lived, 30 min) and a **refresh token** (7 days). The `/auth/refresh` endpoint issues a new access token without re-login.

### UUID Primary Keys
All IDs are UUID strings to avoid sequential enumeration attacks and enable safe distributed generation.

### Pydantic v2 Validation
All inputs are validated by Pydantic before touching the DB. Amounts must be positive, passwords must meet strength requirements, categories can't be blank.

### No Hard-Coded Roles in Routes
Routes use `require_permission("some:permission")` rather than `require_admin()` directly (except user management which is explicitly admin-only). This makes the permission model easy to evolve without touching route code.

### SQLAlchemy 2 Style
Uses `Mapped[type]` + `mapped_column()` syntax (SQLAlchemy 2.0) rather than the legacy `Column()` style for type safety and IDE support.

---

## Possible Extensions

- **Rate limiting** via `slowapi` (token bucket per IP)
- **Audit log** table recording who changed what and when
- **CSV export** endpoint for analysts (`records:export` permission already defined)
- **Email verification** on user creation
- **Search** across notes/category with full-text index
