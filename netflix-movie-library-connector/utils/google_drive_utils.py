import os
import json
import re
import pickle
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from loguru import logger


def get_nested_files_with_types(service, folder_id: str, file_types: List[str] = None, 
                               since: Optional[str] = None, page_size: int = 100, 
                               max_depth: int = 10, current_depth: int = 0, 
                               current_path: str = "") -> List[Dict[str, Any]]:
    """
    Recursively get files from Google Drive folder with specified types.
    
    Args:
        service: Google Drive API service instance
        folder_id: Google Drive folder ID
        file_types: List of MIME types to filter
        since: Only get files modified since this date
        page_size: Number of files per page
        max_depth: Maximum recursion depth
        current_depth: Current recursion depth
        current_path: Current folder path
        
    Returns:
        List of file dictionaries with metadata
    """
    try:
        if current_depth >= max_depth:
            logger.warning(f"Maximum depth {max_depth} reached for path: {current_path}")
            return []
        
        files = []
        page_token = None
        
        while True:
            # Build query for files in folder
            query = f"'{folder_id}' in parents and trashed=false"
            if since:
                query += f" and modifiedTime > '{since}'"
            
            # Get files from current folder
            results = service.files().list(
                q=query,
                pageSize=page_size,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, parents)",
                pageToken=page_token
            ).execute()
            
            items = results.get('files', [])
            
            for item in items:
                file_id = item['id']
                file_name = item['name']
                mime_type = item.get('mimeType', '')
                
                # Check if it's a folder
                if mime_type == 'application/vnd.google-apps.folder':
                    # Recursively get files from subfolder
                    subfolder_path = f"{current_path}/{file_name}" if current_path else file_name
                    subfolder_files = get_nested_files_with_types(
                        service, file_id, file_types, since, page_size, 
                        max_depth, current_depth + 1, subfolder_path
                    )
                    files.extend(subfolder_files)
                else:
                    # Check if file type matches filter
                    if not file_types or mime_type in file_types:
                        # Add metadata to file
                        item['folder_path'] = current_path
                        item['extracted_genre'] = extract_genre_from_path(current_path)
                        item['extracted_subgenre'] = extract_subgenre_from_path(current_path)
                        item['extracted_year'] = extract_year_from_path(current_path)
                        files.append(item)
            
            page_token = results.get('nextPageToken')
            if not page_token:
                break
                
        return files
        
    except Exception as e:
        logger.error(f"Error getting nested files: {e}")
        return []


def extract_genre_from_path(folder_path: str) -> str:
    """Extract genre from folder path."""
    if not folder_path:
        return 'unknown'
    
    # Split path and get first part as genre
    path_parts = folder_path.split('/')
    return path_parts[0] if path_parts else 'unknown'


def extract_subgenre_from_path(folder_path: str) -> str:
    """Extract subgenre from folder path."""
    if not folder_path:
        return 'unknown'
    
    # Split path and get second part as subgenre
    path_parts = folder_path.split('/')
    return path_parts[1] if len(path_parts) > 1 else 'unknown'


def extract_year_from_path(folder_path: str) -> int:
    """Extract year from folder path."""
    if not folder_path:
        return 0
    
    year_match = re.search(r'\b(19|20)\d{2}\b', folder_path)
    return int(year_match.group()) if year_match else 0


def download_file_content(service, file_id: str) -> Optional[str]:
    """
    Download file content from Google Drive.
    
    Args:
        service: Google Drive API service instance
        file_id: Google Drive file ID
        
    Returns:
        File content as string, or None if failed
    """
    try:
        request = service.files().get_media(fileId=file_id)
        content = request.execute()
        
        # Decode content if it's bytes
        if isinstance(content, bytes):
            content = content.decode('utf-8')
            
        logger.debug(f"Downloaded content for file ID: {file_id}")
        return content
        
    except Exception as e:
        logger.error(f"Error downloading file {file_id}: {e}")
        return None


def find_folder_by_name(service, folder_name: str) -> Optional[str]:
    """
    Find folder ID by name.
    
    Args:
        service: Google Drive API service instance
        folder_name: Name of the folder to find
        
    Returns:
        Folder ID if found, None otherwise
    """
    try:
        # Search for folder by name
        results = service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields="files(id, name)"
        ).execute()
        
        items = results.get('files', [])
        if items:
            folder_id = items[0]['id']
            logger.info(f"Found folder '{folder_name}' with ID: {folder_id}")
            return folder_id
        else:
            logger.warning(f"Folder '{folder_name}' not found")
            return None
            
    except Exception as e:
        logger.error(f"Error finding folder '{folder_name}': {e}")
        return None


def get_subfolders(service, folder_id: str) -> List[Dict[str, Any]]:
    """
    Get all subfolders in a folder.
    
    Args:
        service: Google Drive API service instance
        folder_id: Google Drive folder ID
        
    Returns:
        List of subfolder dictionaries
    """
    try:
        results = service.files().list(
            q=f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields="files(id, name, mimeType)"
        ).execute()
        
        subfolders = results.get('files', [])
        logger.debug(f"Found {len(subfolders)} subfolders in folder {folder_id}")
        return subfolders
        
    except Exception as e:
        logger.error(f"Error getting subfolders for {folder_id}: {e}")
        return []


def load_saved_credentials(token_file: str = 'token.pickle'):
    """
    Load previously saved OAuth2 credentials.
    
    Args:
        token_file: Path to the token file
        
    Returns:
        Credentials object if valid, None otherwise
    """
    try:
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                credentials = pickle.load(token)
            
            # Check if credentials are still valid
            if credentials and credentials.valid:
                return credentials
            elif credentials and credentials.expired and credentials.refresh_token:
                # Refresh expired credentials
                credentials.refresh(Request())
                # Save refreshed credentials
                save_credentials(credentials, token_file)
                return credentials
            else:
                return None
        return None
        
    except Exception as e:
        logger.debug(f"Could not load saved credentials: {e}")
        return None


def save_credentials(credentials, token_file: str = 'token.pickle'):
    """
    Save OAuth2 credentials for future use.
    
    Args:
        credentials: Credentials object to save
        token_file: Path to save the token file
    """
    try:
        with open(token_file, 'wb') as token:
            pickle.dump(credentials, token)
        logger.info("Credentials saved for future use")
    except Exception as e:
        logger.warning(f"Could not save credentials: {e}")


def parse_json_content(file_content: str) -> Optional[Dict[str, Any]]:
    """
    Parse JSON content from file.
    
    Args:
        file_content: Raw file content as string
        
    Returns:
        Parsed JSON as dictionary, or None if failed
    """
    try:
        json_data = json.loads(file_content)
        return json_data
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON content: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing JSON: {e}")
        return None


def extract_text_from_json(json_data: Dict[str, Any]) -> str:
    """
    Extract searchable text from JSON data.
    
    Args:
        json_data: Parsed JSON dictionary
        
    Returns:
        Extracted text as string
    """
    try:
        text_parts = []
        for key, value in json_data.items():
            if isinstance(value, (str, int, float)):
                text_parts.append(f"{key}: {value}")
            elif isinstance(value, list):
                text_parts.append(f"{key}: {', '.join(map(str, value))}")
        
        return " | ".join(text_parts)
    except Exception as e:
        logger.error(f"Error extracting text from JSON: {e}")
        return ""