"""Process schemas."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class ProcessBase(BaseModel):
    """Base process schema."""
    process_name: str
    process_code: str
    description: Optional[str] = None
    status: str = "active"


class ProcessCreate(ProcessBase):
    """Process creation schema."""
    pass


class ProcessUpdate(BaseModel):
    """Process update schema."""
    process_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class ProcessResponse(ProcessBase):
    """Process response schema."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
