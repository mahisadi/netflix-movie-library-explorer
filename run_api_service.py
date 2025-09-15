#!/usr/bin/env python3
"""
Run the Netflix Movie Library API Service

This script starts the FastAPI service that provides GraphQL and REST APIs
for searching and filtering movie data from RedisSearch.
"""

import sys
import os
import uvicorn
from loguru import logger

# Add the service directory to the path
service_dir = os.path.join(os.path.dirname(__file__), "netflix-movie-library-service")
sys.path.insert(0, service_dir)

def main():
    """Main function to run the API service."""
    try:
        logger.info("🚀 Starting Netflix Movie Library API Service...")
        logger.info("📊 Connecting to RedisSearch from netflix-movie-library-connector...")
        logger.info("🌐 GraphQL endpoint: http://localhost:8000/graphql")
        logger.info("📚 API documentation: http://localhost:8000/docs")
        logger.info("🔍 Health check: http://localhost:8000/health")
        logger.info("🎬 Movies endpoint: http://localhost:8000/api/movies")
        
        # Run the FastAPI application
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("👋 API service stopped by user")
    except Exception as e:
        logger.error(f" Failed to start API service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
