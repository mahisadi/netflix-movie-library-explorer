"""
REST API Routes for Movie Search

Provides REST endpoints for movie search functionality using RedisSearch.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from loguru import logger
import time
import sys
import os

# Add the netflix-movie-library-connector project to the path
connector_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "netflix-movie-library-connector")
sys.path.insert(0, connector_path)

from services.redis_search_service import RedisSearchService

router = APIRouter(prefix="/api/movies", tags=["movies"])


# Pydantic models for request/response
class MovieSearchRequest(BaseModel):
    """Request model for movie search."""
    query: Optional[str] = Field(None, description="Search query text")
    page: int = Field(1, ge=1, description="Page number (1-based)")
    page_size: int = Field(20, ge=1, le=100, description="Number of results per page")
    sort_field: Optional[str] = Field("relevance", description="Field to sort by")
    sort_direction: Optional[str] = Field("desc", description="Sort direction (asc/desc)")
    
    # TAG field filters
    genres: Optional[List[str]] = Field(None, description="Filter by genres")
    subgenres: Optional[List[str]] = Field(None, description="Filter by subgenres")
    languages: Optional[List[str]] = Field(None, description="Filter by languages")
    production_houses: Optional[List[str]] = Field(None, description="Filter by production houses")
    sources: Optional[List[str]] = Field(None, description="Filter by data sources")
    
    # NUMERIC range filters
    min_year: Optional[int] = Field(None, ge=1900, le=2030, description="Minimum year")
    max_year: Optional[int] = Field(None, ge=1900, le=2030, description="Maximum year")
    min_rating: Optional[float] = Field(None, ge=0.0, le=10.0, description="Minimum IMDB rating")
    max_rating: Optional[float] = Field(None, ge=0.0, le=10.0, description="Maximum IMDB rating")
    min_popularity: Optional[int] = Field(None, ge=0, description="Minimum popularity score")
    max_popularity: Optional[int] = Field(None, ge=0, description="Maximum popularity score")
    
    # Text search filters
    director: Optional[str] = Field(None, description="Filter by director name")
    writer: Optional[str] = Field(None, description="Filter by writer name")
    stars: Optional[str] = Field(None, description="Filter by actor/actress name")
    
    # Faceted search
    include_facets: bool = Field(False, description="Include faceted search data")


class MovieResponse(BaseModel):
    """Response model for a single movie."""
    id: str
    file_id: str
    title: str
    movie_plot: str
    content: str
    director: str
    writer: str
    stars: List[str]
    imdb_rating: float
    popu: int
    genre: str
    subgenre: str
    language: str
    production_house: str
    source: str
    country: str
    awards: List[str]
    year: int
    modified_time: str
    folder_path: str
    file_name: str
    url: str
    content_type: str
    limited_to: str
    restricted_to: str
    created_at: str
    updated_at: str


class FacetValue(BaseModel):
    """Facet value with count."""
    value: str
    count: int


class FacetData(BaseModel):
    """Faceted search data."""
    field: str
    values: List[FacetValue]


class MovieSearchResponse(BaseModel):
    """Response model for movie search results."""
    movies: List[MovieResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    facets: Optional[List[FacetData]] = None
    search_time_ms: float


class FilterOptionsResponse(BaseModel):
    """Response model for available filter options."""
    genres: List[str]
    subgenres: List[str]
    languages: List[str]
    countries: List[str]
    years: List[int]
    production_houses: List[str]


# Dependency to get RedisSearch service
def get_redis_service() -> RedisSearchService:
    """Get RedisSearch service instance."""
    return RedisSearchService()


@router.post("/search", response_model=MovieSearchResponse)
async def search_movies(
    request: MovieSearchRequest,
    redis_service: RedisSearchService = Depends(get_redis_service)
):
    """
    Search for movies with advanced filtering using RedisSearch.
    
    Supports:
    - Full-text search across movie content
    - TAG field filtering (genres, languages, etc.)
    - NUMERIC range filtering (year, rating, popularity)
    - Sorting by various fields
    - Pagination
    - Faceted search data
    """
    try:
        start_time = time.time()
        
        # Build search query
        query = request.query or "*"
        
        # Build filters for RedisSearch
        filters = {}
        
        # TAG field filters
        if request.genres:
            filters['genre'] = request.genres
        if request.subgenres:
            filters['subgenre'] = request.subgenres
        if request.languages:
            filters['language'] = request.languages
        if request.production_houses:
            filters['production_house'] = request.production_houses
        if request.sources:
            filters['source'] = request.sources
        
        # NUMERIC range filters
        if request.min_year is not None and request.max_year is not None:
            filters['year'] = f"({request.min_year} {request.max_year})"
        elif request.min_year is not None:
            filters['year'] = f"({request.min_year} +inf)"
        elif request.max_year is not None:
            filters['year'] = f"(-inf {request.max_year})"
        
        if request.min_rating is not None and request.max_rating is not None:
            filters['imdb_rating'] = f"({request.min_rating} {request.max_rating})"
        elif request.min_rating is not None:
            filters['imdb_rating'] = f"({request.min_rating} +inf)"
        elif request.max_rating is not None:
            filters['imdb_rating'] = f"(-inf {request.max_rating})"
        
        if request.min_popularity is not None and request.max_popularity is not None:
            filters['popu'] = f"({request.min_popularity} {request.max_popularity})"
        elif request.min_popularity is not None:
            filters['popu'] = f"({request.min_popularity} +inf)"
        elif request.max_popularity is not None:
            filters['popu'] = f"(-inf {request.max_popularity})"
        
        # Build sort field
        sort_by = None
        if request.sort_field and request.sort_field != "relevance":
            direction = "ASC" if request.sort_direction == "asc" else "DESC"
            sort_by = f"{request.sort_field} {direction}"
        
        # Calculate pagination
        offset = (request.page - 1) * request.page_size
        
        # Perform search
        if filters:
            # Use advanced_search for complex filtering
            documents = redis_service.advanced_search(
                query=query,
                filters=filters,
                sort_by=sort_by,
                offset=offset,
                limit=request.page_size
            )
        else:
            # Use regular search for simple queries
            documents = redis_service.search(
                query=query,
                offset=offset,
                limit=request.page_size,
                sort_by=sort_by
            )
        
        # Convert documents to MovieResponse objects
        movies = []
        for movie_data in documents:
            # Handle stars field
            stars = movie_data.get('stars', [])
            if isinstance(stars, str):
                try:
                    import json
                    stars = json.loads(stars) if stars else []
                except:
                    stars = [stars] if stars else []
            elif not isinstance(stars, list):
                stars = []
            
            # Handle awards field
            awards = movie_data.get('awards', [])
            if isinstance(awards, str):
                try:
                    import json
                    awards = json.loads(awards) if awards else []
                except:
                    awards = [awards] if awards else []
            elif not isinstance(awards, list):
                awards = []

            movie = MovieResponse(
                id=movie_data.get('id', ''),
                file_id=movie_data.get('file_id', ''),
                title=movie_data.get('title', ''),
                movie_plot=movie_data.get('movie_plot', ''),
                content=movie_data.get('content', ''),
                director=movie_data.get('director', ''),
                writer=movie_data.get('writer', ''),
                stars=stars,
                imdb_rating=float(movie_data.get('imdb_rating', 0.0)),
                popu=int(movie_data.get('popu', 0)),
                genre=movie_data.get('genre', ''),
                subgenre=movie_data.get('subgenre', ''),
                language=movie_data.get('language', ''),
                production_house=movie_data.get('production_house', ''),
                source=movie_data.get('source', ''),
                country=movie_data.get('country', ''),
                awards=awards,
                year=int(movie_data.get('year', 0)),
                modified_time=movie_data.get('modified_time', ''),
                folder_path=movie_data.get('folder_path', ''),
                file_name=movie_data.get('file_name', ''),
                url=movie_data.get('url', ''),
                content_type=movie_data.get('content_type', ''),
                limited_to=movie_data.get('limited_to', ''),
                restricted_to=movie_data.get('restricted_to', ''),
                created_at=str(movie_data.get('created_at', '')),
                updated_at=str(movie_data.get('updated_at', ''))
            )
            movies.append(movie)
        
        # Get total count for pagination
        total_count = redis_service.get_document_count()
        
        # Calculate pagination info
        total_pages = (total_count + request.page_size - 1) // request.page_size
        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Get facets if requested
        facets = None
        if request.include_facets:
            facets = await _get_facet_data(redis_service)
        
        logger.info(f"REST search completed: {len(movies)} movies found in {search_time:.2f}ms")
        
        return MovieSearchResponse(
            movies=movies,
            total_count=total_count,
            page=request.page,
            page_size=request.page_size,
            total_pages=total_pages,
            has_next=request.page < total_pages,
            has_previous=request.page > 1,
            facets=facets,
            search_time_ms=search_time
        )
        
    except Exception as e:
        logger.error(f"REST search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/search", response_model=MovieSearchResponse)
async def search_movies_get(
    q: Optional[str] = Query(None, description="Search query text"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of results per page"),
    sort_field: Optional[str] = Query("relevance", description="Field to sort by"),
    sort_direction: Optional[str] = Query("desc", description="Sort direction (asc/desc)"),
    genres: Optional[str] = Query(None, description="Comma-separated list of genres"),
    subgenres: Optional[str] = Query(None, description="Comma-separated list of subgenres"),
    languages: Optional[str] = Query(None, description="Comma-separated list of languages"),
    production_houses: Optional[str] = Query(None, description="Comma-separated list of production houses"),
    sources: Optional[str] = Query(None, description="Comma-separated list of data sources"),
    min_year: Optional[int] = Query(None, ge=1900, le=2030, description="Minimum year"),
    max_year: Optional[int] = Query(None, ge=1900, le=2030, description="Maximum year"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=10.0, description="Minimum IMDB rating"),
    max_rating: Optional[float] = Query(None, ge=0.0, le=10.0, description="Maximum IMDB rating"),
    min_popularity: Optional[int] = Query(None, ge=0, description="Minimum popularity score"),
    max_popularity: Optional[int] = Query(None, ge=0, description="Maximum popularity score"),
    director: Optional[str] = Query(None, description="Filter by director name"),
    writer: Optional[str] = Query(None, description="Filter by writer name"),
    stars: Optional[str] = Query(None, description="Filter by star names"),
    country: Optional[str] = Query(None, description="Filter by country"),
    awards: Optional[str] = Query(None, description="Filter by awards"),
    redis_service: RedisSearchService = Depends(get_redis_service)
):
    """
    Search for movies with advanced filtering using RedisSearch (GET endpoint).
    
    Supports:
    - Full-text search across movie content
    - TAG field filtering (genres, languages, etc.)
    - NUMERIC range filtering (year, rating, popularity)
    - Sorting by various fields
    - Pagination
    - Faceted search data
    """
    try:
        start_time = time.time()
        
        # Build search query
        query = q or "*"
        
        # Parse comma-separated lists
        genre_list = genres.split(",") if genres else None
        subgenre_list = subgenres.split(",") if subgenres else None
        language_list = languages.split(",") if languages else None
        production_house_list = production_houses.split(",") if production_houses else None
        source_list = sources.split(",") if sources else None
        
        # Build filters
        filters = []
        
        # TAG field filters
        if genre_list:
            genre_filter = " OR ".join([f"@genre:{{{genre.strip()}}}" for genre in genre_list])
            filters.append(f"({genre_filter})")
        
        if subgenre_list:
            subgenre_filter = " OR ".join([f"@subgenre:{{{subgenre.strip()}}}" for subgenre in subgenre_list])
            filters.append(f"({subgenre_filter})")
        
        if language_list:
            language_filter = " OR ".join([f"@language:{{{language.strip()}}}" for language in language_list])
            filters.append(f"({language_filter})")
        
        if production_house_list:
            prod_filter = " OR ".join([f"@production_house:{{{prod.strip()}}}" for prod in production_house_list])
            filters.append(f"({prod_filter})")
        
        if source_list:
            source_filter = " OR ".join([f"@source:{{{source.strip()}}}" for source in source_list])
            filters.append(f"({source_filter})")
        
        # NUMERIC range filters
        if min_year is not None or max_year is not None:
            year_filter = "@year:["
            year_filter += str(min_year) if min_year is not None else "1900"
            year_filter += " "
            year_filter += str(max_year) if max_year is not None else "2030"
            year_filter += "]"
            filters.append(year_filter)
        
        if min_rating is not None or max_rating is not None:
            rating_filter = "@imdb_rating:["
            rating_filter += str(min_rating) if min_rating is not None else "0"
            rating_filter += " "
            rating_filter += str(max_rating) if max_rating is not None else "10"
            rating_filter += "]"
            filters.append(rating_filter)
        
        if min_popularity is not None or max_popularity is not None:
            pop_filter = "@popu:["
            pop_filter += str(min_popularity) if min_popularity is not None else "0"
            pop_filter += " "
            pop_filter += str(max_popularity) if max_popularity is not None else "1000000"
            pop_filter += "]"
            filters.append(pop_filter)
        
        # Text search filters
        if director:
            filters.append(f"@director:{director}")
        
        if writer:
            filters.append(f"@writer:{writer}")
        
        if stars:
            filters.append(f"@stars:{stars}")
        
        if country:
            filters.append(f"@country:{country}")
        
        if awards:
            filters.append(f"@awards:{awards}")
        
        # Combine query with filters
        if filters:
            full_query = f"{query} {' '.join(filters)}"
        else:
            full_query = query
        
        # Build sort criteria
        sort_by = None
        if sort_field and sort_field != "relevance":
            sort_direction_str = "ASC" if sort_direction == "asc" else "DESC"
            sort_by = f"@{sort_field}:{sort_direction_str}"
        
        # Perform search
        logger.info(f"Searching with query: {full_query}")
        results = redis_service.search(full_query, limit=page_size, offset=(page - 1) * page_size, sort_by=sort_by)
        
        # Convert results to response format
        movies = []
        for doc in results:
            movie = MovieResponse(
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
        
        logger.info(f"Search completed: {len(movies)} movies found in {search_time:.2f}ms")
        
        return MovieSearchResponse(
            movies=movies,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
            search_time_ms=search_time
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/filters", response_model=FilterOptionsResponse)
async def get_filter_options(
    redis_service: RedisSearchService = Depends(get_redis_service)
):
    """
    Get available filter options for the search interface.
    
    Returns all unique values for filterable fields.
    """
    try:
        # Get all documents for filtering
        all_docs = redis_service.search("*", limit=1000)  # Get up to 1000 docs for filtering
        
        # Extract unique values for each filter field
        genres = set()
        subgenres = set()
        languages = set()
        countries = set()
        years = set()
        production_houses = set()
        
        for doc in all_docs:
            if doc.get('genre'):
                genres.add(doc['genre'])
            if doc.get('subgenre'):
                subgenres.add(doc['subgenre'])
            if doc.get('language'):
                languages.add(doc['language'])
            if doc.get('country'):
                countries.add(doc['country'])
            if doc.get('year'):
                try:
                    years.add(int(doc['year']))
                except (ValueError, TypeError):
                    pass
            if doc.get('production_house'):
                production_houses.add(doc['production_house'])
        
        return FilterOptionsResponse(
            genres=sorted(list(genres)),
            subgenres=sorted(list(subgenres)),
            languages=sorted(list(languages)),
            countries=sorted(list(countries)),
            years=sorted(list(years)),
            production_houses=sorted(list(production_houses))
        )
        
    except Exception as e:
        logger.error(f"Get filter options error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get filter options: {str(e)}")


@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie_by_id(
    movie_id: str,
    redis_service: RedisSearchService = Depends(get_redis_service)
):
    """
    Get a specific movie by its ID.
    
    Args:
        movie_id: Movie ID (can be file_id or full Redis key)
    """
    try:
        # Get document from RedisSearch
        document = redis_service.get_document(movie_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        # Handle stars field
        stars = document.get('stars', [])
        if isinstance(stars, str):
            try:
                import json
                stars = json.loads(stars) if stars else []
            except:
                stars = [stars] if stars else []
        elif not isinstance(stars, list):
            stars = []
        
        # Handle awards field
        awards = document.get('awards', [])
        if isinstance(awards, str):
            try:
                import json
                awards = json.loads(awards) if awards else []
            except:
                awards = [awards] if awards else []
        elif not isinstance(awards, list):
            awards = []

        return MovieResponse(
            id=document.get('id', ''),
            file_id=document.get('file_id', ''),
            title=document.get('title', ''),
            movie_plot=document.get('movie_plot', ''),
            content=document.get('content', ''),
            director=document.get('director', ''),
            writer=document.get('writer', ''),
            stars=stars,
            imdb_rating=float(document.get('imdb_rating', 0.0)),
            popu=int(document.get('popu', 0)),
            genre=document.get('genre', ''),
            subgenre=document.get('subgenre', ''),
            language=document.get('language', ''),
            production_house=document.get('production_house', ''),
            source=document.get('source', ''),
            country=document.get('country', ''),
            awards=awards,
            year=int(document.get('year', 0)),
            modified_time=document.get('modified_time', ''),
            folder_path=document.get('folder_path', ''),
            file_name=document.get('file_name', ''),
            url=document.get('url', ''),
            content_type=document.get('content_type', ''),
            limited_to=document.get('limited_to', ''),
            restricted_to=document.get('restricted_to', ''),
            created_at=str(document.get('created_at', '')),
            updated_at=str(document.get('updated_at', ''))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get movie by ID error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get movie: {str(e)}")


async def _get_facet_data(redis_service: RedisSearchService) -> List[FacetData]:
    """Get faceted search data for filter options."""
    try:
        facets = []
        
        # Get all documents for faceting
        all_docs = redis_service.search("*", limit=1000)
        
        # Get genre facets
        genre_counts = {}
        for doc in all_docs:
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
        for doc in all_docs:
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
        for doc in all_docs:
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
