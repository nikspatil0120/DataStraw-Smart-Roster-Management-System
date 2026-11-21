"""Conflict model."""
from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime, date
import uuid
import enum
from app.database import Base


class ConflictType(str, enum.Enum):
    """Conflict types."""
    INSUFFICIENT_COVERAGE = "insufficient_coverage"
    EMPLOYEE_UNAVAILABLE = "employee_unavailable"
    OVERLAPPING_SHIFTS = "overlapping_shifts"
    UNAUTHORIZED_ASSIGNMENT = "unauthorized_assignment"
    LEAVE_CONFLICT = "leave_conflict"
    WEEKLY_OFF_CONFLICT = "weekly_off_conflict"
    HOLIDAY_CONFLICT = "holiday_conflict"
    CAPACITY_EXCEEDED = "capacity_exceeded"
    INVALID_PROCESS_ASSIGNMENT = "invalid_process_assignment"


class ConflictSeverity(str, enum.Enum):
    """Conflict severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Conflict(Base):
    """Scheduling conflict."""
    __tablename__ = "conflicts"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    roster_id = Column(PG_UUID(as_uuid=True), ForeignKey("rosters.id"), nullable=False, index=True)
    employee_id = Column(PG_UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True, index=True)
    brand_id = Column(PG_UUID(as_uuid=True), ForeignKey("brands.id"), nullable=False, index=True)
    process_id = Column(PG_UUID(as_uuid=True), ForeignKey("processes.id"), nullable=True, index=True)
    conflict_date = Column(Date, nullable=False, index=True)
    conflict_type = Column(String(50), nullable=False)
    severity = Column(String(50), default=ConflictSeverity.MEDIUM.value)
    description = Column(String(1000), nullable=False)
    suggested_resolution = Column(String(1000), nullable=True)
    resolved = Column(Integer, default=0)  # 0 = unresolved, 1 = resolved
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roster = relationship("Roster", back_populates="conflicts")
    employee = relationship("Employee", foreign_keys=[employee_id])
    brand = relationship("Brand", back_populates="conflicts")
    process = relationship("Process", back_populates="conflicts")
