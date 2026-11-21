"""Advanced scheduling routes (change management, regeneration)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from uuid import UUID
from pydantic import BaseModel
from typing import List

from app.database import get_db
from app.models import (
    Roster, RosterEntry, Employee, Availability, Leave, Assignment
)
from app.models.roster import AssignmentStatus
from app.scheduler.engine import ConstraintBasedScheduler
from app.services.validation_service import ValidationService
from app.api.routes.scheduling import _prepare_scheduling_input
from app.utils.date_utils import get_month_dates

router = APIRouter(prefix="/api/scheduling", tags=["scheduling"])


class EmployeeUnavailabilityRequest(BaseModel):
    """Request to mark employee unavailable."""
    employee_id: UUID
    start_date: date
    end_date: date
    reason: str = "Employee unavailable"


class RegenerateRequest(BaseModel):
    """Request to regenerate affected assignments."""
    roster_id: UUID
    employee_id: UUID


@router.post("/mark-unavailable")
async def mark_employee_unavailable(
    request: EmployeeUnavailabilityRequest,
    db: Session = Depends(get_db),
):
    """Mark employee unavailable for a date range."""
    try:
        # Add availability records
        current_date = request.start_date
        while current_date <= request.end_date:
            # Check if already exists
            existing = db.query(Availability).filter(
                Availability.employee_id == request.employee_id,
                Availability.date == current_date,
            ).first()
            
            if not existing:
                availability = Availability(
                    employee_id=request.employee_id,
                    date=current_date,
                    availability_status="unavailable",
                    reason=request.reason,
                )
                db.add(availability)
            
            current_date += __import__('datetime').timedelta(days=1)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Employee marked unavailable from {request.start_date} to {request.end_date}",
            "affected_dates": (request.end_date - request.start_date).days + 1,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/regenerate-affected")
async def regenerate_affected_roster(
    request: RegenerateRequest,
    db: Session = Depends(get_db),
):
    """Regenerate roster entries affected by employee unavailability."""
    try:
        # Get roster
        roster = db.query(Roster).filter(Roster.id == request.roster_id).first()
        if not roster:
            raise HTTPException(status_code=404, detail="Roster not found")
        
        # Get affected entries (entries for this employee)
        affected_entries = db.query(RosterEntry).filter(
            RosterEntry.roster_id == request.roster_id,
            RosterEntry.employee_id == request.employee_id,
            RosterEntry.assignment_status == AssignmentStatus.WORKING.value,
        ).all()
        
        # Get available backup employees for each brand/process
        backups = {}
        for entry in affected_entries:
            key = (entry.brand_id, entry.process_id)
            if key not in backups:
                # Find other employees assigned to this brand/process
                other_assignments = db.query(Assignment).filter(
                    Assignment.brand_id == entry.brand_id,
                    Assignment.process_id == entry.process_id,
                    Assignment.employee_id != request.employee_id,
                    Assignment.status == "active",
                ).all()
                
                # Check their availability
                candidates = []
                for assign in other_assignments:
                    avail = db.query(Availability).filter(
                        Availability.employee_id == assign.employee_id,
                        Availability.date == entry.roster_date,
                        Availability.availability_status == "unavailable",
                    ).first()
                    
                    if not avail:  # Employee is available
                        emp = db.query(Employee).filter(
                            Employee.id == assign.employee_id
                        ).first()
                        candidates.append({
                            "employee_id": assign.employee_id,
                            "employee_name": emp.full_name,
                            "priority": assign.priority,
                        })
                
                backups[key] = sorted(candidates, key=lambda x: x["priority"])
        
        # Prepare suggestions
        suggestions = []
        for entry in affected_entries:
            key = (entry.brand_id, entry.process_id)
            candidates = backups.get(key, [])
            
            suggestion = {
                "date": entry.roster_date.isoformat(),
                "original_employee_id": str(request.employee_id),
                "brand_id": str(entry.brand_id),
                "process_id": str(entry.process_id) if entry.process_id else None,
                "backup_options": candidates[:3],  # Top 3 options
                "has_backup": len(candidates) > 0,
            }
            suggestions.append(suggestion)
        
        return {
            "success": True,
            "roster_id": str(request.roster_id),
            "affected_dates": len(affected_entries),
            "suggestions": suggestions,
            "message": f"Found {len(affected_entries)} affected entries. Showing backup options.",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/apply-changes")
async def apply_suggested_changes(
    roster_id: UUID,
    changes: List[dict],
    db: Session = Depends(get_db),
):
    """Apply suggested changes to roster."""
    try:
        roster = db.query(Roster).filter(Roster.id == roster_id).first()
        if not roster:
            raise HTTPException(status_code=404, detail="Roster not found")
        
        applied = 0
        for change in changes:
            # Find entry to update
            entry = db.query(RosterEntry).filter(
                RosterEntry.roster_id == roster_id,
                RosterEntry.roster_date == __import__('datetime').datetime.fromisoformat(change["date"]).date(),
                RosterEntry.employee_id == change["original_employee_id"],
            ).first()
            
            if entry:
                # Update with new employee
                entry.employee_id = change["new_employee_id"]
                entry.is_manual = True
                db.commit()
                applied += 1
        
        # Revalidate roster
        validation_service = ValidationService(db)
        is_valid, conflicts = validation_service.validate_roster(roster)
        if conflicts:
            validation_service.persist_conflicts(roster, conflicts)
        
        return {
            "success": True,
            "applied_changes": applied,
            "conflicts_after": len(conflicts),
            "message": f"Applied {applied} changes. Roster revalidated.",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
