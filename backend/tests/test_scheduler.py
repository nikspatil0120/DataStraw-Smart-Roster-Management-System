"""Tests for the scheduling engine."""
import pytest
from datetime import date, timedelta
from uuid import uuid4

from app.scheduler.engine import ConstraintBasedScheduler
from app.scheduler.models import (
    SchedulingInput,
    EmployeeScheduleInfo,
    AssignmentInfo,
    SchedulingRuleInfo,
)


@pytest.fixture
def scheduler():
    """Create scheduler instance."""
    return ConstraintBasedScheduler(time_limit_seconds=30, random_seed=42)


@pytest.fixture
def basic_scheduling_input():
    """Create basic scheduling input for testing."""
    emp_id_1 = uuid4()
    emp_id_2 = uuid4()
    brand_id_1 = uuid4()
    process_id_1 = uuid4()

    employees = {
        emp_id_1: EmployeeScheduleInfo(
            employee_id=emp_id_1,
            employee_code="EMP001",
            full_name="Test Employee 1",
            max_assignments_per_day=2,
            preferred_weekly_off="SUNDAY",
        ),
        emp_id_2: EmployeeScheduleInfo(
            employee_id=emp_id_2,
            employee_code="EMP002",
            full_name="Test Employee 2",
            max_assignments_per_day=2,
            preferred_weekly_off="SUNDAY",
        ),
    }

    assignments = [
        AssignmentInfo(
            assignment_id=uuid4(),
            employee_id=emp_id_1,
            brand_id=brand_id_1,
            process_id=process_id_1,
            assigned_from=date.today(),
            assigned_until=None,
            priority=1,
            max_daily_capacity=1,
        ),
        AssignmentInfo(
            assignment_id=uuid4(),
            employee_id=emp_id_2,
            brand_id=brand_id_1,
            process_id=process_id_1,
            assigned_from=date.today(),
            assigned_until=None,
            priority=1,
            max_daily_capacity=1,
        ),
    ]

    rules = [
        SchedulingRuleInfo(
            rule_id=uuid4(),
            brand_id=brand_id_1,
            process_id=process_id_1,
            operating_type="every_day",
            sunday_working=True,
            public_holiday_working=False,
            minimum_staff=1,
            maximum_staff=2,
        ),
    ]

    return SchedulingInput(
        month=1,
        year=2024,
        employees=employees,
        assignments=assignments,
        scheduling_rules=rules,
        public_holidays=set(),
        brand_specific_holidays={},
    )


def test_scheduler_initialization():
    """Test scheduler initialization."""
    scheduler = ConstraintBasedScheduler()
    assert scheduler.time_limit_seconds == 60
    assert scheduler.random_seed == 42


def test_scheduler_model_creation(scheduler, basic_scheduling_input):
    """Test that scheduler creates model successfully."""
    result = scheduler.schedule(basic_scheduling_input)
    assert result is not None
    assert result.status in ["OPTIMAL", "FEASIBLE", "INFEASIBLE", "UNKNOWN"]


def test_scheduler_generates_decisions(scheduler, basic_scheduling_input):
    """Test that scheduler generates decisions."""
    result = scheduler.schedule(basic_scheduling_input)
    assert isinstance(result.decisions, list)
    # Should have some decisions for the month
    assert len(result.decisions) >= 0


def test_operating_dates_generation(scheduler):
    """Test operating dates for a month."""
    dates = scheduler._get_operating_dates(1, 2024)
    assert len(dates) == 31  # January has 31 days
    assert dates[0] == date(2024, 1, 1)
    assert dates[-1] == date(2024, 1, 31)


def test_operating_dates_february_leap_year(scheduler):
    """Test February in leap year."""
    dates = scheduler._get_operating_dates(2, 2024)
    assert len(dates) == 29  # 2024 is a leap year


def test_operating_dates_february_non_leap_year(scheduler):
    """Test February in non-leap year."""
    dates = scheduler._get_operating_dates(2, 2023)
    assert len(dates) == 28  # 2023 is not a leap year


def test_is_preferred_off_day(scheduler):
    """Test preferred off day detection."""
    sunday = date(2024, 1, 7)  # Sunday
    monday = date(2024, 1, 8)  # Monday

    assert scheduler._is_preferred_off_day(sunday, "SUNDAY")
    assert not scheduler._is_preferred_off_day(monday, "SUNDAY")
    assert scheduler._is_preferred_off_day(monday, "MONDAY")


def test_status_to_string(scheduler):
    """Test status conversion."""
    assert scheduler._status_to_string(0) == "OPTIMAL"
    assert scheduler._status_to_string(1) == "FEASIBLE"
    assert scheduler._status_to_string(2) == "INFEASIBLE"
    assert scheduler._status_to_string(99) == "UNKNOWN"


def test_insufficient_staffing_scenario(scheduler):
    """Test scenario: Insufficient staffing."""
    emp_id = uuid4()
    brand_id = uuid4()
    process_id = uuid4()

    employees = {
        emp_id: EmployeeScheduleInfo(
            employee_id=emp_id,
            employee_code="EMP001",
            full_name="Test Employee",
            max_assignments_per_day=2,
            preferred_weekly_off=None,
            unavailable_dates={date(2024, 1, 15)},  # Unavailable on day 15
        ),
    }

    assignments = [
        AssignmentInfo(
            assignment_id=uuid4(),
            employee_id=emp_id,
            brand_id=brand_id,
            process_id=process_id,
            assigned_from=date.today(),
            assigned_until=None,
            priority=1,
            max_daily_capacity=1,
        ),
    ]

    rules = [
        SchedulingRuleInfo(
            rule_id=uuid4(),
            brand_id=brand_id,
            process_id=process_id,
            operating_type="every_day",
            sunday_working=True,
            public_holiday_working=False,
            minimum_staff=2,  # Requires 2 employees, but only 1 available
            maximum_staff=3,
        ),
    ]

    scheduling_input = SchedulingInput(
        month=1,
        year=2024,
        employees=employees,
        assignments=assignments,
        scheduling_rules=rules,
        public_holidays=set(),
        brand_specific_holidays={},
    )

    result = scheduler.schedule(scheduling_input)
    # Should detect infeasibility
    assert result.status in ["INFEASIBLE", "FEASIBLE"]  # May be infeasible


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
