"""Scheduler data models."""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Dict, Set, Optional
from uuid import UUID


@dataclass
class EmployeeScheduleInfo:
    """Employee scheduling information."""
    employee_id: UUID
    employee_code: str
    full_name: str
    max_assignments_per_day: int
    preferred_weekly_off: Optional[str]
    joining_date: Optional[date]
    unavailable_dates: Set[date] = field(default_factory=set)
    leave_dates: Set[date] = field(default_factory=set)
    comp_off_dates: Set[date] = field(default_factory=set)


@dataclass
class AssignmentInfo:
    """Assignment information."""
    assignment_id: UUID
    employee_id: UUID
    brand_id: UUID
    process_id: Optional[UUID]
    assigned_from: date
    assigned_until: Optional[date]
    priority: int
    max_daily_capacity: int


@dataclass
class SchedulingRuleInfo:
    """Scheduling rule information."""
    rule_id: UUID
    brand_id: UUID
    process_id: Optional[UUID]
    operating_type: str
    sunday_working: bool
    public_holiday_working: bool
    minimum_staff: int
    maximum_staff: Optional[int]
    preferred_staff: Optional[int]


@dataclass
class SchedulingInput:
    """Input data for the scheduling engine."""
    month: int
    year: int
    employees: Dict[UUID, EmployeeScheduleInfo]
    assignments: List[AssignmentInfo]
    scheduling_rules: List[SchedulingRuleInfo]
    public_holidays: Set[date]
    brand_specific_holidays: Dict[UUID, Set[date]]


@dataclass
class ScheduleDecision:
    """A single scheduling decision."""
    employee_id: UUID
    brand_id: UUID
    process_id: Optional[UUID]
    date: date
    assigned: bool


@dataclass
class SchedulingResult:
    """Result of scheduling."""
    status: str  # OPTIMAL, FEASIBLE, INFEASIBLE, UNKNOWN
    decisions: List[ScheduleDecision] = field(default_factory=list)
    objective_value: Optional[float] = None
    conflicts: List[str] = field(default_factory=list)
    diagnostics: Dict = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)
