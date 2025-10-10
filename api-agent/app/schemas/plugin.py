"""
Pydantic schemas for Plugin entity
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class PluginBase(BaseModel):
    """Base plugin schema"""

    name: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    description: Optional[str] = None
    docker_image_url: str


class PluginCreate(PluginBase):
    """Schema for creating a new plugin"""

    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None


class PluginUpdate(BaseModel):
    """Schema for updating a plugin"""

    version: Optional[str] = Field(None, pattern=r"^\d+\.\d+\.\d+$")
    description: Optional[str] = None
    docker_image_url: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None


class PluginInDB(PluginBase):
    """Schema for plugin in database"""

    id: int
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Plugin(PluginInDB):
    """Schema for plugin response"""

    pass


class PluginList(BaseModel):
    """Schema for paginated plugin list response"""

    total: int
    items: list[Plugin]
