"""
MongoDB connection and data operations for the Weather API.
Supports both weather station data and interpolated weather data.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from app.config import settings


class MongoDBManager:
    """Manager for MongoDB operations."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton implementation to ensure one database connection."""
        if cls._instance is None:
            cls._instance = super(MongoDBManager, cls).__new__(cls)
            cls._instance._client = None
            cls._instance._db = None
            cls._instance._weather_collection = None
            cls._instance._interpolation_collection = None  # New collection for interpolated data
            cls._instance._initialize_connection()
        return cls._instance
    
    def _initialize_connection(self) -> None:
        """Initialize the MongoDB connection and collections."""
        try:
            self._client = MongoClient(settings.MONGODB_URI)
            self._db = self._client[settings.MONGODB_DB_NAME]
            
            # Initialize weather station collection
            self._weather_collection = self._db[settings.WEATHER_COLLECTION]
            
            # Initialize interpolation collection
            self._interpolation_collection = self._db[settings.INTERPOLATION_COLLECTION]
            
            # Create geo index for location-based queries in weather collection
            self._weather_collection.create_index([("location", pymongo.GEOSPHERE)])
            
            # Create index for timestamp-based queries in weather collection
            self._weather_collection.create_index([("entries.timestamp", pymongo.ASCENDING)])
            
            # Create indexes for interpolation collection
            self._interpolation_collection.create_index([("location", pymongo.GEOSPHERE)])
            self._interpolation_collection.create_index([("timestamp", pymongo.ASCENDING)])
            
            print("MongoDB connection initialized successfully")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            raise
    
    @property
    def client(self) -> MongoClient:
        """Get MongoDB client."""
        return self._client
    
    @property
    def db(self) -> Database:
        """Get database instance."""
        return self._db
    
    @property
    def weather_collection(self) -> Collection:
        """Get weather station collection."""
        return self._weather_collection
    
    @property
    def interpolation_collection(self) -> Collection:
        """Get interpolation data collection."""
        return self._interpolation_collection
    
    #
    # Weather Station Data Methods
    #
    
    def insert_weather_station(self, station_data: Dict[str, Any]) -> str:
        """
        Insert a weather station with its data into the database.
        
        Args:
            station_data: Dictionary containing station information and readings
            
        Returns:
            str: ID of the inserted document
        """
        result = self._weather_collection.insert_one(station_data)
        return str(result.inserted_id)
    
    def insert_many_weather_stations(self, stations_data: List[Dict[str, Any]]) -> List[str]:
        """
        Insert multiple weather stations with their data into the database.
        
        Args:
            stations_data: List of dictionaries containing station information and readings
            
        Returns:
            List[str]: IDs of the inserted documents
        """
        result = self._weather_collection.insert_many(stations_data)
        return [str(id) for id in result.inserted_ids]

    def find_stations_by_location(self, longitude: float, latitude: float, max_distance: int = 10000) -> List[Dict[str, Any]]:
        """
        Find weather stations near a given location.
        
        Args:
            longitude: Longitude coordinate
            latitude: Latitude coordinate
            max_distance: Maximum distance in meters (default: 10km)
            
        Returns:
            List[Dict]: List of weather stations near the specified location
        """
        query = {
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "$maxDistance": max_distance
                }
            }
        }
        
        return list(self._weather_collection.find(query))
    
    def find_entries_by_timestamp(self, timestamp: datetime, 
                                 max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Find weather entries across all stations for a specific timestamp.
        
        Args:
            timestamp: Datetime object to search for
            max_results: Maximum number of results to return
            
        Returns:
            List[Dict]: List of weather entries matching the timestamp
        """
        pipeline = [
            {
                "$unwind": "$entries"
            },
            {
                "$match": {
                    "entries.timestamp": timestamp
                }
            },
            {
                "$project": {
                    "station_id": "$station_id",
                    "station_name": "$station_name",
                    "location": "$location",
                    "entry": "$entries"
                }
            },
            {
                "$limit": max_results
            }
        ]
        
        return list(self._weather_collection.aggregate(pipeline))
    
    def find_entries_by_time_range(self, start_time: datetime, end_time: datetime, 
                                  max_results: int = 1000) -> List[Dict[str, Any]]:
        """
        Find weather entries across all stations within a time range.
        
        Args:
            start_time: Start datetime for the range
            end_time: End datetime for the range
            max_results: Maximum number of results to return
            
        Returns:
            List[Dict]: List of weather entries within the time range
        """
        pipeline = [
            {
                "$unwind": "$entries"
            },
            {
                "$match": {
                    "entries.timestamp": {
                        "$gte": start_time,
                        "$lte": end_time
                    }
                }
            },
            {
                "$project": {
                    "station_id": "$station_id",
                    "station_name": "$station_name",
                    "location": "$location",
                    "entry": "$entries"
                }
            },
            {
                "$limit": max_results
            }
        ]
        
        return list(self._weather_collection.aggregate(pipeline))
    
    def find_station_by_id(self, station_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a weather station by its ID.
        
        Args:
            station_id: The ID of the station to find
            
        Returns:
            Optional[Dict]: The weather station document if found, None otherwise
        """
        return self._weather_collection.find_one({"station_id": station_id})
    
    def update_station_metadata(self, station_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for a weather station.
        
        Args:
            station_id: The ID of the station to update
            metadata: Dictionary of metadata fields to update
            
        Returns:
            bool: True if the update was successful, False otherwise
        """
        result = self._weather_collection.update_one(
            {"station_id": station_id},
            {"$set": metadata}
        )
        
        return result.modified_count > 0
    
    def add_entries_to_station(self, station_id: str, entries: List[Dict[str, Any]]) -> bool:
        """
        Add new entries to an existing weather station.
        
        Args:
            station_id: The ID of the station to update
            entries: List of new weather entries to add
            
        Returns:
            bool: True if the update was successful, False otherwise
        """
        result = self._weather_collection.update_one(
            {"station_id": station_id},
            {"$push": {"entries": {"$each": entries}}}
        )
        
        return result.modified_count > 0
    
    def count_stations(self) -> int:
        """
        Count the total number of weather stations in the database.
        
        Returns:
            int: Number of weather stations
        """
        return self._weather_collection.count_documents({})
    
    def get_all_stations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all weather stations in the database.
        
        Args:
            limit: Maximum number of stations to return
            
        Returns:
            List[Dict]: List of weather stations
        """
        return list(self._weather_collection.find({}).limit(limit))
    
    #
    # Interpolation Data Methods
    #
    
    def clear_interpolation_collection(self) -> int:
        """
        Clear all interpolated data.
        
        Returns:
            int: Number of documents deleted
        """
        result = self._interpolation_collection.delete_many({})
        return result.deleted_count
    
    def insert_interpolation_data(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Union[str, List[str]]:
        """
        Insert interpolated weather data into MongoDB.
        
        Args:
            data: Single document or list of documents with interpolation data
            
        Returns:
            Union[str, List[str]]: ID(s) of the inserted document(s)
        """
        if isinstance(data, list):
            result = self._interpolation_collection.insert_many(data)
            return [str(id) for id in result.inserted_ids]
        else:
            result = self._interpolation_collection.insert_one(data)
            return str(result.inserted_id)
    
    def find_interpolation_by_timestamp(self, timestamp: datetime, 
                                        max_results: int = 1000) -> List[Dict[str, Any]]:
        """
        Get interpolation data for a specific timestamp.
        
        Args:
            timestamp: Datetime object to search for
            max_results: Maximum number of results to return
            
        Returns:
            List[Dict]: List of interpolation data points matching the timestamp
        """
        return list(self._interpolation_collection.find(
            {"timestamp": timestamp}
        ).limit(max_results))
    
    def find_interpolation_by_time_range(self, start_time: datetime, end_time: datetime,
                                         max_results: int = 10000) -> List[Dict[str, Any]]:
        """
        Get interpolation data within a time range.
        
        Args:
            start_time: Start datetime for the range
            end_time: End datetime for the range
            max_results: Maximum number of results to return
            
        Returns:
            List[Dict]: List of interpolation data points within the time range
        """
        return list(self._interpolation_collection.find({
            "timestamp": {
                "$gte": start_time,
                "$lte": end_time
            }
        }).limit(max_results))
    
    def find_interpolation_near_point(self, longitude: float, latitude: float, 
                                      timestamp: Optional[datetime] = None,
                                      max_distance: int = 10000,
                                      max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Find interpolated data points near a specified location.
        
        Args:
            longitude: Longitude coordinate
            latitude: Latitude coordinate
            timestamp: Optional specific timestamp to filter by
            max_distance: Maximum distance in meters (default: 10km)
            max_results: Maximum number of results to return
            
        Returns:
            List[Dict]: List of interpolation data points near the specified location
        """
        query = {
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "$maxDistance": max_distance
                }
            }
        }
        
        if timestamp:
            query["timestamp"] = timestamp
            
        return list(self._interpolation_collection.find(query).limit(max_results))
    
    def count_interpolation_points(self) -> int:
        """
        Count the total number of interpolation data points in the database.
        
        Returns:
            int: Number of interpolation data points
        """
        return self._interpolation_collection.count_documents({})
    
    def get_available_interpolation_timestamps(self) -> List[datetime]:
        """
        Get all available timestamps for interpolation data.
        
        Returns:
            List[datetime]: List of unique timestamps in the interpolation collection
        """
        return self._interpolation_collection.distinct("timestamp")


# Export the singleton instance
mongodb_manager = MongoDBManager()