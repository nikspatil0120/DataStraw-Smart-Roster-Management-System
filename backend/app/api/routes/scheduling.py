"""Scheduling routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
import logging

from app.database import get_db
from app.models import (
    Roster,
    RosterEntry,
    Employee,
    Brand,
    Process,
    Assignment,
    Leave,
    Holiday,
    SchedulingRule,
    Availability,
    Conflict,
)
from app.models.roster import RosterStatus, AssignmentStatus
from app.scheduler.engine import ConstraintBasedScheduler
from app.scheduler.models import (
    SchedulingInput,
    EmployeeScheduleInfo,
    AssignmentInfo,
    SchedulingRuleInfo,
    ScheduleDecision,
)
from app.services.validation_service import ValidationService
from app.utils.date_utils import get_month_dates
from app.utils.response import success_response
from app.config import settings

router = APIRouter(prefix="/api/scheduling", tags=["scheduling"])
logger = logging.getLogger(__name__)


class GenerateRosterRequest(BaseModel):
    """Generate roster request."""
    roster_name: str
    month: int
    year: int


class ValidateRosterRequest(BaseModel):
    """Validate roster request."""
    roster_id: UUID


@router.post("/generate")
async def generate_roster(
    request: GenerateRosterRequest,
    db: Session = Depends(get_db),
):
    """Generate a new monthly roster."""
    try:
        # Validate month/year
        if not (1 <= request.month <= 12 and 2000 <= request.year <= 2100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid month or year",
            )

        # Check for existing roster
        existing = db.query(Roster).filter(
            Roster.month == request.month,
            Roster.year == request.year,
            Roster.status != RosterStatus.ARCHIVED.value,
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Roster already exists for {request.month}/{request.year}",
            )

        # Prepare scheduling input
        scheduling_input = _prepare_scheduling_input(db, request.month, request.year)
        operating_dates = get_month_dates(request.month, request.year)

        # Run scheduler
        scheduler = ConstraintBasedScheduler(
            time_limit_seconds=300,
            random_seed=settings.solver_random_seed,
        )
        result = scheduler.schedule(scheduling_input)
        
        # Fallback: if infeasible, generate simple round-robin assignments
        if result.status == "INFEASIBLE":
            logger.warning("Solver returned INFEASIBLE - using fallback assignment")
            from itertools import cycle
            
            # Get all active assignments
            all_assignments = db.query(Assignment).filter(Assignment.status == "active").all()
            if all_assignments:
                # Simple round-robin: assign employees to brands for each day
                emp_list = list(scheduling_input.employees.keys())
                assign_cycle = cycle(all_assignments)
                
                for d in operating_dates:
                    for i in range(min(3, len(emp_list))):  # Assign 3 employees per day
                        emp_id = emp_list[i % len(emp_list)]
                        assignment = next(assign_cycle)
                        
                        result.decisions.append(
                            ScheduleDecision(
                                employee_id=emp_id,
                                brand_id=assignment.brand_id,
                                process_id=assignment.process_id,
                                date=d,
                                assigned=True,
                            )
                        )
            result.status = "FEASIBLE (FALLBACK)"
        
        logger.info(f"Scheduler status: {result.status}")
        logger.info(f"Decisions count: {len(result.decisions)}")


        # Create roster
        roster = Roster(
            roster_name=request.roster_name,
            month=request.month,
            year=request.year,
            status=RosterStatus.GENERATED.value,
            generated_at=datetime.utcnow(),
        )
        db.add(roster)
        db.flush()

        # Add roster entries from decisions
        logger.info(f"Adding {len(result.decisions)} entries to roster")
        for decision in result.decisions:
            entry = RosterEntry(
                roster_id=roster.id,
                employee_id=decision.employee_id,
                brand_id=decision.brand_id,
                process_id=decision.process_id,
                roster_date=decision.date,
                assignment_status=AssignmentStatus.WORKING.value,
            )
            db.add(entry)

        db.commit()
        logger.info(f"Roster created with {len(result.decisions)} entries")

        # Validate roster
        validation_service = ValidationService(db)
        is_valid, conflicts = validation_service.validate_roster(roster)

        if conflicts:
            validation_service.persist_conflicts(roster, conflicts)

        roster.status = RosterStatus.VALIDATED.value if is_valid else RosterStatus.GENERATED.value
        db.commit()

        return {
            "success": True,
            "roster_id": str(roster.id),
            "status": str(result.status),  # Convert OR-Tools status to string
            "is_valid": is_valid,
            "conflict_count": len(conflicts),
            "diagnostics": str(result.diagnostics) if result.diagnostics else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scheduling failed: {str(e)}",
        )


@router.post("/validate")
async def validate_roster(
    request: ValidateRosterRequest,
    db: Session = Depends(get_db),
):
    """Validate an existing roster."""
    roster = db.query(Roster).filter(Roster.id == request.roster_id).first()

    if not roster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roster not found",
        )

    validation_service = ValidationService(db)
    is_valid, conflicts = validation_service.validate_roster(roster)

    if conflicts:
        validation_service.persist_conflicts(roster, conflicts)

    roster.status = RosterStatus.VALIDATED.value if is_valid else RosterStatus.GENERATED.value
    db.commit()

    return {
        "success": True,
        "is_valid": is_valid,
        "conflict_count": len(conflicts),
        "conflicts": conflicts,
    }


def _prepare_scheduling_input(
    db: Session,
    month: int,
    year: int,
) -> SchedulingInput:
    """Prepare input for the scheduling engine."""
    operating_dates = get_month_dates(month, year)

    # Get all active employees
    employees_db = db.query(Employee).filter(
        Employee.employment_status == "active"
    ).all()

    employees = {}
    for emp in employees_db:
        unavailable_dates = set()
        leave_dates = set()
        comp_off_dates = set()

        # Get unavailable dates
        availability_records = db.query(Availability).filter(
            Availability.employee_id == emp.id,
            Availability.date.in_(operating_dates),
            Availability.availability_status == "unavailable",
        ).all()
        unavailable_dates = {a.date for a in availability_records}

        # Get approved leave dates
        leaves = db.query(Leave).filter(
            Leave.employee_id == emp.id,
            Leave.status == "approved",
            Leave.start_date <= max(operating_dates),
            Leave.end_date >= min(operating_dates),
        ).all()

        for leave in leaves:
            for d in operating_dates:
                if leave.start_date <= d <= leave.end_date:
                    if leave.leave_type == "comp_off":
                        comp_off_dates.add(d)
                    else:
                        leave_dates.add(d)

        employees[emp.id] = EmployeeScheduleInfo(
            employee_id=emp.id,
            employee_code=emp.employee_code,
            full_name=emp.full_name,
            max_assignments_per_day=emp.max_assignments_per_day,
            preferred_weekly_off=emp.preferred_weekly_off,
            joining_date=emp.joining_date,
            unavailable_dates=unavailable_dates,
            leave_dates=leave_dates,
            comp_off_dates=comp_off_dates,
        )

    # Get assignments
    assignments_db = db.query(Assignment).filter(
        Assignment.status == "active",
    ).all()

    assignments = []
    for assign in assignments_db:
        assignments.append(
            AssignmentInfo(
                assignment_id=assign.id,
                employee_id=assign.employee_id,
                brand_id=assign.brand_id,
                process_id=assign.process_id,
                assigned_from=assign.assigned_from,
                assigned_until=assign.assigned_until,
                priority=assign.priority,
                max_daily_capacity=assign.max_daily_capacity,
            )
        )

    # Get scheduling rules
    rules_db = db.query(SchedulingRule).filter(
        SchedulingRule.status == "active",
    ).all()

    rules = []
    for rule in rules_db:
        rules.append(
            SchedulingRuleInfo(
                rule_id=rule.id,
                brand_id=rule.brand_id,
                process_id=rule.process_id,
                operating_type=rule.operating_type,
                sunday_working=rule.sunday_working,
                public_holiday_working=rule.public_holiday_working,
                minimum_staff=rule.minimum_staff,
                maximum_staff=rule.maximum_staff,
                preferred_staff=rule.preferred_staff,
            )
        )

    # Get public holidays
    holidays_db = db.query(Holiday).filter(
        Holiday.status == "active",
        Holiday.holiday_date.in_(operating_dates),
    ).all()

    public_holidays = set()
    brand_specific_holidays = {}

    for holiday in holidays_db:
        if holiday.applicable_scope == "company":
            public_holidays.add(holiday.holiday_date)
        elif holiday.brand_id:
            if holiday.brand_id not in brand_specific_holidays:
                brand_specific_holidays[holiday.brand_id] = set()
            brand_specific_holidays[holiday.brand_id].add(holiday.holiday_date)

    return SchedulingInput(
        month=month,
        year=year,
        employees=employees,
        assignments=assignments,
        scheduling_rules=rules,
        public_holidays=public_holidays,
        brand_specific_holidays=brand_specific_holidays,
    )
