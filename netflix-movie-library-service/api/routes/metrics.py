from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from api.services.metrics_service import metrics_service
from api.services.logging_service import logging_service
import time

router = APIRouter(prefix="/metrics", tags=["metrics"])


class UserActionRequest(BaseModel):
    action: str
    user_id: str
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class SearchQueryRequest(BaseModel):
    query: str
    results_count: int
    user_id: str
    session_id: Optional[str] = None
    filters: Optional[Dict[str, Any]] = {}


class PageViewRequest(BaseModel):
    page: str
    user_id: str
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class ApiCallRequest(BaseModel):
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    user_id: str
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


@router.post("/track-action")
async def track_user_action(request: UserActionRequest):
    """Track user actions and interactions."""
    try:
        start_time = time.time()
        
        metrics_service.track_user_action(
            action=request.action,
            user_id=request.user_id,
            metadata=request.metadata
        )
        
        response_time = (time.time() - start_time) * 1000
        
        # Log the API call
        logging_service.log_api_request(
            method="POST",
            endpoint="/metrics/track-action",
            status_code=200,
            response_time_ms=response_time,
            user_id=request.user_id
        )
        
        return {"status": "success", "message": "Action tracked successfully"}
        
    except Exception as e:
        logging_service.log_error(e, "metrics_api", {"action": "track_user_action"})
        raise HTTPException(status_code=500, detail="Failed to track user action")


@router.post("/track-search")
async def track_search_query(request: SearchQueryRequest):
    """Track search queries and their effectiveness."""
    try:
        start_time = time.time()
        
        metrics_service.track_search_query(
            query=request.query,
            results_count=request.results_count,
            user_id=request.user_id,
            filters=request.filters
        )
        
        response_time = (time.time() - start_time) * 1000
        
        # Log the API call
        logging_service.log_api_request(
            method="POST",
            endpoint="/metrics/track-search",
            status_code=200,
            response_time_ms=response_time,
            user_id=request.user_id
        )
        
        return {"status": "success", "message": "Search query tracked successfully"}
        
    except Exception as e:
        logging_service.log_error(e, "metrics_api", {"action": "track_search_query"})
        raise HTTPException(status_code=500, detail="Failed to track search query")


@router.post("/track-page-view")
async def track_page_view(request: PageViewRequest):
    """Track page views and navigation patterns."""
    try:
        start_time = time.time()
        
        metrics_service.track_page_view(
            page=request.page,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        response_time = (time.time() - start_time) * 1000
        
        # Log the API call
        logging_service.log_api_request(
            method="POST",
            endpoint="/metrics/track-page-view",
            status_code=200,
            response_time_ms=response_time,
            user_id=request.user_id
        )
        
        return {"status": "success", "message": "Page view tracked successfully"}
        
    except Exception as e:
        logging_service.log_error(e, "metrics_api", {"action": "track_page_view"})
        raise HTTPException(status_code=500, detail="Failed to track page view")


@router.post("/track-api-call")
async def track_api_call(request: ApiCallRequest):
    """Track API calls and performance metrics."""
    try:
        start_time = time.time()
        
        metrics_service.track_api_call(
            endpoint=request.endpoint,
            method=request.method,
            status_code=request.status_code,
            response_time_ms=request.response_time_ms,
            user_id=request.user_id
        )
        
        response_time = (time.time() - start_time) * 1000
        
        # Log the API call
        logging_service.log_api_request(
            method="POST",
            endpoint="/metrics/track-api-call",
            status_code=200,
            response_time_ms=response_time,
            user_id=request.user_id
        )
        
        return {"status": "success", "message": "API call tracked successfully"}
        
    except Exception as e:
        logging_service.log_error(e, "metrics_api", {"action": "track_api_call"})
        raise HTTPException(status_code=500, detail="Failed to track API call")


@router.get("/user/{user_id}")
async def get_user_metrics(user_id: str, days: int = 7):
    """Get user-specific metrics."""
    try:
        metrics = metrics_service.get_user_metrics(user_id, days)
        return metrics
        
    except Exception as e:
        logging_service.log_error(e, "metrics_api", {"action": "get_user_metrics", "user_id": user_id})
        raise HTTPException(status_code=500, detail="Failed to get user metrics")


@router.get("/global")
async def get_global_metrics(days: int = 7):
    """Get global system metrics."""
    try:
        metrics = metrics_service.get_global_metrics(days)
        return metrics
        
    except Exception as e:
        logging_service.log_error(e, "metrics_api", {"action": "get_global_metrics"})
        raise HTTPException(status_code=500, detail="Failed to get global metrics")


@router.get("/logs")
async def get_logs(component: Optional[str] = None, level: Optional[str] = None, hours: int = 24, limit: int = 100):
    """Get application logs."""
    try:
        logs = logging_service.get_logs(component, level, hours, limit)
        return {"logs": logs, "count": len(logs)}
        
    except Exception as e:
        logging_service.log_error(e, "metrics_api", {"action": "get_logs"})
        raise HTTPException(status_code=500, detail="Failed to get logs")


@router.get("/logs/errors")
async def get_error_logs(hours: int = 24, limit: int = 50):
    """Get error logs specifically."""
    try:
        logs = logging_service.get_error_logs(hours, limit)
        return {"error_logs": logs, "count": len(logs)}
        
    except Exception as e:
        logging_service.log_error(e, "metrics_api", {"action": "get_error_logs"})
        raise HTTPException(status_code=500, detail="Failed to get error logs")


@router.get("/logs/api")
async def get_api_logs(hours: int = 24, limit: int = 100):
    """Get API logs specifically."""
    try:
        logs = logging_service.get_api_logs(hours, limit)
        return {"api_logs": logs, "count": len(logs)}
        
    except Exception as e:
        logging_service.log_error(e, "metrics_api", {"action": "get_api_logs"})
        raise HTTPException(status_code=500, detail="Failed to get API logs")


@router.post("/cleanup")
async def cleanup_old_data(metrics_days: int = 30, logs_days: int = 7):
    """Clean up old metrics and log data."""
    try:
        metrics_service.cleanup_old_data(metrics_days)
        logging_service.cleanup_old_logs(logs_days)
        
        return {
            "status": "success", 
            "message": f"Cleanup completed: metrics older than {metrics_days} days, logs older than {logs_days} days"
        }
        
    except Exception as e:
        logging_service.log_error(e, "metrics_api", {"action": "cleanup_old_data"})
        raise HTTPException(status_code=500, detail="Failed to cleanup old data")
