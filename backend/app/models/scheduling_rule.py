"""Scheduling rule model."""
from sqlalchemy import Column, String, DateTime, Date, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime, date
import uuid
import enum
from app.database import Base


class OperatingType(str, enum.Enum):
    """Operating types."""
    EVERY_DAY = "every_day"
    EXCEPT_PUBLIC_HOLIDAYS = "except_public_holidays"
    EXCEPT_SUNDAYS_AND_PUBLIC_HOLIDAYS = "except_sundays_and_public_holidays"
    CUSTOM = "custom"


class SchedulingRule(Base):
    """Scheduling rules for brand and process."""
    __tablename__ = "scheduling_rules"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(PG_UUID(as_uuid=True), ForeignKey("brands.id"), nullable=False, index=True)
    process_id = Column(PG_UUID(as_uuid=True), ForeignKey("processes.id"), nullable=True, index=True)
    operating_type = Column(String(50), default="every_day")
    sunday_working = Column(Boolean, default=True)
    public_holiday_working = Column(Boolean, default=False)
    minimum_staff = Column(Integer, default=1)
    maximum_staff = Column(Integer, nullable=True)
    preferred_staff = Column(Integer, nullable=True)
    priority = Column(Integer, default=1)
    effective_from = Column(Date, default=date.today)
    effective_until = Column(Date, nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    brand = relationship("Brand", back_populates="scheduling_rules")
    process = relationship("Process", back_populates="scheduling_rules")
