"""
Weather API application package.
"""
from fastapi import FastAPI

from app.config import settings
from app.api.routes import router as api_router


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application
    """
    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
    )
    
    # Include API routes
    app.include_router(api_router)
    
    return app