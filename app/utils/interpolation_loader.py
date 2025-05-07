"""
Utility for loading interpolation data from CSV files into MongoDB.
"""
import os
import csv
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any

from app.db.mongodb import mongodb_manager


def load_interpolation_data(directory_path: str, clear_existing: bool = True) -> Tuple[int, int]:
    """
    Load interpolation data from CSV files in the specified directory.
    
    Args:
        directory_path: Path to directory containing interpolation CSV files
        clear_existing: Whether to clear existing interpolation data
    
    Returns:
        Tuple[int, int]: (Number of files processed, total data points loaded)
    """
    # Clear existing data if requested
    if clear_existing:
        deleted_count = mongodb_manager.clear_interpolation_collection()
        print(f"Cleared {deleted_count} existing interpolation data points")
    
    files_processed = 0
    total_points = 0
    
    # Process each CSV file in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.csv'):
            # Extract timestamp from filename
            # Assuming filename format contains timestamp like: data_2024-05-01T12:00:00.csv
            timestamp_match = filename.replace(".csv", "").replace("_", ":")
            timestamp_match = datetime.strptime(timestamp_match, "%Y-%m-%dT%H:%M:%S")
            
            if not timestamp_match:
                print(f"Skipping {filename} - cannot extract timestamp")
                continue
                
            timestamp = timestamp_match
            # timestamp = datetime.fromisoformat(timestamp_str)
            
            file_path = os.path.join(directory_path, filename)
            points_loaded = process_interpolation_file(file_path, timestamp)
            
            files_processed += 1
            total_points += points_loaded
            print(f"Processed {filename}: {points_loaded} data points")
    
    print(f"Completed loading {files_processed} files with {total_points} interpolation points")
    return files_processed, total_points


def process_interpolation_file(file_path: str, timestamp: datetime) -> int:
    """
    Process a single interpolation CSV file and load into MongoDB.
    
    Args:
        file_path: Path to the CSV file
        timestamp: Timestamp extracted from filename
        
    Returns:
        int: Number of data points loaded
    """
    data_points = []
    
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        
        for row in csv_reader:
            try:
                # Create GeoJSON location point
                longitude = float(row['Longitude'])
                latitude = float(row['Latitude'])
                
                # Prepare document for MongoDB
                document = {
                    "timestamp": timestamp,
                    "location": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "temperature": float(row['Interpolated_Temp - °C']),
                    "wind_speed": float(row['Interpolated_Avg Wind Speed - km/h']),
                    "dew_point": float(row['Interpolated_Dew Point - °C']),
                    "humidity": float(row['Interpolated_Hum - %'])
                }
                
                data_points.append(document)
            except (KeyError, ValueError) as e:
                print(f"Error processing row in {file_path}: {e}")
                continue
    
    # Insert data points in batches
    if data_points:
        mongodb_manager.insert_interpolation_data(data_points)
    
    return len(data_points)