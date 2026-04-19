from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserUpdate, UserOut, UserOutFull
from app.services import user_service
from app.middleware.auth import get_current_user, require_permission, require_admin
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserOut, status_code=201, summary="Create a new user (Admin only)")
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return user_service.create_user(data, db)


@router.get("", summary="List all users (Admin only)")
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = user_service.list_users(db, page, page_size)
    result["items"] = [UserOut.model_validate(u) for u in result["items"]]
    return result


@router.get("/{user_id}", response_model=UserOutFull, summary="Get user by ID (Admin only)")
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return user_service.get_user_by_id(user_id, db)


@router.patch("/{user_id}", response_model=UserOut, summary="Update user")
def update_user(
    user_id: str,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Admins can update any user's name, role, and status.
    Non-admins can only update their own name.
    """
    return user_service.update_user(user_id, data, db, current_user)


@router.delete("/{user_id}", status_code=204, summary="Delete user (Admin only)")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user_service.delete_user(user_id, db, current_user)
