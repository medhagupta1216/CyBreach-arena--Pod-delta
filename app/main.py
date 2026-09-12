from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.settings import settings
from app.database.connection import Base, engine

# Notification Hub models
from app.models.notification import Notification
from app.models.notification_preference import NotificationPreference

# Analytics Engine model
from app.models.analytics_metrics import AnalyticsMetric

# Notification Hub routers
from app.api.notification_routes import router as notification_router
from app.api.preference_routes import router as preference_router

# Analytics Engine router
from app.api.analytics_engine_routes import router as analytics_router

# Notification Hub exception handlers
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Analytics Engine exception handlers
from app.core.exceptions import (
    AnalyticsNotFoundException,
    AnalyticsValidationException,
    AnalyticsDatabaseException,
    analytics_not_found_handler,
    analytics_validation_handler,
    analytics_database_handler,
)

# Database
Base.metadata.create_all(bind=engine)

# FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="CyBreach Arena Backend",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

# Notification Hub exception handlers
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

# Analytics Engine exception handlers
app.add_exception_handler(
    AnalyticsNotFoundException,
    analytics_not_found_handler,
)

app.add_exception_handler(
    AnalyticsValidationException,
    analytics_validation_handler,
)

app.add_exception_handler(
    AnalyticsDatabaseException,
    analytics_database_handler,
)

# Notification Hub routes
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

# Analytics Engine routes
app.include_router(
    analytics_router,
)

# Root health check
@app.get(
    "/",
    summary="Root Health Check",
    description="Checks whether the CyBreach Arena backend is running.",
)
async def home():
    return {
        "application": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "Running",
        "database": "Connected",
    }

# Detailed health check
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