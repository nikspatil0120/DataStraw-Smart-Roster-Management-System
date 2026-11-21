"""Roster validation service."""
from datetime import date, datetime
from typing import Dict, List, Set, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
import logging

from app.models import (
    Roster,
    RosterEntry,
    Employee,
    Assignment,
    Leave,
    Holiday,
    SchedulingRule,
    Availability,
    Conflict,
)
from app.models.roster import AssignmentStatus
from app.models.conflict import ConflictType, ConflictSeverity

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for validating rosters."""

    def __init__(self, db: Session):
        """Initialize validation service."""
        self.db = db

    def validate_roster(self, roster: Roster) -> Tuple[bool, List[Dict]]:
        """Validate a roster comprehensively."""
        conflicts = []

        # Run all validations
        conflicts.extend(self._check_coverage(roster))
        conflicts.extend(self._check_employee_conflicts(roster))
        conflicts.extend(self._check_leave_conflicts(roster))
        conflicts.extend(self._check_unauthorized_assignments(roster))

        # Determine if roster is valid (no critical conflicts)
        has_critical = any(c["severity"] == "critical" for c in conflicts)
        is_valid = not has_critical

        return is_valid, conflicts

    def _check_coverage(self, roster: Roster) -> List[Dict]:
        """Check minimum staffing coverage."""
        conflicts = []

        # Group entries by date, brand, process
        coverage_map = {}
        for entry in roster.entries:
            if entry.assignment_status == AssignmentStatus.WORKING:
                key = (entry.roster_date, entry.brand_id, entry.process_id)
                if key not in coverage_map:
                    coverage_map[key] = []
                coverage_map[key].append(entry.employee_id)

        # Check against scheduling rules
        for rule in self.db.query(SchedulingRule).all():
            for entry in roster.entries:
                if entry.brand_id != rule.brand_id:
                    continue
                if rule.process_id and entry.process_id != rule.process_id:
                    continue

                key = (entry.roster_date, entry.brand_id, entry.process_id)
                actual_count = len(coverage_map.get(key, []))

                if actual_count < rule.minimum_staff:
                    conflicts.append(
                        {
                            "type": ConflictType.INSUFFICIENT_COVERAGE.value,
                            "severity": ConflictSeverity.CRITICAL.value,
                            "date": entry.roster_date,
                            "brand_id": entry.brand_id,
                            "process_id": entry.process_id,
                            "description": f"Insufficient coverage. Required: {rule.minimum_staff}, Actual: {actual_count}",
                            "suggested_resolution": "Assign additional eligible employees",
                        }
                    )

        return conflicts

    def _check_employee_conflicts(self, roster: Roster) -> List[Dict]:
        """Check for employee-level conflicts."""
        conflicts = []

        # Check daily capacity
        daily_assignments = {}
        for entry in roster.entries:
            if entry.assignment_status == AssignmentStatus.WORKING:
                key = (entry.employee_id, entry.roster_date)
                if key not in daily_assignments:
                    daily_assignments[key] = 0
                daily_assignments[key] += 1

        for entry in roster.entries:
            employee = self.db.query(Employee).filter_by(id=entry.employee_id).first()
            if not employee:
                continue

            key = (entry.employee_id, entry.roster_date)
            daily_count = daily_assignments.get(key, 0)

            if daily_count > employee.max_assignments_per_day:
                conflicts.append(
                    {
                        "type": ConflictType.CAPACITY_EXCEEDED.value,
                        "severity": ConflictSeverity.HIGH.value,
                        "date": entry.roster_date,
                        "employee_id": entry.employee_id,
                        "description": f"Employee exceeds daily capacity. Assigned: {daily_count}, Limit: {employee.max_assignments_per_day}",
                        "suggested_resolution": "Remove one or more assignments",
                    }
                )

        return conflicts

    def _check_leave_conflicts(self, roster: Roster) -> List[Dict]:
        """Check for leave and availability conflicts."""
        conflicts = []

        for entry in roster.entries:
            if entry.assignment_status == AssignmentStatus.WORKING:
                # Check approved leaves
                leave = (
                    self.db.query(Leave)
                    .filter(
                        Leave.employee_id == entry.employee_id,
                        Leave.start_date <= entry.roster_date,
                        Leave.end_date >= entry.roster_date,
                        Leave.status == "approved",
                    )
                    .first()
                )

                if leave:
                    conflicts.append(
                        {
                            "type": ConflictType.LEAVE_CONFLICT.value,
                            "severity": ConflictSeverity.CRITICAL.value,
                            "date": entry.roster_date,
                            "employee_id": entry.employee_id,
                            "description": f"Employee assigned during approved leave ({leave.leave_type})",
                            "suggested_resolution": "Remove assignment or cancel leave",
                        }
                    )

                # Check availability
                availability = (
                    self.db.query(Availability)
                    .filter(
                        Availability.employee_id == entry.employee_id,
                        Availability.date == entry.roster_date,
                        Availability.availability_status == "unavailable",
                    )
                    .first()
                )

                if availability:
                    conflicts.append(
                        {
                            "type": ConflictType.EMPLOYEE_UNAVAILABLE.value,
                            "severity": ConflictSeverity.CRITICAL.value,
                            "date": entry.roster_date,
                            "employee_id": entry.employee_id,
                            "description": f"Employee unavailable: {availability.reason}",
                            "suggested_resolution": "Mark employee as available or remove assignment",
                        }
                    )

        return conflicts

    def _check_unauthorized_assignments(self, roster: Roster) -> List[Dict]:
        """Check for unauthorized brand/process assignments."""
        conflicts = []

        for entry in roster.entries:
            if entry.assignment_status == AssignmentStatus.WORKING:
                # Check if employee is assigned to this brand/process
                assignment = (
                    self.db.query(Assignment)
                    .filter(
                        Assignment.employee_id == entry.employee_id,
                        Assignment.brand_id == entry.brand_id,
                        Assignment.process_id == entry.process_id,
                    )
                    .first()
                )

                if not assignment:
                    conflicts.append(
                        {
                            "type": ConflictType.UNAUTHORIZED_ASSIGNMENT.value,
                            "severity": ConflictSeverity.CRITICAL.value,
                            "date": entry.roster_date,
                            "employee_id": entry.employee_id,
                            "brand_id": entry.brand_id,
                            "process_id": entry.process_id,
                            "description": "Employee not assigned to this brand/process",
                            "suggested_resolution": "Remove assignment or create an assignment record",
                        }
                    )

        return conflicts

    def persist_conflicts(
        self,
        roster: Roster,
        conflicts: List[Dict],
    ) -> None:
        """Persist conflicts to the database."""
        # Clear existing conflicts
        self.db.query(Conflict).filter_by(roster_id=roster.id).delete()

        # Add new conflicts (only if brand_id is present)
        for conflict_data in conflicts:
            if not conflict_data.get("brand_id"):
                continue  # Skip conflicts without brand_id
                
            conflict = Conflict(
                roster_id=roster.id,
                employee_id=conflict_data.get("employee_id"),
                brand_id=conflict_data.get("brand_id"),
                process_id=conflict_data.get("process_id"),
                conflict_date=conflict_data.get("date"),
                conflict_type=conflict_data.get("type"),
                severity=conflict_data.get("severity"),
                description=conflict_data.get("description"),
                suggested_resolution=conflict_data.get("suggested_resolution"),
            )
            self.db.add(conflict)

        self.db.commit()
