"""
Utilities for loading weather data from files into MongoDB.
"""
import os
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, Generator

import pandas as pd
from dateutil import parser

from app.config import settings
from app.db.mongodb import mongodb_manager


class WeatherDataLoader:
    """Loader for weather data files."""
    
    def __init__(self, data_directory: str):
        """
        Initialize the data loader.
        
        Args:
            data_directory: Path to the directory containing weather data files
        """
        self.data_directory = Path(data_directory)
        self.db_manager = mongodb_manager
    
    def _parse_datetime(self, datetime_str: str) -> Optional[datetime]:
        """
        Parse a datetime string into a datetime object.
        
        Args:
            datetime_str: String representation of date and time
            
        Returns:
            Optional[datetime]: Parsed datetime object or None if parsing fails
        """
        try:
            return parser.parse(datetime_str)
        except (ValueError, TypeError):
            return None
    
    def _is_may_2024(self, dt: Optional[datetime]) -> bool:
        """
        Check if a datetime is in May 2024.
        
        Args:
            dt: Datetime object to check
            
        Returns:
            bool: True if the datetime is in May 2024, False otherwise
        """
        if dt is None:
            return False
        
        return dt.year == settings.TARGET_YEAR and dt.month == settings.TARGET_MONTH
    
    def _extract_station_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract station metadata from the file path or contents.
        For this example, we're generating station IDs based on the file name.
        In a real-world scenario, this would parse actual metadata from the file.
        
        Args:
            file_path: Path to the weather data file
            
        Returns:
            Dict[str, Any]: Dictionary containing station metadata
        """
        # Generate a station ID from the file name
        station_id = f"WS{file_path.stem.replace(' ', '').upper()}"
        
        # Generate a station name from the file name
        station_name = file_path.stem.replace('_', ' ').title()
        
        # In a real implementation, you would extract actual coordinates from the file
        # Here we're using placeholder coordinates
        # This should be replaced with actual extraction logic based on your data format
        
        # Placeholder: different placeholder coordinates for each file to simulate different stations
        import hashlib
        hash_val = int(hashlib.md5(file_path.name.encode()).hexdigest(), 16)
        
        # Generate pseudo-random but deterministic coordinates between -180 to 180 for longitude
        # and -90 to 90 for latitude
        longitude = (hash_val % 36000) / 100 - 180
        latitude = ((hash_val // 36000) % 18000) / 100 - 90
        
        return {
            "station_id": station_id,
            "station_name": station_name,
            "location": {
                "type": "Point",
                "coordinates": [longitude, latitude]
            }
        }
    
    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a single weather data file.
        
        Args:
            file_path: Path to the weather data file
            
        Returns:
            Dict[str, Any]: Dictionary containing station data with May 2024 entries
        """
        print(f"Processing file: {file_path}")
        
        # Extract metadata from the file
        station_data = self._extract_station_metadata(file_path)
        station_data["entries"] = []
        
        try:
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Ensure all required columns are present
            for col in settings.COLUMNS_TO_KEEP:
                if col not in df.columns:
                    print(f"Warning: Column '{col}' not found in {file_path}")
                    continue
            
            # Filter only the columns we want to keep
            df = df[[col for col in settings.COLUMNS_TO_KEEP if col in df.columns]]
            
            # Parse the datetime column
            df['timestamp'] = df['Date & Time'].apply(self._parse_datetime)
            
            # Filter for May 2024 data
            may_2024_data = df[df['timestamp'].apply(self._is_may_2024)]
            
            if may_2024_data.empty:
                print(f"No May 2024 data found in {file_path}")
                return station_data
            
            # Convert the filtered data to a list of dictionaries
            entries = []
            for _, row in may_2024_data.iterrows():
                entry = {
                    "timestamp": row['timestamp'],
                    "Temp - °C": float(row['Temp - °C']) if 'Temp - °C' in row else 0.0,
                    "Hum - %": float(row['Hum - %']) if 'Hum - %' in row else 0.0,
                    "Dew Point - °C": float(row['Dew Point - °C']) if 'Dew Point - °C' in row else 0.0,
                    "Avg Wind Speed - km/h": float(row['Avg Wind Speed - km/h']) if 'Avg Wind Speed - km/h' in row else 0.0
                }
                entries.append(entry)
            
            station_data["entries"] = entries
            print(f"Added {len(entries)} entries from {file_path}")
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
        
        return station_data
    
    def load_all_files(self) -> List[str]:
        """
        Load all weather data files from the data directory.
        
        Returns:
            List[str]: List of inserted station document IDs
        """
        station_data_list = []
        
        try:
            # Find all CSV files in the data directory
            csv_files = list(self.data_directory.glob("*.csv"))
            
            if not csv_files:
                print(f"No CSV files found in {self.data_directory}")
                return []
            
            print(f"Found {len(csv_files)} CSV files to process")
            
            # Process each file
            for file_path in csv_files:
                station_data = self.process_file(file_path)
                if station_data and station_data["entries"]:
                    station_data_list.append(station_data)
            
            # Insert all stations into the database
            if station_data_list:
                result_ids = self.db_manager.insert_many_weather_stations(station_data_list)
                print(f"Successfully loaded {len(result_ids)} weather stations into MongoDB")
                return result_ids
            else:
                print("No valid station data found to insert")
                return []
            
        except Exception as e:
            print(f"Error loading weather data: {e}")
            return []


def load_data_from_directory(directory_path: str) -> List[str]:
    """
    Load weather data from a directory into MongoDB.
    
    Args:
        directory_path: Path to the directory containing weather data files
        
    Returns:
        List[str]: List of inserted station document IDs
    """
    loader = WeatherDataLoader(directory_path)
    return loader.load_all_files()