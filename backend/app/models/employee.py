"""Employee model."""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer, Date, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime, date
import uuid
import enum
from app.database import Base


class EmploymentStatus(str, enum.Enum):
    """Employment status."""
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    INACTIVE = "inactive"
    TERMINATED = "terminated"


class EmployeeRole(str, enum.Enum):
    """Employee roles."""
    POD_LEAD = "pod_lead"
    SENIOR_EXECUTIVE = "senior_executive"
    EXECUTIVE = "executive"
    TRAINEE = "trainee"


class Employee(Base):
    """Employee model."""
    __tablename__ = "employees"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_code = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)
    pod_id = Column(PG_UUID(as_uuid=True), ForeignKey("pods.id"), nullable=True)
    role = Column(String(50), default=EmployeeRole.EXECUTIVE.value)
    employment_status = Column(String(50), default=EmploymentStatus.ACTIVE.value)
    joining_date = Column(Date, nullable=True)
    max_assignments_per_day = Column(Integer, default=2)
    preferred_weekly_off = Column(String(50), nullable=True)  # e.g., "SUNDAY", "MONDAY"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pod = relationship("Pod", back_populates="employees", foreign_keys=[pod_id])
    assignments = relationship("Assignment", back_populates="employee", cascade="all, delete-orphan")
    availability = relationship("Availability", back_populates="employee", cascade="all, delete-orphan")
    leaves = relationship("Leave", back_populates="employee", cascade="all, delete-orphan")
    roster_entries = relationship("RosterEntry", back_populates="employee", cascade="all, delete-orphan")
