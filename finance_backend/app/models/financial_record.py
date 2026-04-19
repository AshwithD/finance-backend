import uuid
from datetime import datetime, timezone, date
from sqlalchemy import String, Numeric, Date, DateTime, Enum as SAEnum, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class TransactionType(str):
    INCOME = "income"
    EXPENSE = "expense"


import enum

class TxType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    type: Mapped[TxType] = mapped_column(SAEnum(TxType), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # soft delete

    # Who created / last modified
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    updated_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self) -> str:
        return f"<FinancialRecord {self.type} {self.amount} [{self.category}]>"
