from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.router import api_router
from app.db.session import SessionLocal
from app.db.init_db import init_db, seed_admin

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables + seed admin
    init_db()
    db = SessionLocal()
    try:
        seed_admin(db)
    finally:
        db.close()

    redis = aioredis.from_url("redis://localhost:6379")
    FastAPICache.init(RedisBackend(redis), prefix="finance-cache")
    yield
    # Shutdown: nothing needed here


app = FastAPI(
    title="Finance Data Processing & Access Control API",
    description=(
        "Backend for a finance dashboard supporting role-based access control, "
        "financial record management, and aggregated analytics."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global exception handlers ─────────────────────────────────────────────────

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"detail": "A database error occurred. Please try again."},
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."},
    )


# ── Routes ────────────────────────────────────────────────────────────────────

app.include_router(api_router)


@app.get("/", tags=["Health"], summary="Health check")
def health():
    return {"status": "ok", "message": "Finance API is running"}
