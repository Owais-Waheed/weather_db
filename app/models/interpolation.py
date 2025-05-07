from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class InterpolationPoint(BaseModel):
    """Model for a single interpolated data point."""
    longitude: float
    latitude: float
    temperature: float = Field(alias="Interpolated_Temp - °C")
    wind_speed: float = Field(alias="Interpolated_Avg Wind Speed - km/h")
    dew_point: float = Field(alias="Interpolated_Dew Point - °C")
    humidity: float = Field(alias="Interpolated_Hum - %")
    timestamp: datetime  # Will be extracted from the filename

class InterpolationData(BaseModel):
    """Model for interpolation data response."""
    timestamp: datetime
    points: List[InterpolationPoint]
    
class InterpolationQuery(BaseModel):
    """Model for querying interpolated data."""
    timestamp: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    radius: Optional[float] = None  # Search radius in meters