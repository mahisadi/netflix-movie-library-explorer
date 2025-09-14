import redis
import json
from typing import List, Dict, Any, Optional
from loguru import logger
from utils.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB



class RedisSearchService:

    """RedisSearch service for indexing and managing movie data."""

    def __init__(self):
        self.redis_client = None
        self.index_name = "movie_library"
        self._connect()
        
    def _index_exists(self) -> bool:
        """Check if the RedisSearch index exists."""
        try:
            info = self.redis_client.execute_command("FT.INFO", self.index_name)
            return True
        except Exception as e:
            # Index doesn't exist if we get an error
            logger.debug(f"Index {self.index_name} does not exist: {e}")
            return False

    def _connect(self):
        """Establish connection to Redis."""
        try:
            self.redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD if REDIS_PASSWORD else None,
                db=REDIS_DB,
                decode_responses=True
            )
            
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def create_index(self):
        """Create RedisSearch index with movie schema if it doesn't exist."""
        try:
            # Check if index already exists
            if self._index_exists():
                logger.info(f"RedisSearch index '{self.index_name}' already exists")
                return True
            # Define the enhanced schema for movie data with SORTABLE and FILTERABLE attributes
            schema_definition = [
                # SEARCHABLE FIELDS (TEXT with weights)
                "title", "TEXT", "WEIGHT", "5.0",
                "stars", "TEXT", "WEIGHT", "3.0", 
                "country", "TEXT", "WEIGHT", "2.0",
                "director", "TEXT", "WEIGHT", "3.0",
                "writer", "TEXT", "WEIGHT", "2.0",
                "movie_plot", "TEXT", "WEIGHT", "1.0",
                "awards", "TEXT", "WEIGHT", "1.0",
                "content", "TEXT", "WEIGHT", "1.0",
                
                # FACETED FIELDS (TAG for filtering and faceting)
                "genre", "TAG",
                "subgenre", "TAG", 
                "language", "TAG",
                "production_house", "TAG",
                "source", "TAG",
                
                # SORTABLE AND FILTERABLE FIELDS (NUMERIC with SORTABLE)
                "year", "NUMERIC", "SORTABLE",
                "imdb_rating", "NUMERIC", "SORTABLE",
                "popu", "NUMERIC", "SORTABLE",
                
                # SORTABLE AND FILTERABLE FIELDS (TEXT with SORTABLE)
                "modified_time", "TEXT", "SORTABLE",
                
                # REGULAR FIELDS (TEXT without special attributes)
                "file_id", "TEXT",
                "folder_path", "TEXT",
                "file_name", "TEXT",
                "url", "TEXT"
            ]
            
            # Create the index using raw Redis command
            # "PREFIX", "1", "movie:" to index hashes with keys starting with "movie:"
            # It helps in organizing and querying movie records
            result = self.redis_client.execute_command(
                "FT.CREATE", self.index_name,
                "ON", "HASH",
                "PREFIX", "1", "movie:",
                "LANGUAGE", "english",
                "SCHEMA", *schema_definition
            )
            
            logger.info(f"Created RedisSearch index: {self.index_name}")
            return True
            
        except redis.exceptions.ResponseError as e:
            if "index already exists" in str(e).lower():
                logger.info(f"Index {self.index_name} already exists")
                return True
            else:
                logger.error(f"Failed to create index: {e}")
                raise
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            raise

    def drop_index(self):
        """Drop the RedisSearch index."""
        try:
            self.redis_client.execute_command("FT.DROPINDEX", self.index_name, "DD")
            logger.info(f"Dropped RedisSearch index: {self.index_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to drop index: {e}")
            return False
    
    def index_document(self, document_id: str, data: Dict[str, Any]) -> bool:
        """Index a single document."""
        try:
            # Prepare document data for RedisSearch
            doc_data = {
                "title": data.get("title", ""),
                "stars": " ".join(data.get("stars", [])),  # Convert array to space-separated string
                "country": data.get("country", ""),
                "director": data.get("director", ""),
                "writer": data.get("writer", ""),
                "movie_plot": data.get("movie_plot", ""),
                "awards": " ".join(data.get("awards", [])),  # Convert array to space-separated string
                "content": data.get("content", ""),
                "file_id": data.get("id", ""),
                # Filterable fields
                "genre": data.get("genre", "unknown"),
                "subgenre": data.get("subgenre", "unknown"),
                "language": data.get("language", "unknown"),
                "production_house": data.get("production_house", "unknown"),
                "source": data.get("source", "google_drive"),
                
                # Numeric fields
                "year": data.get("year", 0),
                "imdb_rating": data.get("imdb_rating", 0.0),
                "popu": data.get("popu", 0),
                
                # System fields
                "folder_path": data.get("folder_path", ""),
                "modified_time": data.get("modified_time", ""),
                "file_name": data.get("file_name", ""),
                "url": data.get("url", "")
            }
            
            # Index the document as a Redis Hash using google drive file id as primary key
            redis_key = f"movie:{document_id}"
            self.redis_client.hset(redis_key, mapping=doc_data)
            
            logger.debug(f"Indexed document: {redis_key} (file_id: {doc_data.get('file_id', 'N/A')})")
            return redis_key  # Return the full Redis key
            
        except Exception as e:
            logger.error(f"Failed to index document {document_id}: {e}")
            return False
    
    def index_batch(self, documents: List[Dict[str, Any]]) -> int:
        """Index multiple documents in batch."""
        try:
            indexed_count = 0
            
            for doc in documents:
                document_id = doc.get("id", "")
                if not document_id:
                    logger.warning("Skipping document without ID")
                    continue
                
                if self.index_document(document_id, doc):
                    indexed_count += 1
            
            logger.info(f"Batch indexed {indexed_count}/{len(documents)} documents")
            return indexed_count
            
        except Exception as e:
            logger.error(f"Batch indexing failed: {e}")
            return 0
    
    def delete_document(self, redis_key: str) -> bool:
        """Delete a document from the index using the full Redis key."""
        try:
            # If the key doesn't start with "movie:", add the prefix
            if not redis_key.startswith("movie:"):
                redis_key = f"movie:{redis_key}"
            
            self.redis_client.delete(redis_key)
            logger.debug(f"Deleted document: {redis_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document {redis_key}: {e}")
            return False
    
    def get_index_info(self) -> Dict[str, Any]:
        """Get index information."""
        try:
            info = self.redis_client.execute_command("FT.INFO", self.index_name)
            # Convert the list response to a dictionary
            result = {}
            for i in range(0, len(info), 2):
                if i + 1 < len(info):
                    result[info[i]] = info[i + 1]
            return result
        except Exception as e:
            logger.error(f"Failed to get index info: {e}")
            return {}
    
    def get_document_count(self) -> int:
        """Get total number of documents in the index."""
        try:
            info = self.get_index_info()
            return int(info.get("num_docs", 0))
        except Exception as e:
            logger.error(f"Failed to get document count: {e}")
            return 0
    
    def get_document(self, redis_key: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by Redis key."""
        try:
            # If the key doesn't start with "movie:", add the prefix
            if not redis_key.startswith("movie:"):
                redis_key = f"movie:{redis_key}"
            
            document = self.redis_client.hgetall(redis_key)
            
            if document:
                # Convert Redis hash to dictionary
                doc_dict = dict(document)
                # Add the full Redis key as the document ID
                doc_dict["id"] = redis_key  # movie:{document_id}
                return doc_dict
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get document {redis_key}: {e}")
            return None
    
    def add_document(self, index_name: str, document_id: str, data: Dict[str, Any]) -> bool:
        """Add a document to the index (alias for index_document)."""
        return self.index_document(document_id, data)
    
    def search(self, query: str, offset: int = 0, limit: int = 10, sort_by: Optional[str] = None, filter_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for documents using RedisSearch."""
        try:
            # Build the search command
            cmd = ["FT.SEARCH", self.index_name, query]

            # Add filtering if specified
            # This is one of use case for Tech Employees can filter results by genre, year and ratings.
            if filter_by:
                cmd.extend(["FILTERBY", filter_by])
            
            # Add sorting if specified
            if sort_by:
                cmd.extend(["SORTBY", sort_by])
            
            # Add pagination
            cmd.extend(["LIMIT", str(offset), str(limit)])
            
            # Execute the search
            result = self.redis_client.execute_command(*cmd)
            
            if not result or len(result) < 2:
                return []
            
            # Parse the result
            documents = []
            
            # Skip the first element (total count) and process documents
            for i in range(1, len(result), 2):
                if i + 1 < len(result):
                    doc_id = result[i]
                    doc_data = result[i + 1]
                    
                    # Convert the flat list to a dictionary
                    doc_dict = {}
                    for j in range(0, len(doc_data), 2):
                        if j + 1 < len(doc_data):
                            key = doc_data[j]
                            value = doc_data[j + 1]
                            doc_dict[key] = value
                    
                    # Add the full Redis key as the document ID
                    doc_dict["id"] = doc_id  # Keep the full Redis key: movie:{id}
                    
                    documents.append(doc_dict)
            
            logger.debug(f"Search query '{query}' returned {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def health_check(self) -> bool:
        """Check if Redis and RedisSearch are healthy."""
        try:
            # Check Redis connection
            self.redis_client.ping()
            
            # Check if RedisSearch module is loaded
            modules = self.redis_client.execute_command("MODULE", "LIST")
            redissearch_loaded = any("search" in str(module).lower() for module in modules)
            
            if not redissearch_loaded:
                logger.error("RedisSearch module not loaded")
                return False
            
            logger.info("RedisSearch health check passed")
            return True
            
        except Exception as e:
            logger.error(f"RedisSearch health check failed: {e}")
            return False
