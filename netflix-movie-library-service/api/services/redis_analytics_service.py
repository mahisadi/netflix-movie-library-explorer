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
    
    def track_page_view(self, page: str, user_country: str = 'Unknown', user_info: dict = None) -> bool:
        """Track page view with enhanced user context and 30-day TTL."""
        try:
            today = self.get_today_string()
            month = self.get_month_string()
            
            # Extract user info if provided
            if user_info:
                unique_record_id = user_info.get('uniqueRecordId', f"unknown:{time.time()}")
                user_email = user_info.get('email', 'unknown@example.com')
                user_name = user_info.get('fullName', 'Unknown User')
                city = user_info.get('city', 'Unknown')
                timezone = user_info.get('timezone', 'Unknown')
                nationality = user_info.get('nationality', 'Unknown')
            else:
                unique_record_id = f"unknown:{time.time()}"
                user_email = 'unknown@example.com'
                user_name = 'Unknown User'
                city = 'Unknown'
                timezone = 'Unknown'
                nationality = 'Unknown'
            
            # Increment daily page views (this is what get_page_views_data reads)
            self.redis.hincrby(f"page_views:daily:{today}", page, 1)
            
            # Increment monthly country distribution
            self.redis.hincrby(f"user_countries:monthly:{month}", user_country, 1)
            
            # Store detailed user context with 30-day TTL
            user_context_key = f"user_context:{user_email}:{today}"
            self.redis.hset(user_context_key, mapping={
                "unique_record_id": unique_record_id,
                "user_email": user_email,
                "user_name": user_name,
                "country": user_country,
                "city": city,
                "timezone": timezone,
                "nationality": nationality,
                "last_seen": time.time(),
                "last_page": page
            })
            self.redis.expire(user_context_key, 30 * 24 * 60 * 60)  # 30 days TTL
            
            # Store page view record with unique identifier and 30-day TTL
            page_view_key = f"page_view_record:{unique_record_id}:{today}"
            self.redis.hset(page_view_key, mapping={
                "page": page,
                "user_email": user_email,
                "user_name": user_name,
                "country": user_country,
                "city": city,
                "timezone": timezone,
                "timestamp": time.time(),
                "unique_record_id": unique_record_id
            })
            self.redis.expire(page_view_key, 30 * 24 * 60 * 60)  # 30 days TTL
            
            # Add to time series for real-time analytics (if RedisTimeSeries is available)
            try:
                self.redis.execute_command("TS.ADD", "user_activity:page_views", "*", 1, 
                                         "LABELS", "page", page, "country", user_country, "user_email", user_email)
            except:
                # Fallback to regular Redis operations if RedisTimeSeries is not available
                self.redis.lpush(f"user_activity:page_views:{today}", 
                               json.dumps({
                                   "page": page,
                                   "country": user_country,
                                   "user_email": user_email,
                                   "unique_record_id": unique_record_id,
                                   "timestamp": time.time()
                               }))
                # Set TTL for the list
                self.redis.expire(f"user_activity:page_views:{today}", 30 * 24 * 60 * 60)
            
            logger.debug(f"📊 Tracked page view: {page} from {user_country} (User: {user_name}, Email: {user_email})")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking page view: {e}")
            return False
    
    def track_search_query(self, query: str, results_count: int, user_country: str = 'Unknown', user_info: dict = None) -> bool:
        """Track search query with enhanced user context and 30-day TTL."""
        try:
            today = self.get_today_string()
            
            # Extract user info if provided
            if user_info:
                unique_record_id = user_info.get('uniqueRecordId', f"unknown:{time.time()}")
                user_email = user_info.get('email', 'unknown@example.com')
                user_name = user_info.get('fullName', 'Unknown User')
                city = user_info.get('city', 'Unknown')
                timezone = user_info.get('timezone', 'Unknown')
                nationality = user_info.get('nationality', 'Unknown')
            else:
                unique_record_id = f"unknown:{time.time()}"
                user_email = 'unknown@example.com'
                user_name = 'Unknown User'
                city = 'Unknown'
                timezone = 'Unknown'
                nationality = 'Unknown'
            
            # Increment search frequency
            self.redis.hincrby(f"search_activities:daily:{today}", query, 1)
            
            # Add to search rankings (sorted set)
            self.redis.zadd(f"search_rankings:daily:{today}", {query: results_count})
            
            # Store detailed search record with unique identifier and 30-day TTL
            search_record_key = f"search_record:{unique_record_id}:{today}"
            self.redis.hset(search_record_key, mapping={
                "query": query,
                "results_count": results_count,
                "user_email": user_email,
                "user_name": user_name,
                "country": user_country,
                "city": city,
                "timezone": timezone,
                "nationality": nationality,
                "timestamp": time.time(),
                "unique_record_id": unique_record_id
            })
            self.redis.expire(search_record_key, 30 * 24 * 60 * 60)  # 30 days TTL
            
            # Add to time series
            try:
                self.redis.execute_command("TS.ADD", "user_activity:search_queries", "*", 1,
                                         "LABELS", "query", query, "results", str(results_count), "user_email", user_email)
            except:
                # Fallback to regular Redis operations
                self.redis.lpush(f"user_activity:search_queries:{today}", 
                               json.dumps({
                                   "query": query,
                                   "results": results_count,
                                   "country": user_country,
                                   "user_email": user_email,
                                   "unique_record_id": unique_record_id,
                                   "timestamp": time.time()
                               }))
                # Set TTL for the list
                self.redis.expire(f"user_activity:search_queries:{today}", 30 * 24 * 60 * 60)
            
            logger.debug(f"🔍 Tracked search: '{query}' with {results_count} results (User: {user_name}, Email: {user_email})")
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
    
    def track_page_activity(self, page: str, activity: str, user_country: str = 'Unknown', user_info: dict = None) -> bool:
        """Track page activity with enhanced user context and 30-day TTL."""
        try:
            today = self.get_today_string()
            
            # Extract user info if provided
            if user_info:
                unique_record_id = user_info.get('uniqueRecordId', f"unknown:{time.time()}")
                user_email = user_info.get('email', 'unknown@example.com')
                user_name = user_info.get('fullName', 'Unknown User')
                city = user_info.get('city', 'Unknown')
                timezone = user_info.get('timezone', 'Unknown')
                nationality = user_info.get('nationality', 'Unknown')
            else:
                unique_record_id = f"unknown:{time.time()}"
                user_email = 'unknown@example.com'
                user_name = 'Unknown User'
                city = 'Unknown'
                timezone = 'Unknown'
                nationality = 'Unknown'
            
            # Store activity in a list for recent activities with enhanced data
            activity_data = {
                "visit_page": page,
                "activity": activity,
                "user_profile": {
                    "country": user_country,
                    "city": city,
                    "timezone": timezone,
                    "nationality": nationality
                },
                "user_email": user_email,
                "user_name": user_name,
                "unique_record_id": unique_record_id,
                "timestamp": time.time()
            }
            
            self.redis.lpush(f"page_activities:daily:{today}", json.dumps(activity_data))
            
            # Keep only last 100 activities
            self.redis.ltrim(f"page_activities:daily:{today}", 0, 99)
            
            # Set TTL for the list
            self.redis.expire(f"page_activities:daily:{today}", 30 * 24 * 60 * 60)
            
            # Store detailed activity record with unique identifier and 30-day TTL
            activity_record_key = f"activity_record:{unique_record_id}:{today}"
            self.redis.hset(activity_record_key, mapping={
                "page": page,
                "activity": activity,
                "user_email": user_email,
                "user_name": user_name,
                "country": user_country,
                "city": city,
                "timezone": timezone,
                "nationality": nationality,
                "timestamp": time.time(),
                "unique_record_id": unique_record_id
            })
            self.redis.expire(activity_record_key, 30 * 24 * 60 * 60)  # 30 days TTL
            
            logger.debug(f"📋 Tracked page activity: {page} - {activity} (User: {user_name}, Email: {user_email})")
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
            
            # Get all search record keys for today
            search_record_keys = self.redis.keys(f"search_record:*:{today}")
            
            result = {}
            query_results = {}  # Store query -> results_count mapping
            
            # Process each search record to get actual results count
            for key in search_record_keys:
                search_data = self.redis.hgetall(key)
                if search_data:
                    query = search_data.get('query', '').decode('utf-8') if isinstance(search_data.get('query', ''), bytes) else search_data.get('query', '')
                    results_count = int(search_data.get('results_count', 0))
                    
                    if query:
                        # Store the results count for this query
                        query_results[query] = results_count
            
            # Convert to the expected format
            for query, results_count in query_results.items():
                result[query] = {"resultsCount": results_count}
            
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
    
    def get_user_specific_metrics(self, user_email: str, days: int = 7) -> Dict[str, Any]:
        """Get user-specific metrics for the last N days."""
        try:
            user_metrics = {
                "user_email": user_email,
                "page_views": [],
                "search_queries": [],
                "page_activities": [],
                "summary": {
                    "total_page_views": 0,
                    "total_searches": 0,
                    "total_activities": 0,
                    "unique_pages": set(),
                    "unique_queries": set(),
                    "countries": set()
                }
            }
            
            # Get data for the last N days
            for i in range(days):
                date = time.strftime("%Y-%m-%d", time.localtime(time.time() - (i * 24 * 60 * 60)))
                
                # Get page view records for this user
                page_view_pattern = f"page_view_record:*:{date}"
                page_view_keys = self.redis.keys(page_view_pattern)
                for key in page_view_keys:
                    record = self.redis.hgetall(key)
                    if record.get('user_email') == user_email:
                        user_metrics["page_views"].append(record)
                        user_metrics["summary"]["total_page_views"] += 1
                        user_metrics["summary"]["unique_pages"].add(record.get('page', ''))
                        user_metrics["summary"]["countries"].add(record.get('country', ''))
                
                # Get search records for this user
                search_pattern = f"search_record:*:{date}"
                search_keys = self.redis.keys(search_pattern)
                for key in search_keys:
                    record = self.redis.hgetall(key)
                    if record.get('user_email') == user_email:
                        user_metrics["search_queries"].append(record)
                        user_metrics["summary"]["total_searches"] += 1
                        user_metrics["summary"]["unique_queries"].add(record.get('query', ''))
                        user_metrics["summary"]["countries"].add(record.get('country', ''))
                
                # Get activity records for this user
                activity_pattern = f"activity_record:*:{date}"
                activity_keys = self.redis.keys(activity_pattern)
                for key in activity_keys:
                    record = self.redis.hgetall(key)
                    if record.get('user_email') == user_email:
                        user_metrics["page_activities"].append(record)
                        user_metrics["summary"]["total_activities"] += 1
                        user_metrics["summary"]["countries"].add(record.get('country', ''))
            
            # Convert sets to lists for JSON serialization
            user_metrics["summary"]["unique_pages"] = list(user_metrics["summary"]["unique_pages"])
            user_metrics["summary"]["unique_queries"] = list(user_metrics["summary"]["unique_queries"])
            user_metrics["summary"]["countries"] = list(user_metrics["summary"]["countries"])
            
            logger.debug(f"Retrieved user-specific metrics for {user_email}: {user_metrics['summary']}")
            return user_metrics
            
        except Exception as e:
            logger.error(f"Error getting user-specific metrics: {e}")
            return {"error": str(e)}
    
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
                
                # Delete old user-specific records
                self.redis.delete(f"user_context:*:{old_date}")
                self.redis.delete(f"page_view_record:*:{old_date}")
                self.redis.delete(f"search_record:*:{old_date}")
                self.redis.delete(f"activity_record:*:{old_date}")
            
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
