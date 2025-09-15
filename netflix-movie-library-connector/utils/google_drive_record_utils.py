import json
import uuid
from typing import Dict, Any, Optional, List
from loguru import logger
import re
from utils.config import DOCUMENT_TYPE, CONTENT_TYPES
from services.google_drive_service import GoogleDriveService
from utils.google_drive_utils import parse_json_content, extract_text_from_json



def cleanse_record(
    file_data: Dict[str, Any],
    parsed_content: Optional[Dict[str, Any]] = None,
    record_type: str = "json_file",
    source: str = "google_drive"
) -> Dict[str, Any]:
    """
    Clean and normalize file data for indexing.
    
    Args:
        file_data: Raw file data from Google Drive
        parsed_content: Parsed content from file
        record_type: Type of document
        source: Source system
        
    Returns:
        Cleaned record dictionary
    """
    try:
        # Initialize movie data with default values
        movie_data = {
            "title": None,
            "imdb_rating": None,
            "language": None,
            "country": None,
            "stars": None,
            "director": None,
            "writer": None,
            "popu": None,
            "production_house": None,
            "movie": None,
            "movie_plot": None,
            "awards": None
        }
        
        # Extract basic file information
        file_id = file_data.get('id', '')
        file_name = file_data.get('name', 'Unknown')
        folder_path = file_data.get('folder_path', '')
        modified_time = file_data.get('modifiedTime', '')
        
        # Extract content and metadata
        content = ""
        title = file_name
        metadata = {}
        
        if parsed_content:
            content = parsed_content.get('extracted_text', '')
            title = parsed_content.get('title', file_name)
            metadata = parsed_content.get('metadata', {})
            
            # Update movie data from metadata
            if isinstance(metadata, dict):
                for key, value in metadata.items():
                    if key in movie_data and value:
                        # Convert arrays to strings for Redis Search compatibility
                        if key in ['stars', 'awards'] and isinstance(value, list):
                            movie_data[key] = ', '.join(str(item) for item in value)
                        else:
                            movie_data[key] = value
        
        # Extract genre, subgenre, and year from folder path only
        extracted_genre = extract_genre_from_path(folder_path)
        extracted_subgenre = extract_subgenre_from_path(folder_path)
        extracted_year = extract_year_from_path(folder_path)

        movie_title = movie_data["title"] or title

        # Use folder path extraction only (no JSON content for genre/subgenre/year)
        final_genre = extracted_genre
        final_subgenre = extracted_subgenre
        final_year = extracted_year

        print(f"Final Genre: {final_genre}, title: {movie_title}")
        
        
        return {
            "id": file_id,
            "title": movie_title,
            "content": content,
            "source": source,
            "content_type": CONTENT_TYPES.get("MOVIES", "movie"),
            "doc_type": DOCUMENT_TYPE.get("JSON_FILE", "json_file"),
            "file_name": file_name,
            "folder_path": folder_path,
            "modified_time": modified_time,
            "metadata": metadata,
            "url": f"https://drive.google.com/file/d/{file_id}/view",
            "genre": final_genre,
            "subgenre": final_subgenre,
            "year": final_year,
            "imdb_rating": movie_data["imdb_rating"],
            "language": movie_data["language"],
            "country": movie_data["country"],
            "stars": movie_data["stars"],
            "director": movie_data["director"],
            "writer": movie_data["writer"],
            "popu": movie_data["popu"],
            "production_house": movie_data["production_house"],
            "movie": movie_data["movie"],
            "movie_plot": movie_data["movie_plot"],
            "awards": movie_data["awards"],
        }
        
    except Exception as e:
        logger.error(f"Error cleansing record: {e}")
        return {}


def parse_file_content(drive_service: GoogleDriveService, file_data: Dict[str, Any], mime_type: str) -> Optional[Dict[str, Any]]:
    """
    Parse file content based on MIME type using utility functions.
    
    Args:
        file_data: File metadata from Google Drive
        mime_type: MIME type of the file
        
    Returns:
        Parsed content dictionary or None if failed
    """
    try:
        if mime_type == "application/json":
            # Get the actual file content from Google Drive            
            file_id = file_data.get('id')
            if file_id:
                # Download the file content
                file_content = drive_service.download_file_content(file_id)
                if file_content:
                    # Parse JSON content using utility function
                    json_data = parse_json_content(file_content)
                    if json_data:
                        # Print the JSON content to console
                        logger.info("📄 JSON File Content:")
                        logger.info("=" * 50)
                        logger.info(json.dumps(json_data, indent=2, ensure_ascii=False))
                        logger.info("=" * 50)
                        
                        # Extract text content using utility function
                        extracted_text = extract_text_from_json(json_data)
                        
                        return {
                            "extracted_text": extracted_text,
                            "title": file_data.get('name', 'Unknown'),
                            "metadata": json_data,
                            "raw_content": file_content
                        }
                else:
                    logger.error(f"Failed to download content for file: {file_data.get('name')}")
                    return None
            else:
                logger.error("No file ID found in file data")
                return None
        else:
            logger.warning(f"Unsupported MIME type: {mime_type}")
            return None
            
    except Exception as e:
        logger.error(f"Error parsing file content: {e}")
        return None


def extract_genre_from_path(folder_path: str) -> str:
    """Extract genre from folder path, ensuring it's not a digit."""
    if not folder_path:
        return 'unknown'
    
    # Split path and find first non-digit part as genre
    path_parts = folder_path.split('/')
    
    for part in path_parts:
        part = part.strip()
        if part and not part.isdigit() and not _is_year(part):
            return part
    
    return 'unknown'


def _is_year(text: str) -> bool:
    """Check if text is a year (4-digit number between 1900-2030)."""
    try:
        year = int(text)
        return 1900 <= year <= 2030
    except (ValueError, TypeError):
        return False


def extract_subgenre_from_path(folder_path: str) -> str:
    """Extract subgenre from folder path, ensuring it's not a digit."""
    if not folder_path:
        return 'unknown'
    
    # Split path and find second non-digit part as subgenre
    path_parts = folder_path.split('/')
    
    non_digit_parts = []
    for part in path_parts:
        part = part.strip()
        if part and not part.isdigit() and not _is_year(part):
            non_digit_parts.append(part)
    
    # Return second non-digit part as subgenre, or first if only one exists
    if len(non_digit_parts) >= 2:
        return non_digit_parts[1]
    elif len(non_digit_parts) == 1:
        return non_digit_parts[0]
    
    return 'unknown'


def extract_year_from_path(folder_path: str) -> int:
    """Extract year from folder path."""
    if not folder_path:
        return 0
    
    # Look for 4-digit year in path

    year_match = re.search(r'\b(19|20)\d{2}\b', folder_path)
    return int(year_match.group()) if year_match else 0


def validate_record(record: Dict[str, Any]) -> bool:
    """
    Validate that a record has required fields.
    
    Args:
        record: Record dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['id', 'title', 'file_id', 'source']
    
    for field in required_fields:
        if field not in record or not record[field]:
            logger.warning(f"Record missing required field: {field}")
            return False
    
    return True


def normalize_record_data(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize record data for consistent indexing.
    
    Args:
        record: Record dictionary to normalize
        
    Returns:
        Normalized record dictionary
    """
    try:
        # Normalize string fields
        string_fields = ['title', 'content', 'file_name', 'folder_path', 'genre', 'subgenre']
        for field in string_fields:
            if field in record and record[field]:
                record[field] = str(record[field]).strip()
        
        # Normalize numeric fields
        numeric_fields = ['year', 'imdb_rating', 'popu']
        for field in numeric_fields:
            if field in record and record[field]:
                try:
                    record[field] = float(record[field]) if '.' in str(record[field]) else int(record[field])
                except (ValueError, TypeError):
                    record[field] = 0
        
        # Normalize list fields
        list_fields = ['stars', 'director', 'writer', 'awards']
        for field in list_fields:
            if field in record and record[field]:
                if isinstance(record[field], str):
                    # Split by common delimiters
                    record[field] = [item.strip() for item in record[field].split(',') if item.strip()]
                elif not isinstance(record[field], list):
                    record[field] = [str(record[field])]
        
        return record
        
    except Exception as e:
        logger.error(f"Error normalizing record data: {e}")
        return record


def create_record_summary(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a summary of the record for logging/debugging.
    
    Args:
        record: Record dictionary
        
    Returns:
        Summary dictionary
    """
    return {
        "id": record.get('id', 'Unknown'),
        "title": record.get('title', 'Unknown'),
        "file_id": record.get('file_id', 'Unknown'),
        "genre": record.get('genre', 'Unknown'),
        "year": record.get('year', 0),
        "imdb_rating": record.get('imdb_rating', 0),
        "content_length": len(record.get('content', '')),
        "has_metadata": bool(record.get('metadata')),
        "source": record.get('source', 'Unknown')
    }
