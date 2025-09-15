"""
Search Service for Movie Search API

Handles business logic for movie search operations and communicates
with the RedisSearch service to retrieve and process data.
"""

import sys
import os
from typing import Dict, List, Optional, Any
from loguru import logger
import time

# Add the netflix-movie-library-connector project to the path
connector_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "netflix-movie-library-connector")
sys.path.insert(0, connector_path)

from services.redis_search_service import RedisSearchService
from utils.config import REDISEARCH_INDEX_NAME


class SearchService:
    """Service class for handling movie search operations."""
    
    def __init__(self):
        """Initialize the search service with RedisSearch connection."""
        self.redis_service = RedisSearchService()
        self.index_name = REDISEARCH_INDEX_NAME
        logger.info("SearchService initialized")
    
    async def health_check(self) -> bool:
        """Check if the search service is healthy."""
        try:
            return self.redis_service.health_check()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def build_search_query(
        self,
        search_query: str = "",
        genre: Optional[str] = None,
        subgenre: Optional[str] = None,
        language: Optional[str] = None,
        country: Optional[str] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        rating_min: Optional[float] = None,
        rating_max: Optional[float] = None,
        production_house: Optional[str] = None,
        director: Optional[str] = None,
        actor: Optional[str] = None
    ) -> str:
        """
        Build a RedisSearch query string from search parameters.
        
        Args:
            search_query: Text search query
            genre: Filter by genre
            subgenre: Filter by subgenre
            language: Filter by language
            country: Filter by country
            year_from: Minimum year
            year_to: Maximum year
            rating_min: Minimum IMDB rating
            rating_max: Maximum IMDB rating
            production_house: Filter by production house
            director: Filter by director
            actor: Filter by actor
            
        Returns:
            RedisSearch query string
        """
        try:
            query_parts = []
            
            # Text search across multiple fields
            if search_query:
                # Escape special characters for RedisSearch
                escaped_query = search_query.replace('"', '\\"').replace("'", "\\'")
                
                # Use RedisSearch UNION approach for OR logic
                # Search in fields that work well: content, stars, director, writer
                # Test each field individually and only include working ones
                text_search = f'(@content:{escaped_query}* | @stars:{escaped_query}* | @director:{escaped_query}* | @writer:{escaped_query}*)'
                query_parts.append(text_search)
            else:
                # If no text search, match all documents
                query_parts.append("*")
            
            # Add filters
            if genre:
                query_parts.append(f"@genre:{genre}")
            
            if subgenre:
                query_parts.append(f"@subgenre:{subgenre}")
            
            if language:
                query_parts.append(f"@language:{language}")
            
            if country:
                query_parts.append(f"@country:{country}")
            
            if production_house:
                query_parts.append(f"@production_house:{production_house}")
            
            if director:
                query_parts.append(f"@director:{director}")
            
            if actor:
                query_parts.append(f"@stars:{actor}")
            
            # Add numeric range filters
            if year_from is not None or year_to is not None:
                year_filter = "@year:["
                if year_from is not None:
                    year_filter += str(year_from)
                else:
                    year_filter += "0"
                year_filter += " "
                if year_to is not None:
                    year_filter += str(year_to)
                else:
                    year_filter += "+inf"
                year_filter += "]"
                query_parts.append(year_filter)
            
            if rating_min is not None or rating_max is not None:
                rating_filter = "@imdb_rating:["
                if rating_min is not None:
                    rating_filter += str(rating_min)
                else:
                    rating_filter += "0"
                rating_filter += " "
                if rating_max is not None:
                    rating_filter += str(rating_max)
                else:
                    rating_filter += "10"
                rating_filter += "]"
                query_parts.append(rating_filter)
            
            # Combine all parts with AND
            final_query = " ".join(query_parts)
            
            logger.info(f"🔍 Search query: '{search_query}' -> RedisSearch: {final_query}")
            return final_query
            
        except Exception as e:
            logger.error(f"Error building search query: {e}")
            return "*"  # Fallback to match all
    
    async def search_movies(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20,
        sort_field: str = "relevance",
        sort_direction: str = "desc"
    ) -> Dict[str, Any]:
        """
        Search for movies using RedisSearch.
        
        Args:
            query: RedisSearch query string
            page: Page number (1-based)
            page_size: Number of results per page
            sort_field: Field to sort by
            sort_direction: Sort direction (asc/desc)
            
        Returns:
            Dictionary containing movies and pagination info
        """
        try:
            start_time = time.time()
            
            # Calculate offset for pagination
            offset = (page - 1) * page_size
            
            # Build sort options
            sort_options = self._build_sort_options(sort_field, sort_direction)
            
            # Execute search
            results = self.redis_service.search(
                query=query,
                offset=offset,
                limit=page_size,
                sort_by=sort_options
            )
            
            search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Get total count for pagination
            total_count = self._get_total_count(query)
            
            logger.info(f"Search completed: {len(results)} movies found in {search_time:.2f}ms")
            
            return {
                "movies": results,
                "total_count": total_count,
                "search_time_ms": search_time,
                "page": page,
                "page_size": page_size
            }
            
        except Exception as e:
            logger.error(f"Search movies error: {e}")
            raise Exception(f"Search failed: {str(e)}")
    
    async def get_movie_by_id(self, movie_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific movie by its ID.
        
        Args:
            movie_id: Movie ID
            
        Returns:
            Movie data dictionary or None if not found
        """
        try:
            # Use RedisSearch to find the movie by ID
            query = f"@file_id:{movie_id}"
            results = self.redis_service.search(query, limit=1)
            
            if results:
                return results[0]
            else:
                logger.warning(f"Movie not found: {movie_id}")
                return None
                
        except Exception as e:
            logger.error(f"Get movie by ID error: {e}")
            raise Exception(f"Failed to get movie: {str(e)}")
    
    async def get_search_suggestions(self, query: str, limit: int = 10) -> Dict[str, List[str]]:
        """
        Get search suggestions for autocomplete.
        
        Args:
            query: Partial search query
            limit: Maximum suggestions per category
            
        Returns:
            Dictionary with suggestion lists
        """
        try:
            suggestions = {
                "titles": [],
                "genres": [],
                "directors": [],
                "actors": []
            }
            
            if not query or len(query) < 2:
                return suggestions
            
            # Search for partial matches in different fields
            title_query = f"@title:{query}*"
            genre_query = f"@genre:{query}*"
            director_query = f"@director:{query}*"
            actor_query = f"@stars:{query}*"
            
            # Get suggestions from each field
            title_results = self.redis_service.search(title_query, limit=limit)
            genre_results = self.redis_service.search(genre_query, limit=limit)
            director_results = self.redis_service.search(director_query, limit=limit)
            actor_results = self.redis_service.search(actor_query, limit=limit)
            
            # Extract unique values
            suggestions["titles"] = list(set([movie.get("title", "") for movie in title_results if movie.get("title")]))
            suggestions["genres"] = list(set([movie.get("genre", "") for movie in genre_results if movie.get("genre")]))
            suggestions["directors"] = list(set([movie.get("director", "") for movie in director_results if movie.get("director")]))
            
            # Extract actors from stars arrays
            actors = set()
            for movie in actor_results:
                stars = movie.get("stars", [])
                if isinstance(stars, list):
                    actors.update(stars)
            suggestions["actors"] = list(actors)[:limit]
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Get suggestions error: {e}")
            return {"titles": [], "genres": [], "directors": [], "actors": []}
    
    async def get_filter_options(self) -> Dict[str, List[str]]:
        """
        Get available filter options for the search interface.
        
        Returns:
            Dictionary with available filter values
        """
        try:
            # Get all movies to extract unique filter values
            all_movies = self.redis_service.search("*", limit=1000)  # Adjust limit as needed
            
            options = {
                "genres": set(),
                "subgenres": set(),
                "languages": set(),
                "countries": set(),
                "years": set(),
                "production_houses": set(),
                "sources": set(),
                "content_types": set()
            }
            
            for movie in all_movies:
                if movie.get("genre"):
                    options["genres"].add(movie["genre"])
                if movie.get("subgenre"):
                    options["subgenres"].add(movie["subgenre"])
                if movie.get("language"):
                    options["languages"].add(movie["language"])
                if movie.get("country"):
                    options["countries"].add(movie["country"])
                if movie.get("year"):
                    options["years"].add(int(movie["year"]))
                if movie.get("production_house"):
                    options["production_houses"].add(movie["production_house"])
                if movie.get("source"):
                    options["sources"].add(movie["source"])
                if movie.get("content_type"):
                    options["content_types"].add(movie["content_type"])
            
            # Convert sets to sorted lists
            return {
                "genres": sorted(list(options["genres"])),
                "subgenres": sorted(list(options["subgenres"])),
                "languages": sorted(list(options["languages"])),
                "countries": sorted(list(options["countries"])),
                "years": sorted(list(options["years"]), reverse=True),
                "production_houses": sorted(list(options["production_houses"])),
                "sources": sorted(list(options["sources"])),
                "content_types": sorted(list(options["content_types"]))
            }
            
        except Exception as e:
            logger.error(f"Get filter options error: {e}")
            return {
                "genres": [], "subgenres": [], "languages": [],
                "countries": [], "years": [], "production_houses": [],
                "sources": [], "content_types": []
            }
    
    async def get_search_stats(self) -> Dict[str, Any]:
        """
        Get search statistics and system information.
        
        Returns:
            Dictionary with system metrics
        """
        try:
            # Get index info
            index_info = self.redis_service.get_index_info()
            
            # Get total document count
            total_movies = self.redis_service.get_document_count()
            
            # Calculate index size (approximate)
            index_size_mb = float(index_info.get("inverted_sz_mb", 0)) + float(index_info.get("doc_table_size_mb", 0))
            
            return {
                "total_movies": total_movies,
                "search_time_ms": 0.0,  # Will be set by individual searches
                "index_size_mb": round(index_size_mb, 2),
                "last_updated": index_info.get("indexing", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Get search stats error: {e}")
            return {
                "total_movies": 0,
                "search_time_ms": 0.0,
                "index_size_mb": 0.0,
                "last_updated": "unknown"
            }
    
    def _build_sort_options(self, sort_field: str, sort_direction: str) -> Optional[str]:
        """Build sort options for RedisSearch."""
        if sort_field == "relevance":
            return None  # Use default relevance scoring
        
        # Map GraphQL sort fields to RedisSearch fields
        field_mapping = {
            "title": "title",
            "imdb_rating": "imdb_rating",
            "year": "year",
            "popu": "popu",
            "modified_time": "modified_time"
        }
        
        redis_field = field_mapping.get(sort_field)
        if not redis_field:
            return None
        
        direction = "ASC" if sort_direction.lower() == "asc" else "DESC"
        return f"{redis_field} {direction}"
    
    def _get_total_count(self, query: str) -> int:
        """Get total count of matching documents."""
        try:
            # Execute a count query with limit 0 to get total count
            result = self.redis_service.redis_client.execute_command("FT.SEARCH", self.redis_service.index_name, query, "LIMIT", "0", "0")
            if result and len(result) > 0:
                return int(result[0])  # First element is the total count
            return 0
        except Exception as e:
            logger.error(f"Get total count error: {e}")
            return 0
    
    def _is_valid_genre(self, genre: str) -> bool:
        """
        Check if a genre string is valid (not a folder ID, year, or invalid data).
        
        Args:
            genre: Genre string to validate
            
        Returns:
            True if valid genre, False otherwise
        """
        if not genre or genre == 'Unknown':
            return False
        
        # Filter out years (numeric strings between 1900-2030)
        try:
            year_value = int(genre)
            if 1900 <= year_value <= 2030:
                return False
        except (ValueError, TypeError):
            pass  # Not a year, continue validation
        
        # Filter out folder IDs (long alphanumeric strings)
        if len(genre) > 15:
            alnum_chars = sum(1 for c in genre if c.isalnum())
            total_chars = len(genre)
            if alnum_chars / total_chars > 0.8:  # Mostly alphanumeric
                return False
        
        # Filter out strings that look like folder IDs
        if genre.startswith('1') and len(genre) > 15:
            return False
        
        return True
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Get dashboard statistics from the search index.
        
        Returns:
            Dictionary containing dashboard statistics
        """
        try:
            # Get all movies for statistics
            all_movies = self.redis_service.search("*", limit=10000)  # Get all movies
            
            if not all_movies:
                return {
                    "total_movies": 0,
                    "average_rating": 0.0,
                    "top_genre": "Unknown",
                    "latest_year": 0,
                    "top_5_genres": [],
                    "yearly_stats": []
                }
            
            # Calculate basic statistics
            total_movies = len(all_movies)
            ratings = [float(movie.get('imdb_rating', 0)) for movie in all_movies if movie.get('imdb_rating')]
            average_rating = sum(ratings) / len(ratings) if ratings else 0.0
            
            # Get years and find latest
            years = [int(movie.get('year', 0)) for movie in all_movies if movie.get('year')]
            latest_year = max(years) if years else 0
            
            # Calculate genre statistics
            genre_counts = {}
            for movie in all_movies:
                genre = movie.get('genre', 'Unknown')
                if self._is_valid_genre(genre):
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            # Get top genre
            top_genre = max(genre_counts.items(), key=lambda x: x[1])[0] if genre_counts else "Unknown"
            
            # Get top 5 genres
            top_5_genres = [
                {"name": genre, "count": count}
                for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            ]
            
            # Calculate yearly statistics
            yearly_data = {}
            for movie in all_movies:
                year = int(movie.get('year', 0))
                if year > 0:
                    if year not in yearly_data:
                        yearly_data[year] = {
                            'movies': [],
                            'genres': [],
                            'ratings': []
                        }
                    
                    yearly_data[year]['movies'].append(movie.get('title', 'Unknown'))
                    yearly_data[year]['genres'].append(movie.get('genre', 'Unknown'))
                    if movie.get('imdb_rating'):
                        yearly_data[year]['ratings'].append(float(movie.get('imdb_rating', 0)))
            
            # Build yearly stats
            yearly_stats = []
            for year in sorted(yearly_data.keys(), reverse=True):
                year_data = yearly_data[year]
                
                # Count genres for this year
                year_genre_counts = {}
                for genre in year_data['genres']:
                    if self._is_valid_genre(genre):
                        year_genre_counts[genre] = year_genre_counts.get(genre, 0) + 1
                
                # Get top genres for this year
                top_genres = [
                    genre for genre, count in 
                    sorted(year_genre_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                ]
                
                # Get top movies for this year (by rating)
                movies_with_ratings = [
                    (movie, float(movie_data.get('imdb_rating', 0)))
                    for movie, movie_data in zip(year_data['movies'], all_movies)
                    if movie_data.get('imdb_rating')
                ]
                top_movies = [
                    movie for movie, rating in 
                    sorted(movies_with_ratings, key=lambda x: x[1], reverse=True)[:3]
                ]
                
                # Calculate average rating for this year
                year_avg_rating = sum(year_data['ratings']) / len(year_data['ratings']) if year_data['ratings'] else 0.0
                
                yearly_stats.append({
                    "year": year,
                    "count": len(year_data['movies']),
                    "top_genres": top_genres,
                    "top_movies": top_movies,
                    "average_rating": round(year_avg_rating, 1)
                })
            
            # Get top-rated movies (sorted by rating, descending)
            movies_with_ratings = [
                {
                    "title": movie.get('title', 'Unknown'),
                    "year": int(movie.get('year', 0)),
                    "genre": movie.get('genre', 'Unknown'),
                    "rating": float(movie.get('imdb_rating', 0)),
                    "director": movie.get('director', 'Unknown')
                }
                for movie in all_movies
                if movie.get('imdb_rating') and movie.get('title')
            ]
            
            # Sort by rating (highest first)
            top_rated_movies = sorted(movies_with_ratings, key=lambda x: x['rating'], reverse=True)
            
            return {
                "total_movies": total_movies,
                "average_rating": round(average_rating, 1),
                "top_genre": top_genre,
                "latest_year": latest_year,
                "top_5_genres": top_5_genres,
                "yearly_stats": yearly_stats,
                "top_rated_movies": top_rated_movies
            }
            
        except Exception as e:
            logger.error(f"Get dashboard stats error: {e}")
            return {
                "total_movies": 0,
                "average_rating": 0.0,
                "top_genre": "Unknown",
                "latest_year": 0,
                "top_5_genres": [],
                "yearly_stats": [],
                "top_rated_movies": []
            }
    
    async def create_movie(self, movie_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new movie record."""
        try:
            # Generate a unique ID for the new movie
            import uuid
            movie_id = f"movie_{uuid.uuid4().hex[:12]}"
            
            # Prepare the document data
            document_data = {
                "id": movie_id,
                "title": movie_data.get("title", ""),
                "year": int(movie_data.get("year", 0)),
                "genre": movie_data.get("genre", "unknown"),
                "subgenre": movie_data.get("subgenre", "unknown"),
                "director": movie_data.get("director", ""),
                "stars": movie_data.get("stars", ""),
                "writer": movie_data.get("writer", ""),
                "content": movie_data.get("content", ""),
                "movie_plot": movie_data.get("movie_plot", ""),
                "awards": movie_data.get("awards", ""),
                "imdb_rating": float(movie_data.get("imdb_rating", 0.0)),
                "language": movie_data.get("language", "English"),
                "country": movie_data.get("country", ""),
                "production_house": movie_data.get("production_house", ""),
                "source": "manual_entry",
                "content_type": "movies",
                "limited_to": movie_data.get("limited_to", ""),
                "restricted_to": movie_data.get("restricted_to", ""),
                "created_at": int(time.time()),
                "updated_at": int(time.time())
            }
            
            # Add the document to RedisSearch
            success = self.redis_service.add_document(self.index_name, movie_id, document_data)
            
            if success:
                logger.info(f"Successfully created movie: {movie_id}")
                return {"success": True, "id": movie_id, "message": "Movie created successfully"}
            else:
                logger.error(f"Failed to create movie: {movie_id}")
                return {"success": False, "message": "Failed to create movie"}
                
        except Exception as e:
            logger.error(f"Error creating movie: {e}")
            return {"success": False, "message": f"Error creating movie: {str(e)}"}
    
    async def update_movie(self, movie_id: str, movie_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing movie record."""
        try:
            # First, get the existing document to preserve some fields
            existing_doc = self.redis_service.get_document(movie_id)
            if not existing_doc:
                return {"success": False, "message": "Movie not found"}
            
            # Prepare the updated document data
            document_data = {
                "id": movie_id,
                "title": movie_data.get("title", existing_doc.get("title", "")),
                "year": int(movie_data.get("year", existing_doc.get("year", 0))),
                "genre": movie_data.get("genre", existing_doc.get("genre", "unknown")),
                "subgenre": movie_data.get("subgenre", existing_doc.get("subgenre", "unknown")),
                "director": movie_data.get("director", existing_doc.get("director", "")),
                "stars": movie_data.get("stars", existing_doc.get("stars", "")),
                "writer": movie_data.get("writer", existing_doc.get("writer", "")),
                "content": movie_data.get("content", existing_doc.get("content", "")),
                "movie_plot": movie_data.get("movie_plot", existing_doc.get("movie_plot", "")),
                "awards": movie_data.get("awards", existing_doc.get("awards", "")),
                "imdb_rating": float(movie_data.get("imdb_rating", existing_doc.get("imdb_rating", 0.0))),
                "language": movie_data.get("language", existing_doc.get("language", "English")),
                "country": movie_data.get("country", existing_doc.get("country", "")),
                "production_house": movie_data.get("production_house", existing_doc.get("production_house", "")),
                "source": existing_doc.get("source", "manual_entry"),
                "content_type": existing_doc.get("content_type", "movies"),
                "limited_to": movie_data.get("limited_to", existing_doc.get("limited_to", "")),
                "restricted_to": movie_data.get("restricted_to", existing_doc.get("restricted_to", "")),
                "created_at": existing_doc.get("created_at", int(time.time())),
                "updated_at": int(time.time())
            }
            
            # Update the document in RedisSearch
            success = self.redis_service.add_document(self.index_name, movie_id, document_data)
            
            if success:
                logger.info(f"Successfully updated movie: {movie_id}")
                return {"success": True, "id": movie_id, "message": "Movie updated successfully"}
            else:
                logger.error(f"Failed to update movie: {movie_id}")
                return {"success": False, "message": "Failed to update movie"}
                
        except Exception as e:
            logger.error(f"Error updating movie: {e}")
            return {"success": False, "message": f"Error updating movie: {str(e)}"}
    
    async def delete_movie(self, movie_id: str) -> Dict[str, Any]:
        """Delete a movie record."""
        try:
            # Delete the document from RedisSearch
            success = self.redis_service.delete_document(movie_id)
            
            if success:
                logger.info(f"Successfully deleted movie: {movie_id}")
                return {"success": True, "message": "Movie deleted successfully"}
            else:
                logger.error(f"Failed to delete movie: {movie_id}")
                return {"success": False, "message": "Failed to delete movie"}
                
        except Exception as e:
            logger.error(f"Error deleting movie: {e}")
            return {"success": False, "message": f"Error deleting movie: {str(e)}"}
    
    async def get_movie_by_id(self, movie_id: str) -> Dict[str, Any]:
        """Get a specific movie by ID."""
        try:
            document = self.redis_service.get_document(movie_id)
            if document:
                return {"success": True, "movie": document}
            else:
                return {"success": False, "message": "Movie not found"}
        except Exception as e:
            logger.error(f"Error getting movie: {e}")
            return {"success": False, "message": f"Error getting movie: {str(e)}"}

