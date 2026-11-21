"""Availability model."""
from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime, date
import uuid
import enum
from app.database import Base


class AvailabilityStatus(str, enum.Enum):
    """Availability status."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    HALF_DAY = "half_day"
    LIMITED = "limited"


class Availability(Base):
    """Employee availability for specific dates."""
    __tablename__ = "availability"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(PG_UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    availability_status = Column(String(50), default=AvailabilityStatus.AVAILABLE.value)
    reason = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="availability")
    
    __table_args__ = (
        UniqueConstraint("employee_id", "date", name="availability_employee_date_uq"),
    )
