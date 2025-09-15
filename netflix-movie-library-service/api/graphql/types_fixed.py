"""
GraphQL Types for Movie Search API

Defines all GraphQL types used in the movie search API.
"""

from typing import List, Optional, Dict, Any
from strawberry import field, type
from pydantic import BaseModel


@type
class Movie:
    """Movie data structure with all fields from RedisSearch schema."""
    
    id: str
    file_id: str
    
    # Core movie information
    title: str
    movie_plot: str
    content: str
    
    # People and credits
    director: str
    writer: str
    stars: List[str]
    
    # Ratings and popularity
    imdb_rating: float
    popu: int
    
    # Categorization (TAG fields for filtering)
    genre: str
    subgenre: str
    language: str
    production_house: str
    source: str
    
    # Location and awards
    country: str
    awards: List[str]
    
    # Temporal information (sortable fields)
    year: int
    modified_time: str
    
    # File metadata
    folder_path: str
    file_name: str
    url: str
    
    # System fields
    content_type: str
    
    # Access control fields
    limited_to: str
    restricted_to: str
    
    # Timestamp fields
    created_at: str
    updated_at: str


@type
class YearlyStats:
    """Yearly statistics for dashboard."""
    
    year: int
    count: int
    top_genres: List[str]
    top_movies: List[str]
    average_rating: float


@type
class TopRatedMovie:
    """Top-rated movie information."""
    
    title: str
    year: int
    genre: str
    rating: float
    director: str


@type
class GenreStats:
    """Genre statistics for dashboard."""
    
    name: str
    count: int


@type
class DashboardStats:
    """Dashboard statistics."""
    
    total_movies: int
    average_rating: float
    top_genre: str
    latest_year: int
    top_5_genres: List[GenreStats]
    yearly_stats: List[YearlyStats]
    top_rated_movies: List[TopRatedMovie]


@type
class SearchResult:
    """Search result with pagination."""
    
    movies: List[Movie]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


@type
class SearchSuggestions:
    """Search suggestions for autocomplete."""
    
    titles: List[str]
    genres: List[str]
    directors: List[str]
    actors: List[str]


@type
class FilterOptions:
    """Available filter options."""
    
    genres: List[str]
    subgenres: List[str]
    languages: List[str]
    countries: List[str]
    years: List[int]
    production_houses: List[str]


@type
class SearchStats:
    """Search statistics and system info."""
    
    total_movies: int
    search_time_ms: float
    index_size_mb: float
    last_updated: str


# Input types
@type
class SearchQuery:
    """Search query input."""
    
    search: str
    pagination: PaginationInput
    sort: SortInput


@type
class SearchInput:
    """Search input parameters."""
    
    query: str
    page: int = 1
    page_size: int = 20
    sort_field: str = "relevance"
    sort_direction: str = "desc"


@type
class PaginationInput:
    """Pagination input."""
    
    page: int = 1
    page_size: int = 20


@type
class SortInput:
    """Sorting input."""
    
    field: str = "relevance"
    direction: str = "desc"


# Advanced search types
@type
class YearRange:
    """Year range filter."""
    
    min_year: Optional[int] = None
    max_year: Optional[int] = None


@type
class RatingRange:
    """Rating range filter."""
    
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None


@type
class PopularityRange:
    """Popularity range filter."""
    
    min_popularity: Optional[int] = None
    max_popularity: Optional[int] = None


@type
class MovieFilters:
    """Movie filters for advanced search."""
    
    genres: Optional[List[str]] = None
    subgenres: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    production_houses: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    
    year_range: Optional[YearRange] = None
    rating_range: Optional[RatingRange] = None
    popularity_range: Optional[PopularityRange] = None
    
    director: Optional[str] = None
    writer: Optional[str] = None
    stars: Optional[str] = None


@type
class AdvancedSearchInput:
    """Advanced search input with filters."""
    
    query: Optional[str] = ""
    filters: Optional[MovieFilters] = None
    pagination: PaginationInput
    sort: SortInput
    include_facets: bool = False


@type
class FacetData:
    """Faceted search data for filter options."""
    
    field: str
    values: List[Dict[str, Any]]


@type
class AdvancedSearchResult:
    """Advanced search result with faceted data."""
    
    movies: List[Movie]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    facets: Optional[List[FacetData]] = None
    search_time_ms: float


# CRUD operation types
@type
class MovieInput:
    """Input for creating/updating movies."""
    
    title: str
    year: int
    genre: str
    subgenre: str = ""
    director: str = ""
    stars: str = ""
    writer: str = ""
    content: str = ""
    moviePlot: str = ""
    awards: str = ""
    imdbRating: float = 0.0
    language: str = "English"
    country: str = ""
    productionHouse: str = ""
    limitedTo: str = ""
    restrictedTo: str = ""


@type
class MovieResponse:
    """Response for movie operations."""
    
    success: bool
    message: str
    id: Optional[str] = None
    movie: Optional[Movie] = None


@type
class MoviesListResponse:
    """Response for movie list operations."""
    
    success: bool
    message: str
    movies: List[Movie]
    total_count: int
    page: int
    page_size: int
