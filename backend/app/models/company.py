from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.holiday import Holiday, SurchargeRule
    from app.models.shift import ShiftAssignment, ShiftTemplate, TimesheetDay
    from app.models.worker import Worker


class Company(TimestampMixin, Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subdomain: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    timezone: Mapped[str] = mapped_column(
        String(50), nullable=False, default="America/Bogota"
    )

    suborganizations: Mapped[list[SubOrganization]] = relationship(
        back_populates="company", lazy="select"
    )
    areas: Mapped[list[Area]] = relationship(back_populates="company", lazy="select")
    workers: Mapped[list[Worker]] = relationship(
        back_populates="company", lazy="select"
    )
    shift_templates: Mapped[list[ShiftTemplate]] = relationship(
        back_populates="company", lazy="select"
    )
    shift_assignments: Mapped[list[ShiftAssignment]] = relationship(
        back_populates="company", lazy="select"
    )
    timesheet_days: Mapped[list[TimesheetDay]] = relationship(
        back_populates="company", lazy="select"
    )
    holidays: Mapped[list[Holiday]] = relationship(
        back_populates="company", lazy="select"
    )
    surcharge_rules: Mapped[list[SurchargeRule]] = relationship(
        back_populates="company", lazy="select"
    )


class SubOrganization(TimestampMixin, Base):
    __tablename__ = "suborganizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_suborganization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("suborganizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    company: Mapped[Company] = relationship(
        back_populates="suborganizations", lazy="select"
    )
    parent_suborganization: Mapped[SubOrganization | None] = relationship(
        remote_side=[id],
        back_populates="children",
        lazy="select",
    )
    children: Mapped[list[SubOrganization]] = relationship(
        back_populates="parent_suborganization",
        lazy="select",
    )
    areas: Mapped[list[Area]] = relationship(
        back_populates="suborganization", lazy="select"
    )
    workers: Mapped[list[Worker]] = relationship(
        back_populates="suborganization", lazy="select"
    )
    shift_templates: Mapped[list[ShiftTemplate]] = relationship(
        back_populates="suborganization", lazy="select"
    )


class Area(TimestampMixin, Base):
    __tablename__ = "areas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    suborganization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("suborganizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    manager_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workers.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    company: Mapped[Company] = relationship(back_populates="areas", lazy="select")
    suborganization: Mapped[SubOrganization] = relationship(
        back_populates="areas", lazy="select"
    )
    manager: Mapped[Worker | None] = relationship(
        "Worker",
        foreign_keys=[manager_id],
        lazy="select",
        post_update=True,
    )
    workers: Mapped[list[Worker]] = relationship(
        "Worker",
        back_populates="area",
        lazy="select",
        foreign_keys="Worker.area_id",
    )
    shift_templates: Mapped[list[ShiftTemplate]] = relationship(
        back_populates="area", lazy="select"
    )

    __table_args__ = (
        Index("idx_areas_company_suborganization", "company_id", "suborganization_id"),
    )
