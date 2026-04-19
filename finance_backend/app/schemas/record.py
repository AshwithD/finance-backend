from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, field_validator
from decimal import Decimal
from app.models.financial_record import TxType


class RecordCreate(BaseModel):
    amount: Decimal
    type: TxType
    category: str
    date: date
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v

    @field_validator("category")
    @classmethod
    def category_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Category cannot be empty")
        if len(v) > 100:
            raise ValueError("Category must be 100 chars or fewer")
        return v


class RecordUpdate(BaseModel):
    amount: Optional[Decimal] = None
    type: Optional[TxType] = None
    category: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v


class RecordOut(BaseModel):
    id: str
    amount: Decimal
    type: TxType
    category: str
    date: date
    notes: Optional[str]
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecordFilter(BaseModel):
    type: Optional[TxType] = None
    category: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    page: int = 1
    page_size: int = 20

    @field_validator("page")
    @classmethod
    def page_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Page must be >= 1")
        return v

    @field_validator("page_size")
    @classmethod
    def page_size_range(cls, v: int) -> int:
        if not (1 <= v <= 100):
            raise ValueError("page_size must be between 1 and 100")
        return v


class PaginatedRecords(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[RecordOut]
