"""Availability schemas."""
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from uuid import UUID


class AvailabilityBase(BaseModel):
    """Base availability schema."""
    employee_id: UUID
    date: date
    availability_status: str = "available"
    reason: Optional[str] = None


class AvailabilityCreate(AvailabilityBase):
    """Availability creation schema."""
    pass


class AvailabilityUpdate(BaseModel):
    """Availability update schema."""
    availability_status: Optional[str] = None
    reason: Optional[str] = None


class AvailabilityResponse(AvailabilityBase):
    """Availability response schema."""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
