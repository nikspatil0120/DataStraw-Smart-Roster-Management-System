"""Core scheduling engine using OR-Tools CP-SAT."""
from ortools.sat.python import cp_model
from datetime import date, datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple
from uuid import UUID
import logging

from app.scheduler.models import (
    SchedulingInput,
    SchedulingResult,
    ScheduleDecision,
    EmployeeScheduleInfo,
    AssignmentInfo,
    SchedulingRuleInfo,
)

logger = logging.getLogger(__name__)


class ConstraintBasedScheduler:
    """Constraint-based scheduler using OR-Tools CP-SAT."""

    def __init__(self, time_limit_seconds: int = 60, random_seed: int = 42):
        """Initialize the scheduler."""
        self.time_limit_seconds = time_limit_seconds
        self.random_seed = random_seed
        self.model = None
        self.decisions = None

    def schedule(self, scheduling_input: SchedulingInput) -> SchedulingResult:
        """Generate a roster using constraint-based scheduling."""
        try:
            # Initialize model
            self.model = cp_model.CpModel()
            self.decisions = {}

            # Get all dates in the month
            operating_dates = self._get_operating_dates(
                scheduling_input.month,
                scheduling_input.year,
            )

            # Create decision variables
            self._create_decision_variables(
                scheduling_input,
                operating_dates,
            )

            # Add constraints
            self._add_mandatory_constraints(
                scheduling_input,
                operating_dates,
            )

            # Add soft constraints and optimization objectives
            self._add_soft_constraints(scheduling_input, operating_dates)

            # Solve
            result = self._solve(scheduling_input, operating_dates)

            return result

        except Exception as e:
            logger.error(f"Scheduling error: {str(e)}", exc_info=True)
            return SchedulingResult(
                status="UNKNOWN",
                diagnostics={"error": str(e)},
            )

    def _get_operating_dates(
        self,
        month: int,
        year: int,
    ) -> List[date]:
        """Get all dates in the month."""
        if month == 12:
            next_month_date = date(year + 1, 1, 1)
        else:
            next_month_date = date(year, month + 1, 1)

        first_date = date(year, month, 1)
        dates = []
        current_date = first_date

        while current_date < next_month_date:
            dates.append(current_date)
            current_date += timedelta(days=1)

        return dates

    def _create_decision_variables(
        self,
        scheduling_input: SchedulingInput,
        operating_dates: List[date],
    ):
        """Create binary decision variables for assignments."""
        # For each (employee, brand, process, date) combination
        for emp_id, employee in scheduling_input.employees.items():
            # Find all assignments for this employee
            for assignment in scheduling_input.assignments:
                if assignment.employee_id != emp_id:
                    continue

                for d in operating_dates:
                    # Check if date is within assignment period
                    if assignment.assigned_until and d > assignment.assigned_until:
                        continue
                    if d < assignment.assigned_from:
                        continue

                    key = (emp_id, assignment.brand_id, assignment.process_id, d)
                    self.decisions[key] = self.model.NewBoolVar(
                        f"emp_{emp_id}_brand_{assignment.brand_id}_date_{d}"
                    )

    def _add_mandatory_constraints(
        self,
        scheduling_input: SchedulingInput,
        operating_dates: List[date],
    ):
        """Add mandatory constraints that must never be violated."""

        # Constraint 1: Cannot work when unavailable
        for emp_id, employee in scheduling_input.employees.items():
            for unavail_date in employee.unavailable_dates:
                for key in self.decisions:
                    if key[0] == emp_id and key[3] == unavail_date:
                        self.model.Add(self.decisions[key] == 0)

        # Constraint 2: Approved leave blocks assignment
        for emp_id, employee in scheduling_input.employees.items():
            for leave_date in employee.leave_dates:
                for key in self.decisions:
                    if key[0] == emp_id and key[3] == leave_date:
                        self.model.Add(self.decisions[key] == 0)

        # Constraint 3: Approved comp-offs block assignment
        for emp_id, employee in scheduling_input.employees.items():
            for comp_off_date in employee.comp_off_dates:
                for key in self.decisions:
                    if key[0] == emp_id and key[3] == comp_off_date:
                        self.model.Add(self.decisions[key] == 0)

        # Constraint 4: Employees can only work on assigned brands/processes
        for key in self.decisions:
            emp_id, brand_id, process_id, d = key
            # Find if this assignment exists
            assignment_exists = False
            for assignment in scheduling_input.assignments:
                if (
                    assignment.employee_id == emp_id
                    and assignment.brand_id == brand_id
                    and assignment.process_id == process_id
                ):
                    assignment_exists = True
                    break

            if not assignment_exists:
                self.model.Add(self.decisions[key] == 0)

        # Constraint 5: Minimum staffing requirements
        for rule in scheduling_input.scheduling_rules:
            for d in operating_dates:
                # Check if brand operates on this date
                if not self._brand_operates_on_date(
                    d,
                    rule,
                    scheduling_input,
                ):
                    continue

                # Get all employees assigned to this brand/process combination
                available_decisions = []
                for key in self.decisions:
                    emp_id, brand_id, process_id, date_key = key
                    if (
                        brand_id == rule.brand_id
                        and (rule.process_id is None or process_id == rule.process_id)
                        and date_key == d
                    ):
                        available_decisions.append(self.decisions[key])

                if available_decisions:
                    self.model.Add(
                        sum(available_decisions) >= rule.minimum_staff
                    )

        # Constraint 6: Maximum daily assignments per employee
        for emp_id, employee in scheduling_input.employees.items():
            for d in operating_dates:
                daily_assignments = []
                for key in self.decisions:
                    if key[0] == emp_id and key[3] == d:
                        daily_assignments.append(self.decisions[key])

                if daily_assignments:
                    self.model.Add(
                        sum(daily_assignments) <= employee.max_assignments_per_day
                    )

    def _add_soft_constraints(
        self,
        scheduling_input: SchedulingInput,
        operating_dates: List[date],
    ):
        """Add soft constraints and optimization objectives."""
        # Try to honor preferred weekly offs
        penalties = []
        for emp_id, employee in scheduling_input.employees.items():
            if not employee.preferred_weekly_off:
                continue

            # Find all dates that are the preferred day off
            for d in operating_dates:
                if self._is_preferred_off_day(d, employee.preferred_weekly_off):
                    for key in self.decisions:
                        if key[0] == emp_id and key[3] == d:
                            # Add penalty if employee works on preferred off day
                            penalties.append(self.decisions[key])

        if penalties:
            self.model.Minimize(sum(penalties))

    def _brand_operates_on_date(
        self,
        d: date,
        rule: SchedulingRuleInfo,
        scheduling_input: SchedulingInput,
    ) -> bool:
        """Check if brand operates on a specific date."""
        # Check public holidays
        if d in scheduling_input.public_holidays:
            if rule.brand_id in scheduling_input.brand_specific_holidays:
                if d in scheduling_input.brand_specific_holidays[rule.brand_id]:
                    return rule.public_holiday_working
            return rule.public_holiday_working

        # Check Sundays
        if d.weekday() == 6:  # Sunday
            return rule.sunday_working

        return True

    def _is_preferred_off_day(self, d: date, preferred_off: str) -> bool:
        """Check if date is a preferred off day."""
        weekday_names = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
        if preferred_off.upper() not in weekday_names:
            return False

        weekday_index = weekday_names.index(preferred_off.upper())
        return d.weekday() == weekday_index

    def _solve(
        self,
        scheduling_input: SchedulingInput,
        operating_dates: List[date],
    ) -> SchedulingResult:
        """Solve the model and return results."""
        # Configure solver
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.time_limit_seconds
        solver.parameters.random_seed = self.random_seed
        solver.parameters.log_search_progress = False

        # Solve
        status = solver.Solve(self.model)

        # Process results
        result = SchedulingResult(
            status=self._status_to_string(status),
            diagnostics={
                "solver_status": status,
                "wall_time": solver.wall_time,
                "num_decisions": len(self.decisions),
            },
        )

        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            result.objective_value = solver.ObjectiveValue()

            # Extract decisions
            for key, var in self.decisions.items():
                if solver.BooleanValue(var):
                    emp_id, brand_id, process_id, d = key
                    result.decisions.append(
                        ScheduleDecision(
                            employee_id=emp_id,
                            brand_id=brand_id,
                            process_id=process_id,
                            date=d,
                            assigned=True,
                        )
                    )

        elif status == cp_model.INFEASIBLE:
            result.conflicts.append(
                "No feasible schedule exists. Check for conflicting constraints."
            )

        return result

    def _status_to_string(self, status: int) -> str:
        """Convert solver status to string."""
        status_map = {
            cp_model.OPTIMAL: "OPTIMAL",
            cp_model.FEASIBLE: "FEASIBLE",
            cp_model.INFEASIBLE: "INFEASIBLE",
            cp_model.MODEL_INVALID: "MODEL_INVALID",
        }
        return status_map.get(status, "UNKNOWN")
