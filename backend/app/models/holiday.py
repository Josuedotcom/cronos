from __future__ import annotations

import enum
import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.company import Company


class SurchargeType(str, enum.Enum):
    NOCHE = "night"
    DOMINGO = "sunday_day"
    FERIADO = "sunday_night"
    EXTRA = "overtime_day"
    EXTRA_NOCHE = "overtime_night"


class Holiday(TimestampMixin, Base):
    __tablename__ = "holiday_calendar"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    holiday_date: Mapped[date] = mapped_column(Date, nullable=False)
    holiday_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_public_holiday: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    company: Mapped[Company] = relationship(back_populates="holidays", lazy="select")

    __table_args__ = (
        UniqueConstraint(
            "company_id", "holiday_date", name="uq_holiday_calendar_company_date"
        ),
        Index("idx_holiday_calendar_company", "company_id"),
        Index("idx_holiday_calendar_date", "holiday_date"),
    )


class SurchargeRule(TimestampMixin, Base):
    __tablename__ = "surcharge_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    surcharge_type: Mapped[str] = mapped_column(String(50), nullable=False)
    percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    company: Mapped[Company] = relationship(
        back_populates="surcharge_rules", lazy="select"
    )

    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "surcharge_type",
            "effective_from",
            name="uq_surcharge_rules_company_type_effective_from",
        ),
        Index("idx_surcharge_rules_company", "company_id"),
    )
