"""Shift management service layer for Cronos."""

import uuid
from datetime import date, datetime, time
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.shift import ShiftTemplate, ShiftAssignment, TimesheetDay
from backend.app.models.worker import Worker
from backend.app.models.holiday import HolidayCalendar
from backend.app.services.payroll_engine import HourClassifier, SurchargeCalculator


class ShiftService:
    """Service for shift template and assignment management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ===== SHIFT TEMPLATE OPERATIONS =====

    async def create_shift_template(
        self,
        company_id: uuid.UUID,
        suborganization_id: uuid.UUID,
        area_id: uuid.UUID,
        code: str,
        name: str,
        start_time: time,
        end_time: time,
        description: Optional[str] = None,
    ) -> ShiftTemplate:
        """Create a new shift template."""
        if start_time >= end_time:
            raise ValueError("start_time must be before end_time")

        template = ShiftTemplate(
            company_id=company_id,
            suborganization_id=suborganization_id,
            area_id=area_id,
            code=code,
            name=name,
            start_time=start_time,
            end_time=end_time,
            description=description,
            is_active=True,
        )
        self.session.add(template)
        await self.session.flush()
        return template

    async def get_shift_template(
        self, template_id: uuid.UUID, company_id: uuid.UUID
    ) -> Optional[ShiftTemplate]:
        """Get a shift template by ID (with multi-tenant check)."""
        query = select(ShiftTemplate).where(
            and_(
                ShiftTemplate.id == template_id,
                ShiftTemplate.company_id == company_id,
                ShiftTemplate.is_active == True,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_shift_templates(
        self, company_id: uuid.UUID, area_id: Optional[uuid.UUID] = None
    ) -> List[ShiftTemplate]:
        """List all active shift templates for a company."""
        filters = [
            ShiftTemplate.company_id == company_id,
            ShiftTemplate.is_active == True,
        ]
        if area_id:
            filters.append(ShiftTemplate.area_id == area_id)

        query = select(ShiftTemplate).where(and_(*filters))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_shift_template(
        self,
        template_id: uuid.UUID,
        company_id: uuid.UUID,
        name: Optional[str] = None,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        description: Optional[str] = None,
    ) -> Optional[ShiftTemplate]:
        """Update a shift template."""
        template = await self.get_shift_template(template_id, company_id)
        if not template:
            return None

        if name is not None:
            template.name = name
        if start_time is not None:
            template.start_time = start_time
        if end_time is not None:
            template.end_time = end_time
        if description is not None:
            template.description = description

        await self.session.flush()
        return template

    async def soft_delete_shift_template(
        self, template_id: uuid.UUID, company_id: uuid.UUID
    ) -> bool:
        """Soft-delete a shift template by marking is_active as False."""
        template = await self.get_shift_template(template_id, company_id)
        if not template:
            return False

        template.is_active = False
        await self.session.flush()
        return True

    # ===== SHIFT ASSIGNMENT OPERATIONS =====

    async def validate_shift_assignment(
        self,
        worker_id: uuid.UUID,
        template_id: uuid.UUID,
        assignment_date: date,
        company_id: uuid.UUID,
        exclude_assignment_id: Optional[uuid.UUID] = None,
    ) -> List[str]:
        """
        Validate a shift assignment before creation/update.
        Returns list of validation errors (empty = valid).
        """
        errors = []

        # Check if worker exists and belongs to company
        worker_query = select(Worker).where(
            and_(Worker.id == worker_id, Worker.company_id == company_id)
        )
        worker_result = await self.session.execute(worker_query)
        worker = worker_result.scalar_one_or_none()
        if not worker:
            errors.append(f"Worker {worker_id} not found in company {company_id}")
            return errors

        # Check if template exists and belongs to company
        template = await self.get_shift_template(template_id, company_id)
        if not template:
            errors.append(
                f"Shift template {template_id} not found in company {company_id}"
            )
            return errors

        # Check for duplicate assignment (same worker, same date)
        conflict_filters = [
            ShiftAssignment.worker_id == worker_id,
            ShiftAssignment.assignment_date == assignment_date,
            ShiftAssignment.company_id == company_id,
            ShiftAssignment.status != "absent",
        ]
        if exclude_assignment_id:
            conflict_filters.append(ShiftAssignment.id != exclude_assignment_id)

        conflict_query = select(ShiftAssignment).where(and_(*conflict_filters))
        conflict_result = await self.session.execute(conflict_query)
        existing = conflict_result.scalar_one_or_none()

        if existing:
            errors.append(f"Worker already has a shift assignment on {assignment_date}")

        return errors

    async def create_shift_assignment(
        self,
        worker_id: uuid.UUID,
        template_id: uuid.UUID,
        assignment_date: date,
        company_id: uuid.UUID,
        is_overtime_shift: bool = False,
        notes: Optional[str] = None,
    ) -> ShiftAssignment:
        """Create a new shift assignment."""
        # Validate before creating
        errors = await self.validate_shift_assignment(
            worker_id, template_id, assignment_date, company_id
        )
        if errors:
            raise ValueError(f"Validation errors: {', '.join(errors)}")

        assignment = ShiftAssignment(
            company_id=company_id,
            worker_id=worker_id,
            shift_template_id=template_id,
            assignment_date=assignment_date,
            status="scheduled",
            is_overtime_shift=is_overtime_shift,
            notes=notes,
        )
        self.session.add(assignment)
        await self.session.flush()

        # Trigger payroll calculation
        await self._calculate_timesheet_day(worker_id, assignment_date, company_id)

        return assignment

    async def get_shift_assignment(
        self, assignment_id: uuid.UUID, company_id: uuid.UUID
    ) -> Optional[ShiftAssignment]:
        """Get a shift assignment by ID."""
        query = select(ShiftAssignment).where(
            and_(
                ShiftAssignment.id == assignment_id,
                ShiftAssignment.company_id == company_id,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_shift_assignments(
        self,
        company_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        worker_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
    ) -> List[ShiftAssignment]:
        """List shift assignments with optional filtering."""
        filters = [ShiftAssignment.company_id == company_id]

        if start_date:
            filters.append(ShiftAssignment.assignment_date >= start_date)
        if end_date:
            filters.append(ShiftAssignment.assignment_date <= end_date)
        if worker_id:
            filters.append(ShiftAssignment.worker_id == worker_id)
        if status:
            filters.append(ShiftAssignment.status == status)

        query = select(ShiftAssignment).where(and_(*filters))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_shift_assignment(
        self,
        assignment_id: uuid.UUID,
        company_id: uuid.UUID,
        template_id: Optional[uuid.UUID] = None,
        assignment_date: Optional[date] = None,
        status: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[ShiftAssignment]:
        """Update a shift assignment."""
        assignment = await self.get_shift_assignment(assignment_id, company_id)
        if not assignment:
            return None

        # If changing template or date, validate
        if template_id or assignment_date:
            new_template_id = template_id or assignment.shift_template_id
            new_date = assignment_date or assignment.assignment_date
            errors = await self.validate_shift_assignment(
                assignment.worker_id,
                new_template_id,
                new_date,
                company_id,
                exclude_assignment_id=assignment_id,
            )
            if errors:
                raise ValueError(f"Validation errors: {', '.join(errors)}")

        if template_id:
            assignment.shift_template_id = template_id
        if assignment_date:
            assignment.assignment_date = assignment_date
        if status:
            assignment.status = status
        if notes is not None:
            assignment.notes = notes

        await self.session.flush()

        # Recalculate payroll if date changed
        if assignment_date:
            await self._calculate_timesheet_day(
                assignment.worker_id, assignment_date, company_id
            )
        else:
            await self._calculate_timesheet_day(
                assignment.worker_id, assignment.assignment_date, company_id
            )

        return assignment

    async def soft_delete_shift_assignment(
        self, assignment_id: uuid.UUID, company_id: uuid.UUID
    ) -> bool:
        """Soft-delete a shift assignment."""
        assignment = await self.get_shift_assignment(assignment_id, company_id)
        if not assignment:
            return False

        assignment.status = "cancelled"
        await self.session.flush()

        # Recalculate payroll for that day
        await self._calculate_timesheet_day(
            assignment.worker_id, assignment.assignment_date, company_id
        )

        return True

    # ===== PAYROLL CALCULATION (PRIVATE) =====

    async def _calculate_timesheet_day(
        self, worker_id: uuid.UUID, timesheet_date: date, company_id: uuid.UUID
    ) -> Optional[TimesheetDay]:
        """
        Calculate and cache payroll for a specific day.
        Called whenever shift assignments change.
        """
        # Get all assignments for this worker on this date
        assignments_query = select(ShiftAssignment).where(
            and_(
                ShiftAssignment.worker_id == worker_id,
                ShiftAssignment.assignment_date == timesheet_date,
                ShiftAssignment.company_id == company_id,
                ShiftAssignment.status.in_(["scheduled", "completed"]),
            )
        )
        assignments_result = await self.session.execute(assignments_query)
        assignments = assignments_result.scalars().all()

        # If no active assignments, delete/mark timesheet_day as zero
        if not assignments:
            existing_query = select(TimesheetDay).where(
                and_(
                    TimesheetDay.worker_id == worker_id,
                    TimesheetDay.timesheet_date == timesheet_date,
                    TimesheetDay.company_id == company_id,
                )
            )
            existing_result = await self.session.execute(existing_query)
            existing = existing_result.scalar_one_or_none()
            if existing:
                await self.session.delete(existing)
            return None

        # Get worker and holiday calendar
        worker_query = select(Worker).where(Worker.id == worker_id)
        worker_result = await self.session.execute(worker_query)
        worker = worker_result.scalar_one_or_none()
        if not worker:
            return None

        holidays_query = select(HolidayCalendar.holiday_date).where(
            HolidayCalendar.company_id == company_id
        )
        holidays_result = await self.session.execute(holidays_query)
        holidays = [row[0] for row in holidays_result.all()]

        # Classify hours using payroll engine
        classifier = HourClassifier(holidays=holidays)
        total_classification = None

        for assignment in assignments:
            # Get template
            template_query = select(ShiftTemplate).where(
                ShiftTemplate.id == assignment.shift_template_id
            )
            template_result = await self.session.execute(template_query)
            template = template_result.scalar_one_or_none()
            if not template:
                continue

            # Create datetime objects for shift
            start_dt = datetime.combine(timesheet_date, template.start_time)
            end_dt = datetime.combine(timesheet_date, template.end_time)

            # Handle overnight shifts
            if end_dt <= start_dt:
                end_dt = datetime.combine(
                    timesheet_date + __import__("datetime").timedelta(days=1),
                    template.end_time,
                )

            # Classify hours
            classification = classifier.classify(start_dt, end_dt)

            # Accumulate
            if total_classification is None:
                total_classification = classification
            else:
                total_classification.ordinary_hours += classification.ordinary_hours
                total_classification.night_hours += classification.night_hours
                total_classification.sunday_day_hours += classification.sunday_day_hours
                total_classification.sunday_night_hours += (
                    classification.sunday_night_hours
                )
                total_classification.overtime_day += classification.overtime_day
                total_classification.overtime_night += classification.overtime_night
                total_classification.overtime_sunday_day += (
                    classification.overtime_sunday_day
                )
                total_classification.overtime_sunday_night += (
                    classification.overtime_sunday_night
                )

        # Calculate payroll
        if total_classification:
            payroll = SurchargeCalculator.calculate(
                total_classification, worker.hourly_rate, worker_id=str(worker_id)
            )
        else:
            payroll = None

        # Save or update timesheet_day
        existing_query = select(TimesheetDay).where(
            and_(
                TimesheetDay.worker_id == worker_id,
                TimesheetDay.timesheet_date == timesheet_date,
                TimesheetDay.company_id == company_id,
            )
        )
        existing_result = await self.session.execute(existing_query)
        existing = existing_result.scalar_one_or_none()

        if existing:
            timesheet = existing
        else:
            timesheet = TimesheetDay(
                company_id=company_id,
                worker_id=worker_id,
                timesheet_date=timesheet_date,
            )
            self.session.add(timesheet)

        if total_classification:
            timesheet.ordinary_hours = total_classification.ordinary_hours
            timesheet.night_hours = total_classification.night_hours
            timesheet.sunday_day_hours = total_classification.sunday_day_hours
            timesheet.sunday_night_hours = total_classification.sunday_night_hours
            timesheet.overtime_day = total_classification.overtime_day
            timesheet.overtime_night = total_classification.overtime_night
            timesheet.overtime_sunday_day = total_classification.overtime_sunday_day
            timesheet.overtime_sunday_night = total_classification.overtime_sunday_night

            if payroll:
                timesheet.total_regular_amount = payroll.total_regular_amount
                timesheet.total_surcharge_amount = payroll.total_surcharge_amount
                timesheet.total_gross_amount = payroll.total_gross_amount

        await self.session.flush()
        return timesheet
