from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, AccessTokenResponse
from app.schemas.user import UserOut
from app.services import auth_service
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, summary="Login and receive JWT tokens")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with email + password. Returns access and refresh tokens.
    """
    return auth_service.login(request, db)


@router.post("/refresh", response_model=AccessTokenResponse, summary="Refresh access token")
def refresh(request: RefreshRequest, db: Session = Depends(get_db)):
    """
    Exchange a valid refresh token for a new access token.
    """
    return auth_service.refresh_access_token(request.refresh_token, db)


@router.get("/me", response_model=UserOut, summary="Get current user profile")
def me(current_user: User = Depends(get_current_user)):
    return current_user
