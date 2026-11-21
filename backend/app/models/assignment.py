"""Assignment model."""
from sqlalchemy import Column, String, DateTime, Date, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime, date
import uuid
from app.database import Base


class Assignment(Base):
    """Employee assignment to brand and process."""
    __tablename__ = "assignments"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(PG_UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True)
    brand_id = Column(PG_UUID(as_uuid=True), ForeignKey("brands.id"), nullable=False, index=True)
    process_id = Column(PG_UUID(as_uuid=True), ForeignKey("processes.id"), nullable=True, index=True)
    assigned_from = Column(Date, nullable=False, default=date.today)
    assigned_until = Column(Date, nullable=True)
    priority = Column(Integer, default=1)
    status = Column(String(50), default="active")
    max_daily_capacity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="assignments")
    brand = relationship("Brand", back_populates="assignments")
    process = relationship("Process", back_populates="assignments")
