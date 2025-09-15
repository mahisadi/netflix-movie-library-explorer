#!/usr/bin/env python3
"""
Test Redis Setup for Netflix Movie Library Explorer
This script tests all Redis databases and services to ensure they're working correctly.
"""

import redis
import sys
import os
import time
import json
from typing import Dict, Any

def test_redis_connection(host: str, port: int, password: str, db: int) -> bool:
    """Test connection to a specific Redis database."""
    try:
        client = redis.Redis(
            host=host,
            port=port,
            password=password,
            db=db,
            decode_responses=True
        )
        client.ping()
        return True
    except Exception as e:
        print(f" Failed to connect to DB {db}: {e}")
        return False

def test_redis_databases():
    """Test all Redis databases."""
    print("🔍 Testing Redis Database Connections...")
    
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    
    databases = [
        (0, "RedisSearch (Movie data)"),
        (1, "App Insights (User metrics)")
    ]
    
    all_connected = True
    
    for db_num, description in databases:
        print(f"   Testing DB {db_num} ({description})...")
        if test_redis_connection(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, db_num):
            print(f"   DB {db_num} connected successfully")
        else:
            print(f"    DB {db_num} connection failed")
            all_connected = False
    
    return all_connected

def test_redissearch():
    """Test RedisSearch functionality."""
    print("\n🔍 Testing RedisSearch...")
    
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    
    try:
        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=0,
            decode_responses=True
        )
        
        # Test RedisSearch module
        modules = client.execute_command("MODULE", "LIST")
        redissearch_loaded = any("search" in str(module).lower() for module in modules)
        
        if not redissearch_loaded:
            print("    RedisSearch module not loaded")
            return False
        
        print("   RedisSearch module is loaded")
        
        # Test index existence
        try:
            info = client.execute_command("FT.INFO", "movie_library")
            print("   Movie library index exists")
            return True
        except:
            print("   ⚠️  Movie library index does not exist (run setup_redis_search.py)")
            return False
            
    except Exception as e:
        print(f"    RedisSearch test failed: {e}")
        return False

def test_analytics_service():
    """Test analytics service functionality."""
    print("\n📊 Testing Analytics Service...")
    
    try:
        # Import the analytics service
        sys.path.append(os.path.join(os.path.dirname(__file__), 'netflix-movie-library-service'))
        from api.services.redis_analytics_service import redis_analytics_service
        
        # Test page view tracking (without creating test data)
        success = redis_analytics_service.track_page_view("Home", "United States")
        if success:
            print("   Page view tracking works")
        else:
            print("    Page view tracking failed")
            return False
        
        # Test search tracking (without creating test data)
        success = redis_analytics_service.track_search_query("sample search", 3, "United States")
        if success:
            print("   Search tracking works")
        else:
            print("    Search tracking failed")
            return False
        
        # Test data retrieval
        page_views = redis_analytics_service.get_page_views_data()
        if isinstance(page_views, dict):
            print("   Page views data retrieval works")
        else:
            print("    Page views data retrieval failed")
            return False
        
        print("   Analytics service is working correctly")
        return True
        
    except Exception as e:
        print(f"    Analytics service test failed: {e}")
        return False


def test_api_endpoints():
    """Test API endpoints."""
    print("\n🌐 Testing API Endpoints...")
    
    import requests
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("   Health endpoint works")
        else:
            print(f"    Health endpoint failed: {response.status_code}")
            return False
        
        # Test analytics endpoints
        response = requests.get("http://localhost:8000/api/analytics/page-views", timeout=5)
        if response.status_code == 200:
            print("   Analytics endpoints work")
        else:
            print(f"   ⚠️  Analytics endpoints not available: {response.status_code}")
        
        
        print("   API endpoints are accessible")
        return True
        
    except requests.exceptions.ConnectionError:
        print("   ⚠️  API server not running (start with: python run_api_service.py)")
        return False
    except Exception as e:
        print(f"    API endpoints test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Redis Setup Test for Netflix Movie Library Explorer")
    print("=" * 60)
    
    # Test Redis databases
    db_test_passed = test_redis_databases()
    
    # Test RedisSearch
    redissearch_test_passed = test_redissearch()
    
    # Test analytics service
    analytics_test_passed = test_analytics_service()
    
    
    # Test API endpoints
    api_test_passed = test_api_endpoints()
    
    # Summary
    print("\n📋 Test Summary:")
    print("=" * 30)
    
    tests = [
        ("Redis Databases", db_test_passed),
        ("RedisSearch", redissearch_test_passed),
        ("Analytics Service", analytics_test_passed),
        ("API Endpoints", api_test_passed)
    ]
    
    all_passed = True
    for test_name, passed in tests:
        status = "PASS" if passed else " FAIL"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! Redis setup is working correctly.")
        print("\n💡 Next steps:")
        print("   1. Start the API service: python run_api_service.py")
        print("   2. Start the UI: cd netflix-movie-library-ui && npm run dev")
        print("   3. Access RedisInsight at: http://localhost:8001")
    else:
        print(" Some tests failed. Please check the setup.")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure Redis is running: docker-compose up -d redis")
        print("   2. Run database setup: python setup_redis_databases.py")
        print("   3. Run RedisSearch setup: python setup_redis_search.py")
        print("   4. Install Python dependencies: pip install -r requirements.txt")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
