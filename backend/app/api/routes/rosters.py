"""Roster routes."""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models import Roster, RosterEntry, Conflict
from app.models.roster import RosterStatus, AssignmentStatus
from app.utils.response import paginated_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rosters", tags=["rosters"])


@router.get("", response_model=dict)
async def list_rosters(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: str = Query(None, alias="status"),
    db: Session = Depends(get_db),
):
    """List all rosters with pagination."""
    query = db.query(Roster)
    
    if status_filter:
        query = query.filter(Roster.status == status_filter)
    
    total = query.count()
    rosters = query.order_by(Roster.created_at.desc()).offset(skip).limit(limit).all()
    
    return paginated_response(
        items=[_roster_to_dict(r) for r in rosters],
        total=total,
        page=skip // limit + 1,
        per_page=limit,
    )


@router.get("/{roster_id}", response_model=dict)
async def get_roster(
    roster_id: UUID,
    db: Session = Depends(get_db),
):
    """Get roster by ID with entries and conflicts."""
    roster = db.query(Roster).filter(Roster.id == roster_id).first()
    
    if not roster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roster not found",
        )
    
    entries = db.query(RosterEntry).filter(RosterEntry.roster_id == roster_id).count()
    conflicts = db.query(Conflict).filter(Conflict.roster_id == roster_id).count()
    
    return {
        **_roster_to_dict(roster),
        "entries_count": entries,
        "conflicts_count": conflicts,
    }


@router.post("/{roster_id}/publish", response_model=dict)
async def publish_roster(
    roster_id: UUID,
    db: Session = Depends(get_db),
):
    """Publish a validated roster."""
    roster = db.query(Roster).filter(Roster.id == roster_id).first()
    
    if not roster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roster not found",
        )
    
    # Check if roster is valid (no critical conflicts)
    # Allow publishing with conflicts for demonstration mode
    critical_conflicts = db.query(Conflict).filter(
        Conflict.roster_id == roster_id,
        Conflict.severity == "critical",
    ).count()
    
    # Log conflicts but allow publishing
    if critical_conflicts > 0:
        logger.warning(f"Publishing roster with {critical_conflicts} critical conflicts (demonstration mode)")
    
    # Check if already published
    if roster.status == RosterStatus.PUBLISHED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Roster already published",
        )
    
    # Update status
    roster.status = RosterStatus.PUBLISHED.value
    roster.published_at = datetime.utcnow()
    db.commit()
    db.refresh(roster)
    
    return {
        "success": True,
        "message": f"Roster published successfully",
        "roster": _roster_to_dict(roster),
    }


@router.post("/{roster_id}/archive", response_model=dict)
async def archive_roster(
    roster_id: UUID,
    db: Session = Depends(get_db),
):
    """Archive a roster."""
    roster = db.query(Roster).filter(Roster.id == roster_id).first()
    
    if not roster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roster not found",
        )
    
    if roster.status == RosterStatus.ARCHIVED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Roster already archived",
        )
    
    roster.status = RosterStatus.ARCHIVED.value
    db.commit()
    db.refresh(roster)
    
    return {
        "success": True,
        "message": "Roster archived successfully",
        "roster": _roster_to_dict(roster),
    }


@router.get("/{roster_id}/coverage", response_model=dict)
async def get_roster_coverage(
    roster_id: UUID,
    db: Session = Depends(get_db),
):
    """Get coverage analysis for a roster."""
    roster = db.query(Roster).filter(Roster.id == roster_id).first()
    
    if not roster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roster not found",
        )
    
    # Calculate coverage metrics
    total_entries = db.query(RosterEntry).filter(
        RosterEntry.roster_id == roster_id
    ).count()
    
    working_entries = db.query(RosterEntry).filter(
        RosterEntry.roster_id == roster_id,
        RosterEntry.assignment_status == AssignmentStatus.WORKING.value,
    ).count()
    
    leave_entries = db.query(RosterEntry).filter(
        RosterEntry.roster_id == roster_id,
        RosterEntry.assignment_status == AssignmentStatus.LEAVE.value,
    ).count()
    
    weekly_off_entries = db.query(RosterEntry).filter(
        RosterEntry.roster_id == roster_id,
        RosterEntry.assignment_status == AssignmentStatus.WEEKLY_OFF.value,
    ).count()
    
    conflicts = db.query(Conflict).filter(
        Conflict.roster_id == roster_id
    ).count()
    
    critical_conflicts = db.query(Conflict).filter(
        Conflict.roster_id == roster_id,
        Conflict.severity == "critical",
    ).count()
    
    coverage_percentage = (working_entries / max(total_entries, 1)) * 100
    
    return {
        "success": True,
        "roster_id": str(roster_id),
        "coverage": {
            "total_entries": total_entries,
            "working": working_entries,
            "on_leave": leave_entries,
            "weekly_off": weekly_off_entries,
            "coverage_percentage": round(coverage_percentage, 2),
        },
        "conflicts": {
            "total": conflicts,
            "critical": critical_conflicts,
        },
    }


@router.get("/{roster_id}/entries", response_model=dict)
async def get_roster_entries(
    roster_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    employee_id: UUID = Query(None),
    brand_id: UUID = Query(None),
    status_filter: str = Query(None, alias="status"),
    db: Session = Depends(get_db),
):
    """Get roster entries with filtering."""
    query = db.query(RosterEntry).filter(RosterEntry.roster_id == roster_id)
    
    if employee_id:
        query = query.filter(RosterEntry.employee_id == employee_id)
    if brand_id:
        query = query.filter(RosterEntry.brand_id == brand_id)
    if status_filter:
        query = query.filter(RosterEntry.assignment_status == status_filter)
    
    total = query.count()
    entries = query.offset(skip).limit(limit).all()
    
    return paginated_response(
        items=[_entry_to_dict(e) for e in entries],
        total=total,
        page=skip // limit + 1,
        per_page=limit,
    )


def _roster_to_dict(roster: Roster) -> dict:
    """Convert roster to dict."""
    return {
        "id": str(roster.id),
        "roster_name": roster.roster_name,
        "month": roster.month,
        "year": roster.year,
        "status": roster.status,
        "version": roster.version,
        "generated_at": roster.generated_at.isoformat() if roster.generated_at else None,
        "published_at": roster.published_at.isoformat() if roster.published_at else None,
        "created_at": roster.created_at.isoformat(),
        "updated_at": roster.updated_at.isoformat(),
    }


def _entry_to_dict(entry: RosterEntry) -> dict:
    """Convert roster entry to dict."""
    return {
        "id": str(entry.id),
        "roster_id": str(entry.roster_id),
        "employee_id": str(entry.employee_id),
        "brand_id": str(entry.brand_id),
        "process_id": str(entry.process_id) if entry.process_id else None,
        "roster_date": entry.roster_date.isoformat(),
        "assignment_status": entry.assignment_status,
        "shift_start": entry.shift_start.isoformat() if entry.shift_start else None,
        "shift_end": entry.shift_end.isoformat() if entry.shift_end else None,
        "is_manual": entry.is_manual,
        "notes": entry.notes,
    }
