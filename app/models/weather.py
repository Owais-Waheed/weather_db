"""
Data models for the Weather API.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field


class GeoLocation(BaseModel):
    """Model for geographic location."""
    
    type: str = "Point"
    coordinates: List[float] = Field(..., description="[longitude, latitude]")


class WeatherEntry(BaseModel):
    """Model for a single weather data entry."""
    
    timestamp: datetime = Field(..., description="Date and time of the measurement")
    temperature: float = Field(..., description="Temperature in °C", alias="Temp - °C")
    humidity: float = Field(..., description="Relative humidity in %", alias="Hum - %")
    dew_point: float = Field(..., description="Dew point in °C", alias="Dew Point - °C")
    avg_wind_speed: float = Field(..., description="Average wind speed in km/h", alias="Avg Wind Speed - km/h")
    
    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "timestamp": "2024-05-01T12:00:00",
                "Temp - °C": 22.5,
                "Hum - %": 65.0,
                "Dew Point - °C": 15.7,
                "Avg Wind Speed - km/h": 8.2
            }
        }


class WeatherStation(BaseModel):
    """Model for a weather station with its entries."""
    
    station_id: str = Field(..., description="Unique identifier for the station")
    station_name: str = Field(..., description="Name of the weather station")
    location: GeoLocation = Field(..., description="Geographic location of the station")
    entries: List[WeatherEntry] = Field(default_factory=list, description="Weather data entries")
    
    class Config:
        schema_extra = {
            "example": {
                "station_id": "WS001",
                "station_name": "Central Park Station",
                "location": {
                    "type": "Point",
                    "coordinates": [-73.965355, 40.782865]
                },
                "entries": [
                    {
                        "timestamp": "2024-05-01T12:00:00",
                        "Temp - °C": 22.5,
                        "Hum - %": 65.0,
                        "Dew Point - °C": 15.7,
                        "Avg Wind Speed - km/h": 8.2
                    }
                ]
            }
        }


class WeatherEntryResponse(BaseModel):
    """Model for weather entry responses with station information."""
    
    station_id: str
    station_name: str
    location: GeoLocation
    timestamp: datetime
    temperature: float = Field(..., alias="Temp - °C")
    humidity: float = Field(..., alias="Hum - %")
    dew_point: float = Field(..., alias="Dew Point - °C")
    avg_wind_speed: float = Field(..., alias="Avg Wind Speed - km/h")
    
    class Config:
        allow_population_by_field_name = True


# Request models for API endpoints
class LocationQuery(BaseModel):
    """Model for location-based queries."""
    
    longitude: float = Field(..., description="Longitude coordinate", ge=-180, le=180)
    latitude: float = Field(..., description="Latitude coordinate", ge=-90, le=90)
    max_distance: Optional[int] = Field(10000, description="Maximum distance in meters")


class TimeQuery(BaseModel):
    """Model for time-based queries."""
    
    timestamp: datetime = Field(..., description="Timestamp to search for")


class TimeRangeQuery(BaseModel):
    """Model for time range queries."""
    
    start_time: datetime = Field(..., description="Start of the time range")
    end_time: datetime = Field(..., description="End of the time range")