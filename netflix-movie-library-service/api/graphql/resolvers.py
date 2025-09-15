"""
GraphQL Resolvers for Movie Search API

Implements the business logic for handling GraphQL queries
and communicating with the RedisSearch service.
"""

from typing import List, Optional, Dict, Any
from strawberry import field, type
from loguru import logger
import time
import math

# Import RedisSearch service
import sys
import os
# Add the netflix-movie-library-connector project to the path
connector_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "netflix-movie-library-connector")
sys.path.insert(0, connector_path)
from services.redis_search_service import RedisSearchService

from .types import (
    Movie, SearchResult, SearchSuggestions, FilterOptions, 
    SearchStats, SearchQuery, SearchInput, PaginationInput, SortInput,
    DashboardStats, GenreStats, YearlyStats, TopRatedMovie,
    MovieInput, MovieResponse, MoviesListResponse,
    AdvancedSearchInput, AdvancedSearchResult, MovieFilters,
    YearRange, RatingRange, PopularityRange, FacetData, FacetValue
)


@type
class Query:
    """Root GraphQL query type."""
    
    @field
    async def search_movies(
        self,
        search: SearchInput,
        pagination: Optional[PaginationInput] = None,
        sort: Optional[SortInput] = None
    ) -> SearchResult:
        """
        Search for movies based on various criteria.
        
        Args:
            search: Search criteria including query, filters, etc.
            pagination: Pagination options (page, page_size)
            sort: Sorting options (field, direction)
            
        Returns:
            SearchResult with movies and metadata
        """
        try:
            from api.services.search_service import SearchService
            search_service = SearchService()
            
            # Build search query from SearchInput
            query = search_service.build_search_query(
                search_query=search.query or "",
                genre=search.genre,
                subgenre=search.subgenre,
                language=search.language,
                country=search.country,
                year_from=search.year_from,
                year_to=search.year_to,
                rating_min=search.rating_min,
                rating_max=search.rating_max,
                production_house=search.production_house,
                director=search.director,
                actor=search.actor
            )
            
            # Extract pagination parameters
            page = pagination.page if pagination else 1
            page_size = pagination.page_size if pagination else 20
            
            # Extract sort parameters
            sort_field = sort.field if sort else "relevance"
            sort_direction = sort.direction if sort else "desc"
            
            result = await search_service.search_movies(
                query=query,
                page=page,
                page_size=page_size,
                sort_field=sort_field,
                sort_direction=sort_direction
            )
            
            # Convert to SearchResult format
            from .types import SearchResult, Movie
            movies = []
            for movie_data in result.get("movies", []):
                movie = Movie(
                    id=movie_data.get("id", ""),
                    file_id=movie_data.get("file_id", ""),
                    title=movie_data.get("title", ""),
                    movie_plot=movie_data.get("movie_plot", ""),
                    content=movie_data.get("content", ""),
                    director=movie_data.get("director", ""),
                    writer=movie_data.get("writer", ""),
                    stars=movie_data.get("stars", []) if isinstance(movie_data.get("stars"), list) else (movie_data.get("stars", "").split(', ') if movie_data.get("stars") else []),
                    imdb_rating=float(movie_data.get("imdb_rating", 0.0)),
                    popu=int(movie_data.get("popu", 0)),
                    genre=movie_data.get("genre", ""),
                    subgenre=movie_data.get("subgenre", ""),
                    language=movie_data.get("language", ""),
                    production_house=movie_data.get("production_house", ""),
                    source=movie_data.get("source", ""),
                    country=movie_data.get("country", ""),
                    awards=movie_data.get("awards", []) if isinstance(movie_data.get("awards"), list) else (movie_data.get("awards", "").split(', ') if movie_data.get("awards") else []),
                    year=int(movie_data.get("year", 0)),
                    modified_time=movie_data.get("modified_time", ""),
                    folder_path=movie_data.get("folder_path", ""),
                    file_name=movie_data.get("file_name", ""),
                    url=movie_data.get("url", ""),
                    content_type=movie_data.get("content_type", ""),
                    limited_to=movie_data.get("limited_to", ""),
                    restricted_to=movie_data.get("restricted_to", ""),
                    created_at=movie_data.get("created_at", ""),
                    updated_at=movie_data.get("updated_at", "")
                )
                movies.append(movie)
            
            return SearchResult(
                movies=movies,
                total_count=result.get("total_count", 0),
                page=page,
                page_size=page_size,
                total_pages=(result.get("total_count", 0) + page_size - 1) // page_size,
                has_next=page < ((result.get("total_count", 0) + page_size - 1) // page_size),
                has_previous=page > 1
            )
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise Exception(f"Search failed: {str(e)}")
    
    @field
    async def advanced_search_movies(
        self,
        search: AdvancedSearchInput
    ) -> AdvancedSearchResult:
        """
        Advanced search for movies with comprehensive filtering.
        
        Args:
            search: Advanced search criteria
            
        Returns:
            AdvancedSearchResult with movies, facets, and metadata
        """
        try:
            start_time = time.time()
            
            # Initialize RedisSearch service
            redis_service = RedisSearchService()
            
            # Build search query
            query = search.query or "*"
            
            # Build filters
            filters = []
            
            # TAG field filters
            if search.filters and search.filters.genres:
                genre_filter = " OR ".join([f"@genre:{{{genre}}}" for genre in search.filters.genres])
                filters.append(f"({genre_filter})")
            
            if search.filters and search.filters.subgenres:
                subgenre_filter = " OR ".join([f"@subgenre:{{{subgenre}}}" for subgenre in search.filters.subgenres])
                filters.append(f"({subgenre_filter})")
            
            if search.filters and search.filters.languages:
                language_filter = " OR ".join([f"@language:{{{language}}}" for language in search.filters.languages])
                filters.append(f"({language_filter})")
            
            if search.filters and search.filters.production_houses:
                prod_filter = " OR ".join([f"@production_house:{{{prod}}}" for prod in search.filters.production_houses])
                filters.append(f"({prod_filter})")
            
            if search.filters and search.filters.sources:
                source_filter = " OR ".join([f"@source:{{{source}}}" for source in search.filters.sources])
                filters.append(f"({source_filter})")
            
            # NUMERIC range filters
            if search.filters and search.filters.year_range:
                year_filter = "@year:["
                year_filter += str(search.filters.year_range.min_year) if search.filters.year_range.min_year else "1900"
                year_filter += " "
                year_filter += str(search.filters.year_range.max_year) if search.filters.year_range.max_year else "2030"
                year_filter += "]"
                filters.append(year_filter)
            
            if search.filters and search.filters.rating_range:
                rating_filter = "@imdb_rating:["
                rating_filter += str(search.filters.rating_range.min_rating) if search.filters.rating_range.min_rating else "0"
                rating_filter += " "
                rating_filter += str(search.filters.rating_range.max_rating) if search.filters.rating_range.max_rating else "10"
                rating_filter += "]"
                filters.append(rating_filter)
            
            if search.filters and search.filters.popularity_range:
                pop_filter = "@popu:["
                pop_filter += str(search.filters.popularity_range.min_popularity) if search.filters.popularity_range.min_popularity else "0"
                pop_filter += " "
                pop_filter += str(search.filters.popularity_range.max_popularity) if search.filters.popularity_range.max_popularity else "1000000"
                pop_filter += "]"
                filters.append(pop_filter)
            
            # Text search filters
            if search.filters and search.filters.director:
                filters.append(f"@director:{search.filters.director}")
            
            if search.filters and search.filters.writer:
                filters.append(f"@writer:{search.filters.writer}")
            
            if search.filters and search.filters.stars:
                filters.append(f"@stars:{search.filters.stars}")
            
            if search.filters and search.filters.country:
                filters.append(f"@country:{search.filters.country}")
            
            if search.filters and search.filters.awards:
                filters.append(f"@awards:{search.filters.awards}")
            
            # Combine query with filters
            if filters:
                full_query = f"{query} {' '.join(filters)}"
            else:
                full_query = query
            
            # Build sort criteria
            sort_by = None
            if search.sort_field and search.sort_field != "relevance":
                sort_direction_str = "ASC" if search.sort_direction == "asc" else "DESC"
                sort_by = f"@{search.sort_field}:{sort_direction_str}"
            
            # Perform search
            page = search.page or 1
            page_size = min(search.page_size or 20, search.max_page_size or 100)
            
            logger.info(f"Advanced search with query: {full_query}")
            results = redis_service.search(full_query, limit=page_size, offset=(page - 1) * page_size, sort_by=sort_by)
            
            # Convert results to Movie objects
            movies = []
            for doc in results:
                movie = Movie(
                    id=doc.get('id', ''),
                    file_id=doc.get('file_id', ''),
                    title=doc.get('title', ''),
                    movie_plot=doc.get('movie_plot', ''),
                    content=doc.get('content', ''),
                    director=doc.get('director', ''),
                    writer=doc.get('writer', ''),
                    stars=doc.get('stars', []) if isinstance(doc.get('stars'), list) else (doc.get('stars', '').split(', ') if doc.get('stars') else []),
                    imdb_rating=doc.get('imdb_rating', 0.0),
                    popu=doc.get('popu', 0),
                    genre=doc.get('genre', ''),
                    subgenre=doc.get('subgenre', ''),
                    language=doc.get('language', ''),
                    production_house=doc.get('production_house', ''),
                    source=doc.get('source', ''),
                    country=doc.get('country', ''),
                    awards=doc.get('awards', []) if isinstance(doc.get('awards'), list) else (doc.get('awards', '').split(', ') if doc.get('awards') else []),
                    year=doc.get('year', 0),
                    modified_time=doc.get('modified_time', ''),
                    folder_path=doc.get('folder_path', ''),
                    file_name=doc.get('file_name', ''),
                    url=doc.get('url', ''),
                    content_type=doc.get('content_type', ''),
                    limited_to=doc.get('limited_to', ''),
                    restricted_to=doc.get('restricted_to', ''),
                    created_at=doc.get('created_at', ''),
                    updated_at=doc.get('updated_at', '')
                )
                movies.append(movie)
            
            # Get total count for pagination
            total_count = redis_service.get_document_count()
            
            # Calculate pagination info
            total_pages = (total_count + page_size - 1) // page_size
            search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Get facets if requested
            facets = None
            if search.include_facets:
                facets = await _get_facet_data(redis_service)
            
            logger.info(f"Advanced search completed: {len(movies)} movies found in {search_time:.2f}ms")
            
            return AdvancedSearchResult(
                movies=movies,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1,
                facets=facets,
                search_time_ms=search_time
            )
            
        except Exception as e:
            logger.error(f"Advanced search error: {e}")
            raise Exception(f"Advanced search failed: {str(e)}")
    
    @field
    async def get_movie_by_id(self, id: str) -> Optional[Movie]:
        """
        Get a specific movie by its ID.
        
        Args:
            id: Movie ID
            
        Returns:
            Movie object or None if not found
        """
        try:
            from api.services.search_service import SearchService
            search_service = SearchService()
            
            result = await search_service.get_movie_by_id(id)
            
            if not result or not result.get("success"):
                return None
            
            movie_data = result.get("movie", {})
            
            return Movie(
                id=movie_data.get("id", ""),
                file_id=movie_data.get("file_id", ""),
                title=movie_data.get("title", ""),
                movie_plot=movie_data.get("movie_plot", ""),
                content=movie_data.get("content", ""),
                director=movie_data.get("director", ""),
                writer=movie_data.get("writer", ""),
                stars=movie_data.get("stars", []) if isinstance(movie_data.get("stars"), list) else (movie_data.get("stars", "").split(', ') if movie_data.get("stars") else []),
                imdb_rating=movie_data.get("imdb_rating", 0.0),
                popu=movie_data.get("popu", 0),
                genre=movie_data.get("genre", ""),
                subgenre=movie_data.get("subgenre", ""),
                language=movie_data.get("language", ""),
                production_house=movie_data.get("production_house", ""),
                source=movie_data.get("source", ""),
                country=movie_data.get("country", ""),
                awards=movie_data.get("awards", []) if isinstance(movie_data.get("awards"), list) else (movie_data.get("awards", "").split(', ') if movie_data.get("awards") else []),
                year=movie_data.get("year", 0),
                modified_time=movie_data.get("modified_time", ""),
                folder_path=movie_data.get("folder_path", ""),
                file_name=movie_data.get("file_name", ""),
                url=movie_data.get("url", ""),
                content_type=movie_data.get("content_type", ""),
                limited_to=movie_data.get("limited_to", ""),
                restricted_to=movie_data.get("restricted_to", ""),
                created_at=movie_data.get("created_at", ""),
                updated_at=movie_data.get("updated_at", "")
            )
            
        except Exception as e:
            logger.error(f"Get movie by ID error: {e}")
            return None
    
    @field
    async def get_search_suggestions(
        self, 
        query: str, 
        limit: int = 10
    ) -> SearchSuggestions:
        """
        Get search suggestions for autocomplete functionality.
        
        Args:
            query: Search query text
            limit: Maximum number of suggestions to return
            
        Returns:
            SearchSuggestions object with various suggestion types
        """
        try:
            from api.services.search_service import SearchService
            search_service = SearchService()
            
            suggestions = await search_service.get_search_suggestions(query, limit)
            
            return SearchSuggestions(
                titles=suggestions.get('titles', []),
                genres=suggestions.get('genres', []),
                directors=suggestions.get('directors', []),
                actors=suggestions.get('actors', [])
            )
            
        except Exception as e:
            logger.error(f"Get suggestions error: {e}")
            raise Exception(f"Failed to get suggestions: {str(e)}")
    
    @field
    async def get_filter_options(self) -> FilterOptions:
        """
        Get available filter options for the search interface.
        
        Returns:
            FilterOptions object with all available filter values
        """
        try:
            from api.services.search_service import SearchService
            search_service = SearchService()
            
            options = await search_service.get_filter_options()
            
            return FilterOptions(
                genres=options.get('genres', []),
                subgenres=options.get('subgenres', []),
                languages=options.get('languages', []),
                countries=options.get('countries', []),
                years=options.get('years', []),
                production_houses=options.get('production_houses', [])
            )
            
        except Exception as e:
            logger.error(f"Get filter options error: {e}")
            raise Exception(f"Failed to get filter options: {str(e)}")
    
    @field
    async def get_search_stats(self) -> SearchStats:
        """
        Get search statistics and system information.
        
        Returns:
            SearchStats object with system metrics
        """
        try:
            from api.services.search_service import SearchService
            search_service = SearchService()
            
            stats = await search_service.get_search_stats()
            
            return SearchStats(
                total_movies=stats.get('total_movies', 0),
                search_time_ms=stats.get('search_time_ms', 0.0),
                index_size_mb=stats.get('index_size_mb', 0.0),
                last_updated=stats.get('last_updated', '')
            )
            
        except Exception as e:
            logger.error(f"Get search stats error: {e}")
            raise Exception(f"Failed to get search stats: {str(e)}")
    
    @field
    async def get_dashboard_stats(self) -> DashboardStats:
        """
        Get dashboard statistics for the movie library.
        
        Returns:
            DashboardStats containing comprehensive statistics
        """
        try:
            # Initialize RedisSearch service
            redis_service = RedisSearchService()
            
            # Get basic stats
            total_movies = redis_service.get_document_count()
            
            # Get all movies for analysis
            all_movies = redis_service.search("*", limit=1000)
            
            # Calculate statistics
            genres = {}
            years = {}
            ratings = []
            
            for movie in all_movies:
                # Genre stats
                genre = movie.get('genre', 'Unknown')
                genres[genre] = genres.get(genre, 0) + 1
                
                # Year stats - handle both string and numeric years
                year = movie.get('year', 0)
                try:
                    year_int = int(year) if year else 0
                    if year_int > 1900 and year_int < 2030:  # Reasonable year range
                        years[year_int] = years.get(year_int, 0) + 1
                except (ValueError, TypeError):
                    pass
                
                # Rating stats - handle both string and numeric ratings
                rating = movie.get('imdb_rating', 0)
                try:
                    rating_float = float(rating) if rating else 0
                    if rating_float > 0:
                        ratings.append(rating_float)
                except (ValueError, TypeError):
                    pass
            
            # Top 5 genres
            top_5_genres = [
                GenreStats(name=genre, count=count)
                for genre, count in sorted(genres.items(), key=lambda x: x[1], reverse=True)[:5]
            ]
            
            # Yearly stats - use actual years from data, sorted by year
            yearly_stats = []
            for year in sorted(years.keys()):
                count = years[year]
                yearly_stats.append(YearlyStats(
                    year=year,
                    count=count,
                    top_genres=[g.name for g in top_5_genres[:3]],
                    top_movies=[],
                    average_rating=sum(ratings) / len(ratings) if ratings else 0.0
                ))
            
            # Top rated movies
            top_rated_movies = []
            # Sort by rating, handling string values
            def get_rating_value(movie):
                try:
                    return float(movie.get('imdb_rating', 0))
                except (ValueError, TypeError):
                    return 0.0
            
            for movie in sorted(all_movies, key=get_rating_value, reverse=True)[:5]:
                try:
                    year_int = int(movie.get('year', 0)) if movie.get('year') else 0
                except (ValueError, TypeError):
                    year_int = 0
                    
                top_rated_movies.append(TopRatedMovie(
                    title=movie.get('title', ''),
                    rating=get_rating_value(movie),
                    year=year_int,
                    genre=movie.get('genre', ''),
                    director=movie.get('director', '')
                ))
            
            # Get top genre
            top_genre = max(genres.items(), key=lambda x: x[1])[0] if genres else "Unknown"
            
            # Get latest year
            latest_year = max(years.keys()) if years else 2024
            
            return DashboardStats(
                total_movies=total_movies,
                average_rating=sum(ratings) / len(ratings) if ratings else 0.0,
                top_genre=top_genre,
                latest_year=latest_year,
                top_5_genres=top_5_genres,
                yearly_stats=yearly_stats,
                top_rated_movies=top_rated_movies
            )
            
        except Exception as e:
            logger.error(f"Get dashboard stats error: {e}")
            raise Exception(f"Failed to get dashboard stats: {str(e)}")


@type
class Mutation:
    """Root GraphQL mutation type."""
    
    @field
    async def create_movie(self, movie_data: MovieInput) -> MovieResponse:
        """
        Create a new movie in the database.
        
        Args:
            movie_data: Movie data to create
            
        Returns:
            MovieResponse with success status and movie data
        """
        try:
            from api.services.search_service import SearchService
            search_service = SearchService()
            
            result = await search_service.create_movie(movie_data)
            
            return MovieResponse(
                success=result["success"],
                message=result["message"],
                id=result.get("id"),
                movie=result.get("movie")
            )
            
        except Exception as e:
            logger.error(f"Create movie error: {e}")
            return MovieResponse(
                success=False,
                message=f"Failed to create movie: {str(e)}",
                id=None,
                movie=None
            )
    
    @field
    async def update_movie(self, movie_id: str, movie_data: MovieInput) -> MovieResponse:
        """
        Update an existing movie in the database.
        
        Args:
            movie_id: ID of the movie to update
            movie_data: Updated movie data
            
        Returns:
            MovieResponse with success status and updated movie data
        """
        try:
            from api.services.search_service import SearchService
            search_service = SearchService()
            
            result = await search_service.update_movie(movie_id, movie_data)
            
            return MovieResponse(
                success=result["success"],
                message=result["message"],
                id=movie_id,
                movie=result.get("movie")
            )
            
        except Exception as e:
            logger.error(f"Update movie error: {e}")
            return MovieResponse(
                success=False,
                message=f"Failed to update movie: {str(e)}",
                id=movie_id,
                movie=None
            )
    
    @field
    async def delete_movie(self, movie_id: str) -> MovieResponse:
        """
        Delete a movie from the database.
        
        Args:
            movie_id: ID of the movie to delete
            
        Returns:
            MovieResponse with success status
        """
        try:
            from api.services.search_service import SearchService
            search_service = SearchService()
            
            result = await search_service.delete_movie(movie_id)
            
            return MovieResponse(
                success=result["success"],
                message=result["message"],
                id=movie_id,
                movie=None
            )
            
        except Exception as e:
            logger.error(f"Delete movie error: {e}")
            return MovieResponse(
                success=False,
                message=f"Failed to delete movie: {str(e)}",
                id=None,
                movie=None
            )
    
    @field
    async def get_movie(self, movie_id: str) -> MovieResponse:
        """
        Get a specific movie by ID.
        
        Args:
            movie_id: ID of the movie to retrieve
            
        Returns:
            MovieResponse with movie data
        """
        try:
            from api.services.search_service import SearchService
            search_service = SearchService()
            
            result = await search_service.get_movie_by_id(movie_id)
            
            if result["success"]:
                movie_data = result["movie"]
                # Convert to Movie type
                movie = Movie(
                    id=movie_data.get("id", ""),
                    title=movie_data.get("title", ""),
                    imdb_rating=float(movie_data.get("imdb_rating", 0.0)),
                    language=movie_data.get("language", "English"),
                    country=movie_data.get("country", ""),
                    stars=movie_data.get("stars", "").split(",") if movie_data.get("stars") else [],
                    director=movie_data.get("director", ""),
                    writer=movie_data.get("writer", ""),
                    movie_plot=movie_data.get("movie_plot", ""),
                    awards=movie_data.get("awards", "").split(",") if movie_data.get("awards") else [],
                    year=int(movie_data.get("year", 0)),
                    genre=movie_data.get("genre", ""),
                    subgenre=movie_data.get("subgenre", ""),
                    production_house=movie_data.get("production_house", ""),
                    source=movie_data.get("source", ""),
                    file_id=movie_data.get("file_id", ""),
                    content=movie_data.get("content", ""),
                    folder_path=movie_data.get("folder_path", ""),
                    file_name=movie_data.get("file_name", ""),
                    url=movie_data.get("url", ""),
                    content_type=movie_data.get("content_type", ""),
                    limited_to=movie_data.get("limited_to", ""),
                    restricted_to=movie_data.get("restricted_to", ""),
                    modified_time=movie_data.get("modified_time", ""),
                    created_at=movie_data.get("created_at", ""),
                    updated_at=movie_data.get("updated_at", ""),
                    popu=int(movie_data.get("popu", 0))
                )
                
                return MovieResponse(
                    success=True,
                    message="Movie retrieved successfully",
                    id=movie_id,
                    movie=movie
                )
            else:
                return MovieResponse(
                    success=False,
                    message=result["message"],
                    id=movie_id,
                    movie=None
                )
                
        except Exception as e:
            logger.error(f"Get movie error: {e}")
            return MovieResponse(
                success=False,
                message=f"Failed to get movie: {str(e)}",
                id=movie_id,
                movie=None
            )


async def _get_facet_data(redis_service: RedisSearchService) -> List[FacetData]:
    """Get faceted search data for filter options."""
    try:
        facets = []
        
        # Get genre facets
        genre_facets = redis_service.search("*", limit=0)  # Get all for faceting
        genre_counts = {}
        for doc in genre_facets:
            genre = doc.get('genre', '')
            if genre:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        if genre_counts:
            facets.append(FacetData(
                field="genre",
                values=[FacetValue(value=k, count=v) for k, v in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)]
            ))
        
        # Get language facets
        language_counts = {}
        for doc in genre_facets:
            language = doc.get('language', '')
            if language:
                language_counts[language] = language_counts.get(language, 0) + 1
        
        if language_counts:
            facets.append(FacetData(
                field="language",
                values=[FacetValue(value=k, count=v) for k, v in sorted(language_counts.items(), key=lambda x: x[1], reverse=True)]
            ))
        
        # Get production house facets
        prod_counts = {}
        for doc in genre_facets:
            prod = doc.get('production_house', '')
            if prod:
                prod_counts[prod] = prod_counts.get(prod, 0) + 1
        
        if prod_counts:
            facets.append(FacetData(
                field="production_house",
                values=[FacetValue(value=k, count=v) for k, v in sorted(prod_counts.items(), key=lambda x: x[1], reverse=True)]
            ))
        
        return facets
        
    except Exception as e:
        logger.error(f"Error getting facet data: {e}")
        return []