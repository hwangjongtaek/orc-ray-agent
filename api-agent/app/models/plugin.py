"""
TDD GREEN Phase: Plugin model implementation
Implementing minimum code to make tests pass
"""

from sqlalchemy import Column, DateTime, Integer, JSON, String
from sqlalchemy.sql import func

from app.core.db import Base


class Plugin(Base):
    __tablename__ = "plugins"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    version = Column(String, nullable=False)
    description = Column(String)
    docker_image_url = Column(String, nullable=False)
    input_schema = Column(JSON)
    output_schema = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
