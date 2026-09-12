from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Application settings
    PROJECT_NAME: str = "CyBreach Notification Hub"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # Database settings
    DATABASE_URL: str = "sqlite:///./cybreach.db"

    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    # Security
    ALLOWED_HOSTS: List[str] = ["*"]
    SECRET_KEY: str = "your-secret-key-here"

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
from app.core.settings import settings

# Project Configuration
PROJECT_NAME = settings.PROJECT_NAME
VERSION = settings.VERSION
ENVIRONMENT = settings.ENVIRONMENT

# Database Configuration
DATABASE_URL = settings.DATABASE_URL

# CORS Configuration
CORS_ORIGINS = settings.CORS_ORIGINS

# Security Configuration
SECRET_KEY = settings.SECRET_KEY

# Analytics Configuration
ANALYTICS_RETENTION_DAYS = settings.ANALYTICS_RETENTION_DAYS
CACHE_TTL_SECONDS = settings.CACHE_TTL_SECONDS
