#!/usr/bin/env python3
"""
Ingest Sample Data to Google Drive with Nested Directory Structure
- Creates nested folders: {genre}/{sub-genre}/{year}/
- Saves movies as JSON files: {title}_{year}.json
- Handles deduplication by checking existing files
"""

import json
import sys
import os
import random
from typing import Dict, List, Set

# Add the connector path to import modules
sys.path.append('netflix-movie-library-connector')

from services.google_drive_service import GoogleDriveService

def normalize_title(title: str) -> str:
    """Create normalized title for file naming."""
    return title.lower().replace(' ', '_').replace(':', '').replace('-', '_').replace('.', '').replace("'", '')

def get_existing_files(google_drive_service: GoogleDriveService, target_folder_id: str) -> Set[str]:
    """Get list of existing movie files in the target folder."""
    print("🔍 Checking existing files in Google Drive...")
    
    try:
        # Get all files in the target folder and subfolders
        existing_files = set()
        
        # List all files in the target folder using the correct method
        files = google_drive_service.listfiles(include_nested=True, file_types=['.json'])
        
        for file in files:
            if file.get('name', '').endswith('.json'):
                # Extract title from filename (remove .json and year suffix)
                filename = file['name'].replace('.json', '')
                # Remove year suffix if present (e.g., "_1941")
                if '_' in filename:
                    parts = filename.split('_')
                    if parts[-1].isdigit():
                        filename = '_'.join(parts[:-1])
                existing_files.add(filename.lower())
        
        print(f"✅ Found {len(existing_files)} existing movie files")
        return existing_files
        
    except Exception as e:
        print(f"❌ Error checking existing files: {e}")
        return set()

def create_nested_folder_structure(google_drive_service: GoogleDriveService, target_folder_id: str, genre: str, sub_genre: str, year: str) -> str:
    """Create nested folder structure: genre/sub-genre/year/"""
    try:
        # Create genre folder
        genre_folder_id = google_drive_service.find_folder_by_name_in_parent(genre, target_folder_id)
        if not genre_folder_id:
            genre_folder_id = google_drive_service.create_folder(genre, target_folder_id)
        
        # Create sub-genre folder inside genre
        sub_genre_folder_id = google_drive_service.find_folder_by_name_in_parent(sub_genre, genre_folder_id)
        if not sub_genre_folder_id:
            sub_genre_folder_id = google_drive_service.create_folder(sub_genre, genre_folder_id)
        
        # Create year folder inside sub-genre
        year_folder_id = google_drive_service.find_folder_by_name_in_parent(year, sub_genre_folder_id)
        if not year_folder_id:
            year_folder_id = google_drive_service.create_folder(year, sub_genre_folder_id)
        
        return year_folder_id
        
    except Exception as e:
        print(f"❌ Error creating nested folder structure: {e}")
        return None

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

def identify_new_movies(sample_data: List[Dict], existing_files: Set[str]) -> List[Dict]:
    """Identify movies that don't exist in Google Drive."""
    print("🔍 Identifying new movies...")
    
    new_movies = []
    duplicate_count = 0
    
    for movie in sample_data:
        title = movie.get('title', '')
        if not title:
            continue
            
        normalized_title = normalize_title(title)
        
        if normalized_title not in existing_files:
            new_movies.append(movie)
        else:
            duplicate_count += 1
    
    print(f"📊 Analysis Results:")
    print(f"   - Total sample movies: {len(sample_data)}")
    print(f"   - Existing in Google Drive: {duplicate_count}")
    print(f"   - New movies to upload: {len(new_movies)}")
    
    return new_movies

def upload_movies_to_google_drive(new_movies: List[Dict], google_drive_service: GoogleDriveService, target_folder_id: str):
    """Upload new movies to Google Drive with nested structure."""
    if not new_movies:
        print("✅ No new movies to upload!")
        return
    
    print(f"🚀 Uploading {len(new_movies)} new movies to Google Drive...")
    
    success_count = 0
    error_count = 0
    
    for i, movie in enumerate(new_movies, 1):
        try:
            title = movie.get('title', 'Unknown')
            year = movie.get('year', 'Unknown')
            genre = movie.get('genre', 'Unknown')
            sub_genre = movie.get('sub-genre', 'Unknown')
            
            # Create nested folder structure
            folder_id = create_nested_folder_structure(google_drive_service, target_folder_id, genre, sub_genre, year)
            
            if not folder_id:
                print(f"❌ Failed to create folder structure for '{title}'")
                error_count += 1
                continue
            
            # Create filename
            filename = f"{title}_{year}.json"
            
            # Convert movie data to JSON string
            movie_json = json.dumps(movie, indent=2)
            
            # Upload file to Google Drive using the correct method
            google_drive_service.upload_file(filename, movie_json, folder_id)
            
            success_count += 1
            
            if i % 10 == 0:  # Progress update every 10 movies
                print(f"   📈 Progress: {i}/{len(new_movies)} movies uploaded")
                
        except Exception as e:
            print(f"❌ Error uploading movie '{title}': {e}")
            error_count += 1
    
    print(f"🎉 Upload Complete!")
    print(f"   - Successfully uploaded: {success_count}")
    print(f"   - Errors: {error_count}")

def main():
    """Main execution function."""
    print("🎬 Sample Data to Google Drive Ingestion")
    print("=" * 50)
    
    # Target folder ID (the main folder where we'll create nested structure)
    TARGET_FOLDER_ID = "1Z-Bqt69UgrGkwo0ArjHaNrA7uUmUm2r6"
    
    try:
        # Initialize Google Drive service
        print("🔧 Initializing Google Drive service...")
        google_drive_service = GoogleDriveService()
        
        # Step 1: Load sample data
        sample_data = load_sample_data()
        
        if not sample_data:
            print("❌ No sample data found!")
            return
        
        # Step 2: Check existing files
        existing_files = get_existing_files(google_drive_service, TARGET_FOLDER_ID)
        
        # Step 3: Identify new movies
        new_movies = identify_new_movies(sample_data, existing_files)
        
        # Step 4: Upload new movies
        upload_movies_to_google_drive(new_movies, google_drive_service, TARGET_FOLDER_ID)
        
        print("\n✅ Sample data ingestion to Google Drive completed!")
        print(f"📁 Target folder: {TARGET_FOLDER_ID}")
        print("🔄 Next step: Run the connector to ingest from Google Drive to Redis")
        
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")

if __name__ == "__main__":
    main()
