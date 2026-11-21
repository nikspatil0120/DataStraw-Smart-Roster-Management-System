"""Pod schemas."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class PodBase(BaseModel):
    """Base pod schema."""
    pod_name: str
    description: Optional[str] = None
    status: str = "active"


class PodCreate(PodBase):
    """Pod creation schema."""
    pod_lead_id: Optional[UUID] = None


class PodUpdate(BaseModel):
    """Pod update schema."""
    pod_name: Optional[str] = None
    pod_lead_id: Optional[UUID] = None
    description: Optional[str] = None
    status: Optional[str] = None


class PodResponse(PodBase):
    """Pod response schema."""
    id: UUID
    pod_lead_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
