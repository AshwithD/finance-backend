# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from app.db.session import get_db
# from app.schemas.dashboard import DashboardSummary, DashboardInsights
# from app.services import dashboard_service
# from app.middleware.auth import require_permission
# from app.models.user import User

# router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# @router.get(
#     "/summary",
#     response_model=DashboardSummary,
#     summary="Basic financial summary (Viewer+)",
# )
# def summary(
#     db: Session = Depends(get_db),
#     _: User = Depends(require_permission("dashboard:read")),
# ):
#     """
#     Returns total income, total expenses, net balance, and record counts.
#     Available to all authenticated users (Viewer, Analyst, Admin).
#     """
#     return dashboard_service.get_summary(db)


# @router.get(
#     "/insights",
#     response_model=DashboardInsights,
#     summary="Full insights with trends and breakdowns (Analyst+)",
# )
# def insights(
#     db: Session = Depends(get_db),
#     _: User = Depends(require_permission("dashboard:insights")),
# ):
#     """
#     Returns the full dashboard payload:
#     - Summary totals
#     - Category-wise breakdown (income & expense)
#     - Monthly trends (last 12 months)
#     - 10 most recent transactions

#     Requires Analyst or Admin role.
#     """
#     return dashboard_service.get_full_insights(db)



from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.dashboard import DashboardSummary, DashboardInsights
from app.services import dashboard_service
from app.middleware.auth import require_permission
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummary,
    summary="Basic financial summary (Viewer+)",
)
def summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("dashboard:read")),
):
    return dashboard_service.get_summary(db)


@router.get(
    "/insights",
    response_model=DashboardInsights,
    summary="Full insights with trends and breakdowns (Analyst+)",
)
def insights(
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("dashboard:insights")),
):
    return dashboard_service.get_full_insights(db)