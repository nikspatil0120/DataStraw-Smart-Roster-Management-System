"""Holiday model."""
from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime, date
import uuid
from app.database import Base


class Holiday(Base):
    """Public holiday."""
    __tablename__ = "holidays"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    holiday_name = Column(String(255), nullable=False)
    holiday_date = Column(Date, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    applicable_scope = Column(String(50), default="company")  # company, brand
    brand_id = Column(PG_UUID(as_uuid=True), ForeignKey("brands.id"), nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    brand = relationship("Brand", back_populates="holidays")
