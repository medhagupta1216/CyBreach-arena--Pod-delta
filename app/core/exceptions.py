from fastapi import Request
from fastapi.responses import JSONResponse


class AnalyticsNotFoundException(Exception):
    """Raised when an analytics record or tenant is not found."""

    def __init__(self, message: str = "Analytics record not found"):
        self.message = message
        super().__init__(self.message)


class AnalyticsValidationException(Exception):
    """Raised when analytics data fails business validation."""

    def __init__(self, message: str = "Invalid analytics data"):
        self.message = message
        super().__init__(self.message)


class AnalyticsDatabaseException(Exception):
    """Raised when a database operation fails."""

    def __init__(self, message: str = "Database operation failed"):
        self.message = message
        super().__init__(self.message)


async def analytics_not_found_handler(
    request: Request,
    exc: AnalyticsNotFoundException
):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message}
    )


async def analytics_validation_handler(
    request: Request,
    exc: AnalyticsValidationException
):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message}
    )


async def analytics_database_handler(
    request: Request,
    exc: AnalyticsDatabaseException
):
    return JSONResponse(
        status_code=500,
        content={"detail": exc.message}
    )