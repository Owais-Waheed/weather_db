# # """
# # Entry point for the Weather API application.
# # """
# # import argparse
# # import os
# # import sys
# # from pathlib import Path

# # import uvicorn

# # from app import create_app
# # from app.utils.data_loader import load_data_from_directory
# # from interpolation_loader import load_interpolated_data


# # def main():
# #     """
# #     Main entry point for the Weather API application.
    
# #     This function parses command-line arguments, loads data if requested,
# #     and starts the API server.
# #     """
# #     parser = argparse.ArgumentParser(description="Weather API Server")
# #     parser.add_argument(
# #         "--load-data",
# #         metavar="DATA_DIR",
# #         help="Load data from the specified directory before starting the server"
# #     )
# #     parser.add_argument(
# #         "--host",
# #         default="0.0.0.0",
# #         help="Host to bind the server to (default: 0.0.0.0)"
# #     )
# #     parser.add_argument(
# #         "--port",
# #         type=int,
# #         default=8000,
# #         help="Port to bind the server to (default: 8000)"
# #     )
# #     parser.add_argument(
# #         "--reload",
# #         action="store_true",
# #         help="Enable auto-reload for development"
# #     )

# #     parser.add_argument("--load-interpolated", help="Path to interpolated CSV files", type=str)

# #     if args.load_interpolated:
# #         from app.db.mongodb import get_db
# #         db = get_db()
# #         load_interpolated_data(db, args.load_interpolated)
# #         print("Interpolated data loaded successfully.")
# #         return
    
# #     args = parser.parse_args()
    
# #     # Load data if requested
# #     if args.load_data:
# #         data_dir = Path(args.load_data)
# #         if not data_dir.exists() or not data_dir.is_dir():
# #             print(f"Error: {args.load_data} is not a valid directory")
# #             sys.exit(1)
        
# #         print(f"Loading data from {data_dir}...")
# #         result_ids = load_data_from_directory(data_dir)
# #         print(f"Loaded {len(result_ids)} weather stations")
    
# #     # Start the API server
# #     print(f"Starting Weather API server on {args.host}:{args.port}")
# #     app = create_app()
# #     uvicorn.run(
# #         "app:create_app",
# #         host=args.host,
# #         port=args.port,
# #         reload=args.reload,
# #         factory=True
# #     )


# # if __name__ == "__main__":
# #     main()








# import argparse
# import asyncio
# import uvicorn
# from app import create_app
# from app.utils.data_loader import load_data
# from app.utils.interpolation_loader import load_interpolation_data  # Import new loader

# app = create_app()

# async def main():
#     parser = argparse.ArgumentParser(description="Weather Station API")
#     parser.add_argument("--load-data", help="Path to directory with weather station CSV files")
#     parser.add_argument("--load-interpolation", help="Path to directory with interpolation CSV files")
#     parser.add_argument("--reload", action="store_true", help="Enable hot reloading for development")
#     args = parser.parse_args()
    
#     if args.load_data:
#         await load_data(args.load_data)
    
#     if args.load_interpolation:
#         await load_interpolation_data(args.load_interpolation)
    
#     if not (args.load_data or args.load_interpolation):
#         uvicorn.run(
#             "main:app", 
#             host="0.0.0.0", 
#             port=8000, 
#             reload=args.reload
#         )

# if __name__ == "__main__":
#     asyncio.run(main())

"""
Main entry point for the Weather Station API application.
"""
import argparse
import uvicorn
from fastapi import FastAPI

from app.config import settings
from app.api import routes
from app.api import interpolation
from app.utils import data_loader
from app.utils import interpolation_loader


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.API_TITLE,
        description="REST API for accessing weather station data and interpolated weather data",
        version=settings.API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Include routers
    app.include_router(routes.router)
    app.include_router(interpolation.router)
    
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint that returns API status."""
        return {
            "status": "ok",
            "message": f"Welcome to the {settings.API_TITLE}",
            "version": settings.API_VERSION,
            "docs_url": "/docs"
        }
    
    return app


app = create_application()


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description=settings.API_TITLE)
    
    # Command line arguments
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    
    # Data loading arguments
    parser.add_argument("--load-weather-data", help="Path to directory with weather station CSV files")
    parser.add_argument("--load-interpolation", help="Path to directory with interpolation CSV files")
    
    args = parser.parse_args()
    
    # Handle data loading
    if args.load_weather_data:
        print(f"Loading weather station data from {args.load_weather_data}")
        data_loader.load_data_from_directory(args.load_weather_data)
    
    if args.load_interpolation:
        print(f"Loading interpolation data from {args.load_interpolation}")
        interpolation_loader.load_interpolation_data(args.load_interpolation)
    
    # Start the API server if not loading data
    if not (args.load_weather_data or args.load_interpolation):
        uvicorn.run(
            "main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info" 
        )


if __name__ == "__main__":
    main()