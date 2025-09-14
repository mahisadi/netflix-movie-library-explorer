import os
import json
from dotenv import load_dotenv

load_dotenv()

# Google Drive Configuration
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
GOOGLE_DRIVE_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")

# Handle OAuth2 credentials
google_drive_cred_json = os.environ.get('GOOGLE_DRIVE_CRED_JSON')
if google_drive_cred_json:
    try:
        GOOGLE_DRIVE_CRED = json.loads(google_drive_cred_json)
    except json.JSONDecodeError:
        GOOGLE_DRIVE_CRED = {}
else:
    GOOGLE_DRIVE_CRED = {}

# Redis Configuration
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
REDIS_DB = int(os.environ.get("REDIS_DB", "0"))

# RedisSearch Configuration (uses same Redis instance)
REDISEARCH_INDEX_NAME = os.environ.get("REDISEARCH_INDEX_NAME", "movies_index")
REDISEARCH_PREFIX = os.environ.get("REDISEARCH_PREFIX", "movie:")

# Logging Configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_RETENTION_DAYS = int(os.environ.get("LOG_RETENTION_DAYS", "30"))

# Sync Configuration
DEFAULT_FILE_TYPES = os.environ.get("DEFAULT_FILE_TYPES", "application/json").split(",")
MAX_FILES_PER_SYNC = int(os.environ.get("MAX_FILES_PER_SYNC", "1000"))
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "50"))

# Document Sources and Types
DOCUMENT_SOURCES = {
    "GOOGLE_DRIVE": "google_drive"
}

CONTENT_TYPES = {
    "MOVIES": "movies"
}

DOCUMENT_TYPE = {
    "JSON_FILE": "json_file"
}