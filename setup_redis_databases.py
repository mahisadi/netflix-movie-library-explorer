#!/usr/bin/env python3
"""
Setup Redis Databases for Netflix Movie Library Explorer
This script sets up the proper Redis database structure:
- DB 0: RedisSearch (Movie data)
- DB 1: App Insights (User metrics)
- DB 2: Service Insights (Application logs)
"""

import redis
import sys
import os
from typing import Dict, Any

def setup_redis_databases():
    """Setup Redis databases with proper structure"""
    
    # Redis connection settings
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    
    try:
        print("🔧 Setting up Redis databases for Netflix Movie Library Explorer...")
        
        # Clear all databases first
        print("🗑️  Clearing all databases...")
        for db_num in range(16):
            try:
                redis_client = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    password=REDIS_PASSWORD,
                    db=db_num,
                    decode_responses=True
                )
                redis_client.ping()
                key_count = redis_client.dbsize()
                if key_count > 0:
                    redis_client.flushdb()
                    print(f"   ✅ Cleared DB {db_num}: {key_count} keys")
            except:
                pass
        
        print("✅ All databases cleared")
        
        # Setup DB 0 - RedisSearch (Movie data)
        print("\n📊 Setting up DB 0 - RedisSearch (Movie data)...")
        db0_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=0,
            decode_responses=True
        )
        db0_client.ping()
        print("   ✅ DB 0 connected")
        
        # Setup DB 1 - App Insights (User metrics)
        print("📊 Setting up DB 1 - App Insights (User metrics)...")
        db1_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=1,
            decode_responses=True
        )
        db1_client.ping()
        print("   ✅ DB 1 connected")
        
        # Setup DB 2 - Service Insights (Application logs)
        print("📊 Setting up DB 2 - Service Insights (Application logs)...")
        db2_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=2,
            decode_responses=True
        )
        db2_client.ping()
        print("   ✅ DB 2 connected")
        
        # Initialize time-series structures for analytics (DB 1)
        print("\n📈 Setting up Analytics time-series structures...")
        try:
            # Page views time series
            db1_client.execute_command("TS.CREATE", "user_activity:page_views", 
                                     "RETENTION", "90d", 
                                     "LABELS", "type", "page_views")
            
            # Search queries time series
            db1_client.execute_command("TS.CREATE", "user_activity:search_queries", 
                                     "RETENTION", "30d", 
                                     "LABELS", "type", "search")
            
            # Country distribution time series
            db1_client.execute_command("TS.CREATE", "user_activity:country_distribution", 
                                     "RETENTION", "180d", 
                                     "LABELS", "type", "geography")
            
            print("   ✅ Analytics time-series structures created")
        except Exception as e:
            print(f"   ⚠️  Time-series setup failed (RedisTimeSeries module may not be available): {e}")
        
        # Initialize time-series structures for operations (DB 2)
        print("\n⚙️  Setting up Operations time-series structures...")
        try:
            # System metrics time series
            db2_client.execute_command("TS.CREATE", "system_metrics:cpu_usage", 
                                     "RETENTION", "7d", 
                                     "LABELS", "type", "cpu")
            
            db2_client.execute_command("TS.CREATE", "system_metrics:memory_usage", 
                                     "RETENTION", "7d", 
                                     "LABELS", "type", "memory")
            
            db2_client.execute_command("TS.CREATE", "system_metrics:redis_memory", 
                                     "RETENTION", "7d", 
                                     "LABELS", "type", "redis")
            
            # Application metrics time series
            db2_client.execute_command("TS.CREATE", "app_metrics:response_time", 
                                     "RETENTION", "3d", 
                                     "LABELS", "type", "performance")
            
            db2_client.execute_command("TS.CREATE", "app_metrics:error_rate", 
                                     "RETENTION", "7d", 
                                     "LABELS", "type", "errors")
            
            print("   ✅ Operations time-series structures created")
        except Exception as e:
            print(f"   ⚠️  Time-series setup failed (RedisTimeSeries module may not be available): {e}")
        
        # Initialize configuration data
        print("\n🔧 Setting up configuration data...")
        
        # Operations configuration (DB 2)
        db2_client.hset("operations:configuration", mapping={
            "cpu_threshold": "80",
            "memory_threshold": "85",
            "redis_threshold": "90",
            "response_time_threshold": "2000",
            "error_rate_threshold": "5",
            "alerting_enabled": "true",
            "alert_email": "admin@netflix.com",
            "alert_webhook": "",
            "metrics_retention_days": "7",
            "logs_retention_days": "30",
            "alerts_retention_days": "90"
        })
        
        print("   ✅ Configuration data initialized")
        
        # Verify the setup
        print("\n🔍 Verifying database setup...")
        
        # Check each database
        databases = [
            (0, "RedisSearch (Movie data)"),
            (1, "App Insights (User metrics)"),
            (2, "Service Insights (Application logs)")
        ]
        
        for db_num, description in databases:
            try:
                client = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    password=REDIS_PASSWORD,
                    db=db_num,
                    decode_responses=True
                )
                client.ping()
                db_keys = client.dbsize()
                print(f"   DB {db_num} ({description}): {db_keys} keys")
            except Exception as e:
                print(f"   DB {db_num} ({description}): Error - {e}")
        
        print("\n✅ Redis database setup complete!")
        print("   📊 DB 0: RedisSearch (Movie data) - Ready for ingestion")
        print("   📊 DB 1: App Insights (User metrics) - Ready for tracking")
        print("   📊 DB 2: Service Insights (Application logs) - Ready for logging")
        
        print("\n💡 Next steps:")
        print("   1. Run: python setup_redis_search.py (to create RedisSearch indexes)")
        print("   2. Start the API service: python run_api_service.py")
        print("   3. Start the UI: cd netflix-movie-library-ui && npm run dev")
        print("   4. Access RedisInsight at: http://localhost:8001")
        
    except Exception as e:
        print(f"❌ Error setting up Redis databases: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🔧 Redis Database Setup for Netflix Movie Library Explorer")
    print("=" * 60)
    setup_redis_databases()
    print("\n🎬 Database setup complete!")
