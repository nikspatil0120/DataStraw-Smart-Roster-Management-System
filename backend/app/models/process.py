"""Process model."""
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime
import uuid
from app.database import Base


class Process(Base):
    """Process model."""
    __tablename__ = "processes"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_name = Column(String(255), nullable=False, unique=True)
    process_code = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(String(1000), nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignments = relationship("Assignment", back_populates="process", cascade="all, delete-orphan")
    scheduling_rules = relationship("SchedulingRule", back_populates="process", cascade="all, delete-orphan")
    roster_entries = relationship("RosterEntry", back_populates="process", cascade="all, delete-orphan")
    conflicts = relationship("Conflict", back_populates="process", cascade="all, delete-orphan")
