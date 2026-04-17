#!/usr/bin/env python3
"""
Quick validation script for Payroll Engine implementation.
Tests basic functionality without pytest infrastructure.
"""

import sys
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.payroll_engine import (
    HourClassifier,
    SurchargeCalculator,
    HourClassification,
)


def test_basic_day_shift():
    """Test: 8-hour day shift (06:00-14:00) = 8 ordinary hours."""
    print("\n[TEST 1] Basic Day Shift (06:00-14:00)")
    classifier = HourClassifier(holidays=[])
    start = datetime(2026, 1, 15, 6, 0, 0)
    end = datetime(2026, 1, 15, 14, 0, 0)

    result = classifier.classify(start, end)
    print(f"  Ordinary hours: {result.ordinary_hours} (expected 8.00)")
    print(f"  Night hours: {result.night_hours} (expected 0.00)")
    assert result.ordinary_hours == Decimal("8.00"), "Failed: ordinary hours"
    assert result.night_hours == Decimal("0.00"), "Failed: night hours"
    print("  ✓ PASS")


def test_night_shift():
    """Test: 8-hour night shift (21:00-06:00) = 8 night hours."""
    print("\n[TEST 2] Night Shift (21:00-06:00)")
    classifier = HourClassifier(holidays=[])
    start = datetime(2026, 1, 15, 21, 0, 0)
    end = datetime(2026, 1, 16, 6, 0, 0)

    result = classifier.classify(start, end)
    print(f"  Ordinary hours: {result.ordinary_hours} (expected 0.00)")
    print(f"  Night hours: {result.night_hours} (expected 9.00)")
    assert result.night_hours == Decimal("9.00"), "Failed: night hours"
    assert result.ordinary_hours == Decimal("0.00"), "Failed: ordinary hours"
    print("  ✓ PASS")


def test_midnight_crossing():
    """Test: Shift crossing midnight (22:00-06:00)."""
    print("\n[TEST 3] Midnight Crossing (22:00-06:00)")
    classifier = HourClassifier(holidays=[])
    start = datetime(2026, 1, 15, 22, 0, 0)
    end = datetime(2026, 1, 16, 6, 0, 0)

    result = classifier.classify(start, end)
    print(f"  Ordinary hours: {result.ordinary_hours} (expected 0.00)")
    print(f"  Night hours: {result.night_hours} (expected 8.00)")
    assert result.night_hours == Decimal("8.00"), "Failed: night hours"
    print("  ✓ PASS")


def test_sunday_shift():
    """Test: Day shift on Sunday (06:00-14:00) = 8 sunday_day_hours."""
    print("\n[TEST 4] Sunday Day Shift")
    classifier = HourClassifier(holidays=[])
    # January 18, 2026 is a Sunday
    start = datetime(2026, 1, 18, 6, 0, 0)
    end = datetime(2026, 1, 18, 14, 0, 0)

    result = classifier.classify(start, end)
    print(f"  Sunday day hours: {result.sunday_day_hours} (expected 8.00)")
    print(f"  Ordinary hours: {result.ordinary_hours} (expected 0.00)")
    assert result.sunday_day_hours == Decimal("8.00"), "Failed: sunday day hours"
    print("  ✓ PASS")


def test_payroll_calculation():
    """Test: Payroll calculation for 8 ordinary hours at $15,000/hour."""
    print("\n[TEST 5] Payroll Calculation")
    hours = HourClassification(ordinary_hours=Decimal("8.00"))
    hourly_rate = Decimal("15000.00")

    result = SurchargeCalculator.calculate(hours, hourly_rate)
    print(f"  Total gross: ${result.total_gross_amount} (expected $120,000.00)")
    print(f"  Total regular: ${result.total_regular_amount} (expected $120,000.00)")
    print(f"  Total surcharge: ${result.total_surcharge_amount} (expected $0.00)")
    assert result.total_gross_amount == Decimal("120000.00"), "Failed: gross amount"
    assert result.total_surcharge_amount == Decimal("0.00"), "Failed: surcharge"
    print("  ✓ PASS")


def test_payroll_night_hours():
    """Test: Payroll for 8 night hours (35% surcharge)."""
    print("\n[TEST 6] Night Hours Surcharge Calculation")
    hours = HourClassification(night_hours=Decimal("8.00"))
    hourly_rate = Decimal("15000.00")

    result = SurchargeCalculator.calculate(hours, hourly_rate)
    # 8 * $15,000 * 1.35 = $162,000
    expected = Decimal("162000.00")
    print(f"  Total gross: ${result.total_gross_amount} (expected ${expected})")
    assert result.total_gross_amount == expected, (
        f"Failed: expected {expected}, got {result.total_gross_amount}"
    )
    print("  ✓ PASS")


def test_fractional_hours():
    """Test: Fractional hours (3.5 hours)."""
    print("\n[TEST 7] Fractional Hours (3.5 ordinary hours)")
    classifier = HourClassifier(holidays=[])
    start = datetime(2026, 1, 15, 8, 30, 0)
    end = datetime(2026, 1, 15, 12, 0, 0)

    result = classifier.classify(start, end)
    print(f"  Ordinary hours: {result.ordinary_hours} (expected 3.50)")
    assert result.ordinary_hours == Decimal("3.50"), "Failed: fractional hours"
    print("  ✓ PASS")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Payroll Engine Validation Tests")
    print("=" * 60)

    try:
        test_basic_day_shift()
        test_night_shift()
        test_midnight_crossing()
        test_sunday_shift()
        test_payroll_calculation()
        test_payroll_night_hours()
        test_fractional_hours()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
