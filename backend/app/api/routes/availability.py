"""Availability routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date
from uuid import UUID
from pydantic import BaseModel

from app.database import get_db
from app.models import Availability
from app.utils.response import paginated_response

router = APIRouter(prefix="/api/availability", tags=["availability"])


class AvailabilityCreate(BaseModel):
    employee_id: UUID
    date: date
    availability_status: str = "available"
    reason: str = None


class AvailabilityUpdate(BaseModel):
    availability_status: str = None
    reason: str = None


@router.get("", response_model=dict)
async def list_availability(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    employee_id: UUID = Query(None),
    status_filter: str = Query(None, alias="status"),
    db: Session = Depends(get_db),
):
    """List availability records."""
    query = db.query(Availability)
    
    if employee_id:
        query = query.filter(Availability.employee_id == employee_id)
    if status_filter:
        query = query.filter(Availability.availability_status == status_filter)
    
    total = query.count()
    records = query.offset(skip).limit(limit).all()
    
    return paginated_response(
        items=[_avail_to_dict(a) for a in records],
        total=total,
        page=skip // limit + 1,
        per_page=limit,
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_availability(
    request: AvailabilityCreate,
    db: Session = Depends(get_db),
):
    """Mark employee unavailable on a date."""
    availability = Availability(**request.model_dump())
    db.add(availability)
    db.commit()
    db.refresh(availability)
    return {
        "success": True,
        "availability": _avail_to_dict(availability),
    }


@router.get("/{availability_id}")
async def get_availability(
    availability_id: UUID,
    db: Session = Depends(get_db),
):
    """Get availability record."""
    avail = db.query(Availability).filter(Availability.id == availability_id).first()
    if not avail:
        raise HTTPException(status_code=404, detail="Availability record not found")
    return {
        "success": True,
        "availability": _avail_to_dict(avail),
    }


@router.put("/{availability_id}")
async def update_availability(
    availability_id: UUID,
    request: AvailabilityUpdate,
    db: Session = Depends(get_db),
):
    """Update availability."""
    avail = db.query(Availability).filter(Availability.id == availability_id).first()
    if not avail:
        raise HTTPException(status_code=404, detail="Availability record not found")
    
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(avail, field, value)
    
    db.commit()
    db.refresh(avail)
    return {
        "success": True,
        "availability": _avail_to_dict(avail),
    }


@router.delete("/{availability_id}", status_code=204)
async def delete_availability(
    availability_id: UUID,
    db: Session = Depends(get_db),
):
    """Delete availability record."""
    avail = db.query(Availability).filter(Availability.id == availability_id).first()
    if not avail:
        raise HTTPException(status_code=404, detail="Availability record not found")
    db.delete(avail)
    db.commit()


def _avail_to_dict(a: Availability) -> dict:
    return {
        "id": str(a.id),
        "employee_id": str(a.employee_id),
        "date": a.date.isoformat(),
        "availability_status": a.availability_status,
        "reason": a.reason,
        "created_at": a.created_at.isoformat(),
    }
