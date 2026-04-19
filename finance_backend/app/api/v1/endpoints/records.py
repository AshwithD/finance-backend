from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.record import RecordCreate, RecordUpdate, RecordOut, RecordFilter, PaginatedRecords
from app.services import record_service
from app.middleware.auth import require_permission, get_current_user
from app.models.user import User
from app.models.financial_record import TxType

router = APIRouter(prefix="/records", tags=["Financial Records"])


@router.post("", response_model=RecordOut, status_code=201, summary="Create a financial record (Admin only)")
def create_record(
    data: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("records:create")),
):
    return record_service.create_record(data, db, current_user)


@router.get("", response_model=PaginatedRecords, summary="List financial records (Viewer+)")
def list_records(
    type: Optional[TxType] = Query(None),
    category: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("records:read")),
):
    filters = RecordFilter(
        type=type,
        category=category,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    return record_service.list_records(filters, db)


@router.get("/{record_id}", response_model=RecordOut, summary="Get a single record (Viewer+)")
def get_record(
    record_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("records:read")),
):
    return record_service.get_record(record_id, db)


@router.patch("/{record_id}", response_model=RecordOut, summary="Update a record (Admin only)")
def update_record(
    record_id: str,
    data: RecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("records:update")),
):
    return record_service.update_record(record_id, data, db, current_user)


@router.delete("/{record_id}", status_code=204, summary="Soft-delete a record (Admin only)")
def delete_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("records:delete")),
):
    record_service.soft_delete_record(record_id, db, current_user)
