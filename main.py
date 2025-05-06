"""
Entry point for the Weather API application.
"""
import argparse
import os
import sys
from pathlib import Path

import uvicorn

from app import create_app
from app.utils.data_loader import load_data_from_directory


def main():
    """
    Main entry point for the Weather API application.
    
    This function parses command-line arguments, loads data if requested,
    and starts the API server.
    """
    parser = argparse.ArgumentParser(description="Weather API Server")
    parser.add_argument(
        "--load-data",
        metavar="DATA_DIR",
        help="Load data from the specified directory before starting the server"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    args = parser.parse_args()
    
    # Load data if requested
    if args.load_data:
        data_dir = Path(args.load_data)
        if not data_dir.exists() or not data_dir.is_dir():
            print(f"Error: {args.load_data} is not a valid directory")
            sys.exit(1)
        
        print(f"Loading data from {data_dir}...")
        result_ids = load_data_from_directory(data_dir)
        print(f"Loaded {len(result_ids)} weather stations")
    
    # Start the API server
    print(f"Starting Weather API server on {args.host}:{args.port}")
    app = create_app()
    uvicorn.run(
        "app:create_app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        factory=True
    )


if __name__ == "__main__":
    main()