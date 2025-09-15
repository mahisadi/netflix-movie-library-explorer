#!/usr/bin/env python3
"""
Ingest Clean Sample Data to Google Drive with Random Nested Structure

This script takes the cleaned sample_data.json and uploads it to Google Drive
with the structure: 1Z-Bqt69UgrGkwo0ArjHaNrA7uUmUm2r6/{genre}/{sub-genre}/{year}/{title}_{year}.json

The folder structure is randomized, and the JSON files don't contain genre/sub-genre/year info.
"""

import json
import os
import sys
import random
from pathlib import Path

# Add the connector directory to the path
connector_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "netflix-movie-library-connector")
sys.path.insert(0, connector_path)

from services.google_drive_service import GoogleDriveService

def normalize_title(title):
    """Normalize title for file naming."""
    if not title:
        return "unknown"
    
    # Remove special characters and normalize
    normalized = title.lower()
    normalized = normalized.replace(' ', '_')
    normalized = normalized.replace('-', '_')
    normalized = normalized.replace(':', '')
    normalized = normalized.replace('?', '')
    normalized = normalized.replace('!', '')
    normalized = normalized.replace('.', '')
    normalized = normalized.replace(',', '')
    normalized = normalized.replace("'", '')
    normalized = normalized.replace('"', '')
    normalized = normalized.replace('(', '')
    normalized = normalized.replace(')', '')
    normalized = normalized.replace('[', '')
    normalized = normalized.replace(']', '')
    normalized = normalized.replace('&', 'and')
    
    # Remove multiple underscores
    while '__' in normalized:
        normalized = normalized.replace('__', '_')
    
    # Remove leading/trailing underscores
    normalized = normalized.strip('_')
    
    return normalized

def load_sample_data():
    """Load the cleaned sample data."""
    with open('sample_data.json', 'r') as f:
        return json.load(f)

def get_existing_files(google_drive_service, target_folder_id):
    """Get existing files in the target folder to avoid duplicates."""
    try:
        files = google_drive_service.listfiles(target_folder_id)
        existing_titles = set()
        for file in files:
            # Extract title from filename (remove .json and year suffix)
            filename = file['name']
            if filename.endswith('.json'):
                # Remove .json extension and year suffix
                title_part = filename[:-5]  # Remove .json
                # Remove year suffix (last 4 digits)
                if title_part.endswith('_20') or title_part.endswith('_19'):
                    title_part = title_part[:-5]  # Remove _YYYY
                existing_titles.add(title_part.lower().replace(' ', '').replace('-', ''))
        return existing_titles
    except Exception as e:
        print(f"Warning: Could not fetch existing files: {e}")
        return set()

def create_nested_folder_structure(google_drive_service, target_folder_id, genre, subgenre, year):
    """Create random nested folder structure: {genre}/{sub-genre}/{year}/ or {year}/{sub-genre}/{genre}/ or {sub-genre}/{year}/{genre}/"""
    try:
        # Randomly choose folder structure pattern
        patterns = [
            [genre, subgenre, year],      # {genre}/{sub-genre}/{year}/
            [year, subgenre, genre],      # {year}/{sub-genre}/{genre}/
            [subgenre, year, genre]       # {sub-genre}/{year}/{genre}/
        ]
        
        # Randomly select a pattern
        selected_pattern = random.choice(patterns)
        folder_path = "/".join(selected_pattern)
        
        print(f"Using random pattern: {folder_path}")
        
        # Create nested folders based on selected pattern
        current_folder_id = target_folder_id
        
        for i, folder_name in enumerate(selected_pattern):
            # Find or create folder
            folder_id = google_drive_service.find_folder_by_name_in_parent(folder_name, current_folder_id)
            if not folder_id:
                folder_id = google_drive_service.create_folder(folder_name, current_folder_id)
                print(f"Created folder: {folder_name}")
            
            current_folder_id = folder_id
        
        print(f"Created complete folder structure: {folder_path}")
        return current_folder_id
        
    except Exception as e:
        print(f"Error creating folder structure for {genre}/{subgenre}/{year}: {e}")
        return None

def clean_movie_data(movie):
    """Remove genre, sub-genre, and year from movie data."""
    cleaned_movie = movie.copy()
    
    # Remove genre, sub-genre, and year fields
    cleaned_movie.pop('genre', None)
    cleaned_movie.pop('sub-genre', None)
    cleaned_movie.pop('year', None)
    
    return cleaned_movie

def upload_movies_to_google_drive():
    """Main function to upload movies to Google Drive."""
    print("🚀 Starting clean data ingestion to Google Drive...")
    
    # Initialize Google Drive service
    google_drive_service = GoogleDriveService()
    
    # Load sample data
    movies = load_sample_data()
    print(f"📊 Loaded {len(movies)} movies from sample_data.json")
    
    # Find target folder
    target_folder_id = google_drive_service.find_folder_by_name('1Z-Bqt69UgrGkwo0ArjHaNrA7uUmUm2r6')
    if not target_folder_id:
        print("❌ Target folder '1Z-Bqt69UgrGkwo0ArjHaNrA7uUmUm2r6' not found!")
        return
    
    print(f"📁 Found target folder: 1Z-Bqt69UgrGkwo0ArjHaNrA7uUmUm2r6 (ID: {target_folder_id})")
    
    # Get existing files to avoid duplicates
    existing_titles = get_existing_files(google_drive_service, target_folder_id)
    print(f"📋 Found {len(existing_titles)} existing files")
    
    # Process movies
    uploaded_count = 0
    skipped_count = 0
    error_count = 0
    
    for i, movie in enumerate(movies):
        try:
            title = movie['title']
            genre = movie['genre']
            subgenre = movie['sub-genre']
            year = movie['year']
            
            # Normalize title for duplicate check
            normalized_title = normalize_title(title)
            
            if normalized_title in existing_titles:
                print(f"⏭️  Skipping {title} (already exists)")
                skipped_count += 1
                continue
            
            # Create random folder structure
            folder_id = create_nested_folder_structure(
                google_drive_service, 
                target_folder_id, 
                genre, 
                subgenre, 
                year
            )
            
            if not folder_id:
                print(f"❌ Failed to create folder structure for {title}")
                error_count += 1
                continue
            
            # Clean movie data (remove genre, sub-genre, year)
            cleaned_movie = clean_movie_data(movie)
            
            # Create filename
            safe_title = normalize_title(title)
            filename = f"{safe_title}_{year}.json"
            
            # Upload file
            file_content = json.dumps(cleaned_movie, indent=2)
            upload_result = google_drive_service.upload_file(
                filename, 
                file_content, 
                folder_id
            )
            
            if upload_result:
                print(f"✅ Uploaded: {title} -> {genre}/{subgenre}/{year}/{filename}")
                uploaded_count += 1
            else:
                print(f"❌ Failed to upload: {title}")
                error_count += 1
                
        except Exception as e:
            print(f"❌ Error processing {movie.get('title', 'Unknown')}: {e}")
            error_count += 1
    
    print(f"\n🎉 Upload completed!")
    print(f"✅ Successfully uploaded: {uploaded_count}")
    print(f"⏭️  Skipped (duplicates): {skipped_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📊 Total processed: {len(movies)}")

if __name__ == "__main__":
    upload_movies_to_google_drive()
