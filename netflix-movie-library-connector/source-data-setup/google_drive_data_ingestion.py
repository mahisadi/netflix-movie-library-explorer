#!/usr/bin/env python3
"""
Google Drive Data Ingestion Script
Reads sample_data.json and ingests records into Google Drive with nested folder structure.
Each record gets a random folder hierarchy: {genre}/{sub-genre}/{year} or {year}/{genre}/{sub-genre}, etc.
"""

import os
import sys
import json
import random
from typing import List, Dict, Any, Optional
from loguru import logger

# Add the connector path to sys.path to import the services
connector_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, connector_path)

from services.google_drive_service import GoogleDriveService

class GoogleDriveDataIngestion:
    """Handles ingestion of movie data into Google Drive with nested folder structure."""
    
    def __init__(self):
        """Initialize the Google Drive service."""
        self.drive_service = GoogleDriveService()
        self.root_folder_name = "1Z-Bqt69UgrGkwo0ArjHaNrA7uUmUm2r6"
        self.root_folder_id = None
        
    def is_authenticated(self) -> bool:
        """Check if Google Drive service is authenticated."""
        return self.drive_service.is_authenticated()
    
    def ensure_root_folder_exists(self) -> None:
        """Ensure the root folder exists and get its ID."""
        try:
            # Find existing root folder
            self.root_folder_id = self.drive_service.find_folder_by_name(self.root_folder_name)
            
            if self.root_folder_id:
                logger.info(f"Found existing root folder '{self.root_folder_name}' with ID: {self.root_folder_id}")
            else:
                # Create root folder if it doesn't exist
                logger.info(f"Creating root folder '{self.root_folder_name}'...")
                self.root_folder_id = self.drive_service.create_folder(self.root_folder_name, None)
                
                if self.root_folder_id:
                    logger.info(f"Created root folder '{self.root_folder_name}' with ID: {self.root_folder_id}")
                else:
                    raise Exception(f"Failed to create root folder '{self.root_folder_name}'")
                
        except Exception as e:
            logger.error(f"Error ensuring root folder exists: {e}")
            raise
    
    def read_sample_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Read sample data from JSON file."""
        try:
            if not os.path.exists(file_path):
                logger.error(f"Sample data file not found: {file_path}")
                return []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Successfully read {len(data)} records from {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Error reading sample data: {e}")
            return []
    
    def get_folder_structure(self, record: Dict[str, Any]) -> List[str]:
        """
        Generate random folder structure for a record.
        Returns a list of folder names in random order.
        """
        components = []
        
        # Add genre if available
        genre = record.get('genre')
        if genre and genre.strip():
            components.append(genre.strip())
        
        # Add sub-genre if available
        sub_genre = record.get('sub-genre')
        if sub_genre and sub_genre.strip():
            components.append(sub_genre.strip())
        
        # Add year if available
        year = record.get('year')
        if year and str(year).strip():
            components.append(str(year).strip())
        
        # Shuffle the components to create random folder structure
        random.shuffle(components)
        
        return components
    
    def create_nested_folders(self, folder_components: List[str], parent_id: str) -> str:
        """
        Create nested folder structure and return the final folder ID.
        """
        current_parent_id = parent_id
        
        for folder_name in folder_components:
            try:
                # Check if folder already exists in current parent
                existing_folder_id = self.drive_service.find_folder_by_name_in_parent(folder_name, current_parent_id)
                
                if existing_folder_id:
                    logger.info(f"Folder '{folder_name}' already exists with ID: {existing_folder_id}")
                    current_parent_id = existing_folder_id
                else:
                    # Create new folder
                    new_folder_id = self.drive_service.create_folder(folder_name, current_parent_id)
                    
                    if new_folder_id:
                        logger.info(f"Created folder '{folder_name}' with ID: {new_folder_id}")
                        current_parent_id = new_folder_id
                    else:
                        logger.error(f"Failed to create folder '{folder_name}'")
                        raise Exception(f"Failed to create folder '{folder_name}'")
                        
            except Exception as e:
                logger.error(f"Error creating folder '{folder_name}': {e}")
                raise
        
        return current_parent_id
    
    def get_filename(self, record: Dict[str, Any]) -> str:
        """Generate filename for a record."""
        title = record.get('title', 'Unknown')
        year = record.get('year', 'Unknown')
        
        # Clean title for filename (remove special characters)
        clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_title = clean_title.replace(' ', '_')
        
        return f"{clean_title}_{year}.json"
    
    def upload_record_as_json(self, record: Dict[str, Any], folder_id: str) -> Optional[str]:
        """Upload a record as a JSON file to the specified folder."""
        try:
            # Create filename: {title}_{year}.json
            filename = self.get_filename(record)
            
            # Convert record to JSON string
            json_content = json.dumps(record, indent=2, ensure_ascii=False)
            
            # Upload file
            file_id = self.drive_service.upload_file(filename, json_content, folder_id)
            
            if file_id:
                logger.info(f"Uploaded '{filename}' with ID: {file_id}")
                return file_id
            else:
                logger.error(f"Failed to upload '{filename}'")
                return None
                
        except Exception as e:
            logger.error(f"Error uploading record as JSON: {e}")
            return None
    
    def ingest_data(self, sample_data_path: str) -> Dict[str, Any]:
        """
        Main method to ingest sample data into Google Drive.
        Returns summary of the ingestion process.
        """
        try:
            # Check authentication
            if not self.is_authenticated():
                logger.error("Google Drive service is not authenticated")
                return {"success": False, "error": "Authentication failed"}
            
            # Ensure root folder exists
            self.ensure_root_folder_exists()
            
            # Read sample data
            records = self.read_sample_data(sample_data_path)
            
            if not records:
                logger.warning("No records found in sample data")
                return {"success": False, "error": "No records found"}
            
            # Statistics
            stats = {
                "total_records": len(records),
                "successful_uploads": 0,
                "failed_uploads": 0,
                "created_folders": set(),
                "uploaded_files": []
            }
            
            logger.info(f"Starting ingestion of {len(records)} records...")
            
            # Process each record
            for i, record in enumerate(records, 1):
                try:
                    logger.info(f"Processing record {i}/{len(records)}: {record.get('title', 'Unknown')}")
                    
                    # Get random folder structure for this record
                    folder_components = self.get_folder_structure(record)
                    logger.info(f"Folder structure: {'/'.join(folder_components)}")
                    
                    # Create nested folders
                    final_folder_id = self.create_nested_folders(
                        folder_components, self.root_folder_id
                    )
                    
                    # Track created folders
                    folder_path = f"{self.root_folder_name}/{'/'.join(folder_components)}"
                    stats["created_folders"].add(folder_path)
                    
                    # Upload record as JSON file INSIDE the nested folder structure
                    file_id = self.upload_record_as_json(record, final_folder_id)
                    
                    if file_id:
                        stats["successful_uploads"] += 1
                        stats["uploaded_files"].append({
                            "title": record.get('title'),
                            "year": record.get('year'),
                            "file_id": file_id,
                            "folder_path": folder_path,
                            "file_location": f"{folder_path}/{self.get_filename(record)}"
                        })
                    else:
                        stats["failed_uploads"] += 1
                    
                    logger.info(f"Completed record {i}/{len(records)}")
                    
                except Exception as e:
                    logger.error(f"Error processing record {i}: {e}")
                    stats["failed_uploads"] += 1
                    continue
            
            # Convert set to list for JSON serialization
            stats["created_folders"] = list(stats["created_folders"])
            
            # Log summary
            logger.info("=" * 60)
            logger.info("INGESTION SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Total records processed: {stats['total_records']}")
            logger.info(f"Successful uploads: {stats['successful_uploads']}")
            logger.info(f"Failed uploads: {stats['failed_uploads']}")
            logger.info(f"Unique folder paths created: {len(stats['created_folders'])}")
            logger.info("=" * 60)
            
            return {
                "success": True,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            return {"success": False, "error": str(e)}

def main():
    """Main function to run the data ingestion."""
    logger.info("🚀 Starting Google Drive Data Ingestion")
    logger.info("=" * 60)
    
    # Initialize ingestion service
    ingestion = GoogleDriveDataIngestion()
    
    # Check authentication
    if not ingestion.is_authenticated():
        logger.error("❌ Google Drive authentication failed")
        logger.error("Please ensure your Google Drive credentials are properly configured")
        return
    
    logger.info("✅ Google Drive authentication successful")
    
    # Find sample data file
    sample_data_path = "sample_data.json"  # Look in current directory (source-data-setup)
    
    if not os.path.exists(sample_data_path):
        logger.error(f"❌ Sample data file not found: {sample_data_path}")
        return
    
    logger.info(f"📁 Found sample data file: {sample_data_path}")
    
    # Run ingestion
    result = ingestion.ingest_data(sample_data_path)
    
    if result["success"]:
        logger.info("🎉 Data ingestion completed successfully!")
        
        # Save detailed results to file
        results_file = "ingestion_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info(f"📊 Detailed results saved to: {results_file}")
        
    else:
        logger.error(f"❌ Data ingestion failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
