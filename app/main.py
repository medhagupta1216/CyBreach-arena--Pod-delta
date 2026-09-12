from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import settings

from app.database.db_connection import (
    Base,
    engine
)

from app.models.analytics_metrics import AnalyticsMetric

from app.api.analytics_engine_routes import (
    router as analytics_router
)

from app.core.exceptions import (
    AnalyticsNotFoundException,
    AnalyticsValidationException,
    AnalyticsDatabaseException,
    analytics_not_found_handler,
    analytics_validation_handler,
    analytics_database_handler
)


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

Base.metadata.create_all(
    bind=engine
)


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="CyBreach Analytics Engine Backend",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,

    allow_origins=settings.CORS_ORIGINS,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# --------------------------------------------------
# EXCEPTION HANDLERS
# --------------------------------------------------

app.add_exception_handler(
    AnalyticsNotFoundException,
    analytics_not_found_handler
)

app.add_exception_handler(
    AnalyticsValidationException,
    analytics_validation_handler
)

app.add_exception_handler(
    AnalyticsDatabaseException,
    analytics_database_handler
)


# --------------------------------------------------
# ROUTES
# --------------------------------------------------

app.include_router(
    analytics_router
)


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/")
def health_check():

    return {
        "application":
            settings.PROJECT_NAME,

        "version":
            settings.VERSION,

        "status":
            "Running",

        "database":
            "Connected"
    }