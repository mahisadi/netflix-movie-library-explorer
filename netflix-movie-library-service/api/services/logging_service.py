from typing import Dict, Any, List, Optional
from loguru import logger
import time
import json

class LoggingService:
    """Service for managing application logs."""
    
    def __init__(self):
        self.logs = []
        logger.info("Logging service initialized")
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, response_time_ms: float, user_id: str):
        """Log API requests."""
        try:
            log_entry = {
                "type": "api_request",
                "method": method,
                "endpoint": endpoint,
                "status_code": status_code,
                "response_time_ms": response_time_ms,
                "user_id": user_id,
                "timestamp": time.time()
            }
            
            self.logs.append(log_entry)
            logger.info(f"API {method} {endpoint} - {status_code} - {response_time_ms}ms")
            
        except Exception as e:
            logger.error(f"Error logging API request: {e}")
    
    def log_error(self, error: Exception, component: str, metadata: Optional[Dict[str, Any]] = None):
        """Log errors."""
        try:
            log_entry = {
                "type": "error",
                "component": component,
                "error_message": str(error),
                "error_type": type(error).__name__,
                "metadata": metadata or {},
                "timestamp": time.time()
            }
            
            self.logs.append(log_entry)
            logger.error(f"Error in {component}: {error}")
            
        except Exception as e:
            logger.error(f"Error logging error: {e}")
    
    def log_info(self, message: str, component: str, metadata: Optional[Dict[str, Any]] = None):
        """Log info messages."""
        try:
            log_entry = {
                "type": "info",
                "component": component,
                "message": message,
                "metadata": metadata or {},
                "timestamp": time.time()
            }
            
            self.logs.append(log_entry)
            logger.info(f"{component}: {message}")
            
        except Exception as e:
            logger.error(f"Error logging info: {e}")
    
    def log_warning(self, message: str, component: str, metadata: Optional[Dict[str, Any]] = None):
        """Log warning messages."""
        try:
            log_entry = {
                "type": "warning",
                "component": component,
                "message": message,
                "metadata": metadata or {},
                "timestamp": time.time()
            }
            
            self.logs.append(log_entry)
            logger.warning(f"{component}: {message}")
            
        except Exception as e:
            logger.error(f"Error logging warning: {e}")
    
    def get_logs(self, component: Optional[str] = None, level: Optional[str] = None, hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """Get application logs."""
        try:
            cutoff_time = time.time() - (hours * 60 * 60)
            
            filtered_logs = []
            for log in self.logs:
                if log["timestamp"] < cutoff_time:
                    continue
                
                if component and log.get("component") != component:
                    continue
                
                if level and log.get("type") != level:
                    continue
                
                filtered_logs.append(log)
            
            # Sort by timestamp (newest first) and limit
            filtered_logs.sort(key=lambda x: x["timestamp"], reverse=True)
            return filtered_logs[:limit]
            
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return []
    
    def get_error_logs(self, hours: int = 24, limit: int = 50) -> List[Dict[str, Any]]:
        """Get error logs specifically."""
        return self.get_logs(level="error", hours=hours, limit=limit)
    
    def get_api_logs(self, hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """Get API logs specifically."""
        return self.get_logs(level="api_request", hours=hours, limit=limit)
    
    def cleanup_old_logs(self, days: int = 7):
        """Clean up old log data."""
        try:
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            self.logs = [log for log in self.logs if log["timestamp"] >= cutoff_time]
            logger.info(f"Cleaned up logs older than {days} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old logs: {e}")

# Create a singleton instance
logging_service = LoggingService()
