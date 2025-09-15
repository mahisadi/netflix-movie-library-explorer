#!/usr/bin/env python3
"""
Google Drive Folder Management Utilities
Provides utilities for managing Google Drive folder operations like moving content and deleting files.
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional
from loguru import logger

# Add the connector path to sys.path to import the services
connector_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, connector_path)

from services.google_drive_service import GoogleDriveService

class GoogleDriveFolderManager:
    """Handles Google Drive folder management operations."""
    
    def __init__(self):
        """Initialize the Google Drive service."""
        self.drive_service = GoogleDriveService()
        
    def is_authenticated(self) -> bool:
        """Check if Google Drive service is authenticated."""
        return self.drive_service.is_authenticated()
    
    def find_folder_by_name_enhanced(self, folder_name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """
        Enhanced version of find_folder_by_name that can search within a specific parent.
        
        Args:
            folder_name: Name of the folder to find
            parent_id: Optional parent folder ID to search within
            
        Returns:
            Folder ID if found, None otherwise
        """
        try:
            # Build query based on whether we're searching within a parent
            if parent_id:
                query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false"
            else:
                query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            
            results = self.drive_service.service.files().list(
                q=query,
                fields="files(id, name, parents)"
            ).execute()
            
            items = results.get('files', [])
            if items:
                # If searching globally, return the first match
                # If searching within parent, verify the parent matches
                for item in items:
                    if parent_id:
                        if parent_id in item.get('parents', []):
                            folder_id = item['id']
                            logger.info(f"Found folder '{folder_name}' with ID: {folder_id} in parent {parent_id}")
                            return folder_id
                    else:
                        folder_id = item['id']
                        logger.info(f"Found folder '{folder_name}' with ID: {folder_id}")
                        return folder_id
                
                logger.warning(f"Folder '{folder_name}' not found in specified parent")
                return None
            else:
                logger.warning(f"Folder '{folder_name}' not found")
                return None
                
        except Exception as e:
            logger.error(f"Error finding folder '{folder_name}': {e}")
            return None
    
    def move_content_between_folders(self, source_folder_name: str, target_folder_name: str) -> Dict[str, Any]:
        """
        Move all content from source folder to target folder.
        Returns summary of the move operation.
        """
        try:
            # Check authentication
            if not self.is_authenticated():
                logger.error("Google Drive service is not authenticated")
                return {"success": False, "error": "Authentication failed"}
            
            # Find source folder
            source_folder_id = self.find_folder_by_name_enhanced(source_folder_name)
            if not source_folder_id:
                logger.error(f"Source folder '{source_folder_name}' not found")
                return {"success": False, "error": f"Source folder '{source_folder_name}' not found"}
            
            logger.info(f"Found source folder '{source_folder_name}' with ID: {source_folder_id}")
            
            # Find or create target folder
            target_folder_id = self.find_folder_by_name_enhanced(target_folder_name)
            if not target_folder_id:
                logger.info(f"Creating target folder '{target_folder_name}'...")
                target_folder_id = self.drive_service.create_folder(target_folder_name, None)
                
                if not target_folder_id:
                    logger.error("Failed to create/find target folder")
                    return {"success": False, "error": "Failed to create/find target folder"}
            
            logger.info(f"Found/created target folder '{target_folder_name}' with ID: {target_folder_id}")
            
            # Get all content from source folder
            logger.info("Getting all content from source folder...")
            all_content = self.get_all_files_in_folder(source_folder_id)
            
            # Also get direct subfolders
            results = self.drive_service.service.files().list(
                q=f"'{source_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
                fields="files(id, name, mimeType)"
            ).execute()
            
            subfolders = results.get('files', [])
            
            logger.info(f"Found {len(all_content)} files and {len(subfolders)} subfolders to move")
            
            # Statistics
            stats = {
                "source_folder_id": source_folder_id,
                "target_folder_id": target_folder_id,
                "files_moved": 0,
                "folders_moved": 0,
                "failed_moves": 0,
                "moved_files": [],
                "moved_folders": []
            }
            
            # Move all subfolders first
            logger.info("Moving subfolders...")
            for folder_data in subfolders:
                folder_id = folder_data['id']
                folder_name = folder_data['name']
                
                logger.info(f"Moving folder: {folder_name}")
                success = self.move_folder_to_folder(folder_id, target_folder_id)
                
                if success:
                    stats["folders_moved"] += 1
                    stats["moved_folders"].append({
                        "name": folder_name,
                        "id": folder_id
                    })
                else:
                    stats["failed_moves"] += 1
            
            # Move all files
            logger.info("Moving files...")
            for file_data in all_content:
                file_id = file_data['id']
                file_name = file_data['name']
                
                logger.info(f"Moving file: {file_name}")
                success = self.move_file_to_folder(file_id, target_folder_id)
                
                if success:
                    stats["files_moved"] += 1
                    stats["moved_files"].append({
                        "name": file_name,
                        "id": file_id
                    })
                else:
                    stats["failed_moves"] += 1
            
            # Log summary
            logger.info("=" * 60)
            logger.info("MOVE OPERATION SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Source folder: {source_folder_name} (ID: {source_folder_id})")
            logger.info(f"Target folder: {target_folder_name} (ID: {target_folder_id})")
            logger.info(f"Folders moved: {stats['folders_moved']}")
            logger.info(f"Files moved: {stats['files_moved']}")
            logger.info(f"Failed moves: {stats['failed_moves']}")
            logger.info("=" * 60)
            
            return {
                "success": True,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Move operation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_all_files_in_folder(self, folder_id: str) -> List[Dict[str, Any]]:
        """Get all files (including nested) from a folder."""
        try:
            all_files = []
            
            # Get direct files in the folder
            results = self.drive_service.service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="files(id, name, mimeType, parents)"
            ).execute()
            
            files = results.get('files', [])
            
            for file_data in files:
                if file_data.get('mimeType') == 'application/vnd.google-apps.folder':
                    # It's a folder, recursively get its contents
                    nested_files = self.get_all_files_in_folder(file_data['id'])
                    all_files.extend(nested_files)
                else:
                    # It's a file, add it to the list
                    file_data['folder_path'] = f"source_folder/..."
                    all_files.append(file_data)
            
            return all_files
            
        except Exception as e:
            logger.error(f"Error getting files from folder {folder_id}: {e}")
            return []
    
    def move_file_to_folder(self, file_id: str, target_folder_id: str) -> bool:
        """Move a file to a target folder."""
        try:
            # Get current parents of the file
            file = self.drive_service.service.files().get(
                fileId=file_id,
                fields='parents'
            ).execute()
            
            previous_parents = ",".join(file.get('parents', []))
            
            # Move the file to the new parent
            self.drive_service.service.files().update(
                fileId=file_id,
                addParents=target_folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            
            logger.info(f"Moved file {file_id} to folder {target_folder_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error moving file {file_id}: {e}")
            return False
    
    def move_folder_to_folder(self, folder_id: str, target_folder_id: str) -> bool:
        """Move a folder to a target folder."""
        try:
            # Get current parents of the folder
            folder = self.drive_service.service.files().get(
                fileId=folder_id,
                fields='parents'
            ).execute()
            
            previous_parents = ",".join(folder.get('parents', []))
            
            # Move the folder to the new parent
            self.drive_service.service.files().update(
                fileId=folder_id,
                addParents=target_folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            
            logger.info(f"Moved folder {folder_id} to folder {target_folder_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error moving folder {folder_id}: {e}")
            return False
    
    def delete_root_json_files(self, root_folder_name: str) -> Dict[str, Any]:
        """
        Delete all JSON files from the root directory of a folder.
        Returns summary of the deletion operation.
        """
        try:
            # Check authentication
            if not self.is_authenticated():
                logger.error("Google Drive service is not authenticated")
                return {"success": False, "error": "Authentication failed"}
            
            # Find root folder
            root_folder_id = self.find_folder_by_name_enhanced(root_folder_name)
            if not root_folder_id:
                logger.error(f"Root folder '{root_folder_name}' not found")
                return {"success": False, "error": "Root folder not found"}
            
            # Get root JSON files
            root_files = self.get_root_json_files(root_folder_id)
            
            if not root_files:
                logger.info("No JSON files found in root directory")
                return {
                    "success": True,
                    "stats": {
                        "total_files": 0,
                        "deleted_files": 0,
                        "failed_deletions": 0,
                        "deleted_file_names": []
                    }
                }
            
            # Statistics
            stats = {
                "total_files": len(root_files),
                "deleted_files": 0,
                "failed_deletions": 0,
                "deleted_file_names": []
            }
            
            logger.info(f"Starting deletion of {len(root_files)} JSON files from root directory...")
            
            # Delete each file
            for file_data in root_files:
                file_id = file_data['id']
                file_name = file_data['name']
                
                logger.info(f"Deleting: {file_name}")
                success = self.delete_file(file_id, file_name)
                
                if success:
                    stats["deleted_files"] += 1
                    stats["deleted_file_names"].append(file_name)
                else:
                    stats["failed_deletions"] += 1
            
            # Log summary
            logger.info("=" * 60)
            logger.info("ROOT JSON FILES DELETION SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Root folder: {root_folder_name} (ID: {root_folder_id})")
            logger.info(f"Total files found: {stats['total_files']}")
            logger.info(f"Successfully deleted: {stats['deleted_files']}")
            logger.info(f"Failed deletions: {stats['failed_deletions']}")
            logger.info("=" * 60)
            
            return {
                "success": True,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Deletion operation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_root_json_files(self, root_folder_id: str) -> List[Dict[str, Any]]:
        """Get all JSON files directly in the root folder (not in subfolders)."""
        try:
            # Query for files directly in the root folder with .json extension
            query = f"'{root_folder_id}' in parents and mimeType='application/json' and trashed=false"
            
            results = self.drive_service.service.files().list(
                q=query,
                fields="files(id, name, mimeType, parents)"
            ).execute()
            
            files = results.get('files', [])
            
            # Filter to only include files directly in the root folder
            root_files = []
            for file_data in files:
                if root_folder_id in file_data.get('parents', []):
                    root_files.append(file_data)
            
            logger.info(f"Found {len(root_files)} JSON files in root directory")
            return root_files
            
        except Exception as e:
            logger.error(f"Error getting root JSON files: {e}")
            return []
    
    def delete_file(self, file_id: str, file_name: str) -> bool:
        """Delete a file by its ID."""
        try:
            self.drive_service.service.files().delete(fileId=file_id).execute()
            logger.info(f"Deleted file: {file_name} (ID: {file_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {file_name} (ID: {file_id}): {e}")
            return False

def main():
    """Main function for folder management operations."""
    logger.info("🔧 Google Drive Folder Manager")
    logger.info("=" * 60)
    
    # Initialize manager
    manager = GoogleDriveFolderManager()
    
    # Check authentication
    if not manager.is_authenticated():
        logger.error("❌ Google Drive authentication failed")
        logger.error("Please ensure your Google Drive credentials are properly configured")
        return
    
    logger.info("✅ Google Drive authentication successful")
    
    # Example usage - you can modify this based on your needs
    logger.info("Available operations:")
    logger.info("1. Move content between folders")
    logger.info("2. Delete root JSON files")
    logger.info("3. Custom operations")
    
    # For demonstration, show how to use the manager
    logger.info("Manager initialized successfully. Use the class methods for specific operations.")

if __name__ == "__main__":
    main()
