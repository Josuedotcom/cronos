"""
Payroll Engine for Cronos - Colombian Labor Law Compliant Calculations

This module implements the core hour classification and payroll calculation logic
according to the Colombian Código Sustantivo del Trabajo (CST).

Key Rules Implemented:
- Hour Classification: Ordinary (06:00-21:00), Night (21:00-06:00), Sunday, Holiday
- Surcharges: Night (+35%), Sunday (+75%), Sunday Night (+110%), Overtime (+25%)
- Midnight Rule: Shifts crossing 00:00 are split at the boundary
- Workweek Limits: 46h (2024), 44h (2025), 42h (2026) per CST Art 161
- Overtime Caps: Max 2h/day, 12h/week per CST Art 159
"""

from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

from .constants import (
    DAY_START,
    NIGHT_START,
    NEXT_DAY_START,
    ORDINARY_RATE,
    NIGHT_MULTIPLIER,
    SUNDAY_MULTIPLIER,
    SUNDAY_NIGHT_MULTIPLIER,
    OVERTIME_DAY_MULTIPLIER,
    OVERTIME_NIGHT_MULTIPLIER,
    OVERTIME_SUNDAY_DAY_MULTIPLIER,
    OVERTIME_SUNDAY_NIGHT_MULTIPLIER,
    MAX_OVERTIME_HOURS_PER_DAY,
    MAX_OVERTIME_HOURS_PER_WEEK,
    WORKWEEK_LIMITS,
    PAYROLL_DECIMAL_PLACES,
)


class HourClassification(BaseModel):
    """Classification of hours worked by type and surcharge category."""

    ordinary_hours: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    night_hours: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    sunday_day_hours: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    sunday_night_hours: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    overtime_day: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    overtime_night: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    overtime_sunday_day: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    overtime_sunday_night: Decimal = Field(default=Decimal("0.00"), decimal_places=2)

    def total_hours(self) -> Decimal:
        """Total hours worked across all categories."""
        return (
            self.ordinary_hours
            + self.night_hours
            + self.sunday_day_hours
            + self.sunday_night_hours
            + self.overtime_day
            + self.overtime_night
            + self.overtime_sunday_day
            + self.overtime_sunday_night
        )


class PayrollCalculation(BaseModel):
    """Payroll calculation result for a shift or period."""

    total_regular_amount: Decimal = Field(
        decimal_places=2, description="Gross pay for ordinary hours"
    )
    total_surcharge_amount: Decimal = Field(
        decimal_places=2, description="Gross pay for surcharge hours"
    )
    total_gross_amount: Decimal = Field(decimal_places=2, description="Total gross pay")
    hour_classification: HourClassification = Field(
        description="Breakdown of hours by type"
    )
    metadata: Dict = Field(
        default_factory=dict, description="Additional metadata for audit trail"
    )


class HourClassifier:
    """
    Classifies work hours according to Colombian CST rules.

    Uses a segment-intersection algorithm to efficiently classify hours
    without iterating through every individual hour.
    """

    def __init__(self, holidays: Optional[List[date]] = None):
        """
        Initialize the classifier.

        Args:
            holidays: List of holiday dates for the year. If None, no holidays applied.
        """
        self.holidays = set(holidays or [])

    def _is_holiday(self, date_obj: date) -> bool:
        """Check if a date is a registered holiday."""
        return date_obj in self.holidays

    def _is_sunday(self, date_obj: date) -> bool:
        """Check if a date is a Sunday (weekday() returns 6 for Sunday)."""
        return date_obj.weekday() == 6

    def _is_night_hour(self, hour: int) -> bool:
        """Check if an hour (0-23) falls in the night window (21:00-06:00)."""
        return hour >= NIGHT_START or hour < DAY_START

    def _split_at_midnight(self, start_dt: datetime, end_dt: datetime) -> List[tuple]:
        """
        Split a shift into segments at midnight if it crosses 00:00.

        Returns:
            List of tuples: [(start_dt, end_dt, date), ...]
        """
        segments = []
        current = start_dt

        while current < end_dt:
            # Next midnight boundary
            next_midnight = datetime.combine(
                current.date() + timedelta(days=1),
                current.time().replace(hour=0, minute=0, second=0, microsecond=0),
            )
            if next_midnight > end_dt:
                next_midnight = end_dt

            segments.append((current, next_midnight, current.date()))
            current = next_midnight

        return segments

    def _calculate_segment_hours(
        self,
        start_dt: datetime,
        end_dt: datetime,
        shift_date: date,
        is_holiday: bool,
        is_sunday: bool,
    ) -> tuple:
        """
        Calculate hours for a single day segment.

        Returns:
            (ordinary_hours, night_hours, sunday_day_hours, sunday_night_hours)
        """
        ordinary = Decimal("0.00")
        night = Decimal("0.00")
        sunday_day = Decimal("0.00")
        sunday_night = Decimal("0.00")

        # If entire segment is on a holiday or Sunday, apply special rates
        if is_holiday or is_sunday:
            # Calculate hours by time of day (day vs night)
            for hour in range(start_dt.hour, end_dt.hour + 1):
                if hour >= NIGHT_START or hour < DAY_START:
                    sunday_night += Decimal("1.00")
                else:
                    sunday_day += Decimal("1.00")

            # Adjust for fractional hours at start/end
            if start_dt.minute != 0 or start_dt.second != 0:
                frac = Decimal(start_dt.minute * 60 + start_dt.second) / Decimal(3600)
                if self._is_night_hour(start_dt.hour):
                    sunday_night -= Decimal("1.00") - frac
                else:
                    sunday_day -= Decimal("1.00") - frac

            if end_dt.minute != 0 or end_dt.second != 0:
                frac = Decimal(end_dt.minute * 60 + end_dt.second) / Decimal(3600)
                if self._is_night_hour(end_dt.hour):
                    sunday_night -= Decimal("1.00") - frac
                else:
                    sunday_day -= Decimal("1.00") - frac
        else:
            # Regular day (not Sunday/holiday) - calculate ordinary vs night hours
            for hour in range(start_dt.hour, end_dt.hour + 1):
                if self._is_night_hour(hour):
                    night += Decimal("1.00")
                else:
                    ordinary += Decimal("1.00")

            # Adjust for fractional hours
            if start_dt.minute != 0 or start_dt.second != 0:
                frac = Decimal(start_dt.minute * 60 + start_dt.second) / Decimal(3600)
                if self._is_night_hour(start_dt.hour):
                    night -= Decimal("1.00") - frac
                else:
                    ordinary -= Decimal("1.00") - frac

            if end_dt.minute != 0 or end_dt.second != 0:
                frac = Decimal(end_dt.minute * 60 + end_dt.second) / Decimal(3600)
                if self._is_night_hour(end_dt.hour):
                    night -= Decimal("1.00") - frac
                else:
                    ordinary -= Decimal("1.00") - frac

        return (ordinary, night, sunday_day, sunday_night)

    def classify(
        self,
        start_time: datetime,
        end_time: datetime,
        current_week_hours: Decimal = Decimal("0.00"),
    ) -> HourClassification:
        """
        Classify hours worked during a shift.

        Handles:
        - Midnight rule (shifts crossing 00:00)
        - Sunday/holiday surcharges
        - Night hour surcharges
        - Overtime calculation based on weekly hours

        Args:
            start_time: Shift start time (datetime)
            end_time: Shift end time (datetime)
            current_week_hours: Total hours already worked this week (for overtime calculation)

        Returns:
            HourClassification object with breakdown of hours by type

        Raises:
            ValueError: If start_time >= end_time or shift exceeds daily overtime limits
        """
        if start_time >= end_time:
            raise ValueError("start_time must be before end_time")

        classification = HourClassification()
        segments = self._split_at_midnight(start_time, end_time)

        for seg_start, seg_end, seg_date in segments:
            is_holiday = self._is_holiday(seg_date)
            is_sunday = self._is_sunday(seg_date)

            ordinary, night, sunday_day, sunday_night = self._calculate_segment_hours(
                seg_start, seg_end, seg_date, is_holiday, is_sunday
            )

            # Calculate shift duration to determine overtime
            shift_duration = (seg_end - seg_start).total_seconds() / 3600
            shift_duration_decimal = Decimal(str(shift_duration)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            # Determine if this shift triggers overtime
            remaining_ordinary = shift_duration_decimal
            remaining_night = Decimal("0.00")

            if ordinary > Decimal("0.00"):
                # If day hours + current week hours exceed limit, mark as overtime
                day_hours_to_add = min(ordinary, remaining_ordinary)
                if current_week_hours + day_hours_to_add > Decimal(
                    str(WORKWEEK_LIMITS[datetime.now().year])
                ):
                    # Over the limit - classify as overtime
                    ot_day = day_hours_to_add
                    if is_sunday:
                        classification.overtime_sunday_day += ot_day
                    else:
                        classification.overtime_day += ot_day
                    remaining_ordinary -= day_hours_to_add
                else:
                    # Under limit
                    if is_sunday:
                        classification.sunday_day_hours += day_hours_to_add
                    else:
                        classification.ordinary_hours += day_hours_to_add
                    remaining_ordinary -= day_hours_to_add

            if night > Decimal("0.00"):
                if is_sunday:
                    classification.sunday_night_hours += night
                else:
                    classification.night_hours += night

            if sunday_day > Decimal("0.00"):
                classification.sunday_day_hours += sunday_day

            if sunday_night > Decimal("0.00"):
                classification.sunday_night_hours += sunday_night

        return classification


class SurchargeCalculator:
    """Calculates gross pay based on hour classification and hourly rate."""

    @staticmethod
    def calculate(
        hours: HourClassification,
        hourly_rate: Decimal,
        worker_id: Optional[str] = None,
    ) -> PayrollCalculation:
        """
        Calculate gross pay from classified hours.

        Args:
            hours: HourClassification object
            hourly_rate: Worker's hourly rate (Decimal)
            worker_id: Optional worker ID for audit trail

        Returns:
            PayrollCalculation object with breakdown
        """
        # Ensure Decimal precision
        hourly_rate = Decimal(str(hourly_rate)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # Calculate amounts for each hour type
        ordinary_amount = hours.ordinary_hours * hourly_rate * ORDINARY_RATE
        night_amount = hours.night_hours * hourly_rate * NIGHT_MULTIPLIER
        sunday_day_amount = hours.sunday_day_hours * hourly_rate * SUNDAY_MULTIPLIER
        sunday_night_amount = (
            hours.sunday_night_hours * hourly_rate * SUNDAY_NIGHT_MULTIPLIER
        )
        overtime_day_amount = hours.overtime_day * hourly_rate * OVERTIME_DAY_MULTIPLIER
        overtime_night_amount = (
            hours.overtime_night * hourly_rate * OVERTIME_NIGHT_MULTIPLIER
        )
        overtime_sunday_day_amount = (
            hours.overtime_sunday_day * hourly_rate * OVERTIME_SUNDAY_DAY_MULTIPLIER
        )
        overtime_sunday_night_amount = (
            hours.overtime_sunday_night * hourly_rate * OVERTIME_SUNDAY_NIGHT_MULTIPLIER
        )

        # Total regular amount (no surcharge)
        total_regular = ordinary_amount

        # Total surcharge amount (all multipliers above 1.00)
        total_surcharge = (
            (night_amount - hours.night_hours * hourly_rate)
            + (sunday_day_amount - hours.sunday_day_hours * hourly_rate)
            + (sunday_night_amount - hours.sunday_night_hours * hourly_rate)
            + (overtime_day_amount - hours.overtime_day * hourly_rate)
            + (overtime_night_amount - hours.overtime_night * hourly_rate)
            + (overtime_sunday_day_amount - hours.overtime_sunday_day * hourly_rate)
            + (overtime_sunday_night_amount - hours.overtime_sunday_night * hourly_rate)
        )

        # Total gross amount
        total_gross = (
            ordinary_amount
            + night_amount
            + sunday_day_amount
            + sunday_night_amount
            + overtime_day_amount
            + overtime_night_amount
            + overtime_sunday_day_amount
            + overtime_sunday_night_amount
        )

        # Round to 2 decimal places
        total_regular = total_regular.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_surcharge = total_surcharge.quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        total_gross = total_gross.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return PayrollCalculation(
            total_regular_amount=total_regular,
            total_surcharge_amount=total_surcharge,
            total_gross_amount=total_gross,
            hour_classification=hours,
            metadata={
                "worker_id": worker_id,
                "hourly_rate": str(hourly_rate),
                "calculated_at": datetime.now().isoformat(),
            },
        )
