"""Brand schemas."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class BrandBase(BaseModel):
    """Base brand schema."""
    brand_name: str
    brand_code: str
    description: Optional[str] = None
    status: str = "active"


class BrandCreate(BrandBase):
    """Brand creation schema."""
    pass


class BrandUpdate(BaseModel):
    """Brand update schema."""
    brand_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class BrandResponse(BrandBase):
    """Brand response schema."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
