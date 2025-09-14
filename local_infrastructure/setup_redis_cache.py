import redis
import sys
import os

def setup_redis_databases():
    """Setup Redis databases with proper structure"""
    
    # Redis connection settings
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    
    try:
        print(" Setting up Redis databases...")
        
        # Clear all databases first
        print(" Clearing all databases...")
        try:
            redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                db=0,
                decode_responses=True
            )
            redis_client.ping()
            key_count = redis_client.dbsize()
            if key_count > 0:
                redis_client.flushdb()
                print(f" Cleared Redis Search DB : {key_count} keys")
        except:
                pass
                
        # Setup RedisSearch (Movie data)
        print("\n Setting up DB - RedisSearch (Movie data)...")
        db_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=0,
            decode_responses=True
        )
        db_client.ping()
        print("connected")
   
        # Verify the setup
        print("\n Verifying database setup...")
        
        # Check DB 0
        db_keys = db_client.dbsize()
        print(f" RedisSearch: {db_keys} keys")
        
        
        print(" Redis database setup complete!")
        
    except Exception as e:
        print(f" Error setting up Redis databases: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("\n Redis Database Setup")
    setup_redis_databases()
    print("\n Database setup complete!")
