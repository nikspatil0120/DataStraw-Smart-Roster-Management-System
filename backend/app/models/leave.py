"""Leave model."""
from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime, date
import uuid
import enum
from app.database import Base


class LeaveType(str, enum.Enum):
    """Leave types."""
    PLANNED = "planned"
    SICK = "sick"
    EMERGENCY = "emergency"
    COMP_OFF = "comp_off"


class LeaveStatus(str, enum.Enum):
    """Leave status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Leave(Base):
    """Leave record."""
    __tablename__ = "leaves"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(PG_UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    leave_type = Column(String(50), nullable=False)
    status = Column(String(50), default=LeaveStatus.PENDING.value)
    reason = Column(String(500), nullable=True)
    approved_by = Column(PG_UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="leaves")
