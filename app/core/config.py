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