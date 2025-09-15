#!/usr/bin/env python3
"""
Setup RedisSearch Index for Netflix Movie Library Explorer
This script creates the RedisSearch index with proper schema for movie data.
"""

import redis
import sys
import os

def setup_redis_search():
    """Setup RedisSearch index with movie schema"""
    
    # Redis connection settings
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    REDIS_DB = int(os.getenv('REDIS_DB', '0'))
    
    try:
        print("🔍 Setting up RedisSearch index for Netflix Movie Library Explorer...")
        
        # Connect to Redis DB 0 (Search Data)
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=REDIS_DB,
            decode_responses=True
        )
        
        # Test connection
        redis_client.ping()
        print(f"✅ Connected to Redis at {REDIS_HOST}:{REDIS_PORT} (DB {REDIS_DB})")
        
        # Check if RedisSearch module is loaded
        try:
            modules = redis_client.execute_command("MODULE", "LIST")
            redissearch_loaded = any("search" in str(module).lower() for module in modules)
            
            if not redissearch_loaded:
                print("❌ RedisSearch module not loaded. Please use redis/redis-stack image.")
                sys.exit(1)
            
            print("✅ RedisSearch module is loaded")
        except Exception as e:
            print(f"⚠️  Could not check RedisSearch module: {e}")
        
        # Index name
        index_name = "movie_library"
        
        # Check if index already exists
        try:
            redis_client.execute_command("FT.INFO", index_name)
            print(f"ℹ️  Index '{index_name}' already exists")
            
            # Ask if user wants to recreate it
            response = input("Do you want to recreate the index? (y/N): ").strip().lower()
            if response == 'y':
                print("🗑️  Dropping existing index...")
                redis_client.execute_command("FT.DROPINDEX", index_name, "DD")
                print("✅ Existing index dropped")
            else:
                print("✅ Using existing index")
                return
        except:
            # Index doesn't exist, continue with creation
            pass
        
        # Create the RedisSearch index
        print(f"📊 Creating RedisSearch index: {index_name}")
        
        # Define the enhanced schema for movie data
        schema_definition = [
            # SEARCHABLE FIELDS (TEXT with weights)
            "title", "TEXT", "WEIGHT", "5.0",
            "stars", "TEXT", "WEIGHT", "3.0", 
            "country", "TEXT", "WEIGHT", "2.0",
            "director", "TEXT", "WEIGHT", "3.0",
            "writer", "TEXT", "WEIGHT", "2.0",
            "movie_plot", "TEXT", "WEIGHT", "1.0",
            "awards", "TEXT", "WEIGHT", "1.0",
            "content", "TEXT", "WEIGHT", "1.0",
            
            # FACETED FIELDS (TAG for filtering and faceting)
            "genre", "TAG",
            "subgenre", "TAG", 
            "language", "TAG",
            "production_house", "TAG",
            "source", "TAG",
            
            # SORTABLE AND FILTERABLE FIELDS (NUMERIC with SORTABLE)
            "year", "NUMERIC", "SORTABLE",
            "imdb_rating", "NUMERIC", "SORTABLE",
            "popu", "NUMERIC", "SORTABLE",
            
            # SORTABLE AND FILTERABLE FIELDS (TEXT with SORTABLE)
            "modified_time", "TEXT", "SORTABLE",
            
            # PRIMARY KEY FIELD (used as Redis key for uniqueness)
            "file_id", "TEXT", "WEIGHT", "10.0", "SORTABLE",
            
            # REGULAR FIELDS (TEXT without special attributes)
            "folder_path", "TEXT",
            "file_name", "TEXT",
            "url", "TEXT"
        ]
        
        # Create the index using raw Redis command
        result = redis_client.execute_command(
            "FT.CREATE", index_name,
            "ON", "HASH",
            "PREFIX", "1", "movie:",
            "LANGUAGE", "english",
            "SCHEMA", *schema_definition
        )
        
        print(f"✅ Created RedisSearch index: {index_name}")
        
        # Verify the index was created
        try:
            info = redis_client.execute_command("FT.INFO", index_name)
            print("\n📋 Index Information:")
            
            # Convert the list response to a dictionary for better display
            info_dict = {}
            for i in range(0, len(info), 2):
                if i + 1 < len(info):
                    info_dict[info[i]] = info[i + 1]
            
            # Display key information
            key_fields = [
                "index_name", "num_docs", "num_fields", "inverted_sz_mb", 
                "doc_table_size_mb", "indexing"
            ]
            
            for field in key_fields:
                if field in info_dict:
                    print(f"   {field}: {info_dict[field]}")
            
        except Exception as e:
            print(f"⚠️  Could not retrieve index info: {e}")
        
        print("\n✅ RedisSearch setup complete!")
        print("   🎬 Ready for movie data indexing")
        print("   🔍 Search functionality available")
        print("   📊 Faceted search and filtering enabled")
        
    except Exception as e:
        print(f"❌ Error setting up RedisSearch: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🔍 RedisSearch Setup for Netflix Movie Library Explorer")
    print("=" * 55)
    setup_redis_search()
    print("\n🎬 RedisSearch setup complete!")
