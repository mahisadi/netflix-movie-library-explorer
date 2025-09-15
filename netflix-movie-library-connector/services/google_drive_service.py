from loguru import logger
from typing import List, Optional, Dict, Any
from utils.config import GOOGLE_DRIVE_CRED, GOOGLE_DRIVE_PERMISSION_SCOPE,GOOGLE_DRIVE_AUTH_FLOW_REDIRECT_URI
from utils.google_drive_utils import (
    get_nested_files_with_types,
    download_file_content,
    find_folder_by_name,
    get_subfolders,
    load_saved_credentials,
    save_credentials
)
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import webbrowser
from googleapiclient.http import MediaIoBaseUpload
import io



class GoogleDriveService:

    """ Process Authentication and fetch files form Google Drive."""

    def __init__(self):
        self.service = None
        self._authenticate()
    
    def is_authenticated(self) -> bool:
        """Check if the service is properly authenticated."""
        return self.service is not None
    
    def _authenticate(self):
        """Authenticate with Google Drive API using OAuth2 or service account."""
        try:
            credentials = None
            
            # Try service account credentials first (preferred for server applications)
            if GOOGLE_DRIVE_CRED and ('web' in GOOGLE_DRIVE_CRED or 'installed' in GOOGLE_DRIVE_CRED):
                logger.info("Using OAuth2 credentials for Google Drive API")
                credentials = self._authenticate_oauth2()
            else:
                raise ValueError("No valid credentials provided. Set either GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_DRIVE_CRED_JSON")
            
            self.service = build('drive', 'v3', credentials=credentials)
            logger.info("Successfully authenticated with Google Drive API")
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Drive API: {e}")
            raise  # Re-raise the exception to stop execution
    
    def _authenticate_oauth2(self):
        """Authenticate using OAuth2 credentials."""
        try:
            # Try to load saved credentials first
            credentials = self._load_saved_credentials()
            if credentials:
                logger.info("Using saved OAuth2 credentials")
                return credentials
            
            # If no saved credentials, start OAuth2 flow
            logger.info("No saved credentials found. Starting OAuth2 flow...")
            
            # Create OAuth2 flow
            flow = Flow.from_client_config(
                GOOGLE_DRIVE_CRED,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            
            # Get authorization URL
            auth_url, _ = flow.authorization_url(prompt='consent')
            logger.info(f"Please visit this URL to authorize the application: {auth_url}")
            logger.info("After authorization, you'll see a page with an authorization code.")
            logger.info("Copy the code and paste it below.")
            
            # Open the browser
            import webbrowser
            webbrowser.open(auth_url)
            
            # Get authorization code from user
            auth_code = input('Enter the authorization code: ')
            
            # Exchange authorization code for credentials
            flow.fetch_token(code=auth_code)
            credentials = flow.credentials
            
            # Save credentials for future use
            self._save_credentials(credentials)
            
            return credentials
            
        except Exception as e:
            logger.error(f"OAuth2 authentication failed: {e}")
            raise
    
    def _load_saved_credentials(self):
        """Load previously saved OAuth2 credentials."""
        return load_saved_credentials()
    
    def _save_credentials(self, credentials):
        """Save OAuth2 credentials for future use."""
        save_credentials(credentials)
    
        
    def _get_nested_files_with_types(self, folder_id: str, file_types: List[str] = None, 
                         since: Optional[str] = None, page_size: int = 100, 
                         max_depth: int = 10, current_depth: int = 0, 
                         current_path: str = "") -> List[Dict[str, Any]]:
        """Get nested files with types using utility function."""
        return get_nested_files_with_types(
            self.service, folder_id, file_types, since, page_size, 
            max_depth, current_depth, current_path
        )
    
    
    def _get_subfolders(self, folder_id: str) -> List[Dict[str, Any]]:
        """Get all subfolders from a parent folder using utility function."""
        return get_subfolders(self.service, folder_id)
        

    
    def find_folder_by_name(self, folder_name: str) -> Optional[str]:
        """Find folder ID by folder name using utility function."""
        if self.service is None:
            logger.error("Google Drive service is not initialized. Authentication failed.")
            return None
        return find_folder_by_name(self.service, folder_name)

    def find_folder_by_name_in_parent(self, folder_name: str, parent_id: str) -> Optional[str]:
        """Find folder ID by name within a specific parent folder."""
        try:
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false"
            
            results = self.service.files().list(
                q=query,
                pageSize=10,
                fields="files(id, name)"
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                return folders[0]['id']
            return None
                
        except Exception as e:
            logger.error(f"Error searching for folder '{folder_name}' in parent '{parent_id}': {e}")
            return None

    def create_folder(self, folder_name: str, parent_id: str) -> Optional[str]:
        """Create a new folder in Google Drive."""
        try:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            logger.info(f"Created folder '{folder_name}' with ID: {folder_id}")
            return folder_id
            
        except Exception as e:
            logger.error(f"Error creating folder '{folder_name}': {e}")
            return None

    def upload_file(self, file_name: str, file_content: str, parent_id: str) -> Optional[str]:
        """Upload a file to Google Drive."""
        try:
            from googleapiclient.http import MediaIoBaseUpload
            import io
            
            file_metadata = {
                'name': file_name,
                'parents': [parent_id]
            }
            
            # Create media object
            media = MediaIoBaseUpload(
                io.BytesIO(file_content.encode('utf-8')),
                mimetype='application/json',
                resumable=True
            )
            
            # Create file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            logger.info(f"Uploaded file '{file_name}' with ID: {file_id}")
            return file_id
            
        except Exception as e:
            logger.error(f"Error uploading file '{file_name}': {e}")
            return None

    def download_file_content(self, file_id: str) -> Optional[str]:
        """Download file content from Google Drive using utility function."""
        return download_file_content(self.service, file_id)

    def extract_metadata_from_path(self, folder_path: str) -> Dict[str, Any]:
        """Extract genre, subgenre, and year from folder path using utility functions."""
        from utils.google_drive_utils import extract_genre_from_path, extract_subgenre_from_path, extract_year_from_path
        
        return {
            "genre": extract_genre_from_path(folder_path),
            "subgenre": extract_subgenre_from_path(folder_path),
            "year": extract_year_from_path(folder_path)
        }

    def listfiles(self, folder_name:str=None, since:Optional[str]=None, page_size=100, include_nested:bool = True, file_types:List[str]=None) -> List[Dict[str, Any]]:

        try:
            drive_files = []
            page_token = None
            
            # If folder_id looks like a name (contains hyphens), search for it by name
            folder_id = None
            if folder_name and ('-' in folder_name and len(folder_name) > 20):
                folder_id = self.find_folder_by_name(folder_name)
                if not folder_id:
                    logger.error(f"Could not find folder with name: {folder_id}")
                    return []
            
            # Build query based on parameters
            query_parts = ['trashed=false']
            
            if folder_id:
                query_parts.append(f"'{folder_id}' in parents")
            else:
                # List all accessible files/folders
                query_parts.append("mimeType='application/vnd.google-apps.folder'")
            
            if file_types and 'application/json' in file_types:
                query_parts.append("mimeType='application/json'")
            elif not folder_id:
                # If listing all folders, don't filter by mimeType
                pass
                
            if since and since != 100:  # Skip invalid since values
                # Fix the date format for Google Drive API
                since_str = str(since)
                if len(since_str) == 4:  # Just year
                    query_parts.append(f"modifiedTime>='{since_str}-01-01T00:00:00Z'")
                else:
                    query_parts.append(f"modifiedTime>='{since_str}T00:00:00Z'")
                
            request_query = " and ".join(query_parts)

            # Recursion Function Until Finding Files
            while True:
                results = self.service.files().list(
                    q=request_query,
                    pageSize=page_size,
                    pageToken=page_token,
                    fields="nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, webViewLink, parents, owners, permissions)"
                ).execute()
                
                drive_files.extend(results.get('files', []))
                page_token = results.get('nextPageToken')
                
                if not page_token:
                    break
            
            # If include_nested is True, also get files from subfolders
            if include_nested and folder_id:
                # Only get JSON files from nested folders
                json_file_types = ['application/json'] if file_types is None else file_types
                nested_files = self._get_nested_files_with_types(folder_id, json_file_types, since, page_size)
                drive_files.extend(nested_files)
            
            # Extract metadata from folder paths for each file
            for file_data in drive_files:
                folder_path = file_data.get('folder_path', '')
                if folder_path:
                    # Extract metadata from folder path
                    path_metadata = self.extract_metadata_from_path(folder_path)
                    # Add extracted metadata to file data
                    file_data.update({
                        "extracted_genre": path_metadata['genre'],
                        "extracted_subgenre": path_metadata['subgenre'],
                        "extracted_year": path_metadata['year']
                    })
                    logger.info(f"📁 File: {file_data.get('name', 'Unknown')}")
                    logger.info(f"   📂 Path: {folder_path}")
                    logger.info(f"   🎭 Genre: {path_metadata['genre']}")
                    logger.info(f"   🎪 Subgenre: {path_metadata['subgenre']}")
                    logger.info(f"   📅 Year: {path_metadata['year']}")
                    logger.info("")
            
            logger.info(f"Retrieved {len(drive_files)} files from folder {folder_id} (including nested)")

            return drive_files
        
        except Exception as ex:
            logger.error(f"Exception - Fetching files from google drive: {ex}")
            return []
