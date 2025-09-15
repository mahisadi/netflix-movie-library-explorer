"""
Redis Analytics Service for Netflix Movie Library Explorer
Handles real-time analytics data collection and retrieval using Redis DB 1.
"""

import redis
import json
import time
from typing import Dict, Any, List, Optional
from loguru import logger
from .redis_service import redis_service

class RedisAnalyticsService:
    """Service for managing analytics data in Redis DB 1."""
    
    def __init__(self):
        """Initialize the analytics service."""
        self.redis = redis_service.get_analytics_db()
        logger.info("Redis Analytics Service initialized")
    
    def track_page_view(self, page: str, user_country: str = 'Unknown') -> bool:
        """Track page view with country information."""
        try:
            today = self.get_today_string()
            month = self.get_month_string()
            
            # Increment daily page views
            self.redis.hincrby(f"page_views:daily:{today}", page, 1)
            
            # Increment monthly country distribution
            self.redis.hincrby(f"user_countries:monthly:{month}", user_country, 1)
            
            # Add to time series for real-time analytics (if RedisTimeSeries is available)
            try:
                self.redis.execute_command("TS.ADD", "user_activity:page_views", "*", 1, 
                                         "LABELS", "page", page, "country", user_country)
            except:
                # Fallback to regular Redis operations if RedisTimeSeries is not available
                self.redis.lpush(f"user_activity:page_views:{today}", 
                               json.dumps({
                                   "page": page,
                                   "country": user_country,
                                   "timestamp": time.time()
                               }))
            
            logger.debug(f"📊 Tracked page view: {page} from {user_country}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking page view: {e}")
            return False
    
    def track_search_query(self, query: str, results_count: int, user_country: str = 'Unknown') -> bool:
        """Track search query with results count."""
        try:
            today = self.get_today_string()
            
            # Increment search frequency
            self.redis.hincrby(f"search_activities:daily:{today}", query, 1)
            
            # Add to search rankings (sorted set)
            self.redis.zadd(f"search_rankings:daily:{today}", {query: results_count})
            
            # Add to time series
            try:
                self.redis.execute_command("TS.ADD", "user_activity:search_queries", "*", 1,
                                         "LABELS", "query", query, "results", str(results_count))
            except:
                # Fallback to regular Redis operations
                self.redis.lpush(f"user_activity:search_queries:{today}", 
                               json.dumps({
                                   "query": query,
                                   "results": results_count,
                                   "country": user_country,
                                   "timestamp": time.time()
                               }))
            
            logger.debug(f"🔍 Tracked search: '{query}' with {results_count} results")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking search query: {e}")
            return False
    
    def track_user_country(self, country: str) -> bool:
        """Track user country for analytics."""
        try:
            month = self.get_month_string()
            
            # Increment country count
            self.redis.hincrby(f"user_countries:monthly:{month}", country, 1)
            
            # Add to country rankings
            self.redis.zadd(f"country_rankings:monthly:{month}", {country: 1})
            
            # Add to time series
            try:
                self.redis.execute_command("TS.ADD", "user_activity:country_distribution", "*", 1,
                                         "LABELS", "country", country)
            except:
                # Fallback to regular Redis operations
                self.redis.lpush(f"user_activity:country_distribution:{month}", 
                               json.dumps({
                                   "country": country,
                                   "timestamp": time.time()
                               }))
            
            logger.debug(f"🌍 Tracked user country: {country}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking user country: {e}")
            return False
    
    def track_page_activity(self, page: str, activity: str, user_country: str = 'Unknown') -> bool:
        """Track page activity (clicks, interactions, etc.)."""
        try:
            today = self.get_today_string()
            
            # Store activity in a list for recent activities
            activity_data = {
                "visit_page": page,
                "activity": activity,
                "user_profile": {"country": user_country},
                "timestamp": time.time()
            }
            
            self.redis.lpush(f"page_activities:daily:{today}", json.dumps(activity_data))
            
            # Keep only last 100 activities
            self.redis.ltrim(f"page_activities:daily:{today}", 0, 99)
            
            logger.debug(f"📋 Tracked page activity: {page} - {activity}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking page activity: {e}")
            return False
    
    def get_page_views_data(self) -> Dict[str, int]:
        """Get page views data for Insights dashboard."""
        try:
            today = self.get_today_string()
            page_views = self.redis.hgetall(f"page_views:daily:{today}")
            
            return {
                "Home": int(page_views.get("Home", 0)),
                "Library": int(page_views.get("Library", 0)),
                "Insights": int(page_views.get("Insights", 0))
            }
        except Exception as e:
            logger.error(f"Error getting page views data: {e}")
            return {"Home": 0, "Library": 0, "Insights": 0}
    
    def get_search_activities_data(self) -> Dict[str, Dict[str, int]]:
        """Get search activities data for Insights dashboard."""
        try:
            today = self.get_today_string()
            search_activities = self.redis.hgetall(f"search_activities:daily:{today}")
            
            result = {}
            for query, count in search_activities.items():
                result[query] = {"resultsCount": int(count)}
            
            return result
        except Exception as e:
            logger.error(f"Error getting search activities data: {e}")
            return {}
    
    def get_user_countries_data(self) -> Dict[str, int]:
        """Get user countries data for Insights dashboard."""
        try:
            month = self.get_month_string()
            countries = self.redis.hgetall(f"user_countries:monthly:{month}")
            
            result = {}
            for country, count in countries.items():
                result[country] = int(count)
            
            return result
        except Exception as e:
            logger.error(f"Error getting user countries data: {e}")
            return {}
    
    def get_page_activities_data(self) -> List[Dict[str, Any]]:
        """Get page activities data for Insights dashboard."""
        try:
            today = self.get_today_string()
            activities = self.redis.lrange(f"page_activities:daily:{today}", 0, -1)
            
            result = []
            for activity in activities:
                try:
                    result.append(json.loads(activity))
                except json.JSONDecodeError:
                    continue
            
            return result
        except Exception as e:
            logger.error(f"Error getting page activities data: {e}")
            return []
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary."""
        try:
            today = self.get_today_string()
            month = self.get_month_string()
            
            # Get all analytics data
            page_views = self.get_page_views_data()
            search_activities = self.get_search_activities_data()
            user_countries = self.get_user_countries_data()
            page_activities = self.get_page_activities_data()
            
            # Calculate totals
            total_page_views = sum(page_views.values())
            total_searches = sum(activity["resultsCount"] for activity in search_activities.values())
            total_countries = len(user_countries)
            total_activities = len(page_activities)
            
            return {
                "page_views": page_views,
                "search_activities": search_activities,
                "user_countries": user_countries,
                "page_activities": page_activities,
                "summary": {
                    "total_page_views": total_page_views,
                    "total_searches": total_searches,
                    "total_countries": total_countries,
                    "total_activities": total_activities,
                    "date": today,
                    "month": month
                }
            }
        except Exception as e:
            logger.error(f"Error getting analytics summary: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 30) -> bool:
        """Clean up old analytics data."""
        try:
            cutoff_date = time.time() - (days * 24 * 60 * 60)
            today = self.get_today_string()
            
            # Clean up old daily data
            for i in range(days + 1, days + 31):  # Clean up data older than specified days
                old_date = time.strftime("%Y-%m-%d", time.localtime(cutoff_date - (i * 24 * 60 * 60)))
                
                # Delete old keys
                self.redis.delete(f"page_views:daily:{old_date}")
                self.redis.delete(f"search_activities:daily:{old_date}")
                self.redis.delete(f"page_activities:daily:{old_date}")
                self.redis.delete(f"user_activity:page_views:{old_date}")
                self.redis.delete(f"user_activity:search_queries:{old_date}")
            
            logger.info(f"Cleaned up analytics data older than {days} days")
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return False
    
    def get_today_string(self) -> str:
        """Get today's date as YYYY-MM-DD string."""
        return time.strftime("%Y-%m-%d")
    
    def get_month_string(self) -> str:
        """Get current month as YYYY-MM string."""
        return time.strftime("%Y-%m")
    
    def health_check(self) -> Dict[str, Any]:
        """Check analytics service health."""
        try:
            self.redis.ping()
            return {
                "status": "healthy",
                "message": "Redis Analytics Service is operational",
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Redis Analytics Service error: {str(e)}",
                "timestamp": time.time()
            }

# Create singleton instance
redis_analytics_service = RedisAnalyticsService()
