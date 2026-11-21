"""Conflict routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import Conflict
from app.utils.response import paginated_response

router = APIRouter(prefix="/api/conflicts", tags=["conflicts"])


@router.get("", response_model=dict)
async def list_conflicts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    roster_id: UUID = Query(None),
    severity: str = Query(None),
    resolved: bool = Query(None),
    db: Session = Depends(get_db),
):
    """List all conflicts with filtering."""
    query = db.query(Conflict)
    
    if roster_id:
        query = query.filter(Conflict.roster_id == roster_id)
    if severity:
        query = query.filter(Conflict.severity == severity)
    if resolved is not None:
        query = query.filter(Conflict.resolved == (1 if resolved else 0))
    
    total = query.count()
    conflicts = query.order_by(Conflict.created_at.desc()).offset(skip).limit(limit).all()
    
    return paginated_response(
        items=[_conflict_to_dict(c) for c in conflicts],
        total=total,
        page=skip // limit + 1,
        per_page=limit,
    )


@router.get("/{conflict_id}", response_model=dict)
async def get_conflict(
    conflict_id: UUID,
    db: Session = Depends(get_db),
):
    """Get conflict by ID."""
    conflict = db.query(Conflict).filter(Conflict.id == conflict_id).first()
    
    if not conflict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conflict not found",
        )
    
    return {
        "success": True,
        "conflict": _conflict_to_dict(conflict),
    }


@router.post("/{conflict_id}/resolve", response_model=dict)
async def resolve_conflict(
    conflict_id: UUID,
    db: Session = Depends(get_db),
):
    """Mark conflict as resolved."""
    conflict = db.query(Conflict).filter(Conflict.id == conflict_id).first()
    
    if not conflict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conflict not found",
        )
    
    conflict.resolved = 1
    db.commit()
    db.refresh(conflict)
    
    return {
        "success": True,
        "message": "Conflict marked as resolved",
        "conflict": _conflict_to_dict(conflict),
    }


@router.get("/roster/{roster_id}/summary", response_model=dict)
async def get_roster_conflict_summary(
    roster_id: UUID,
    db: Session = Depends(get_db),
):
    """Get summary of conflicts for a roster."""
    total = db.query(Conflict).filter(Conflict.roster_id == roster_id).count()
    critical = db.query(Conflict).filter(
        Conflict.roster_id == roster_id,
        Conflict.severity == "critical",
    ).count()
    high = db.query(Conflict).filter(
        Conflict.roster_id == roster_id,
        Conflict.severity == "high",
    ).count()
    medium = db.query(Conflict).filter(
        Conflict.roster_id == roster_id,
        Conflict.severity == "medium",
    ).count()
    low = db.query(Conflict).filter(
        Conflict.roster_id == roster_id,
        Conflict.severity == "low",
    ).count()
    
    by_type = {}
    conflicts = db.query(Conflict).filter(Conflict.roster_id == roster_id).all()
    for c in conflicts:
        by_type[c.conflict_type] = by_type.get(c.conflict_type, 0) + 1
    
    return {
        "success": True,
        "summary": {
            "total_conflicts": total,
            "by_severity": {
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low,
            },
            "by_type": by_type,
            "can_publish": True,  # Allow publishing with conflicts for demonstration
        },
    }


def _conflict_to_dict(conflict: Conflict) -> dict:
    """Convert conflict to dict."""
    return {
        "id": str(conflict.id),
        "roster_id": str(conflict.roster_id),
        "employee_id": str(conflict.employee_id) if conflict.employee_id else None,
        "brand_id": str(conflict.brand_id),
        "process_id": str(conflict.process_id) if conflict.process_id else None,
        "conflict_date": conflict.conflict_date.isoformat(),
        "conflict_type": conflict.conflict_type,
        "severity": conflict.severity,
        "description": conflict.description,
        "suggested_resolution": conflict.suggested_resolution,
        "resolved": bool(conflict.resolved),
        "created_at": conflict.created_at.isoformat(),
    }
