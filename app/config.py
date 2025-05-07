"""
Configuration settings for the Weather API application.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # MongoDB settings
    MONGODB_URI: str = "mongodb+srv://user:1234@cluster0.aitkuse.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    MONGODB_DB_NAME: str = "weather_data"
    WEATHER_COLLECTION: str = "weather_stations"
    INTERPOLATION_COLLECTION: str = "interpolated_data"  # New collection for interpolated data
    
    # API settings
    API_TITLE: str = "Weather Station API"
    API_DESCRIPTION: str = "API for retrieving weather data from multiple stations based on location and time"
    API_VERSION: str = "0.1.0"

    # Data processing settings
    MAX_RESULTS_DEFAULT: int = 100
    MAX_DISTANCE_DEFAULT: int = 10000  # meters (10km)
    
    # Data filtering
    TARGET_MONTH: int = 5  # May
    TARGET_YEAR: int = 2024
    
    # Columns to keep
    COLUMNS_TO_KEEP: list[str] = [
        "Date & Time",
        "Temp - °C",
        "Hum - %", 
        "Dew Point - °C",
        "Avg Wind Speed - km/h"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# """
# Configuration settings for the Weather API.
# """
# from pydantic_settings import BaseSettings


# class Settings(BaseSettings):
#     """Application settings."""
    
#     # API settings
#     APP_NAME: str = "Weather Station API"
#     API_VERSION: str = "v1"
#     DEBUG: bool = True
    
#     # MongoDB settings
#     MONGODB_URI: str = "mongodb+srv://user:1234@cluster0.aitkuse.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
#     MONGODB_DB_NAME: str = "weather_data"
#     WEATHER_COLLECTION: str = "weather_stations"
#     INTERPOLATION_COLLECTION: str = "interpolated_data"  # New collection for interpolated data
    
#     # Data processing settings
#     MAX_RESULTS_DEFAULT: int = 100
#     MAX_DISTANCE_DEFAULT: int = 10000  # meters (10km)
    
#     class Config:
#         """Pydantic config."""
#         case_sensitive = True
#         env_file = ".env"


# # Create settings instance
# settings = Settings()