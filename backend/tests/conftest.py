"""
Pytest configuration and shared fixtures for Cronos tests.
"""

import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List


@pytest.fixture
def sample_holidays() -> List[date]:
    """Sample Colombian holiday calendar for testing."""
    return [
        date(2026, 1, 1),  # New Year
        date(2026, 1, 12),  # Epiphany (observed)
        date(2026, 2, 16),  # Presidents' Day
        date(2026, 3, 25),  # St. Joseph
        date(2026, 4, 2),  # Maundy Thursday
        date(2026, 4, 3),  # Good Friday
        date(2026, 5, 1),  # Labor Day
        date(2026, 5, 11),  # Ascension
        date(2026, 6, 1),  # Corpus Christi
        date(2026, 6, 8),  # Sacred Heart
        date(2026, 7, 1),  # St. Peter & St. Paul
        date(2026, 7, 20),  # Independence Day
        date(2026, 8, 7),  # Battle of Boyacá
        date(2026, 8, 17),  # Assumption (observed)
        date(2026, 10, 12),  # Columbus Day
        date(2026, 11, 2),  # All Souls' Day
        date(2026, 11, 16),  # Independence of Cartagena
        date(2026, 12, 8),  # Immaculate Conception
        date(2026, 12, 25),  # Christmas
    ]


@pytest.fixture
def sample_hourly_rate() -> Decimal:
    """Standard minimum hourly rate (Colombian legal minimum ~$15,000/hour in 2026)."""
    return Decimal("15000.00")


@pytest.fixture
def sample_shift_2026_01_15_day() -> tuple:
    """Sample day shift (06:00-14:00) on January 15, 2026 (Thursday)."""
    start = datetime(2026, 1, 15, 6, 0, 0)
    end = datetime(2026, 1, 15, 14, 0, 0)
    return (start, end)


@pytest.fixture
def sample_shift_2026_01_15_night() -> tuple:
    """Sample night shift (20:00-04:00 next day) on January 15-16, 2026 (Thursday-Friday)."""
    start = datetime(2026, 1, 15, 20, 0, 0)
    end = datetime(2026, 1, 16, 4, 0, 0)
    return (start, end)


@pytest.fixture
def sample_shift_2026_01_18_sunday() -> tuple:
    """Sample shift on Sunday, January 18, 2026 (06:00-14:00)."""
    start = datetime(2026, 1, 18, 6, 0, 0)
    end = datetime(2026, 1, 18, 14, 0, 0)
    return (start, end)


@pytest.fixture
def sample_shift_2026_01_18_sunday_night() -> tuple:
    """Sample night shift on Sunday, January 18-19, 2026 (20:00-04:00)."""
    start = datetime(2026, 1, 18, 20, 0, 0)
    end = datetime(2026, 1, 19, 4, 0, 0)
    return (start, end)


@pytest.fixture
def sample_shift_fractional() -> tuple:
    """Sample shift with fractional hours (08:30-16:45) = 8.25 hours."""
    start = datetime(2026, 1, 15, 8, 30, 0)
    end = datetime(2026, 1, 15, 16, 45, 0)
    return (start, end)


@pytest.fixture
def sample_shift_midnight_crossing() -> tuple:
    """Sample shift crossing midnight (22:00-06:00) = 8 hours."""
    start = datetime(2026, 1, 15, 22, 0, 0)
    end = datetime(2026, 1, 16, 6, 0, 0)
    return (start, end)
