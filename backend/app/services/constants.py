"""Constants for payroll engine calculations (Colombian CST)."""

from decimal import Decimal
from enum import Enum

# Working hour boundaries (in 24-hour format)
DAY_START = 6  # 06:00 AM
NIGHT_START = 21  # 09:00 PM
NEXT_DAY_START = 6  # 06:00 AM next day

# Surcharge multipliers (CST - Código Sustantivo del Trabajo)
ORDINARY_RATE = Decimal("1.00")  # Base rate
NIGHT_SURCHARGE = Decimal("0.35")  # 35% surcharge for night hours (21:00-06:00)
SUNDAY_SURCHARGE = Decimal("0.75")  # 75% surcharge for Sunday
SUNDAY_NIGHT_SURCHARGE = Decimal(
    "1.10"
)  # 110% surcharge for Sunday night (21:00-06:00 on Sunday)
OVERTIME_SURCHARGE = Decimal("0.25")  # 25% surcharge for overtime
OVERTIME_NIGHT_SURCHARGE = Decimal("0.35")  # 35% surcharge for overtime at night

# Calculated combined rates
NIGHT_MULTIPLIER = Decimal("1.35")  # 1.00 + 0.35
SUNDAY_MULTIPLIER = Decimal("1.75")  # 1.00 + 0.75
SUNDAY_NIGHT_MULTIPLIER = Decimal("2.10")  # 1.00 + 1.10
OVERTIME_DAY_MULTIPLIER = Decimal("1.25")  # 1.00 + 0.25
OVERTIME_NIGHT_MULTIPLIER = Decimal(
    "1.75"
)  # 1.00 + 0.35 (note: different from Sunday night)
OVERTIME_SUNDAY_DAY_MULTIPLIER = Decimal("2.00")  # 1.00 + 0.75 + 0.25
OVERTIME_SUNDAY_NIGHT_MULTIPLIER = Decimal(
    "2.50"
)  # 1.00 + 1.10 + 0.25 (conservative: 1.00 + 1.10 + 0.40)

# Workweek limits (hours per week) by year
WORKWEEK_LIMITS = {
    2024: 46,  # CST Art 161 - 46 hours/week
    2025: 44,  # Expected reduction
    2026: 42,  # Expected reduction
}

# Overtime limits
MAX_OVERTIME_HOURS_PER_DAY = Decimal("2.0")  # Max 2h overtime per day (CST Art 159)
MAX_OVERTIME_HOURS_PER_WEEK = Decimal("12.0")  # Max 12h overtime per week (CST Art 159)

# Habitual Sunday threshold (if worker works 3+ Sundays in a month, considered "habitual")
HABITUAL_SUNDAY_THRESHOLD = 3

# Precision for payroll calculations
PAYROLL_DECIMAL_PLACES = 2
