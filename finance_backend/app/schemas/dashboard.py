from pydantic import BaseModel
from typing import List
from decimal import Decimal

from fastapi_cache.decorator import cache


class CategoryTotal(BaseModel):
    category: str
    total: Decimal


class MonthlyTrend(BaseModel):
    year: int
    month: int
    income: Decimal
    expense: Decimal
    net: Decimal


class DashboardSummary(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal
    record_count: int
    income_count: int
    expense_count: int


class DashboardInsights(BaseModel):
    summary: DashboardSummary
    category_totals_income: List[CategoryTotal]
    category_totals_expense: List[CategoryTotal]
    monthly_trends: List[MonthlyTrend]
    recent_records: List  # List[RecordOut] — typed in service to avoid circular import



