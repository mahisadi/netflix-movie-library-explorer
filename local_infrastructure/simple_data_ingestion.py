#!/usr/bin/env python3
"""
Simple Data Ingestion Script
- Works directly with JSON data without Google Drive formatting
- Handles deduplication using title normalization
"""

import json
import sys
import os
from typing import Dict, Set, List

# Add the connector path to import modules
sys.path.append('netflix-movie-library-connector')

from services.redis_search_service import RedisSearchService

def normalize_title(title: str) -> str:
    """Create deduplication key from title."""
    return title.lower().replace(' ', '').replace(':', '').replace('-', '').replace('.', '').replace("'", '')

def cleanse_json_record(record: Dict) -> Dict:
    """Clean JSON record for Redis Search indexing."""
    cleaned = {}
    
    # Required fields with defaults
    cleaned['title'] = str(record.get('title', 'Unknown'))
    cleaned['year'] = str(record.get('year', 'Unknown'))
    cleaned['genre'] = str(record.get('genre', 'Unknown'))
    cleaned['rating'] = float(record.get('imdb_rating', 0.0))
    cleaned['language'] = str(record.get('language', 'Unknown'))
    cleaned['country'] = str(record.get('country', 'Unknown'))
    
    # Optional fields
    if 'sub-genre' in record:
        cleaned['sub_genre'] = str(record['sub-genre'])
    
    if 'stars' in record and record['stars']:
        if isinstance(record['stars'], list):
            cleaned['stars'] = ', '.join(str(star) for star in record['stars'])
        else:
            cleaned['stars'] = str(record['stars'])
    
    if 'director' in record:
        cleaned['director'] = str(record['director'])
    
    if 'awards' in record and record['awards']:
        if isinstance(record['awards'], list):
            cleaned['awards'] = ', '.join(str(award) for award in record['awards'])
        else:
            cleaned['awards'] = str(record['awards'])
    
    return cleaned

def fetch_existing_titles() -> Set[str]:
    """Fetch all existing movie titles from Redis Search."""
    print("🔍 Fetching existing movie titles from Redis Search...")
    
    try:
        search_service = RedisSearchService()
        documents = search_service.search("*", limit=1000)
        
        existing_titles = set()
        for doc in documents:
            title = doc.get('title', '')
            if title:
                normalized = normalize_title(title)
                existing_titles.add(normalized)
        
        print(f"✅ Found {len(existing_titles)} existing movies in Redis Search")
        return existing_titles
        
    except Exception as e:
        print(f"❌ Error fetching existing titles: {e}")
        return set()

def load_sample_data() -> List[Dict]:
    """Load sample data from JSON file."""
    print("📂 Loading sample data from JSON file...")
    
    try:
        with open('local_infrastructure/sample_data.json', 'r') as f:
            data = json.load(f)
        
        print(f"✅ Loaded {len(data)} records from sample_data.json")
        return data
        
    except Exception as e:
        print(f"❌ Error loading sample data: {e}")
        return []

def identify_new_records(sample_data: List[Dict], existing_titles: Set[str]) -> List[Dict]:
    """Identify records that don't exist in Redis."""
    print("🔍 Identifying new records...")
    
    new_records = []
    duplicate_count = 0
    
    for record in sample_data:
        title = record.get('title', '')
        if not title:
            continue
            
        normalized_title = normalize_title(title)
        
        if normalized_title not in existing_titles:
            new_records.append(record)
        else:
            duplicate_count += 1
    
    print(f"📊 Analysis Results:")
    print(f"   - Total sample records: {len(sample_data)}")
    print(f"   - Existing in Redis: {duplicate_count}")
    print(f"   - New records to ingest: {len(new_records)}")
    
    return new_records

def ingest_new_records(new_records: List[Dict]):
    """Ingest new records into Redis Search."""
    if not new_records:
        print("✅ No new records to ingest!")
        return
    
    print(f"🚀 Ingesting {len(new_records)} new records...")
    
    try:
        search_service = RedisSearchService()
        
        success_count = 0
        error_count = 0
        
        for i, record in enumerate(new_records, 1):
            try:
                # Clean the record for Redis Search
                cleansed_record = cleanse_json_record(record)
                
                # Generate document ID from title
                doc_id = f"movie:{normalize_title(record.get('title', 'unknown'))}"
                
                # Add to Redis Search
                search_service.add_document("movies", doc_id, cleansed_record)
                success_count += 1
                
                if i % 10 == 0:  # Progress update every 10 records
                    print(f"   📈 Progress: {i}/{len(new_records)} records processed")
                    
            except Exception as e:
                print(f"❌ Error ingesting record '{record.get('title', 'Unknown')}': {e}")
                error_count += 1
        
        print(f"🎉 Ingestion Complete!")
        print(f"   - Successfully ingested: {success_count}")
        print(f"   - Errors: {error_count}")
        
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")

def main():
    """Main execution function."""
    print("🎬 Simple Data Ingestion Script")
    print("=" * 50)
    
    # Step 1: Fetch existing titles
    existing_titles = fetch_existing_titles()
    
    # Step 2: Load sample data
    sample_data = load_sample_data()
    
    if not sample_data:
        print("❌ No sample data found!")
        return
    
    # Step 3: Identify new records
    new_records = identify_new_records(sample_data, existing_titles)
    
    # Step 4: Ingest new records
    ingest_new_records(new_records)
    
    print("\n✅ Simple ingestion completed!")

if __name__ == "__main__":
    main()
