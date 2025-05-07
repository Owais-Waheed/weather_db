"""
API routes for interpolated weather data.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.db.mongodb import mongodb_manager


# API Models
class LocationQuery(BaseModel):
    """Model for querying by location."""
    longitude: float
    latitude: float
    max_distance: Optional[int] = Field(default=10000, description="Maximum distance in meters")


class TimestampQuery(BaseModel):
    """Model for querying by timestamp."""
    timestamp: datetime


class TimeRangeQuery(BaseModel):
    """Model for querying by time range."""
    start_time: datetime
    end_time: datetime


class LocationTimestampQuery(BaseModel):
    """Model for querying by location and timestamp."""
    longitude: float
    latitude: float
    timestamp: datetime
    max_distance: Optional[int] = Field(default=10000, description="Maximum distance in meters")


class InterpolationPoint(BaseModel):
    """Model for a single interpolated data point."""
    longitude: float
    latitude: float
    temperature: float = Field(alias="temperature")
    wind_speed: float = Field(alias="wind_speed")
    dew_point: float = Field(alias="dew_point")
    humidity: float = Field(alias="humidity")
    timestamp: datetime


class InterpolationResponse(BaseModel):
    """Response model for interpolation data."""
    timestamp: datetime
    point_count: int
    points: List[InterpolationPoint]


class InterpolationTimeRangeResponse(BaseModel):
    """Response model for time range queries."""
    start_time: datetime
    end_time: datetime
    timestamp_count: int
    total_points: int
    data: List[InterpolationResponse]


# Create the router
router = APIRouter(prefix="/api/v1/interpolation", tags=["Interpolation Data"])


@router.get("/status")
async def get_interpolation_status():
    """Get the status of interpolation data in the database."""
    count = mongodb_manager.count_interpolation_points()
    timestamps = mongodb_manager.get_available_interpolation_timestamps()
    
    return {
        "status": "ok",
        "total_points": count,
        "timestamp_count": len(timestamps),
        "timestamps": sorted(timestamps) if timestamps else []
    }


@router.post("/by-timestamp", response_model=InterpolationResponse)
async def get_interpolation_by_timestamp(query: TimestampQuery):
    """
    Get interpolated weather data for a specific timestamp.
    
    Args:
        query: Timestamp to search for
        
    Returns:
        InterpolationResponse: Interpolation data for the timestamp
    """
    data = mongodb_manager.find_interpolation_by_timestamp(query.timestamp)
    
    if not data:
        raise HTTPException(status_code=404, detail=f"No interpolation data found for timestamp {query.timestamp}")
    
    # Transform the data to match the response model
    points = []
    for point in data:
        points.append(InterpolationPoint(
            longitude=point["location"]["coordinates"][0],
            latitude=point["location"]["coordinates"][1],
            temperature=point["temperature"],
            wind_speed=point["wind_speed"],
            dew_point=point["dew_point"],
            humidity=point["humidity"],
            timestamp=point["timestamp"]
        ))
    
    return InterpolationResponse(
        timestamp=query.timestamp,
        point_count=len(points),
        points=points
    )


@router.post("/by-time-range", response_model=InterpolationTimeRangeResponse)
async def get_interpolation_by_time_range(query: TimeRangeQuery):
    """
    Get interpolated weather data within a time range.
    
    Args:
        query: Time range to search for
        
    Returns:
        InterpolationTimeRangeResponse: Interpolation data within the time range
    """
    data = mongodb_manager.find_interpolation_by_time_range(query.start_time, query.end_time)
    
    if not data:
        raise HTTPException(
            status_code=404, 
            detail=f"No interpolation data found between {query.start_time} and {query.end_time}"
        )
    
    # Group data by timestamp
    grouped_data = {}
    for point in data:
        ts = point["timestamp"]
        if ts not in grouped_data:
            grouped_data[ts] = []
        
        grouped_data[ts].append(InterpolationPoint(
            longitude=point["location"]["coordinates"][0],
            latitude=point["location"]["coordinates"][1],
            temperature=point["temperature"],
            wind_speed=point["wind_speed"],
            dew_point=point["dew_point"],
            humidity=point["humidity"],
            timestamp=point["timestamp"]
        ))
    
    # Create response objects for each timestamp
    timestamp_responses = []
    for ts, points in grouped_data.items():
        timestamp_responses.append(InterpolationResponse(
            timestamp=ts,
            point_count=len(points),
            points=points
        ))
    
    # Sort responses by timestamp
    timestamp_responses.sort(key=lambda x: x.timestamp)
    
    # Calculate total points
    total_points = sum(len(ts_data.points) for ts_data in timestamp_responses)
    
    return InterpolationTimeRangeResponse(
        start_time=query.start_time,
        end_time=query.end_time,
        timestamp_count=len(timestamp_responses),
        total_points=total_points,
        data=timestamp_responses
    )


@router.post("/by-location", response_model=List[InterpolationResponse])
async def get_interpolation_by_location(query: LocationQuery):
    """
    Get interpolated weather data near a specific location for all available timestamps.
    
    Args:
        query: Location and distance parameters
        
    Returns:
        List[InterpolationResponse]: Interpolation data near the location
    """
    data = mongodb_manager.find_interpolation_near_point(
        query.longitude, 
        query.latitude, 
        timestamp=None,
        max_distance=query.max_distance
    )
    
    if not data:
        raise HTTPException(
            status_code=404, 
            detail=f"No interpolation data found near coordinates ({query.longitude}, {query.latitude})"
        )
    
    # Group data by timestamp
    grouped_data = {}
    for point in data:
        ts = point["timestamp"]
        if ts not in grouped_data:
            grouped_data[ts] = []
        
        grouped_data[ts].append(InterpolationPoint(
            longitude=point["location"]["coordinates"][0],
            latitude=point["location"]["coordinates"][1],
            temperature=point["temperature"],
            wind_speed=point["wind_speed"],
            dew_point=point["dew_point"],
            humidity=point["humidity"],
            timestamp=point["timestamp"]
        ))
    
    # Create response objects for each timestamp
    timestamp_responses = []
    for ts, points in grouped_data.items():
        timestamp_responses.append(InterpolationResponse(
            timestamp=ts,
            point_count=len(points),
            points=points
        ))
    
    # Sort responses by timestamp
    timestamp_responses.sort(key=lambda x: x.timestamp)
    
    return timestamp_responses


@router.post("/by-location-and-timestamp", response_model=InterpolationResponse)
async def get_interpolation_by_location_and_timestamp(query: LocationTimestampQuery):
    """
    Get interpolated weather data near a specific location for a specific timestamp.
    
    Args:
        query: Location, timestamp, and distance parameters
        
    Returns:
        InterpolationResponse: Interpolation data near the location at the timestamp
    """
    data = mongodb_manager.find_interpolation_near_point(
        query.longitude, 
        query.latitude, 
        timestamp=query.timestamp,
        max_distance=query.max_distance
    )
    
    if not data:
        raise HTTPException(
            status_code=404, 
            detail=f"No interpolation data found near coordinates ({query.longitude}, {query.latitude}) at {query.timestamp}"
        )
    
    # Transform the data to match the response model
    points = []
    for point in data:
        points.append(InterpolationPoint(
            longitude=point["location"]["coordinates"][0],
            latitude=point["location"]["coordinates"][1],
            temperature=point["temperature"],
            wind_speed=point["wind_speed"],
            dew_point=point["dew_point"],
            humidity=point["humidity"],
            timestamp=point["timestamp"]
        ))
    
    return InterpolationResponse(
        timestamp=query.timestamp,
        point_count=len(points),
        points=points
    )