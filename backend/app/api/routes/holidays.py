"""Holiday routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date
from uuid import UUID
from pydantic import BaseModel

from app.database import get_db
from app.models import Holiday
from app.utils.response import paginated_response

router = APIRouter(prefix="/api/holidays", tags=["holidays"])


class HolidayCreate(BaseModel):
    holiday_name: str
    holiday_date: date
    description: str = None
    applicable_scope: str = "company"  # company, brand
    brand_id: UUID = None


class HolidayUpdate(BaseModel):
    holiday_name: str = None
    holiday_date: date = None
    description: str = None
    applicable_scope: str = None
    brand_id: UUID = None


@router.get("", response_model=dict)
async def list_holidays(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all holidays."""
    total = db.query(Holiday).count()
    holidays = db.query(Holiday).offset(skip).limit(limit).all()
    
    return paginated_response(
        items=[_holiday_to_dict(h) for h in holidays],
        total=total,
        page=skip // limit + 1,
        per_page=limit,
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_holiday(
    request: HolidayCreate,
    db: Session = Depends(get_db),
):
    """Create holiday."""
    holiday = Holiday(**request.model_dump())
    db.add(holiday)
    db.commit()
    db.refresh(holiday)
    return {
        "success": True,
        "holiday": _holiday_to_dict(holiday),
    }


@router.get("/{holiday_id}")
async def get_holiday(
    holiday_id: UUID,
    db: Session = Depends(get_db),
):
    """Get holiday."""
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    return {
        "success": True,
        "holiday": _holiday_to_dict(holiday),
    }


@router.put("/{holiday_id}")
async def update_holiday(
    holiday_id: UUID,
    request: HolidayUpdate,
    db: Session = Depends(get_db),
):
    """Update holiday."""
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(holiday, field, value)
    
    db.commit()
    db.refresh(holiday)
    return {
        "success": True,
        "holiday": _holiday_to_dict(holiday),
    }


@router.delete("/{holiday_id}", status_code=204)
async def delete_holiday(
    holiday_id: UUID,
    db: Session = Depends(get_db),
):
    """Delete holiday."""
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    db.delete(holiday)
    db.commit()


def _holiday_to_dict(h: Holiday) -> dict:
    return {
        "id": str(h.id),
        "holiday_name": h.holiday_name,
        "holiday_date": h.holiday_date.isoformat(),
        "description": h.description,
        "applicable_scope": h.applicable_scope,
        "brand_id": str(h.brand_id) if h.brand_id else None,
        "status": h.status,
    }
