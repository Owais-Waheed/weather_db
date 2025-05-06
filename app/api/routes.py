"""
API routes for the Weather API.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from pydantic import BaseModel

from app.db.mongodb import mongodb_manager
from app.models.weather import (
    WeatherStation, 
    WeatherEntry, 
    WeatherEntryResponse,
    LocationQuery,
    TimeQuery,
    TimeRangeQuery
)


router = APIRouter(prefix="/api/v1")


@router.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    """
    Root endpoint to verify API is running.
    
    Returns:
        Dict[str, str]: Status message
    """
    return {"status": "Weather API is running"}


@router.get("/stations", response_model=List[WeatherStation])
async def get_stations(limit: int = Query(10, ge=1, le=100)) -> List[WeatherStation]:
    """
    Get a list of weather stations.
    
    Args:
        limit: Maximum number of stations to return
        
    Returns:
        List[WeatherStation]: List of weather stations
    """
    try:
        stations = mongodb_manager.get_all_stations(limit=limit)
        return stations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stations: {str(e)}")


@router.get("/stations/{station_id}", response_model=WeatherStation)
async def get_station_by_id(station_id: str = Path(..., description="The ID of the station to retrieve")) -> WeatherStation:
    """
    Get a weather station by its ID.
    
    Args:
        station_id: ID of the station to retrieve
        
    Returns:
        WeatherStation: The requested weather station
    """
    try:
        station = mongodb_manager.find_station_by_id(station_id)
        if not station:
            raise HTTPException(status_code=404, detail=f"Station with ID {station_id} not found")
        return station
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving station: {str(e)}")


@router.post("/stations/by-location", response_model=List[WeatherStation])
async def find_stations_by_location(query: LocationQuery) -> List[WeatherStation]:
    """
    Find weather stations near a given location.
    
    Args:
        query: Location query parameters
        
    Returns:
        List[WeatherStation]: List of nearby weather stations
    """
    try:
        stations = mongodb_manager.find_stations_by_location(
            longitude=query.longitude,
            latitude=query.latitude,
            max_distance=query.max_distance
        )
        return stations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding stations by location: {str(e)}")


@router.post("/weather/by-timestamp", response_model=List[WeatherEntryResponse])
async def find_entries_by_timestamp(query: TimeQuery) -> List[WeatherEntryResponse]:
    """
    Find weather entries across all stations for a specific timestamp.
    
    Args:
        query: Time query parameters
        
    Returns:
        List[WeatherEntryResponse]: List of weather entries matching the timestamp
    """
    try:
        entries = mongodb_manager.find_entries_by_timestamp(query.timestamp)
        
        # Transform the results into the response model format
        formatted_entries = []
        for entry in entries:
            formatted_entry = {
                "station_id": entry["station_id"],
                "station_name": entry["station_name"],
                "location": entry["location"],
                "timestamp": entry["entry"]["timestamp"],
                "Temp - °C": entry["entry"]["Temp - °C"],
                "Hum - %": entry["entry"]["Hum - %"],
                "Dew Point - °C": entry["entry"]["Dew Point - °C"],
                "Avg Wind Speed - km/h": entry["entry"]["Avg Wind Speed - km/h"]
            }
            formatted_entries.append(formatted_entry)
        
        return formatted_entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding entries by timestamp: {str(e)}")


@router.post("/weather/by-time-range", response_model=List[WeatherEntryResponse])
async def find_entries_by_time_range(query: TimeRangeQuery) -> List[WeatherEntryResponse]:
    """
    Find weather entries across all stations within a time range.
    
    Args:
        query: Time range query parameters
        
    Returns:
        List[WeatherEntryResponse]: List of weather entries within the time range
    """
    try:
        if query.end_time < query.start_time:
            raise HTTPException(
                status_code=400, 
                detail="End time must be after start time"
            )
        
        entries = mongodb_manager.find_entries_by_time_range(
            start_time=query.start_time,
            end_time=query.end_time
        )
        
        # Transform the results into the response model format
        formatted_entries = []
        for entry in entries:
            formatted_entry = {
                "station_id": entry["station_id"],
                "station_name": entry["station_name"],
                "location": entry["location"],
                "timestamp": entry["entry"]["timestamp"],
                "Temp - °C": entry["entry"]["Temp - °C"],
                "Hum - %": entry["entry"]["Hum - %"],
                "Dew Point - °C": entry["entry"]["Dew Point - °C"],
                "Avg Wind Speed - km/h": entry["entry"]["Avg Wind Speed - km/h"]
            }
            formatted_entries.append(formatted_entry)
        
        return formatted_entries
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding entries by time range: {str(e)}")


@router.get("/stats/stations-count")
async def get_stations_count() -> Dict[str, int]:
    """
    Get the total number of weather stations in the database.
    
    Returns:
        Dict[str, int]: Number of weather stations
    """
    try:
        count = mongodb_manager.count_stations()
        return {"stations_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error counting stations: {str(e)}")