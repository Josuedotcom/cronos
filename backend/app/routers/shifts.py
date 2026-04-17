"""FastAPI routes for shift management (templates and assignments)."""

import uuid
from datetime import date, time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.auth.rbac import require_role
from backend.app.database import get_session
from backend.app.dependencies import get_company_id, get_user_id, get_user_role
from backend.app.schemas import (
    ShiftTemplateCreate,
    ShiftTemplateRead,
    ShiftAssignmentCreate,
    TimesheetDayRead,
)
from backend.app.services.shift_service import ShiftService


router = APIRouter(prefix="/shifts", tags=["shifts"])


# ===== SHIFT TEMPLATE ENDPOINTS =====


@router.post(
    "/templates",
    response_model=ShiftTemplateRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role("manager", "hr_admin")],
)
async def create_shift_template(
    data: ShiftTemplateCreate,
    company_id: uuid.UUID = Depends(get_company_id),
    session: AsyncSession = Depends(get_session),
):
    """Create a new shift template (MANAGER or HR_ADMIN only)."""
    # Verify company_id matches authenticated user's company
    if data.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create template for different company",
        )

    service = ShiftService(session)

    try:
        template = await service.create_shift_template(
            company_id=data.company_id,
            suborganization_id=data.suborganization_id,
            area_id=data.area_id,
            code=data.code,
            name=data.name,
            start_time=data.start_time,
            end_time=data.end_time,
        )
        await session.commit()
        return template
    except ValueError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create shift template",
        )


@router.get("/templates", response_model=List[ShiftTemplateRead])
async def list_shift_templates(
    company_id: uuid.UUID = Depends(get_company_id),
    area_id: Optional[uuid.UUID] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """List all active shift templates for the company."""
    service = ShiftService(session)
    templates = await service.list_shift_templates(company_id, area_id=area_id)
    return templates


@router.get("/templates/{template_id}", response_model=ShiftTemplateRead)
async def get_shift_template(
    template_id: uuid.UUID,
    company_id: uuid.UUID = Depends(get_company_id),
    session: AsyncSession = Depends(get_session),
):
    """Get a specific shift template."""
    service = ShiftService(session)
    template = await service.get_shift_template(template_id, company_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift template not found",
        )
    return template


@router.put(
    "/templates/{template_id}",
    response_model=ShiftTemplateRead,
    dependencies=[require_role("manager", "hr_admin")],
)
async def update_shift_template(
    template_id: uuid.UUID,
    data: ShiftTemplateCreate,
    company_id: uuid.UUID = Depends(get_company_id),
    session: AsyncSession = Depends(get_session),
):
    """Update a shift template (MANAGER or HR_ADMIN only)."""
    if data.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update template for different company",
        )

    service = ShiftService(session)

    try:
        template = await service.update_shift_template(
            template_id,
            company_id,
            name=data.name,
            start_time=data.start_time,
            end_time=data.end_time,
        )
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shift template not found",
            )
        await session.commit()
        return template
    except ValueError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update shift template",
        )


@router.delete(
    "/templates/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[require_role("manager", "hr_admin")],
)
async def delete_shift_template(
    template_id: uuid.UUID,
    company_id: uuid.UUID = Depends(get_company_id),
    session: AsyncSession = Depends(get_session),
):
    """Soft-delete a shift template (MANAGER or HR_ADMIN only)."""
    service = ShiftService(session)
    success = await service.soft_delete_shift_template(template_id, company_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift template not found",
        )
    await session.commit()


# ===== SHIFT ASSIGNMENT ENDPOINTS =====


@router.post(
    "/assignments",
    response_model=TimesheetDayRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role("manager", "hr_admin")],
)
async def create_shift_assignment(
    data: ShiftAssignmentCreate,
    company_id: uuid.UUID = Depends(get_company_id),
    session: AsyncSession = Depends(get_session),
):
    """Create a new shift assignment (MANAGER or HR_ADMIN only)."""
    if data.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create assignment for different company",
        )

    service = ShiftService(session)

    try:
        assignment = await service.create_shift_assignment(
            worker_id=data.worker_id,
            template_id=data.template_id,
            assignment_date=data.assignment_date,
            company_id=data.company_id,
        )
        # Return the calculated timesheet_day
        timesheet = await service._calculate_timesheet_day(
            data.worker_id, data.assignment_date, data.company_id
        )
        await session.commit()
        return timesheet or {}
    except ValueError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create shift assignment",
        )


@router.get("/assignments", response_model=List[TimesheetDayRead])
async def list_shift_assignments(
    company_id: uuid.UUID = Depends(get_company_id),
    user_id: uuid.UUID = Depends(get_user_id),
    user_role: str = Depends(get_user_role),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    worker_id: Optional[uuid.UUID] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """List shift assignments (filtered by RBAC)."""
    service = ShiftService(session)

    # RBAC: WORKER can only see own assignments
    if user_role == "worker":
        worker_id = user_id

    assignments = await service.list_shift_assignments(
        company_id,
        start_date=start_date,
        end_date=end_date,
        worker_id=worker_id,
    )
    return assignments


@router.get(
    "/assignments/{assignment_id}",
    response_model=TimesheetDayRead,
)
async def get_shift_assignment(
    assignment_id: uuid.UUID,
    company_id: uuid.UUID = Depends(get_company_id),
    user_id: uuid.UUID = Depends(get_user_id),
    user_role: str = Depends(get_user_role),
    session: AsyncSession = Depends(get_session),
):
    """Get a specific shift assignment with payroll preview."""
    service = ShiftService(session)
    assignment = await service.get_shift_assignment(assignment_id, company_id)

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift assignment not found",
        )

    # RBAC: WORKER can only see own assignments
    if user_role == "worker" and assignment.worker_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view other worker's assignment",
        )

    # Return calculated timesheet
    timesheet = await service._calculate_timesheet_day(
        assignment.worker_id, assignment.assignment_date, company_id
    )
    return timesheet or {}


@router.put(
    "/assignments/{assignment_id}",
    response_model=TimesheetDayRead,
    dependencies=[require_role("manager", "hr_admin")],
)
async def update_shift_assignment(
    assignment_id: uuid.UUID,
    data: ShiftAssignmentCreate,
    company_id: uuid.UUID = Depends(get_company_id),
    session: AsyncSession = Depends(get_session),
):
    """Update a shift assignment (MANAGER or HR_ADMIN only)."""
    if data.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update assignment for different company",
        )

    service = ShiftService(session)

    try:
        assignment = await service.update_shift_assignment(
            assignment_id,
            company_id,
            template_id=data.template_id,
            assignment_date=data.assignment_date,
        )
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shift assignment not found",
            )
        timesheet = await service._calculate_timesheet_day(
            assignment.worker_id, assignment.assignment_date, company_id
        )
        await session.commit()
        return timesheet or {}
    except ValueError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update shift assignment",
        )


@router.delete(
    "/assignments/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[require_role("manager", "hr_admin")],
)
async def delete_shift_assignment(
    assignment_id: uuid.UUID,
    company_id: uuid.UUID = Depends(get_company_id),
    session: AsyncSession = Depends(get_session),
):
    """Soft-delete a shift assignment (MANAGER or HR_ADMIN only)."""
    service = ShiftService(session)
    success = await service.soft_delete_shift_assignment(assignment_id, company_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift assignment not found",
        )
    await session.commit()
