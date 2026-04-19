from sqlalchemy.orm import Session
from app.db.session import engine, Base
from app.models import user, financial_record  # ensure models are registered
from app.core.config import settings
from app.core.security import hash_password
from app.core.permissions import Role
from app.models.user import User


def init_db() -> None:
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def seed_admin(db: Session) -> None:
    """Create the first admin user if none exists."""
    existing = db.query(User).filter(User.role == Role.ADMIN).first()
    if existing:
        return

    admin = User(
        name=settings.FIRST_ADMIN_NAME,
        email=settings.FIRST_ADMIN_EMAIL,
        hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD),
        role=Role.ADMIN,
    )
    db.add(admin)
    db.commit()
    print(f"[seed] Admin user created: {settings.FIRST_ADMIN_EMAIL}")
