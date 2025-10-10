"""
Pydantic schemas for Job entity
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.models.job import JobStatus


class JobBase(BaseModel):
    """Base job schema"""

    plugin_name: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    input_data: Optional[Dict[str, Any]] = None


class JobCreate(JobBase):
    """Schema for creating a new job"""

    pass


class JobUpdate(BaseModel):
    """Schema for updating a job"""

    status: Optional[JobStatus] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class JobInDB(JobBase):
    """Schema for job in database"""

    id: int
    status: JobStatus
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    owner_id: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Job(JobInDB):
    """Schema for job response"""

    pass


class JobList(BaseModel):
    """Schema for paginated job list response"""

    total: int
    items: list[Job]
