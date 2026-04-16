from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, time
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.company import Area, Company, SubOrganization
    from app.models.worker import Worker


class ShiftAssignmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    ABSENT = "absent"
    SWAPPED = "swapped"


class ShiftTemplate(TimestampMixin, Base):
    __tablename__ = "shift_templates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    suborganization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("suborganizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    area_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("areas.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    company: Mapped[Company] = relationship(
        back_populates="shift_templates", lazy="select"
    )
    suborganization: Mapped[SubOrganization] = relationship(
        back_populates="shift_templates", lazy="select"
    )
    area: Mapped[Area] = relationship(back_populates="shift_templates", lazy="select")

    assignments: Mapped[list[ShiftAssignment]] = relationship(
        back_populates="template", lazy="select"
    )

    __table_args__ = (
        UniqueConstraint("area_id", "code", name="uq_shift_templates_area_code"),
        Index("idx_shift_templates_area", "area_id"),
        Index("idx_shift_templates_company", "company_id"),
    )


class ShiftAssignment(TimestampMixin, Base):
    __tablename__ = "shift_assignments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workers.id", ondelete="CASCADE"), nullable=False
    )
    shift_template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shift_templates.id", ondelete="CASCADE"),
        nullable=False,
    )
    assignment_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[ShiftAssignmentStatus] = mapped_column(
        Enum(ShiftAssignmentStatus, name="shift_assignment_status", native_enum=False),
        nullable=False,
        default=ShiftAssignmentStatus.SCHEDULED,
    )
    is_overtime_shift: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_worker_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workers.id", ondelete="SET NULL"),
        nullable=True,
    )

    company: Mapped[Company] = relationship(
        back_populates="shift_assignments", lazy="select"
    )
    worker: Mapped[Worker] = relationship(
        back_populates="assignments",
        lazy="select",
        foreign_keys=[worker_id],
    )
    template: Mapped[ShiftTemplate] = relationship(
        back_populates="assignments", lazy="select"
    )
    created_by: Mapped[Worker | None] = relationship(
        back_populates="created_assignments",
        lazy="select",
        foreign_keys=[created_by_worker_id],
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('scheduled', 'completed', 'absent', 'swapped')",
            name="ck_shift_assignments_status",
        ),
        UniqueConstraint(
            "worker_id", "assignment_date", name="uq_shift_assignments_worker_date"
        ),
        Index("idx_shift_assignments_worker", "worker_id"),
        Index("idx_shift_assignments_date", "assignment_date"),
        Index("idx_shift_assignments_company", "company_id"),
        Index("idx_shift_assignments_worker_date", "worker_id", "assignment_date"),
        Index("idx_shift_assignments_template", "shift_template_id"),
    )


class TimesheetDay(TimestampMixin, Base):
    __tablename__ = "timesheet_days"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workers.id", ondelete="CASCADE"), nullable=False
    )
    timesheet_date: Mapped[date] = mapped_column(Date, nullable=False)

    ordinary_hours: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=0
    )
    night_hours: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=0
    )
    sunday_day_hours: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=0
    )
    sunday_night_hours: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=0
    )
    overtime_day: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=0
    )
    overtime_night: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=0
    )
    overtime_sunday_day: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=0
    )
    overtime_sunday_night: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=0
    )
    total_regular_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    total_surcharge_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    total_gross_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )

    company: Mapped[Company] = relationship(
        back_populates="timesheet_days", lazy="select"
    )
    worker: Mapped[Worker] = relationship(
        back_populates="timesheet_days", lazy="select"
    )

    __table_args__ = (
        UniqueConstraint(
            "worker_id", "timesheet_date", name="uq_timesheet_days_worker_date"
        ),
        Index("idx_timesheet_days_worker", "worker_id"),
        Index("idx_timesheet_days_date", "timesheet_date"),
        Index("idx_timesheet_days_worker_date", "worker_id", "timesheet_date"),
    )
