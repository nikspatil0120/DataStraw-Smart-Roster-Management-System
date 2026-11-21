"""Employee schemas."""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from uuid import UUID


class EmployeeBase(BaseModel):
    """Base employee schema."""
    employee_code: str
    full_name: str
    email: Optional[str] = None  # Changed from EmailStr to str for flexibility
    phone: Optional[str] = None
    role: str = "executive"
    employment_status: str = "active"
    joining_date: Optional[date] = None
    max_assignments_per_day: int = 2
    preferred_weekly_off: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    """Employee creation schema."""
    pod_id: Optional[UUID] = None


class EmployeeUpdate(BaseModel):
    """Employee update schema."""
    full_name: Optional[str] = None
    email: Optional[str] = None  # Changed from EmailStr to str
    phone: Optional[str] = None
    pod_id: Optional[UUID] = None
    role: Optional[str] = None
    employment_status: Optional[str] = None
    max_assignments_per_day: Optional[int] = None
    preferred_weekly_off: Optional[str] = None


class EmployeeResponse(EmployeeBase):
    """Employee response schema."""
    id: UUID
    pod_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
