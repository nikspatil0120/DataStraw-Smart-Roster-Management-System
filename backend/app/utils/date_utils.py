"""Date utilities."""
from datetime import date, datetime, timedelta
from typing import List


def get_month_dates(month: int, year: int) -> List[date]:
    """Get all dates in a month."""
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    
    current = date(year, month, 1)
    dates = []
    
    while current < next_month:
        dates.append(current)
        current += timedelta(days=1)
    
    return dates


def is_sunday(d: date) -> bool:
    """Check if date is Sunday."""
    return d.weekday() == 6


def is_weekday(d: date) -> bool:
    """Check if date is a weekday."""
    return d.weekday() < 5


def is_saturday(d: date) -> bool:
    """Check if date is Saturday."""
    return d.weekday() == 5


def get_current_month_year() -> tuple:
    """Get current month and year."""
    today = date.today()
    return today.month, today.year
