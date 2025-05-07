# """
# Weather API application package.
# """
# from fastapi import FastAPI

# from app.config import settings
# from app.api.routes import router as api_router


# def create_app() -> FastAPI:
#     """
#     Create and configure the FastAPI application.
    
#     Returns:
#         FastAPI: Configured FastAPI application
#     """
#     app = FastAPI(
#         title=settings.API_TITLE,
#         description=settings.API_DESCRIPTION,
#         version=settings.API_VERSION,
#     )
    
#     # Include API routes
#     app.include_router(api_router)
    
#     return app



from fastapi import FastAPI
from .api import routes
from .api import interpolation  # Import new interpolation routes
from .db.mongodb import MongoDBManager

def create_app():
    app = FastAPI(
        title="Weather Station API",
        description="API for weather data from multiple stations including interpolated data",
        version="1.1.0"
    )
    
    # Event handlers
    @app.on_event("startup")
    async def startup():
        await MongoDBManager.connect()
    
    @app.on_event("shutdown")
    async def shutdown():
        await MongoDBManager.close()
    
    # Include routers
    app.include_router(routes.router)
    app.include_router(interpolation.router)  # Add interpolation router
    
    return app