"""Assignment schemas."""
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from uuid import UUID


class AssignmentBase(BaseModel):
    """Base assignment schema."""
    employee_id: UUID
    brand_id: UUID
    process_id: Optional[UUID] = None
    assigned_from: date
    assigned_until: Optional[date] = None
    priority: int = 1
    max_daily_capacity: int = 1
    status: str = "active"


class AssignmentCreate(AssignmentBase):
    """Assignment creation schema."""
    pass


class AssignmentUpdate(BaseModel):
    """Assignment update schema."""
    assigned_until: Optional[date] = None
    priority: Optional[int] = None
    max_daily_capacity: Optional[int] = None
    status: Optional[str] = None


class AssignmentResponse(AssignmentBase):
    """Assignment response schema."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
