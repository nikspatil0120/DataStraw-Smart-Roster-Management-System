"""Pod model."""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime
import uuid
from app.database import Base


class Pod(Base):
    """Pod model."""
    __tablename__ = "pods"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pod_name = Column(String(255), nullable=False, unique=True)
    pod_lead_id = Column(PG_UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    description = Column(String(1000), nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employees = relationship("Employee", back_populates="pod", foreign_keys="Employee.pod_id")
    pod_lead = relationship("Employee", foreign_keys=[pod_lead_id], viewonly=True)
