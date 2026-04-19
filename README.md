
#💰 Finance Data Processing & Access Control Backend

A production-ready backend system for managing financial records, role-based user access, analytics dashboards, and secure authentication.

🚀 **Live API Docs:** http://13.60.225.199:8000/docs  
📘 **ReDoc Docs:** http://13.60.225.199:8000/redoc

---

## 📌 Project Overview

This project was built as a backend engineering assignment focused on:

- Clean API architecture
- Role-based access control (RBAC)
- Financial records CRUD operations
- Dashboard analytics
- Validation & error handling
- Scalable project structure
- Production deployment

---

## ⚙️ Tech Stack

| Layer | Technology |
|------|------------|
| Backend Framework | FastAPI |
| Language | Python 3.11 |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Authentication | JWT Tokens |
| Password Hashing | Passlib |
| Migrations | Alembic |
| Cache | Redis |
| Deployment | AWS EC2 |
| Testing | Pytest |

---

## ✨ Key Features

### 🔐 Authentication
- JWT Login
- Access Token + Refresh Token
- Secure Password Hashing

### 👥 Role-Based Access Control

Three user roles:

| Role | Permissions |
|------|------------|
| Viewer | View records + dashboard |
| Analyst | Viewer + insights |
| Admin | Full access |

---

### 💳 Financial Records Management

Manage records with:

- Amount
- Type (Income / Expense)
- Category
- Date
- Notes

Operations:

- Create record
- View records
- Update record
- Delete record
- Filter by type/date/category

---

### 📊 Dashboard APIs

Includes:

- Total Income
- Total Expenses
- Net Balance
- Category-wise totals
- Monthly trends
- Recent transactions

---

## 📁 Project Structure

```bash
finance_backend/
│── app/
│   ├── main.py
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── middleware/
│
│── tests/
│── alembic/
│── Dockerfile
│── docker-compose.yml
│── requirements.txt
│── README.md
````

---

## 🔗 Main API Endpoints

### Auth

| Method | Endpoint             |
| ------ | -------------------- |
| POST   | /api/v1/auth/login   |
| POST   | /api/v1/auth/refresh |
| GET    | /api/v1/auth/me      |

---

### Users

| Method | Endpoint           |
| ------ | ------------------ |
| POST   | /api/v1/users      |
| GET    | /api/v1/users      |
| PATCH  | /api/v1/users/{id} |
| DELETE | /api/v1/users/{id} |

---

### Financial Records

| Method | Endpoint             |
| ------ | -------------------- |
| POST   | /api/v1/records      |
| GET    | /api/v1/records      |
| PATCH  | /api/v1/records/{id} |
| DELETE | /api/v1/records/{id} |

---

### Dashboard

| Method | Endpoint                   |
| ------ | -------------------------- |
| GET    | /api/v1/dashboard/summary  |
| GET    | /api/v1/dashboard/insights |

---

## 🖥️ Run Locally

### Clone Repo

```bash
git clone https://github.com/YOUR_USERNAME/finance-backend.git
cd finance-backend
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Server

```bash
uvicorn app.main:app --reload
```

---

## 🐳 Run with Docker

```bash
docker compose up --build
```

---

## 🔐 Default Admin Login

```text
Email: admin@example.com
Password: Admin@123
```

---

## 🧪 Run Tests

```bash
pytest -v
```

---

## ☁️ Deployment

Deployed on AWS EC2 with Docker.

Live Server:

[http://13.60.225.199:8000](http://13.60.225.199:8000)

---

## 💡 Design Highlights

### Soft Delete

Records are not permanently removed.

### Secure JWT Auth

Short-lived access token + refresh token.

### Clean Architecture

Routes → Services → Models

### Precision Handling

Used Decimal/Numeric for financial calculations.

---

## 📈 Future Improvements

* Frontend Dashboard (React)
* Audit Logs
* Export CSV/PDF
* Email Alerts
* Charts Integration

---

## 👨‍💻 Author

**Ashwith Gowda**

Python Backend Developer | FastAPI | Django | PostgreSQL | AWS

---

## ⭐ If you like this project, give it a star!

```
```
