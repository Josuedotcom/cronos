"""FastAPI routes for payroll queries and reports."""

import uuid
from datetime import date
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.auth.rbac import require_role
from backend.app.database import get_session
from backend.app.dependencies import get_company_id, get_user_id, get_user_role
from backend.app.models.shift import TimesheetDay


router = APIRouter(prefix="/payroll", tags=["payroll"])


# Response schemas (inline for now)
class PayrollDailyResponse:
    worker_id: uuid.UUID
    timesheet_date: date
    ordinary_hours: Decimal
    night_hours: Decimal
    sunday_day_hours: Decimal
    sunday_night_hours: Decimal
    overtime_day: Decimal
    overtime_night: Decimal
    overtime_sunday_day: Decimal
    overtime_sunday_night: Decimal
    total_regular_amount: Optional[Decimal]
    total_surcharge_amount: Optional[Decimal]
    total_gross_amount: Optional[Decimal]


class PayrollPeriodResponse:
    worker_id: uuid.UUID
    start_date: date
    end_date: date
    total_ordinary_hours: Decimal
    total_night_hours: Decimal
    total_sunday_day_hours: Decimal
    total_sunday_night_hours: Decimal
    total_overtime_day: Decimal
    total_overtime_night: Decimal
    total_overtime_sunday_day: Decimal
    total_overtime_sunday_night: Decimal
    total_regular_amount: Decimal
    total_surcharge_amount: Decimal
    total_gross_amount: Decimal
    daily_breakdown: List[PayrollDailyResponse]


@router.get("/daily/{worker_id}")
async def get_daily_payroll(
    worker_id: uuid.UUID,
    date_param: date = Query(..., alias="date"),
    company_id: uuid.UUID = Depends(get_company_id),
    user_id: uuid.UUID = Depends(get_user_id),
    user_role: str = Depends(get_user_role),
    session: AsyncSession = Depends(get_session),
):
    """
    Get payroll breakdown for a single day.

    RBAC:
    - WORKER: Can only see own payroll
    - MANAGER: Can see team payroll
    - HR_ADMIN: Can see all payroll
    """
    # RBAC: WORKER can only see own
    if user_role == "worker" and worker_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view other worker's payroll",
        )

    query = select(TimesheetDay).where(
        and_(
            TimesheetDay.worker_id == worker_id,
            TimesheetDay.timesheet_date == date_param,
            TimesheetDay.company_id == company_id,
        )
    )
    result = await session.execute(query)
    timesheet = result.scalar_one_or_none()

    if not timesheet:
        return {
            "worker_id": str(worker_id),
            "timesheet_date": date_param,
            "ordinary_hours": Decimal("0.00"),
            "night_hours": Decimal("0.00"),
            "sunday_day_hours": Decimal("0.00"),
            "sunday_night_hours": Decimal("0.00"),
            "overtime_day": Decimal("0.00"),
            "overtime_night": Decimal("0.00"),
            "overtime_sunday_day": Decimal("0.00"),
            "overtime_sunday_night": Decimal("0.00"),
            "total_regular_amount": None,
            "total_surcharge_amount": None,
            "total_gross_amount": None,
        }

    return {
        "worker_id": str(worker_id),
        "timesheet_date": timesheet.timesheet_date,
        "ordinary_hours": timesheet.ordinary_hours or Decimal("0.00"),
        "night_hours": timesheet.night_hours or Decimal("0.00"),
        "sunday_day_hours": timesheet.sunday_day_hours or Decimal("0.00"),
        "sunday_night_hours": timesheet.sunday_night_hours or Decimal("0.00"),
        "overtime_day": timesheet.overtime_day or Decimal("0.00"),
        "overtime_night": timesheet.overtime_night or Decimal("0.00"),
        "overtime_sunday_day": timesheet.overtime_sunday_day or Decimal("0.00"),
        "overtime_sunday_night": timesheet.overtime_sunday_night or Decimal("0.00"),
        "total_regular_amount": timesheet.total_regular_amount,
        "total_surcharge_amount": timesheet.total_surcharge_amount,
        "total_gross_amount": timesheet.total_gross_amount,
    }


@router.get("/worker/{worker_id}")
async def get_worker_payroll(
    worker_id: uuid.UUID,
    start_date: date = Query(...),
    end_date: date = Query(...),
    company_id: uuid.UUID = Depends(get_company_id),
    user_id: uuid.UUID = Depends(get_user_id),
    user_role: str = Depends(get_user_role),
    session: AsyncSession = Depends(get_session),
):
    """
    Get aggregated payroll for a worker during a period.

    RBAC:
    - WORKER: Can only see own payroll
    - MANAGER: Can see team payroll
    - HR_ADMIN: Can see all payroll
    """
    # RBAC: WORKER can only see own
    if user_role == "worker" and worker_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view other worker's payroll",
        )

    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be <= end_date",
        )

    # Get all timesheet days for the period
    query = select(TimesheetDay).where(
        and_(
            TimesheetDay.worker_id == worker_id,
            TimesheetDay.timesheet_date >= start_date,
            TimesheetDay.timesheet_date <= end_date,
            TimesheetDay.company_id == company_id,
        )
    )
    result = await session.execute(query)
    timesheets = result.scalars().all()

    # Aggregate
    total_ordinary = Decimal("0.00")
    total_night = Decimal("0.00")
    total_sunday_day = Decimal("0.00")
    total_sunday_night = Decimal("0.00")
    total_overtime_day = Decimal("0.00")
    total_overtime_night = Decimal("0.00")
    total_overtime_sunday_day = Decimal("0.00")
    total_overtime_sunday_night = Decimal("0.00")
    total_regular_amount = Decimal("0.00")
    total_surcharge_amount = Decimal("0.00")
    total_gross_amount = Decimal("0.00")

    daily_breakdown = []

    for ts in timesheets:
        total_ordinary += ts.ordinary_hours or Decimal("0.00")
        total_night += ts.night_hours or Decimal("0.00")
        total_sunday_day += ts.sunday_day_hours or Decimal("0.00")
        total_sunday_night += ts.sunday_night_hours or Decimal("0.00")
        total_overtime_day += ts.overtime_day or Decimal("0.00")
        total_overtime_night += ts.overtime_night or Decimal("0.00")
        total_overtime_sunday_day += ts.overtime_sunday_day or Decimal("0.00")
        total_overtime_sunday_night += ts.overtime_sunday_night or Decimal("0.00")
        total_regular_amount += ts.total_regular_amount or Decimal("0.00")
        total_surcharge_amount += ts.total_surcharge_amount or Decimal("0.00")
        total_gross_amount += ts.total_gross_amount or Decimal("0.00")

        daily_breakdown.append(
            {
                "timesheet_date": ts.timesheet_date,
                "ordinary_hours": ts.ordinary_hours or Decimal("0.00"),
                "night_hours": ts.night_hours or Decimal("0.00"),
                "total_gross_amount": ts.total_gross_amount or Decimal("0.00"),
            }
        )

    return {
        "worker_id": str(worker_id),
        "start_date": start_date,
        "end_date": end_date,
        "total_ordinary_hours": total_ordinary,
        "total_night_hours": total_night,
        "total_sunday_day_hours": total_sunday_day,
        "total_sunday_night_hours": total_sunday_night,
        "total_overtime_day": total_overtime_day,
        "total_overtime_night": total_overtime_night,
        "total_overtime_sunday_day": total_overtime_sunday_day,
        "total_overtime_sunday_night": total_overtime_sunday_night,
        "total_regular_amount": total_regular_amount,
        "total_surcharge_amount": total_surcharge_amount,
        "total_gross_amount": total_gross_amount,
        "daily_breakdown": daily_breakdown,
    }


@router.get(
    "/summary",
    dependencies=[require_role("hr_admin")],
)
async def get_payroll_summary(
    start_date: date = Query(...),
    end_date: date = Query(...),
    company_id: uuid.UUID = Depends(get_company_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Get company-wide payroll summary for a period (HR_ADMIN only).

    Uses SQL aggregation for efficiency.
    """
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be <= end_date",
        )

    # Use SQL aggregation for efficiency
    query = select(
        func.count(TimesheetDay.id).label("total_days"),
        func.sum(TimesheetDay.ordinary_hours).label("total_ordinary_hours"),
        func.sum(TimesheetDay.night_hours).label("total_night_hours"),
        func.sum(TimesheetDay.sunday_day_hours).label("total_sunday_day_hours"),
        func.sum(TimesheetDay.sunday_night_hours).label("total_sunday_night_hours"),
        func.sum(TimesheetDay.overtime_day).label("total_overtime_day"),
        func.sum(TimesheetDay.overtime_night).label("total_overtime_night"),
        func.sum(TimesheetDay.total_regular_amount).label("total_regular_amount"),
        func.sum(TimesheetDay.total_surcharge_amount).label("total_surcharge_amount"),
        func.sum(TimesheetDay.total_gross_amount).label("total_gross_amount"),
    ).where(
        and_(
            TimesheetDay.company_id == company_id,
            TimesheetDay.timesheet_date >= start_date,
            TimesheetDay.timesheet_date <= end_date,
        )
    )

    result = await session.execute(query)
    row = result.one()

    return {
        "company_id": str(company_id),
        "start_date": start_date,
        "end_date": end_date,
        "total_days": row.total_days or 0,
        "total_ordinary_hours": row.total_ordinary_hours or Decimal("0.00"),
        "total_night_hours": row.total_night_hours or Decimal("0.00"),
        "total_sunday_day_hours": row.total_sunday_day_hours or Decimal("0.00"),
        "total_sunday_night_hours": row.total_sunday_night_hours or Decimal("0.00"),
        "total_overtime_day": row.total_overtime_day or Decimal("0.00"),
        "total_overtime_night": row.total_overtime_night or Decimal("0.00"),
        "total_regular_amount": row.total_regular_amount or Decimal("0.00"),
        "total_surcharge_amount": row.total_surcharge_amount or Decimal("0.00"),
        "total_gross_amount": row.total_gross_amount or Decimal("0.00"),
    }
