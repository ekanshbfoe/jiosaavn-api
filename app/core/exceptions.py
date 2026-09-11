import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class GlobalExceptionHandler:
    """
    Global exception handling middleware for the FastAPI application.
    """

    def __init__(self, app: FastAPI):
        """
        Initialize the global exception handler.
        Args:
            app (FastAPI): FastAPI application instance
        """

        @app.exception_handler(Exception)
        async def global_exception_handler(_request: Request, exc: Exception):
            """
            Handle unexpected exceptions across the application.
            Args:
                _request (Request): Incoming request
                exc (Exception): Raised exception
            Returns:
                JSONResponse: Standardized error response
            """
            logger.error("Unexpected error: %s", str(exc), exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "An unexpected error occurred",
                    "details": str(exc),
                },
            )
