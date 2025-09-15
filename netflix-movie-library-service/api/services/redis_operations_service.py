"""
Redis Operations Service for Netflix Movie Library Explorer
Handles system monitoring, health checks, and operations data using Redis DB 2.
"""

import redis
import json
import time
import psutil
from typing import Dict, Any, List, Optional
from loguru import logger
from .redis_service import redis_service

class RedisOperationsService:
    """Service for managing operations data in Redis DB 2."""
    
    def __init__(self):
        """Initialize the operations service."""
        self.redis = redis_service.get_operations_db()
        self.metrics = {
            "system": {},
            "performance": {},
            "alerts": []
        }
        logger.info("Redis Operations Service initialized")
    
    def collect_system_metrics(self) -> bool:
        """Collect current system metrics."""
        try:
            timestamp = int(time.time() * 1000)  # Milliseconds
            
            # Collect CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Collect memory usage
            memory_info = psutil.virtual_memory()
            memory_usage = memory_info.percent
            
            # Collect Redis memory usage
            redis_memory = self.get_redis_memory_usage()
            
            # Store in time series (if RedisTimeSeries is available)
            try:
                self.redis.execute_command("TS.ADD", "system_metrics:cpu_usage", timestamp, cpu_usage,
                                         "LABELS", "type", "cpu")
                self.redis.execute_command("TS.ADD", "system_metrics:memory_usage", timestamp, memory_usage,
                                         "LABELS", "type", "memory")
                self.redis.execute_command("TS.ADD", "system_metrics:redis_memory", timestamp, redis_memory,
                                         "LABELS", "type", "redis")
            except:
                # Fallback to regular Redis operations
                self.redis.lpush(f"system_metrics:cpu_usage:{int(time.time())}", 
                               json.dumps({"timestamp": timestamp, "value": cpu_usage}))
                self.redis.lpush(f"system_metrics:memory_usage:{int(time.time())}", 
                               json.dumps({"timestamp": timestamp, "value": memory_usage}))
                self.redis.lpush(f"system_metrics:redis_memory:{int(time.time())}", 
                               json.dumps({"timestamp": timestamp, "value": redis_memory}))
            
            # Update current metrics
            self.metrics["system"] = {
                "cpu": cpu_usage,
                "memory": memory_usage,
                "redis": redis_memory,
                "timestamp": time.time()
            }
            
            logger.debug(f"📊 Collected system metrics: CPU={cpu_usage}%, Memory={memory_usage}%, Redis={redis_memory}%")
            return True
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return False
    
    def collect_performance_metrics(self, response_time: float, error_rate: float) -> bool:
        """Collect application performance metrics."""
        try:
            timestamp = int(time.time() * 1000)  # Milliseconds
            
            # Store in time series (if RedisTimeSeries is available)
            try:
                self.redis.execute_command("TS.ADD", "app_metrics:response_time", timestamp, response_time,
                                         "LABELS", "type", "performance")
                self.redis.execute_command("TS.ADD", "app_metrics:error_rate", timestamp, error_rate,
                                         "LABELS", "type", "errors")
            except:
                # Fallback to regular Redis operations
                self.redis.lpush(f"app_metrics:response_time:{int(time.time())}", 
                               json.dumps({"timestamp": timestamp, "value": response_time}))
                self.redis.lpush(f"app_metrics:error_rate:{int(time.time())}", 
                               json.dumps({"timestamp": timestamp, "value": error_rate}))
            
            # Update current metrics
            self.metrics["performance"] = {
                "responseTime": response_time,
                "errorRate": error_rate,
                "timestamp": time.time()
            }
            
            logger.debug(f"📊 Collected performance metrics: ResponseTime={response_time}ms, ErrorRate={error_rate}%")
            return True
            
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
            return False
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for system alerts based on thresholds."""
        try:
            alerts = []
            current_time = time.time()
            
            # Get configuration
            config = self.get_configuration()
            thresholds = config["systemThresholds"]
            perf_thresholds = config["performanceThresholds"]
            
            # Check CPU threshold
            if self.metrics["system"].get("cpu", 0) > thresholds["cpu"]:
                alerts.append({
                    "type": "warning",
                    "message": f"High CPU usage: {self.metrics['system'].get('cpu', 0):.1f}%",
                    "timestamp": current_time,
                    "severity": "high",
                    "metric": "cpu",
                    "value": self.metrics["system"].get("cpu", 0),
                    "threshold": thresholds["cpu"]
                })
            
            # Check memory threshold
            if self.metrics["system"].get("memory", 0) > thresholds["memory"]:
                alerts.append({
                    "type": "warning",
                    "message": f"High memory usage: {self.metrics['system'].get('memory', 0):.1f}%",
                    "timestamp": current_time,
                    "severity": "high",
                    "metric": "memory",
                    "value": self.metrics["system"].get("memory", 0),
                    "threshold": thresholds["memory"]
                })
            
            # Check Redis memory threshold
            if self.metrics["system"].get("redis", 0) > thresholds["redis"]:
                alerts.append({
                    "type": "warning",
                    "message": f"High Redis memory usage: {self.metrics['system'].get('redis', 0):.1f}%",
                    "timestamp": current_time,
                    "severity": "critical",
                    "metric": "redis",
                    "value": self.metrics["system"].get("redis", 0),
                    "threshold": thresholds["redis"]
                })
            
            # Check response time threshold
            if self.metrics["performance"].get("responseTime", 0) > perf_thresholds["responseTime"]:
                alerts.append({
                    "type": "warning",
                    "message": f"High response time: {self.metrics['performance'].get('responseTime', 0):.1f}ms",
                    "timestamp": current_time,
                    "severity": "medium",
                    "metric": "response_time",
                    "value": self.metrics["performance"].get("responseTime", 0),
                    "threshold": perf_thresholds["responseTime"]
                })
            
            # Check error rate threshold
            if self.metrics["performance"].get("errorRate", 0) > perf_thresholds["errorRate"]:
                alerts.append({
                    "type": "error",
                    "message": f"High error rate: {self.metrics['performance'].get('errorRate', 0):.1f}%",
                    "timestamp": current_time,
                    "severity": "critical",
                    "metric": "error_rate",
                    "value": self.metrics["performance"].get("errorRate", 0),
                    "threshold": perf_thresholds["errorRate"]
                })
            
            # Store alerts
            if alerts:
                self.metrics["alerts"] = alerts
                for alert in alerts:
                    self.redis.lpush("operations:alerts", json.dumps(alert))
                
                # Keep only last 50 alerts
                self.redis.ltrim("operations:alerts", 0, 49)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
            return []
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics for Operations dashboard."""
        try:
            # Get recent system metrics (last hour)
            one_hour_ago = int((time.time() - 3600) * 1000)
            current_time = int(time.time() * 1000)
            
            # Try to get time series data
            try:
                cpu_data = self.redis.execute_command("TS.RANGE", "system_metrics:cpu_usage", one_hour_ago, current_time)
                memory_data = self.redis.execute_command("TS.RANGE", "system_metrics:memory_usage", one_hour_ago, current_time)
                redis_data = self.redis.execute_command("TS.RANGE", "system_metrics:redis_memory", one_hour_ago, current_time)
                
                return {
                    "cpu": {
                        "current": self.metrics["system"].get("cpu", 0),
                        "history": [{"timestamp": point[0], "value": point[1]} for point in cpu_data]
                    },
                    "memory": {
                        "current": self.metrics["system"].get("memory", 0),
                        "history": [{"timestamp": point[0], "value": point[1]} for point in memory_data]
                    },
                    "redis": {
                        "current": self.metrics["system"].get("redis", 0),
                        "history": [{"timestamp": point[0], "value": point[1]} for point in redis_data]
                    },
                    "timestamp": self.metrics["system"].get("timestamp", time.time())
                }
            except:
                # Fallback to regular Redis operations
                return {
                    "cpu": {
                        "current": self.metrics["system"].get("cpu", 0),
                        "history": []
                    },
                    "memory": {
                        "current": self.metrics["system"].get("memory", 0),
                        "history": []
                    },
                    "redis": {
                        "current": self.metrics["system"].get("redis", 0),
                        "history": []
                    },
                    "timestamp": self.metrics["system"].get("timestamp", time.time())
                }
                
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {
                "cpu": {"current": 0, "history": []},
                "memory": {"current": 0, "history": []},
                "redis": {"current": 0, "history": []},
                "timestamp": time.time()
            }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for Operations dashboard."""
        try:
            # Get recent performance metrics (last hour)
            one_hour_ago = int((time.time() - 3600) * 1000)
            current_time = int(time.time() * 1000)
            
            # Try to get time series data
            try:
                response_time_data = self.redis.execute_command("TS.RANGE", "app_metrics:response_time", one_hour_ago, current_time)
                error_rate_data = self.redis.execute_command("TS.RANGE", "app_metrics:error_rate", one_hour_ago, current_time)
                
                return {
                    "responseTime": {
                        "current": self.metrics["performance"].get("responseTime", 0),
                        "history": [{"timestamp": point[0], "value": point[1]} for point in response_time_data]
                    },
                    "errorRate": {
                        "current": self.metrics["performance"].get("errorRate", 0),
                        "history": [{"timestamp": point[0], "value": point[1]} for point in error_rate_data]
                    },
                    "timestamp": self.metrics["performance"].get("timestamp", time.time())
                }
            except:
                # Fallback to regular Redis operations
                return {
                    "responseTime": {
                        "current": self.metrics["performance"].get("responseTime", 0),
                        "history": []
                    },
                    "errorRate": {
                        "current": self.metrics["performance"].get("errorRate", 0),
                        "history": []
                    },
                    "timestamp": self.metrics["performance"].get("timestamp", time.time())
                }
                
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {
                "responseTime": {"current": 0, "history": []},
                "errorRate": {"current": 0, "history": []},
                "timestamp": time.time()
            }
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        try:
            alerts = self.redis.lrange("operations:alerts", 0, 49)
            return [json.loads(alert) for alert in alerts]
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []
    
    def get_redis_info(self) -> Dict[str, Any]:
        """Get Redis information."""
        try:
            info = self.redis.info()
            
            # Parse Redis INFO command output
            parsed_info = {}
            for line in info.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    parsed_info[key] = value.strip()
            
            return {
                "version": parsed_info.get("redis_version", "Unknown"),
                "uptime": int(parsed_info.get("uptime_in_seconds", 0)),
                "connectedClients": int(parsed_info.get("connected_clients", 0)),
                "usedMemory": parsed_info.get("used_memory_human", "0B"),
                "totalCommands": int(parsed_info.get("total_commands_processed", 0)),
                "keyspaceHits": int(parsed_info.get("keyspace_hits", 0)),
                "keyspaceMisses": int(parsed_info.get("keyspace_misses", 0)),
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Error getting Redis info: {e}")
            return {
                "version": "Unknown",
                "uptime": 0,
                "connectedClients": 0,
                "usedMemory": "0B",
                "totalCommands": 0,
                "keyspaceHits": 0,
                "keyspaceMisses": 0,
                "timestamp": time.time()
            }
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get operations configuration."""
        try:
            config = self.redis.hgetall("operations:configuration")
            
            return {
                "systemThresholds": {
                    "cpu": int(config.get("cpu_threshold", 80)),
                    "memory": int(config.get("memory_threshold", 85)),
                    "redis": int(config.get("redis_threshold", 90))
                },
                "performanceThresholds": {
                    "responseTime": int(config.get("response_time_threshold", 2000)),
                    "errorRate": int(config.get("error_rate_threshold", 5))
                },
                "alerting": {
                    "enabled": config.get("alerting_enabled", "true") == "true",
                    "email": config.get("alert_email", ""),
                    "webhook": config.get("alert_webhook", "")
                },
                "retention": {
                    "metrics": int(config.get("metrics_retention_days", 7)),
                    "logs": int(config.get("logs_retention_days", 30)),
                    "alerts": int(config.get("alerts_retention_days", 90))
                }
            }
        except Exception as e:
            logger.error(f"Error getting configuration: {e}")
            return {
                "systemThresholds": {"cpu": 80, "memory": 85, "redis": 90},
                "performanceThresholds": {"responseTime": 2000, "errorRate": 5},
                "alerting": {"enabled": True, "email": "", "webhook": ""},
                "retention": {"metrics": 7, "logs": 30, "alerts": 90}
            }
    
    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """Update operations configuration."""
        try:
            self.redis.hset("operations:configuration", mapping={
                "cpu_threshold": str(config["systemThresholds"]["cpu"]),
                "memory_threshold": str(config["systemThresholds"]["memory"]),
                "redis_threshold": str(config["systemThresholds"]["redis"]),
                "response_time_threshold": str(config["performanceThresholds"]["responseTime"]),
                "error_rate_threshold": str(config["performanceThresholds"]["errorRate"]),
                "alerting_enabled": str(config["alerting"]["enabled"]),
                "alert_email": config["alerting"]["email"],
                "alert_webhook": config["alerting"]["webhook"],
                "metrics_retention_days": str(config["retention"]["metrics"]),
                "logs_retention_days": str(config["retention"]["logs"]),
                "alerts_retention_days": str(config["retention"]["alerts"])
            })
            
            logger.info("Configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def get_redis_memory_usage(self) -> float:
        """Get Redis memory usage percentage."""
        try:
            info = self.redis.info()
            used_memory = int(info.get("used_memory", 0))
            max_memory = int(info.get("maxmemory", 0))
            
            if max_memory > 0:
                return (used_memory / max_memory) * 100
            else:
                return 0.0
        except Exception as e:
            logger.error(f"Error getting Redis memory usage: {e}")
            return 0.0
    
    def health_check(self) -> Dict[str, Any]:
        """Check operations service health."""
        try:
            self.redis.ping()
            return {
                "status": "healthy",
                "message": "Redis Operations Service is operational",
                "metrics": self.metrics,
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Redis Operations Service error: {str(e)}",
                "timestamp": time.time()
            }

# Create singleton instance
redis_operations_service = RedisOperationsService()
