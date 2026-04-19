from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from app.core.permissions import Role
import re


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Role = Role.VIEWER

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        if len(v) > 120:
            raise ValueError("Name must be 120 chars or fewer")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[Role] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: Role
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserOutFull(UserOut):
    updated_at: datetime
