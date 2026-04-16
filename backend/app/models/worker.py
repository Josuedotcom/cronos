from __future__ import annotations

import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.company import Area, Company, SubOrganization
    from app.models.shift import ShiftAssignment, TimesheetDay


class WorkerRole(str, enum.Enum):
    WORKER = "worker"
    MANAGER = "manager"
    HR_ADMIN = "hr_admin"
    SYSTEM_ADMIN = "system_admin"


class Worker(TimestampMixin, Base):
    __tablename__ = "workers"

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
    cedula: Mapped[str] = mapped_column(String(20), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    contract_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="standard"
    )
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    role: Mapped[WorkerRole] = mapped_column(
        Enum(WorkerRole, name="worker_role", native_enum=False),
        nullable=False,
        default=WorkerRole.WORKER,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    company: Mapped[Company] = relationship(back_populates="workers", lazy="select")
    suborganization: Mapped[SubOrganization] = relationship(
        back_populates="workers", lazy="select"
    )
    area: Mapped[Area] = relationship(
        back_populates="workers", lazy="select", foreign_keys=[area_id]
    )

    assignments: Mapped[list[ShiftAssignment]] = relationship(
        "ShiftAssignment",
        back_populates="worker",
        lazy="select",
        foreign_keys="ShiftAssignment.worker_id",
    )
    created_assignments: Mapped[list[ShiftAssignment]] = relationship(
        "ShiftAssignment",
        back_populates="created_by",
        lazy="select",
        foreign_keys="ShiftAssignment.created_by_worker_id",
    )
    timesheet_days: Mapped[list[TimesheetDay]] = relationship(
        back_populates="worker", lazy="select"
    )

    __table_args__ = (
        CheckConstraint(
            "contract_type IN ('standard', 'shift_36h')",
            name="ck_workers_contract_type",
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'on_leave')", name="ck_workers_status"
        ),
        UniqueConstraint("company_id", "cedula", name="uq_workers_company_cedula"),
        Index("idx_workers_company", "company_id"),
        Index("idx_workers_area", "area_id"),
        Index("idx_workers_company_area", "company_id", "area_id"),
    )
