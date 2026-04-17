"""FastAPI routes for holiday management."""

import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.auth.rbac import require_role
from backend.app.database import get_session
from backend.app.dependencies import get_company_id
from backend.app.models.holiday import HolidayCalendar
from backend.app.schemas import HolidayCreate


router = APIRouter(prefix="/holidays", tags=["holidays"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role("hr_admin")],
)
async def create_holiday(
    data: HolidayCreate,
    company_id: uuid.UUID = Depends(get_company_id),
    session: AsyncSession = Depends(get_session),
):
    """Create a new holiday (HR_ADMIN only)."""
    if data.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create holiday for different company",
        )

    # Check if holiday already exists
    existing_query = select(HolidayCalendar).where(
        and_(
            HolidayCalendar.company_id == company_id,
            HolidayCalendar.holiday_date == data.holiday_date,
        )
    )
    existing_result = await session.execute(existing_query)
    existing = existing_result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Holiday already exists on {data.holiday_date}",
        )

    holiday = HolidayCalendar(
        company_id=data.company_id,
        holiday_date=data.holiday_date,
        holiday_name=data.holiday_name,
        is_public_holiday=data.is_public_holiday,
    )
    session.add(holiday)

    try:
        await session.commit()
        return {"id": str(holiday.id), "message": "Holiday created successfully"}
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create holiday",
        )


@router.get("")
async def list_holidays(
    company_id: uuid.UUID = Depends(get_company_id),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """List holidays for a company within a date range."""
    filters = [HolidayCalendar.company_id == company_id]

    if start_date:
        filters.append(HolidayCalendar.holiday_date >= start_date)
    if end_date:
        filters.append(HolidayCalendar.holiday_date <= end_date)

    query = select(HolidayCalendar).where(and_(*filters))
    result = await session.execute(query)
    holidays = result.scalars().all()

    return [
        {
            "id": str(h.id),
            "holiday_date": h.holiday_date,
            "holiday_name": h.holiday_name,
            "is_public_holiday": h.is_public_holiday,
        }
        for h in holidays
    ]


@router.delete(
    "/{holiday_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[require_role("hr_admin")],
)
async def delete_holiday(
    holiday_id: uuid.UUID,
    company_id: uuid.UUID = Depends(get_company_id),
    session: AsyncSession = Depends(get_session),
):
    """Delete a holiday (HR_ADMIN only)."""
    query = select(HolidayCalendar).where(
        and_(
            HolidayCalendar.id == holiday_id,
            HolidayCalendar.company_id == company_id,
        )
    )
    result = await session.execute(query)
    holiday = result.scalar_one_or_none()

    if not holiday:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holiday not found",
        )

    await session.delete(holiday)

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete holiday",
        )
