"""
GraphQL Types for Movie Search API

Defines the GraphQL schema types for movie data, search queries,
and response structures.
"""

from typing import List, Optional, Dict, Any
from strawberry import type, field, input
from datetime import datetime


@type
class Movie:
    """Movie type representing a single movie record."""
    
    # Primary identifier (Redis key)
    id: str = field(description="Unique Redis key identifier (movie:{file_id})")
    file_id: str = field(description="Original file ID (primary key)")
    
    # Core movie information
    title: str = field(description="Movie title")
    movie_plot: str = field(description="Movie plot summary")
    content: str = field(description="Full text content for search")
    
    # People and credits
    director: str = field(description="Movie director")
    writer: str = field(description="Screenplay writer")
    stars: List[str] = field(description="List of main actors/actresses")
    
    # Ratings and popularity
    imdb_rating: float = field(description="IMDB rating (0.0 to 10.0)")
    popu: int = field(description="Popularity score")
    
    # Categorization (TAG fields for filtering)
    genre: str = field(description="Primary genre")
    subgenre: str = field(description="Sub-genre")
    language: str = field(description="Primary language of the movie")
    production_house: str = field(description="Production company")
    source: str = field(description="Data source (e.g., google_drive)")
    
    # Location and awards
    country: str = field(description="Country of origin")
    awards: List[str] = field(description="List of awards received")
    
    # Temporal information (sortable fields)
    year: int = field(description="Release year")
    modified_time: str = field(description="Last modification time")
    
    # File metadata
    folder_path: str = field(description="Folder path in source system")
    file_name: str = field(description="Original file name")
    url: str = field(description="URL to view the file")
    
    # System fields
    content_type: str = field(description="Content type (e.g., movies)")
    
    # Access control fields
    limited_to: str = field(description="Limited access scope")
    restricted_to: str = field(description="Restricted access scope")
    
    # Timestamp fields
    created_at: str = field(description="Record creation timestamp")
    updated_at: str = field(description="Record last update timestamp")


@type
class MovieWithRating:
    """Movie with rating information."""
    
    title: str = field(description="Movie title")
    rating: float = field(description="IMDB rating")


@type
class YearlyStats:
    """Yearly movie statistics."""
    
    year: int = field(description="Year")
    count: int = field(description="Number of movies in this year")
    top_genres: List[str] = field(description="Top genres for this year")
    top_movies: List[MovieWithRating] = field(description="Top movies for this year with ratings")
    average_rating: float = field(description="Average rating for this year")


@type
class TopRatedMovie:
    """Top-rated movie information."""
    
    title: str = field(description="Movie title")
    year: int = field(description="Release year")
    genre: str = field(description="Movie genre")
    rating: float = field(description="IMDB rating")
    director: str = field(description="Movie director")


@type
class GenreStats:
    """Genre statistics."""
    
    name: str = field(description="Genre name")
    count: int = field(description="Number of movies in this genre")


@type
class PaginationInfo:
    """Pagination information."""
    
    page: int = field(description="Current page number")
    page_size: int = field(description="Number of items per page")
    total_pages: int = field(description="Total number of pages")
    total_count: int = field(description="Total number of items")
    has_next: bool = field(description="Whether there are more pages")
    has_previous: bool = field(description="Whether there are previous pages")


@type
class DashboardStats:
    """Dashboard statistics."""
    
    total_movies: int = field(description="Total number of movies")
    total_genres: int = field(description="Total number of unique genres")
    average_rating: float = field(description="Overall average rating")
    top_genre: str = field(description="Most popular genre")
    latest_year: int = field(description="Latest movie year")
    top_5_genres: List[GenreStats] = field(description="Top 5 genres by count")
    yearly_stats: List[YearlyStats] = field(description="Statistics by year")
    top_rated_movies: List[TopRatedMovie] = field(description="Top-rated movies sorted by rating")
    yearly_pagination: PaginationInfo = field(description="Pagination info for yearly stats")


@type
class SearchResult:
    """Search result containing movies and pagination info."""
    
    movies: List[Movie] = field(description="List of matching movies")
    total_count: int = field(description="Total number of matching movies")
    page: int = field(description="Current page number")
    page_size: int = field(description="Number of movies per page")
    total_pages: int = field(description="Total number of pages")
    has_next: bool = field(description="Whether there are more pages")
    has_previous: bool = field(description="Whether there are previous pages")


@type
class SearchSuggestions:
    """Search suggestions for autocomplete functionality."""
    
    titles: List[str] = field(description="Suggested movie titles")
    genres: List[str] = field(description="Suggested genres")
    directors: List[str] = field(description="Suggested directors")
    actors: List[str] = field(description="Suggested actors")


@type
class FilterOptions:
    """Available filter options for the search interface."""
    
    genres: List[str] = field(description="Available genres")
    subgenres: List[str] = field(description="Available subgenres")
    languages: List[str] = field(description="Available languages")
    countries: List[str] = field(description="Available countries")
    years: List[int] = field(description="Available years")
    production_houses: List[str] = field(description="Available production houses")


@type
class SearchStats:
    """Search statistics and metadata."""
    
    total_movies: int = field(description="Total number of movies in database")
    search_time_ms: float = field(description="Search execution time in milliseconds")
    index_size_mb: float = field(description="RedisSearch index size in MB")
    last_updated: str = field(description="Last data update timestamp")


# Input Types

@input
class SearchInput:
    """Input for search queries."""
    
    query: Optional[str] = None
    genre: Optional[str] = None
    subgenre: Optional[str] = None
    language: Optional[str] = None
    country: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    rating_min: Optional[float] = None
    rating_max: Optional[float] = None
    production_house: Optional[str] = None
    director: Optional[str] = None
    actor: Optional[str] = None


@input
class PaginationInput:
    """Input for pagination."""
    
    page: int = 1
    page_size: int = 20
    max_page_size: int = 100


@input
class SortInput:
    """Input for sorting options."""
    
    field: str = "relevance"
    direction: str = "desc"


@input
class SearchQuery:
    """Complete search query input."""
    
    search: SearchInput = field(description="Search criteria")
    pagination: PaginationInput = field(description="Pagination options")
    sort: SortInput = field(description="Sorting options")


# Advanced search input types
@input
class YearRange:
    """Year range filter for movie search."""
    min_year: Optional[int] = field(description="Minimum year", default=None)
    max_year: Optional[int] = field(description="Maximum year", default=None)

@input
class RatingRange:
    """Rating range filter for movie search."""
    min_rating: Optional[float] = field(description="Minimum IMDB rating", default=None)
    max_rating: Optional[float] = field(description="Maximum IMDB rating", default=None)

@input
class PopularityRange:
    """Popularity range filter for movie search."""
    min_popularity: Optional[int] = field(description="Minimum popularity score", default=None)
    max_popularity: Optional[int] = field(description="Maximum popularity score", default=None)

@input
class MovieFilters:
    """Advanced movie search filters using RedisSearch TAG and NUMERIC fields."""
    
    # TAG field filters (exact matches)
    genres: Optional[List[str]] = field(description="Filter by genres", default=None)
    subgenres: Optional[List[str]] = field(description="Filter by subgenres", default=None)
    languages: Optional[List[str]] = field(description="Filter by languages", default=None)
    production_houses: Optional[List[str]] = field(description="Filter by production houses", default=None)
    sources: Optional[List[str]] = field(description="Filter by data sources", default=None)
    
    # NUMERIC range filters
    year_range: Optional[YearRange] = field(description="Filter by year range", default=None)
    rating_range: Optional[RatingRange] = field(description="Filter by rating range", default=None)
    popularity_range: Optional[PopularityRange] = field(description="Filter by popularity range", default=None)
    
    # Text search filters
    director: Optional[str] = field(description="Filter by director name", default=None)
    writer: Optional[str] = field(description="Filter by writer name", default=None)
    stars: Optional[str] = field(description="Filter by actor/actress name", default=None)

@input
class AdvancedSearchInput:
    """Advanced search input with comprehensive filtering options."""
    
    # Basic search
    query: Optional[str] = field(description="Search query text", default="")
    
    # Advanced filters
    filters: Optional[MovieFilters] = field(description="Advanced filters", default=None)
    
    # Pagination
    page: int = field(description="Page number (1-based)", default=1)
    page_size: int = field(description="Number of results per page", default=20)
    max_page_size: int = field(description="Maximum allowed page size", default=1000)
    
    # Sorting
    sort_field: Optional[str] = field(description="Field to sort by", default="relevance")
    sort_direction: Optional[str] = field(description="Sort direction (asc/desc)", default="desc")
    
    # Faceted search
    include_facets: bool = field(description="Include faceted search data", default=False)

@type
class FacetValue:
    """Individual facet value with count."""
    
    value: str
    count: int

@type
class FacetData:
    """Faceted search data for filter options."""
    
    field: str
    values: List[FacetValue]

@type
class AdvancedSearchResult:
    """Advanced search result with faceted data."""
    
    movies: List[Movie] = field(description="List of matching movies")
    total_count: int = field(description="Total number of matching movies")
    page: int = field(description="Current page number")
    page_size: int = field(description="Number of movies per page")
    total_pages: int = field(description="Total number of pages")
    has_next: bool = field(description="Whether there are more pages")
    has_previous: bool = field(description="Whether there are previous pages")
    facets: Optional[List[FacetData]] = field(description="Faceted search data", default=None)
    search_time_ms: float = field(description="Search execution time in milliseconds")

# Enums for better type safety
from enum import Enum

class SortField(str, Enum):
    """Available sort fields based on RedisSearch schema."""
    RELEVANCE = "relevance"
    TITLE = "title"
    RATING = "imdb_rating"
    YEAR = "year"
    POPULARITY = "popu"
    MODIFIED_TIME = "modified_time"
    FILE_ID = "file_id"

class SortDirection(str, Enum):
    """Sort directions."""
    ASC = "asc"
    DESC = "desc"


# Input types for CRUD operations
@input
class MovieInput:
    """Input type for creating/updating movies."""
    
    # Core movie information
    title: str = field(description="Movie title")
    moviePlot: str = field(description="Movie plot summary", default="")
    content: str = field(description="Full text content for search", default="")
    
    # People and credits
    director: str = field(description="Movie director", default="")
    writer: str = field(description="Screenplay writer", default="")
    stars: str = field(description="Main actors/actresses (comma-separated)", default="")
    
    # Ratings and popularity
    imdbRating: float = field(description="IMDB rating (0.0 to 10.0)", default=0.0)
    popu: int = field(description="Popularity score", default=0)
    
    # Categorization
    genre: str = field(description="Primary genre", default="")
    subgenre: str = field(description="Sub-genre", default="")
    language: str = field(description="Primary language", default="English")
    productionHouse: str = field(description="Production company", default="")
    source: str = field(description="Data source", default="manual")
    
    # Location and awards
    country: str = field(description="Country of origin", default="")
    awards: str = field(description="Awards received (comma-separated)", default="")
    
    # Temporal information
    year: int = field(description="Release year", default=2024)
    modifiedTime: str = field(description="Last modification time", default="")
    
    # File metadata
    folderPath: str = field(description="Folder path in source system", default="")
    fileName: str = field(description="Original file name", default="")
    url: str = field(description="URL to view the file", default="")
    
    # System fields
    contentType: str = field(description="Content type", default="movies")
    
    # Access control fields
    limitedTo: str = field(description="Limited access scope", default="")
    restrictedTo: str = field(description="Restricted access scope", default="")
    
    # Timestamp fields
    createdAt: str = field(description="Record creation timestamp", default="")
    updatedAt: str = field(description="Record last update timestamp", default="")


@type
class MovieResponse:
    """Response type for movie operations."""
    
    success: bool = field(description="Whether the operation was successful")
    message: str = field(description="Response message")
    id: Optional[str] = field(description="Movie ID (for create/update operations)")
    movie: Optional[Movie] = field(description="Movie data (for get operations)")


@type
class MoviesListResponse:
    """Response type for listing movies."""
    
    success: bool = field(description="Whether the operation was successful")
    message: str = field(description="Response message")
    movies: List[Movie] = field(description="List of movies")
    total_count: int = field(description="Total number of movies")
    page: int = field(description="Current page number")
    page_size: int = field(description="Number of movies per page")