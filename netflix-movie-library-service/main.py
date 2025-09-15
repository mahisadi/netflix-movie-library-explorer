#!/usr/bin/env python3
"""
FastAPI + GraphQL Movie Search API Service

This service provides a GraphQL API for searching and filtering movie data
stored in RedisSearch. It acts as a service layer between the UI and the
data layer (RedisSearch).
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from loguru import logger
import sys
import os

# Add the netflix-movie-library-connector project to the path
connector_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "netflix-movie-library-connector")
sys.path.insert(0, connector_path)

from api.graphql.schema import create_graphql_app
from api.services.search_service import SearchService
from api.services.redis_service import redis_service
from api.services.redis_analytics_service import redis_analytics_service
from api.routes.metrics import router as metrics_router
from api.routes.movies import router as movies_router
# Redis configuration - using default values
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = None
REDIS_DB = 0

# Configure logging
logger.add(
    os.path.join(os.path.dirname(__file__), "..", "storage", "logs", "api.log"),
    enqueue=True,
    rotation="10 MB",
    retention="7 days"
)

# Create FastAPI application
app = FastAPI(
    title="Movie Search API",
    description="GraphQL API for searching and filtering movie data from RedisSearch",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize search service
search_service = SearchService()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for the API service."""
    try:
        # Check RedisSearch connection
        is_healthy = await search_service.health_check()
        
        # Check Redis service health
        redis_health = redis_service.health_check()
        
        if is_healthy and redis_health["overall"] == "healthy":
            return {
                "status": "healthy",
                "service": "movie-search-api",
                "version": "1.0.0",
                "redis_status": "connected",
                "redis_databases": redis_health["databases"]
            }
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "service": "movie-search-api",
                    "version": "1.0.0",
                    "redis_status": "disconnected",
                    "redis_databases": redis_health.get("databases", {})
                }
            )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "movie-search-api",
                "version": "1.0.0",
                "error": str(e)
            }
        )

# Analytics endpoints
@app.get("/api/analytics/page-views")
async def get_page_views():
    """Get page views analytics data."""
    try:
        data = redis_analytics_service.get_page_views_data()
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error getting page views: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.get("/api/analytics/search-activities")
async def get_search_activities():
    """Get search activities analytics data."""
    try:
        data = redis_analytics_service.get_search_activities_data()
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error getting search activities: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.get("/api/analytics/user-countries")
async def get_user_countries():
    """Get user countries analytics data."""
    try:
        data = redis_analytics_service.get_user_countries_data()
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error getting user countries: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.get("/api/analytics/page-activities")
async def get_page_activities():
    """Get page activities analytics data."""
    try:
        data = redis_analytics_service.get_page_activities_data()
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error getting page activities: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.get("/api/analytics/summary")
async def get_analytics_summary():
    """Get comprehensive analytics summary."""
    try:
        data = redis_analytics_service.get_analytics_summary()
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.get("/api/analytics/user/{user_email}")
async def get_user_metrics(user_email: str, days: int = 7):
    """Get user-specific metrics for the last N days."""
    try:
        data = redis_analytics_service.get_user_specific_metrics(user_email, days)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error getting user metrics: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/api/analytics/track/page-view")
async def track_page_view(data: dict):
    """Track a page view with enhanced user context."""
    try:
        page = data.get("page", "")
        country = data.get("country", "Unknown")
        user_info = data.get("user_info", {})
        success = redis_analytics_service.track_page_view(page, country, user_info)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error tracking page view: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/api/analytics/track/search")
async def track_search_query(data: dict):
    """Track a search query with enhanced user context."""
    try:
        query = data.get("query", "")
        results_count = data.get("results_count", 0)
        country = data.get("country", "Unknown")
        user_info = data.get("user_info", {})
        success = redis_analytics_service.track_search_query(query, results_count, country, user_info)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error tracking search query: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/api/analytics/track/page-activity")
async def track_page_activity(data: dict):
    """Track a page activity with enhanced user context."""
    try:
        page = data.get("page", "")
        activity = data.get("activity", "")
        user_country = data.get("user_country", "Unknown")
        user_info = data.get("user_info", {})
        success = redis_analytics_service.track_page_activity(page, activity, user_country, user_info)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error tracking page activity: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


# API info endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Movie Search API",
        "version": "1.0.0",
        "description": "GraphQL API for searching and filtering movie data",
        "endpoints": {
            "graphql": "/graphql",
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "features": [
            "Full-text search across movie titles, stars, and content",
            "Filter by genre, subgenre, year, rating, language",
            "Sort by relevance, rating, year, popularity",
            "Pagination support",
            "Real-time search suggestions"
        ]
    }

# Include routers
app.include_router(metrics_router)
app.include_router(movies_router)

# Mount GraphQL application
graphql_app = create_graphql_app(search_service)
app.mount("/graphql", graphql_app)

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )

if __name__ == "__main__":
    # Run the application
    logger.info("🚀 Starting Movie Search API Service...")
    logger.info(f"Redis connection: {REDIS_HOST}:{REDIS_PORT}")
    logger.info("GraphQL endpoint: http://localhost:8000/graphql")
    logger.info("API documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

