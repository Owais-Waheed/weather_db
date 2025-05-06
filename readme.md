# Weather Station API

A REST API for searching weather data by location and timestamp from multiple weather stations.

## Features

- Import weather data from CSV files into MongoDB
- Filter data for May 2024
- Index data by location (GeoJSON) and timestamp
- Search weather stations by coordinates
- Retrieve weather readings by exact timestamp or time range
- Only stores required columns: Date & Time, Temperature, Humidity, Dew Point, and Wind Speed

## Project Structure

```
weather-api/
├── app/
│   ├── __init__.py            # Application factory
│   ├── config.py              # Configuration settings
│   ├── db/
│   │   ├── __init__.py
│   │   └── mongodb.py         # MongoDB connection and operations
│   ├── models/
│   │   ├── __init__.py
│   │   └── weather.py         # Data models
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # API endpoints
│   └── utils/
│       ├── __init__.py
│       └── data_loader.py     # Data loading utilities
├── main.py                    # Application entry point
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Prerequisites

1. Python 3.8 or higher
2. MongoDB Atlas account (or a local MongoDB instance)
3. Weather data CSV files with the following columns:
   - Date & Time
   - Temp - °C
   - Hum - %
   - Dew Point - °C
   - Avg Wind Speed - km/h

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/weather-api.git
cd weather-api
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set up MongoDB

The application is configured to use MongoDB Atlas. The connection string is already configured in `app/config.py`:

```python
MONGODB_URI: str = "mongodb+srv://user:1234@cluster0.aitkuse.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
```

Make sure your MongoDB Atlas cluster is properly set up and accessible.

#### MongoDB Atlas Setup

1. Log in to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Create a new cluster if you don't have one
3. Create a database user with the username "user" and password "1234"
4. Add your IP address to the IP Access List in the Network Access section
5. Connect to your cluster and create a database named "weather_data"

### 4. Load data into MongoDB

Place your weather data CSV files in a directory, then run:

```bash
python main.py --load-data /path/to/your/csv/files
```

This will:
1. Process all CSV files in the specified directory
2. Extract station metadata (generating unique station IDs)
3. Filter for May 2024 data
4. Keep only the required columns
5. Insert the data into MongoDB

### 5. Start the API server

```bash
python main.py
```

The API will be available at http://localhost:8000

## API Endpoints

### Root
- `GET /api/v1/` - API status check

### Stations
- `GET /api/v1/stations` - Get all weather stations
- `GET /api/v1/stations/{station_id}` - Get a specific weather station
- `POST /api/v1/stations/by-location` - Find stations near a location

### Weather Data
- `POST /api/v1/weather/by-timestamp` - Find weather readings at a specific timestamp
- `POST /api/v1/weather/by-time-range` - Find weather readings within a time range

### Statistics
- `GET /api/v1/stats/stations-count` - Get the total number of weather stations

## API Usage Examples

### Find stations near a location

```bash
curl -X POST "http://localhost:8000/api/v1/stations/by-location" \
  -H "Content-Type: application/json" \
  -d '{"longitude": -73.9, "latitude": 40.7, "max_distance": 10000}'
```

### Get weather data for a specific timestamp

```bash
curl -X POST "http://localhost:8000/api/v1/weather/by-timestamp" \
  -H "Content-Type: application/json" \
  -d '{"timestamp": "2024-05-01T12:00:00"}'
```

### Get weather data for a time range

```bash
curl -X POST "http://localhost:8000/api/v1/weather/by-time-range" \
  -H "Content-Type: application/json" \
  -d '{"start_time": "2024-05-01T08:00:00", "end_time": "2024-05-01T18:00:00"}'
```

## Documentation

Interactive API documentation is available at http://localhost:8000/docs once the server is running.

## Development

For development with hot reloading, run:

```bash
python main.py --reload
```