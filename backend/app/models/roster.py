"""Roster models."""
from sqlalchemy import Column, String, DateTime, Date, Integer, ForeignKey, Time
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime, date, time
import uuid
import enum
from app.database import Base


class RosterStatus(str, enum.Enum):
    """Roster statuses."""
    DRAFT = "draft"
    GENERATED = "generated"
    VALIDATED = "validated"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class AssignmentStatus(str, enum.Enum):
    """Assignment statuses."""
    WORKING = "working"
    WEEKLY_OFF = "weekly_off"
    PUBLIC_HOLIDAY = "public_holiday"
    LEAVE = "leave"
    COMP_OFF = "comp_off"
    UNAVAILABLE = "unavailable"


class Roster(Base):
    """Monthly roster."""
    __tablename__ = "rosters"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    roster_name = Column(String(255), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(String(50), default=RosterStatus.DRAFT.value)
    generated_at = Column(DateTime, nullable=True)
    generated_by = Column(PG_UUID(as_uuid=True), nullable=True)
    published_at = Column(DateTime, nullable=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    entries = relationship("RosterEntry", back_populates="roster", cascade="all, delete-orphan")
    conflicts = relationship("Conflict", back_populates="roster", cascade="all, delete-orphan")


class RosterEntry(Base):
    """Individual roster entry."""
    __tablename__ = "roster_entries"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    roster_id = Column(PG_UUID(as_uuid=True), ForeignKey("rosters.id"), nullable=False, index=True)
    employee_id = Column(PG_UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True)
    brand_id = Column(PG_UUID(as_uuid=True), ForeignKey("brands.id"), nullable=False, index=True)
    process_id = Column(PG_UUID(as_uuid=True), ForeignKey("processes.id"), nullable=True, index=True)
    roster_date = Column(Date, nullable=False, index=True)
    shift_start = Column(Time, default=time(9, 0))
    shift_end = Column(Time, default=time(17, 0))
    assignment_status = Column(String(50), default=AssignmentStatus.WORKING.value)
    is_manual = Column(String(50), default=False)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roster = relationship("Roster", back_populates="entries")
    employee = relationship("Employee", back_populates="roster_entries")
    brand = relationship("Brand", back_populates="roster_entries")
    process = relationship("Process", back_populates="roster_entries")
