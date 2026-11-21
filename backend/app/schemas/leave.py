"""Leave schemas."""
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from uuid import UUID


class LeaveBase(BaseModel):
    """Base leave schema."""
    employee_id: UUID
    start_date: date
    end_date: date
    leave_type: str
    reason: Optional[str] = None


class LeaveCreate(LeaveBase):
    """Leave creation schema."""
    pass


class LeaveUpdate(BaseModel):
    """Leave update schema."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    leave_type: Optional[str] = None
    reason: Optional[str] = None


class LeaveResponse(LeaveBase):
    """Leave response schema."""
    id: UUID
    status: str
    approved_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
