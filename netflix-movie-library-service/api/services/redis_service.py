"""
Redis Service for Netflix Movie Library Explorer
Handles connections to multiple Redis databases for different purposes.
"""

import redis
import os
from typing import Dict, Any, List, Optional
from loguru import logger

class RedisService:
    """Service class for managing multiple Redis database connections."""
    
    def __init__(self):
        """Initialize Redis connections for all databases."""
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', '6379'))
        self.redis_password = os.getenv('REDIS_PASSWORD', None)
        
        # Initialize connections to different databases
        self.search_db = None      # DB 0 - RedisSearch (Movie data)
        self.analytics_db = None   # DB 1 - App Insights (User metrics)
        self.operations_db = None  # DB 2 - Service Insights (Application logs)
        
        self._connect_all()
    
    def _connect_all(self):
        """Establish connections to all Redis databases."""
        try:
            # DB 0 - RedisSearch (Movie data)
            self.search_db = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                db=0,
                decode_responses=True
            )
            self.search_db.ping()
            logger.info("✅ Connected to Redis DB 0 (RedisSearch)")
            
            # DB 1 - App Insights (User metrics)
            self.analytics_db = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                db=1,
                decode_responses=True
            )
            self.analytics_db.ping()
            logger.info("✅ Connected to Redis DB 1 (App Insights)")
            
            # DB 2 - Service Insights (Application logs)
            self.operations_db = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                db=2,
                decode_responses=True
            )
            self.operations_db.ping()
            logger.info("✅ Connected to Redis DB 2 (Service Insights)")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            raise
    
    def get_search_db(self) -> redis.Redis:
        """Get connection to search database (DB 0)."""
        return self.search_db
    
    def get_analytics_db(self) -> redis.Redis:
        """Get connection to analytics database (DB 1)."""
        return self.analytics_db
    
    def get_operations_db(self) -> redis.Redis:
        """Get connection to operations database (DB 2)."""
        return self.operations_db
    
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all Redis databases."""
        health_status = {
            "overall": "healthy",
            "databases": {},
            "timestamp": None
        }
        
        databases = [
            ("search", self.search_db, "RedisSearch"),
            ("analytics", self.analytics_db, "App Insights"),
            ("operations", self.operations_db, "Service Insights")
        ]
        
        all_healthy = True
        
        for db_name, db_client, description in databases:
            try:
                if db_client:
                    db_client.ping()
                    key_count = db_client.dbsize()
                    health_status["databases"][db_name] = {
                        "status": "healthy",
                        "description": description,
                        "key_count": key_count
                    }
                else:
                    health_status["databases"][db_name] = {
                        "status": "disconnected",
                        "description": description,
                        "key_count": 0
                    }
                    all_healthy = False
            except Exception as e:
                health_status["databases"][db_name] = {
                    "status": "error",
                    "description": description,
                    "error": str(e),
                    "key_count": 0
                }
                all_healthy = False
        
        if not all_healthy:
            health_status["overall"] = "unhealthy"
        
        health_status["timestamp"] = logger.info("Redis health check completed")
        
        return health_status

# Create singleton instance
redis_service = RedisService()
