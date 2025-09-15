#!/usr/bin/env python3
"""
Complete Redis System Setup for Netflix Movie Library Explorer
This script sets up the entire Redis infrastructure including databases, indexes, and services.
"""

import subprocess
import sys
import os
import time
from typing import List, Tuple

def run_command(command: str, description: str) -> Tuple[bool, str]:
    """Run a command and return success status and output."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            print(f"   ✅ {description} completed successfully")
            return True, result.stdout
        else:
            print(f"   ❌ {description} failed: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"   ❌ {description} failed with exception: {e}")
        return False, str(e)

def check_docker_running() -> bool:
    """Check if Docker is running."""
    print("🐳 Checking Docker status...")
    success, output = run_command("docker --version", "Docker version check")
    if not success:
        print("   ❌ Docker is not installed or not running")
        return False
    
    success, output = run_command("docker ps", "Docker daemon check")
    if not success:
        print("   ❌ Docker daemon is not running")
        return False
    
    print("   ✅ Docker is running")
    return True

def start_redis_container() -> bool:
    """Start Redis container using Docker Compose."""
    print("🚀 Starting Redis container...")
    
    # Check if container is already running
    success, output = run_command("docker ps --filter name=redis-movie-explorer", "Check existing Redis container")
    if success and "redis-movie-explorer" in output:
        print("   ✅ Redis container is already running")
        return True
    
    # Start Redis container
    success, output = run_command("docker-compose -f local_infrastructure/docker-compose.yml up -d redis", "Start Redis container")
    if not success:
        print("   ❌ Failed to start Redis container")
        return False
    
    # Wait for Redis to be ready
    print("   ⏳ Waiting for Redis to be ready...")
    for i in range(30):  # Wait up to 30 seconds
        success, output = run_command("docker exec redis-movie-explorer redis-cli ping", "Test Redis connection")
        if success and "PONG" in output:
            print("   ✅ Redis is ready")
            return True
        time.sleep(1)
    
    print("   ❌ Redis failed to start within 30 seconds")
    return False

def install_python_dependencies() -> bool:
    """Install Python dependencies."""
    print("📦 Installing Python dependencies...")
    success, output = run_command("pip install -r requirements.txt", "Install Python dependencies")
    return success

def setup_redis_databases() -> bool:
    """Set up Redis databases."""
    print("🗄️  Setting up Redis databases...")
    success, output = run_command("python setup_redis_databases.py", "Setup Redis databases")
    return success

def setup_redis_search() -> bool:
    """Set up RedisSearch index."""
    print("🔍 Setting up RedisSearch index...")
    success, output = run_command("python setup_redis_search.py", "Setup RedisSearch index")
    return success

def test_redis_setup() -> bool:
    """Test the Redis setup."""
    print("🧪 Testing Redis setup...")
    success, output = run_command("python test_redis_setup.py", "Test Redis setup")
    return success

def start_api_service() -> bool:
    """Start the API service."""
    print("🌐 Starting API service...")
    print("   💡 Starting API service in background...")
    print("   💡 You can stop it later with: pkill -f 'python.*run_api_service.py'")
    
    # Start API service in background
    try:
        subprocess.Popen([
            sys.executable, "run_api_service.py"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait a moment for the service to start
        time.sleep(3)
        
        # Test if the service is running
        success, output = run_command("curl -s http://localhost:8000/health", "Test API service health")
        if success and "healthy" in output:
            print("   ✅ API service is running")
            return True
        else:
            print("   ⚠️  API service may not be ready yet")
            return False
    except Exception as e:
        print(f"   ❌ Failed to start API service: {e}")
        return False

def main():
    """Main setup function."""
    print("🎬 Complete Redis System Setup for Netflix Movie Library Explorer")
    print("=" * 70)
    
    # Check prerequisites
    if not check_docker_running():
        print("\n❌ Setup failed: Docker is required but not running")
        print("   Please install Docker and start the Docker daemon")
        return False
    
    # Step 1: Start Redis container
    if not start_redis_container():
        print("\n❌ Setup failed: Could not start Redis container")
        return False
    
    # Step 2: Install Python dependencies
    if not install_python_dependencies():
        print("\n❌ Setup failed: Could not install Python dependencies")
        return False
    
    # Step 3: Set up Redis databases
    if not setup_redis_databases():
        print("\n❌ Setup failed: Could not set up Redis databases")
        return False
    
    # Step 4: Set up RedisSearch index
    if not setup_redis_search():
        print("\n❌ Setup failed: Could not set up RedisSearch index")
        return False
    
    # Step 5: Test the setup
    if not test_redis_setup():
        print("\n⚠️  Setup completed with warnings: Some tests failed")
        print("   The system may still work, but please check the test output")
    else:
        print("\n✅ All tests passed!")
    
    # Step 6: Start API service
    api_started = start_api_service()
    
    # Summary
    print("\n" + "=" * 70)
    print("🎉 Redis system setup completed!")
    print("\n📋 What was set up:")
    print("   ✅ Redis container with Redis Stack")
    print("   ✅ 6 Redis databases (Search, Analytics, Operations, Cache, Metrics, Logs)")
    print("   ✅ RedisSearch index for movie data")
    print("   ✅ Python dependencies installed")
    print("   ✅ Backend services configured")
    
    if api_started:
        print("   ✅ API service started")
    
    print("\n🌐 Access points:")
    print("   • RedisInsight: http://localhost:8001")
    print("   • API Documentation: http://localhost:8000/docs")
    print("   • API Health Check: http://localhost:8000/health")
    print("   • GraphQL Playground: http://localhost:8000/graphql")
    
    print("\n🚀 Next steps:")
    print("   1. Start the UI: cd netflix-movie-library-ui && npm run dev")
    print("   2. Access the application at: http://localhost:5173")
    print("   3. Monitor Redis with RedisInsight: http://localhost:8001")
    
    print("\n🔧 Management commands:")
    print("   • Stop Redis: docker-compose -f local_infrastructure/docker-compose.yml down")
    print("   • Stop API: pkill -f 'python.*run_api_service.py'")
    print("   • Test setup: python test_redis_setup.py")
    print("   • View logs: docker logs redis-movie-explorer")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
