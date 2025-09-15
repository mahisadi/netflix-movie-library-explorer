"""
GraphQL Schema Definition for Movie Search API

Creates the GraphQL schema and integrates it with FastAPI
using Strawberry GraphQL.
"""

import strawberry
from strawberry.fastapi import GraphQLRouter
from .resolvers import Query, Mutation
from .types import SearchInput, PaginationInput, SortInput


def create_graphql_app(search_service):
    """
    Create and configure the GraphQL application.
    
    Args:
        search_service: SearchService instance for data access
        
    Returns:
        GraphQLRouter instance configured for FastAPI
    """
    
    # Create the GraphQL schema
    schema = strawberry.Schema(
        query=Query,
        mutation=Mutation,
    )
    
    # Create the GraphQL router
    graphql_app = GraphQLRouter(
        schema,
        path="/",
        # Enable GraphQL Playground for development
        graphiql=True
    )
    
    return graphql_app


# Example GraphQL queries for documentation:

EXAMPLE_QUERIES = {
    "search_movies": """
        query SearchMovies($search: SearchInput!, $pagination: PaginationInput, $sort: SortInput) {
            searchMovies(search: $search, pagination: $pagination, sort: $sort) {
                movies {
                    id
                    title
                    imdbRating
                    genre
                    subgenre
                    year
                    language
                    country
                    stars
                    director
                    moviePlot
                    awards
                }
                totalCount
                page
                pageSize
                totalPages
                hasNext
                hasPrevious
            }
        }
    """,
    
    "get_movie_by_id": """
        query GetMovieById($id: String!) {
            getMovieById(id: $id) {
                id
                title
                imdbRating
                genre
                subgenre
                year
                language
                country
                stars
                director
                writer
                moviePlot
                awards
                content
                source
                fileId
                folderPath
                modifiedTime
                fileName
                url
            }
        }
    """,
    
    "get_search_suggestions": """
        query GetSearchSuggestions($query: String!, $limit: Int) {
            getSearchSuggestions(query: $query, limit: $limit) {
                titles
                genres
                directors
                actors
            }
        }
    """,
    
    "get_filter_options": """
        query GetFilterOptions {
            getFilterOptions {
                genres
                subgenres
                languages
                countries
                years
                productionHouses
            }
        }
    """,
    
    "get_search_stats": """
        query GetSearchStats {
            getSearchStats {
                totalMovies
                searchTimeMs
                indexSizeMb
                lastUpdated
            }
        }
    """
}

# Example variables for the queries:

EXAMPLE_VARIABLES = {
    "search_movies": {
        "search": {
            "query": "inception",
            "genre": "action",
            "yearFrom": 2010,
            "ratingMin": 8.0
        },
        "pagination": {
            "page": 1,
            "pageSize": 20
        },
        "sort": {
            "field": "relevance",
            "direction": "desc"
        }
    },
    
    "get_movie_by_id": {
        "id": "drive_1dWoCDnSeycsQqF01inb20e93hxFBHUWF"
    },
    
    "get_search_suggestions": {
        "query": "incept",
        "limit": 5
    }
}