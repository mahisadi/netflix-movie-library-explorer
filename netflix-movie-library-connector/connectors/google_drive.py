from typing import List, Optional
from services.google_drive_service import GoogleDriveService
from services.redis_search_service import RedisSearchService
from utils.config import DEFAULT_FILE_TYPES, DOCUMENT_SOURCES, DOCUMENT_TYPE, GOOGLE_DRIVE_FOLDER_NAME
from loguru import logger
from utils.google_drive_record_utils import (
    cleanse_record,
    parse_file_content
)

class GoogleDriveConnector:
    """Fetch files from Google Drive and index them into RedisSearch."""

    def __init__(self):
            self.drive_service = GoogleDriveService()
            self.redis_service = RedisSearchService()
            

    def _prepare_redis_service(self, recreate_index: bool):
        # Create RedisSearch index (only if it doesn't exist)
        if recreate_index:
            logger.info("🔄 Recreating RedisSearch index...")
            if self.redis_service.create_index():
                logger.info("RedisSearch index recreated successfully")
            else:
                logger.error("Failed to recreate RedisSearch index")
                return
        else:
            logger.info("Checking RedisSearch index...")
            if self.redis_service.create_index():
                logger.info("RedisSearch index is ready")
            else:
                logger.error("Failed to create RedisSearch index")
                return
         

    def fetch(self, folder_name: str = None, file_types: Optional[List[str]] = None, recreate_index: bool = False):
        try:
            # Check if Google Drive service is properly authenticated
            if not self.drive_service.is_authenticated():
                logger.error(" Google Drive service authentication failed. Please check your credentials.")
                return
            
            # Set default file types to JSON only
            if file_types is None:
                file_types = ["application/json"]
            
            # Use default folder ID if not provided
            if folder_name is None:
                folder_name = GOOGLE_DRIVE_FOLDER_NAME
            
            logger.info(f"Starting Google Drive file fetch for folder: {folder_name}")
            logger.info(f"File types: {file_types}")
        
            self._prepare_redis_service(recreate_index)

            # Get files from Google Drive
            files = self.drive_service.listfiles(
                folder_name=folder_name
            )
            
            logger.info(f"Found {len(files)} files to process")
            
            if not files:
                logger.info("No files found to fetch")
                return
            
            # Process files and prepare for indexing
            processed_records = []
            
            for file_data in files:
                try:
                    mime_type = file_data.get('mimeType', '')
                    
                    # Only process JSON files
                    if mime_type != "application/json":
                        logger.warning(f"Skipping non-JSON file: {file_data.get('name', 'Unknown')}")
                        continue
                    
                    # Parse file content
                    parsed_content = parse_file_content(self.drive_service, file_data, mime_type)
                    
                    # Clean and normalize data
                    clean_record = cleanse_record(file_data, parsed_content)
                    
                    if clean_record:
                        processed_records.append(clean_record)
                    
                except Exception as e:
                    logger.error(f"Error processing file {file_data.get('name', 'Unknown')}: {e}")
                    continue
            
            # Index all processed records into RedisSearch
            if processed_records:
                logger.info(f"Indexing {len(processed_records)} records into RedisSearch...")
                indexed_count = self.redis_service.index_batch(processed_records)
                
                if indexed_count > 0:
                    logger.info(f"Successfully indexed {indexed_count} records into RedisSearch")
                    
                    # Get index statistics
                    doc_count = self.redis_service.get_document_count()
                    logger.info(f"Total documents in RedisSearch: {doc_count}")
                else:
                    logger.error("Failed to index records into RedisSearch")
            else:
                logger.warning("No records to index")
            
            logger.info(f"Sync completed. Processed {len(processed_records)} JSON files")
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            raise