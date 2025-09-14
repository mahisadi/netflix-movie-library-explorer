import argparse
from connectors.google_drive import GoogleDriveConnector

from utils.config import GOOGLE_DRIVE_FOLDER_NAME


from os import path
from loguru import logger

# persis logs in the file
logger.add(
    path.join(path.dirname(__file__), "storage", "logs", "stdout.txt"), enqueue=True
)

class Main:
    
    def process(self):
        parser = argparse.ArgumentParser(
            prog="main.py",
            description="Fetches and transforms the content from different sources "
            "and Persists in RedisSearch ( in-memory ) local container",
            epilog="Supports: google_drive connector for fetching and indexing JSON files from nested Google Drive folders.",
        )
        parser.add_argument("connector")
        parser.add_argument("--folder-name", nargs="?", const=None, type=str, help="Google Drive folder name to fetch content")
        parser.add_argument("--file-types", nargs="?", const=None, type=str, help="File types to fetch (i.e. application/json)")
        parser.add_argument("--recreate-index", action="store_true", help="Recreate RedisSearch index before persisting content")

        args = parser.parse_args()
        google_drive = GoogleDriveConnector()

        if args.connector == "google_drive":            
            google_drive.fetch(
                folder_name=GOOGLE_DRIVE_FOLDER_NAME,
                file_types=args.file_types,
                recreate_index=args.recreate_index
            )
        else:
            raise Exception("Please specify a (valid) connector.")



if __name__ == "__main__":
    Main().process()





