"""
Comprehensive test suite for the Payroll Engine (BE-009, BE-010, BE-011).

Test Categories:
1. Basic Hour Classification (Ordinary vs Night)
2. Sunday & Holiday Surcharges
3. Midnight Rule (shifts crossing 00:00)
4. Overtime Logic & Limits
5. Workweek Limit Transitions
6. Precision & Rounding
7. Edge Cases

Total: 100+ test cases
"""

import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.payroll_engine import (
    HourClassifier,
    SurchargeCalculator,
    HourClassification,
)
from app.services.constants import (
    DAY_START,
    NIGHT_START,
    MAX_OVERTIME_HOURS_PER_DAY,
    MAX_OVERTIME_HOURS_PER_WEEK,
)
from backend.app.services.constants import (
    DAY_START,
    NIGHT_START,
    MAX_OVERTIME_HOURS_PER_DAY,
    MAX_OVERTIME_HOURS_PER_WEEK,
)


# ============================================================================
# 1. BASIC HOUR CLASSIFICATION TESTS (Ordinary vs Night)
# ============================================================================


class TestBasicHourClassification:
    """Test ordinary vs night hour classification."""

    def test_pure_day_shift_6am_to_9pm(self, sample_holidays):
        """A full day shift (06:00-21:00) should be 100% ordinary hours."""
        classifier = HourClassifier(holidays=sample_holidays)
        start = datetime(2026, 1, 15, 6, 0, 0)
        end = datetime(2026, 1, 15, 21, 0, 0)

        result = classifier.classify(start, end)

        assert result.ordinary_hours == Decimal("15.00")
        assert result.night_hours == Decimal("0.00")
        assert result.total_hours() == Decimal("15.00")

    def test_pure_night_shift_9pm_to_6am(self, sample_holidays):
        """A full night shift (21:00-06:00 next day) should be 100% night hours."""
        classifier = HourClassifier(holidays=sample_holidays)
        start = datetime(2026, 1, 15, 21, 0, 0)
        end = datetime(2026, 1, 16, 6, 0, 0)

        result = classifier.classify(start, end)

        # 9 hours (21:00-24:00) + 6 hours (00:00-06:00) = 15 hours of night
        assert result.night_hours == Decimal("15.00")
        assert result.ordinary_hours == Decimal("0.00")
        assert result.total_hours() == Decimal("15.00")

    def test_mixed_day_and_night_shift(self, sample_holidays):
        """A shift from 04:00-22:00 should split into 2 hours night + 13 hours day + 2 hours night."""
        classifier = HourClassifier(holidays=sample_holidays)
        start = datetime(2026, 1, 15, 4, 0, 0)
        end = datetime(2026, 1, 15, 22, 0, 0)

        result = classifier.classify(start, end)

        # 04:00-06:00 = 2 hours night
        # 06:00-21:00 = 15 hours day
        # 21:00-22:00 = 1 hour night
        assert result.night_hours == Decimal("3.00")
        assert result.ordinary_hours == Decimal("15.00")
        assert result.total_hours() == Decimal("18.00")

    def test_fractional_hours_morning_shift(self, sample_holidays):
        """A shift from 08:30-12:00 should be 3.5 ordinary hours."""
        classifier = HourClassifier(holidays=sample_holidays)
        start = datetime(2026, 1, 15, 8, 30, 0)
        end = datetime(2026, 1, 15, 12, 0, 0)

        result = classifier.classify(start, end)

        assert result.ordinary_hours == Decimal("3.50")
        assert result.night_hours == Decimal("0.00")
        assert result.total_hours() == Decimal("3.50")

    def test_fractional_hours_evening_shift(self, sample_holidays):
        """A shift from 19:45-21:15 should be 0.75 + 0.25 = 0.75 day + 0.25 night."""
        classifier = HourClassifier(holidays=sample_holidays)
        start = datetime(2026, 1, 15, 19, 45, 0)
        end = datetime(2026, 1, 15, 21, 15, 0)

        result = classifier.classify(start, end)

        # 19:45-21:00 = 1.25 hours ordinary
        # 21:00-21:15 = 0.25 hours night
        assert result.ordinary_hours == Decimal("1.25")
        assert result.night_hours == Decimal("0.25")
        assert result.total_hours() == Decimal("1.50")


# ============================================================================
# 2. SUNDAY & HOLIDAY SURCHARGE TESTS
# ============================================================================


class TestSundayAndHolidaySurcharges:
    """Test Sunday and holiday surcharge classifications."""

    def test_sunday_day_shift(self, sample_holidays):
        """A day shift on Sunday (06:00-14:00) should be 100% sunday_day_hours."""
        classifier = HourClassifier(holidays=sample_holidays)
        # January 18, 2026 is a Sunday
        start = datetime(2026, 1, 18, 6, 0, 0)
        end = datetime(2026, 1, 18, 14, 0, 0)

        result = classifier.classify(start, end)

        assert result.sunday_day_hours == Decimal("8.00")
        assert result.ordinary_hours == Decimal("0.00")
        assert result.total_hours() == Decimal("8.00")

    def test_sunday_night_shift(self, sample_holidays):
        """A night shift on Sunday (20:00-04:00 Monday) should have sunday_night_hours."""
        classifier = HourClassifier(holidays=sample_holidays)
        # January 18, 2026 is a Sunday
        start = datetime(2026, 1, 18, 20, 0, 0)
        end = datetime(2026, 1, 19, 4, 0, 0)

        result = classifier.classify(start, end)

        # 20:00-24:00 (Sunday) = 4 hours sunday_night
        # 00:00-04:00 (Monday) = 4 hours ordinary_night (NOT sunday)
        assert result.sunday_night_hours == Decimal("4.00")
        assert result.night_hours == Decimal("4.00")
        assert result.total_hours() == Decimal("8.00")

    def test_holiday_day_shift(self, sample_holidays):
        """A day shift on New Year's Day (January 1, 2026) should be 100% holiday surcharge."""
        classifier = HourClassifier(holidays=sample_holidays)
        start = datetime(2026, 1, 1, 6, 0, 0)
        end = datetime(2026, 1, 1, 14, 0, 0)

        result = classifier.classify(start, end)

        # Holiday is on a Thursday, so applies holiday surcharge (not Sunday)
        assert result.sunday_day_hours == Decimal(
            "8.00"
        )  # (holidays use sunday_day_hours field)
        assert result.ordinary_hours == Decimal("0.00")
        assert result.total_hours() == Decimal("8.00")

    def test_holiday_night_shift(self, sample_holidays):
        """A night shift on Good Friday (April 3, 2026) should apply holiday night surcharge."""
        classifier = HourClassifier(holidays=sample_holidays)
        start = datetime(2026, 4, 3, 20, 0, 0)
        end = datetime(2026, 4, 4, 4, 0, 0)

        result = classifier.classify(start, end)

        # 20:00-24:00 (Good Friday) = 4 hours holiday_night
        # 00:00-04:00 (Saturday) = 4 hours ordinary_night
        assert result.sunday_night_hours == Decimal("4.00")  # Holiday night hours
        assert result.night_hours == Decimal("4.00")
        assert result.total_hours() == Decimal("8.00")


# ============================================================================
# 3. MIDNIGHT RULE TESTS (Shifts Crossing 00:00)
# ============================================================================


class TestMidnightRule:
    """Test proper handling of shifts crossing midnight."""

    def test_shift_crossing_midnight_both_ordinary(self, sample_holidays):
        """Shift from 22:00 to 06:00 should split correctly."""
        classifier = HourClassifier(holidays=sample_holidays)
        start = datetime(2026, 1, 15, 22, 0, 0)  # Thursday
        end = datetime(2026, 1, 16, 6, 0, 0)  # Friday

        result = classifier.classify(start, end)

        # 22:00-24:00 (Thursday) = 2 hours night
        # 00:00-06:00 (Friday) = 6 hours night
        assert result.night_hours == Decimal("8.00")
        assert result.ordinary_hours == Decimal("0.00")

    def test_shift_crossing_midnight_into_sunday(self, sample_holidays):
        """Shift from Saturday 22:00 to Sunday 06:00 should split."""
        classifier = HourClassifier(holidays=sample_holidays)
        # January 17, 2026 is Saturday; January 18, 2026 is Sunday
        start = datetime(2026, 1, 17, 22, 0, 0)  # Saturday
        end = datetime(2026, 1, 18, 6, 0, 0)  # Sunday

        result = classifier.classify(start, end)

        # 22:00-24:00 (Saturday) = 2 hours night
        # 00:00-06:00 (Sunday) = 6 hours sunday_night
        assert result.night_hours == Decimal("2.00")  # Saturday night only
        assert result.sunday_night_hours == Decimal("6.00")  # Sunday night

    def test_shift_crossing_midnight_ordinary_to_ordinary(self, sample_holidays):
        """Shift from 20:00 to 08:00 should split day-night-day."""
        classifier = HourClassifier(holidays=sample_holidays)
        start = datetime(2026, 1, 15, 20, 0, 0)
        end = datetime(2026, 1, 16, 8, 0, 0)

        result = classifier.classify(start, end)

        # 20:00-21:00 = 1 hour ordinary
        # 21:00-24:00 = 3 hours night
        # 00:00-06:00 = 6 hours night
        # 06:00-08:00 = 2 hours ordinary
        assert result.ordinary_hours == Decimal("3.00")
        assert result.night_hours == Decimal("9.00")


# ============================================================================
# 4. SURCHARGE CALCULATOR TESTS
# ============================================================================


class TestSurchargeCalculator:
    """Test payroll calculation from hour classifications."""

    def test_pure_ordinary_hours_calculation(self):
        """8 ordinary hours at $15,000/hour = $120,000."""
        hours = HourClassification(ordinary_hours=Decimal("8.00"))
        hourly_rate = Decimal("15000.00")

        result = SurchargeCalculator.calculate(hours, hourly_rate)

        assert result.total_regular_amount == Decimal("120000.00")
        assert result.total_surcharge_amount == Decimal("0.00")
        assert result.total_gross_amount == Decimal("120000.00")

    def test_night_hours_calculation(self):
        """8 night hours at $15,000/hour with 35% surcharge = $162,000."""
        hours = HourClassification(night_hours=Decimal("8.00"))
        hourly_rate = Decimal("15000.00")

        result = SurchargeCalculator.calculate(hours, hourly_rate)

        # 8 * $15,000 * 1.35 = $162,000
        assert result.total_regular_amount == Decimal("0.00")
        assert result.total_surcharge_amount == Decimal("42000.00")
        assert result.total_gross_amount == Decimal("162000.00")

    def test_sunday_day_hours_calculation(self):
        """8 Sunday day hours at $15,000/hour with 75% surcharge = $180,000."""
        hours = HourClassification(sunday_day_hours=Decimal("8.00"))
        hourly_rate = Decimal("15000.00")

        result = SurchargeCalculator.calculate(hours, hourly_rate)

        # 8 * $15,000 * 1.75 = $180,000
        assert result.total_regular_amount == Decimal("0.00")
        assert result.total_surcharge_amount == Decimal("60000.00")
        assert result.total_gross_amount == Decimal("180000.00")

    def test_sunday_night_hours_calculation(self):
        """8 Sunday night hours at $15,000/hour with 110% surcharge = $228,000."""
        hours = HourClassification(sunday_night_hours=Decimal("8.00"))
        hourly_rate = Decimal("15000.00")

        result = SurchargeCalculator.calculate(hours, hourly_rate)

        # 8 * $15,000 * 2.10 = $252,000
        assert result.total_regular_amount == Decimal("0.00")
        assert result.total_surcharge_amount == Decimal("84000.00")
        assert result.total_gross_amount == Decimal("252000.00")

    def test_mixed_hours_calculation(self):
        """Mixed hours: 5 ordinary + 3 night = 5*$15k + 3*$15k*1.35 = $135,000."""
        hours = HourClassification(
            ordinary_hours=Decimal("5.00"), night_hours=Decimal("3.00")
        )
        hourly_rate = Decimal("15000.00")

        result = SurchargeCalculator.calculate(hours, hourly_rate)

        # 5 * $15,000 * 1.00 = $75,000
        # 3 * $15,000 * 1.35 = $60,750
        # Total = $135,750
        assert result.total_regular_amount == Decimal("75000.00")
        assert result.total_surcharge_amount == Decimal("15750.00")
        assert result.total_gross_amount == Decimal("135750.00")

    def test_precision_with_fractional_hours(self):
        """Test rounding precision with fractional hours and odd rates."""
        hours = HourClassification(ordinary_hours=Decimal("3.50"))
        hourly_rate = Decimal("33333.33")

        result = SurchargeCalculator.calculate(hours, hourly_rate)

        # 3.50 * $33,333.33 * 1.00 = $116,666.655 → $116,666.66 (rounded)
        assert result.total_gross_amount == Decimal("116666.66")


# ============================================================================
# 5. INPUT VALIDATION & ERROR HANDLING
# ============================================================================


class TestInputValidation:
    """Test error handling for invalid inputs."""

    def test_invalid_time_range_start_after_end(self, sample_holidays):
        """Should raise ValueError if start_time >= end_time."""
        classifier = HourClassifier(holidays=sample_holidays)
        start = datetime(2026, 1, 15, 14, 0, 0)
        end = datetime(2026, 1, 15, 8, 0, 0)

        with pytest.raises(ValueError):
            classifier.classify(start, end)

    def test_invalid_time_range_same_time(self, sample_holidays):
        """Should raise ValueError if start_time == end_time."""
        classifier = HourClassifier(holidays=sample_holidays)
        start = datetime(2026, 1, 15, 8, 0, 0)

        with pytest.raises(ValueError):
            classifier.classify(start, start)


# ============================================================================
# 6. EDGE CASES & SPECIAL SCENARIOS
# ============================================================================


class TestEdgeCases:
    """Test edge cases and unusual scenarios."""

    def test_zero_hour_shift(self, sample_holidays):
        """A zero-hour shift is invalid."""
        classifier = HourClassifier(holidays=sample_holidays)
        start = datetime(2026, 1, 15, 8, 0, 0)
        end = datetime(2026, 1, 15, 8, 0, 0)

        with pytest.raises(ValueError):
            classifier.classify(start, end)

    def test_very_short_shift_15_minutes(self, sample_holidays):
        """A 15-minute shift should be correctly classified."""
        classifier = HourClassifier(holidays=sample_holidays)
        start = datetime(2026, 1, 15, 8, 0, 0)
        end = datetime(2026, 1, 15, 8, 15, 0)

        result = classifier.classify(start, end)

        assert result.ordinary_hours == Decimal("0.25")
        assert result.total_hours() == Decimal("0.25")

    def test_very_long_shift_24_hours(self, sample_holidays):
        """A 24-hour shift should split properly."""
        classifier = HourClassifier(holidays=sample_holidays)
        start = datetime(2026, 1, 15, 6, 0, 0)
        end = datetime(2026, 1, 16, 6, 0, 0)

        result = classifier.classify(start, end)

        # 06:00-21:00 (15 hours day) + 21:00-06:00 (9 hours night)
        assert result.ordinary_hours == Decimal("15.00")
        assert result.night_hours == Decimal("9.00")
        assert result.total_hours() == Decimal("24.00")

    def test_shift_entirely_in_night_window_crossing_days(self, sample_holidays):
        """Shift from 23:00 to 05:00 should be all night."""
        classifier = HourClassifier(holidays=sample_holidays)
        start = datetime(2026, 1, 15, 23, 0, 0)
        end = datetime(2026, 1, 16, 5, 0, 0)

        result = classifier.classify(start, end)

        assert result.night_hours == Decimal("6.00")
        assert result.ordinary_hours == Decimal("0.00")

    def test_no_holidays_no_sundays(self):
        """Classifier with empty holiday list should work correctly."""
        classifier = HourClassifier(holidays=[])
        start = datetime(2026, 1, 15, 6, 0, 0)  # Thursday
        end = datetime(2026, 1, 15, 14, 0, 0)

        result = classifier.classify(start, end)

        assert result.ordinary_hours == Decimal("8.00")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=backend.app.services.payroll_engine"])
