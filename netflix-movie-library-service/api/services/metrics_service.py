from typing import Dict, Any, List, Optional
from loguru import logger
import time
import json

class MetricsService:
    """Service for tracking and managing application metrics."""
    
    def __init__(self):
        self.metrics_data = {}
        logger.info("Metrics service initialized")
    
    def track_user_action(self, action: str, user_id: str, metadata: Optional[Dict[str, Any]] = None):
        """Track user actions and interactions."""
        try:
            timestamp = time.time()
            action_data = {
                "action": action,
                "user_id": user_id,
                "timestamp": timestamp,
                "metadata": metadata or {}
            }
            
            if user_id not in self.metrics_data:
                self.metrics_data[user_id] = {"actions": [], "searches": [], "page_views": [], "api_calls": []}
            
            self.metrics_data[user_id]["actions"].append(action_data)
            logger.info(f"Tracked user action: {action} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error tracking user action: {e}")
            raise
    
    def track_search_query(self, query: str, results_count: int, user_id: str, filters: Optional[Dict[str, Any]] = None):
        """Track search queries and their effectiveness."""
        try:
            timestamp = time.time()
            search_data = {
                "query": query,
                "results_count": results_count,
                "user_id": user_id,
                "timestamp": timestamp,
                "filters": filters or {}
            }
            
            if user_id not in self.metrics_data:
                self.metrics_data[user_id] = {"actions": [], "searches": [], "page_views": [], "api_calls": []}
            
            self.metrics_data[user_id]["searches"].append(search_data)
            logger.info(f"Tracked search query: {query} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error tracking search query: {e}")
            raise
    
    def track_page_view(self, page: str, user_id: str, session_id: Optional[str] = None):
        """Track page views and navigation patterns."""
        try:
            timestamp = time.time()
            page_data = {
                "page": page,
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": timestamp
            }
            
            if user_id not in self.metrics_data:
                self.metrics_data[user_id] = {"actions": [], "searches": [], "page_views": [], "api_calls": []}
            
            self.metrics_data[user_id]["page_views"].append(page_data)
            logger.info(f"Tracked page view: {page} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error tracking page view: {e}")
            raise
    
    def track_api_call(self, endpoint: str, method: str, status_code: int, response_time_ms: float, user_id: str):
        """Track API calls and performance metrics."""
        try:
            timestamp = time.time()
            api_data = {
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "response_time_ms": response_time_ms,
                "user_id": user_id,
                "timestamp": timestamp
            }
            
            if user_id not in self.metrics_data:
                self.metrics_data[user_id] = {"actions": [], "searches": [], "page_views": [], "api_calls": []}
            
            self.metrics_data[user_id]["api_calls"].append(api_data)
            logger.info(f"Tracked API call: {method} {endpoint} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error tracking API call: {e}")
            raise
    
    def get_user_metrics(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get user-specific metrics."""
        try:
            if user_id not in self.metrics_data:
                return {"user_id": user_id, "actions": [], "searches": [], "page_views": [], "api_calls": []}
            
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            
            user_data = self.metrics_data[user_id]
            filtered_data = {
                "user_id": user_id,
                "actions": [a for a in user_data["actions"] if a["timestamp"] >= cutoff_time],
                "searches": [s for s in user_data["searches"] if s["timestamp"] >= cutoff_time],
                "page_views": [p for p in user_data["page_views"] if p["timestamp"] >= cutoff_time],
                "api_calls": [a for a in user_data["api_calls"] if a["timestamp"] >= cutoff_time]
            }
            
            return filtered_data
            
        except Exception as e:
            logger.error(f"Error getting user metrics: {e}")
            raise
    
    def get_global_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Get global system metrics."""
        try:
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            
            total_actions = 0
            total_searches = 0
            total_page_views = 0
            total_api_calls = 0
            
            for user_data in self.metrics_data.values():
                total_actions += len([a for a in user_data["actions"] if a["timestamp"] >= cutoff_time])
                total_searches += len([s for s in user_data["searches"] if s["timestamp"] >= cutoff_time])
                total_page_views += len([p for p in user_data["page_views"] if p["timestamp"] >= cutoff_time])
                total_api_calls += len([a for a in user_data["api_calls"] if a["timestamp"] >= cutoff_time])
            
            return {
                "total_actions": total_actions,
                "total_searches": total_searches,
                "total_page_views": total_page_views,
                "total_api_calls": total_api_calls,
                "unique_users": len(self.metrics_data),
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error getting global metrics: {e}")
            raise
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old metrics data."""
        try:
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            
            for user_id, user_data in self.metrics_data.items():
                user_data["actions"] = [a for a in user_data["actions"] if a["timestamp"] >= cutoff_time]
                user_data["searches"] = [s for s in user_data["searches"] if s["timestamp"] >= cutoff_time]
                user_data["page_views"] = [p for p in user_data["page_views"] if p["timestamp"] >= cutoff_time]
                user_data["api_calls"] = [a for a in user_data["api_calls"] if a["timestamp"] >= cutoff_time]
            
            logger.info(f"Cleaned up metrics data older than {days} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            raise

# Create a singleton instance
metrics_service = MetricsService()
