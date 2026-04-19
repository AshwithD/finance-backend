from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.financial_record import FinancialRecord, TxType
from app.schemas.dashboard import (
    DashboardSummary,
    CategoryTotal,
    MonthlyTrend,
    DashboardInsights,
)
from app.schemas.record import RecordOut


def get_summary(db: Session) -> DashboardSummary:
    base = db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)

    total_income = (
        base.filter(FinancialRecord.type == TxType.INCOME)
        .with_entities(func.coalesce(func.sum(FinancialRecord.amount), 0))
        .scalar()
    )
    total_expenses = (
        base.filter(FinancialRecord.type == TxType.EXPENSE)
        .with_entities(func.coalesce(func.sum(FinancialRecord.amount), 0))
        .scalar()
    )
    income_count = base.filter(FinancialRecord.type == TxType.INCOME).count()
    expense_count = base.filter(FinancialRecord.type == TxType.EXPENSE).count()

    return DashboardSummary(
        total_income=Decimal(str(total_income)),
        total_expenses=Decimal(str(total_expenses)),
        net_balance=Decimal(str(total_income)) - Decimal(str(total_expenses)),
        record_count=income_count + expense_count,
        income_count=income_count,
        expense_count=expense_count,
    )


def get_category_totals(db: Session, tx_type: TxType) -> list[CategoryTotal]:
    base = db.query(FinancialRecord).filter(
        FinancialRecord.is_deleted == False,
        FinancialRecord.type == tx_type,
    )
    rows = (
        base.with_entities(
            FinancialRecord.category,
            func.sum(FinancialRecord.amount).label("total"),
        )
        .group_by(FinancialRecord.category)
        .order_by(func.sum(FinancialRecord.amount).desc())
        .all()
    )
    return [CategoryTotal(category=r.category, total=Decimal(str(r.total))) for r in rows]


def get_monthly_trends(db: Session, months: int = 12) -> list[MonthlyTrend]:
    rows = (
        db.query(
            extract("year", FinancialRecord.date).label("year"),
            extract("month", FinancialRecord.date).label("month"),
            FinancialRecord.type,
            func.sum(FinancialRecord.amount).label("total"),
        )
        .filter(FinancialRecord.is_deleted == False)
        .group_by("year", "month", FinancialRecord.type)
        .order_by("year", "month")
        .all()
    )

    # Aggregate into monthly buckets
    bucket: dict[tuple, dict] = {}
    for row in rows:
        key = (int(row.year), int(row.month))
        if key not in bucket:
            bucket[key] = {"income": Decimal(0), "expense": Decimal(0)}
        if row.type == TxType.INCOME:
            bucket[key]["income"] += Decimal(str(row.total))
        else:
            bucket[key]["expense"] += Decimal(str(row.total))

    return [
        MonthlyTrend(
            year=y,
            month=m,
            income=v["income"],
            expense=v["expense"],
            net=v["income"] - v["expense"],
        )
        for (y, m), v in sorted(bucket.items())
    ][-months:]


def get_recent_records(db: Session, limit: int = 10) -> list[RecordOut]:
    records = (
        db.query(FinancialRecord)
        .filter(FinancialRecord.is_deleted == False)
        .order_by(FinancialRecord.date.desc(), FinancialRecord.created_at.desc())
        .limit(limit)
        .all()
    )
    return [RecordOut.model_validate(r) for r in records]


def get_full_insights(db: Session) -> DashboardInsights:
    return DashboardInsights(
        summary=get_summary(db),
        category_totals_income=get_category_totals(db, TxType.INCOME),
        category_totals_expense=get_category_totals(db, TxType.EXPENSE),
        monthly_trends=get_monthly_trends(db),
        recent_records=get_recent_records(db),
    )
