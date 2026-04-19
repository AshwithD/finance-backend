from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.core.security import hash_password
from app.schemas.user import UserCreate, UserUpdate, UserOut


def create_user(data: UserCreate, db: Session) -> User:
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{data.email}' already exists",
        )
    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_users(db: Session, page: int = 1, page_size: int = 20) -> dict:
    total = db.query(User).count()
    users = db.query(User).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "items": users}


def get_user_by_id(user_id: str, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def update_user(user_id: str, data: UserUpdate, db: Session, requesting_user: User) -> User:
    user = get_user_by_id(user_id, db)

    # Non-admins can only update their own profile (name only)
    from app.core.permissions import Role
    if requesting_user.role != Role.ADMIN:
        if requesting_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify another user")
        if data.role is not None or data.is_active is not None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can change role or status")

    if data.name is not None:
        user.name = data.name.strip()
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active

    db.commit()
    db.refresh(user)
    return user


def delete_user(user_id: str, db: Session, requesting_user: User) -> None:
    if requesting_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself")
    user = get_user_by_id(user_id, db)
    db.delete(user)
    db.commit()
