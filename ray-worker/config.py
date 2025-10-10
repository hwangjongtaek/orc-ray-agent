"""
Configuration for Ray Worker
"""

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    RAY_HEAD_ADDRESS: str = "localhost:10001"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    PLUGIN_REGISTRY_URL: str = "http://localhost:5901"
    RAY_DEBUG: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
