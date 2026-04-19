from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from app.models.financial_record import FinancialRecord, TxType
from app.models.user import User
from app.schemas.record import RecordCreate, RecordUpdate, RecordFilter, PaginatedRecords


def create_record(data: RecordCreate, db: Session, current_user: User) -> FinancialRecord:
    record = FinancialRecord(
        amount=data.amount,
        type=data.type,
        category=data.category.strip(),
        date=data.date,
        notes=data.notes,
        created_by=current_user.id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_records(filters: RecordFilter, db: Session) -> PaginatedRecords:
    query = db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)

    if filters.type:
        query = query.filter(FinancialRecord.type == filters.type)
    if filters.category:
        query = query.filter(FinancialRecord.category.ilike(f"%{filters.category}%"))
    if filters.date_from:
        query = query.filter(FinancialRecord.date >= filters.date_from)
    if filters.date_to:
        query = query.filter(FinancialRecord.date <= filters.date_to)

    total = query.count()
    items = (
        query.order_by(FinancialRecord.date.desc(), FinancialRecord.created_at.desc())
        .offset((filters.page - 1) * filters.page_size)
        .limit(filters.page_size)
        .all()
    )

    return PaginatedRecords(
        total=total,
        page=filters.page,
        page_size=filters.page_size,
        items=items,
    )


def get_record(record_id: str, db: Session) -> FinancialRecord:
    record = (
        db.query(FinancialRecord)
        .filter(FinancialRecord.id == record_id, FinancialRecord.is_deleted == False)
        .first()
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


def update_record(record_id: str, data: RecordUpdate, db: Session, current_user: User) -> FinancialRecord:
    record = get_record(record_id, db)

    update_data = data.model_dump(exclude_unset=True)
    if "category" in update_data and update_data["category"]:
        update_data["category"] = update_data["category"].strip()

    for field, value in update_data.items():
        setattr(record, field, value)

    record.updated_by = current_user.id
    db.commit()
    db.refresh(record)
    return record


def soft_delete_record(record_id: str, db: Session, current_user: User) -> None:
    record = get_record(record_id, db)
    record.is_deleted = True
    record.updated_by = current_user.id
    db.commit()
