from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.database.connection import Base, engine
from app.core.config import settings

# Import models so SQLAlchemy registers them
from app.models.notification import Notification
from app.models.notification_preference import NotificationPreference

# Import routers
from app.api.notification_routes import router as notification_router
from app.api.preference_routes import router as preference_router

# Import exception handlers
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


# ============================================================
# DATABASE
# ============================================================

# Create tables if they do not already exist.
# Alembic migrations should be used in production.
Base.metadata.create_all(bind=engine)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="CyBreach Notification Hub API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# TRUSTED HOST
# ============================================================

if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )


# ============================================================
# EXCEPTION HANDLERS
# ============================================================

app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    Exception,
    general_exception_handler,
)


# ============================================================
# API ROUTES
# ============================================================

app.include_router(
    notification_router,
    prefix="/api/v1/notifications",
    tags=["Notifications"],
)

app.include_router(
    preference_router,
    prefix="/api/v1/preferences",
    tags=["Preferences"],
)


# ============================================================
# ROOT HEALTH CHECK
# ============================================================

@app.get(
    "/",
    summary="Root Health Check",
    description="Checks whether the Notification Hub backend is running.",
)
async def home():
    return {
        "application": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "Running",
        "service": "Notification Hub",
        "database": "Connected",
    }


# ============================================================
# DETAILED HEALTH CHECK
# ============================================================

@app.get(
    "/api/v1/health",
    summary="Detailed Health Check",
    description="Detailed health check for monitoring.",
)
async def health_check():
    return {
        "status": "healthy",
        "application": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }