"""
TDD GREEN Phase: Job model implementation
Implementing minimum code to make tests pass
"""

import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.db import Base


class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    plugin_name = Column(String, index=True, nullable=False)
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.QUEUED)
    input_data = Column(JSON)
    result = Column(JSON)
    error_message = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    # Relationship with User
    owner = relationship("User", back_populates="jobs")
