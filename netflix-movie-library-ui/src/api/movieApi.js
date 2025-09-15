import { request, gql } from 'graphql-request'

const API_URL = 'http://localhost:8000/graphql/'

// GraphQL queries
const SEARCH_MOVIES_QUERY = gql`
  query SearchMovies($search: SearchInput!, $pagination: PaginationInput, $sort: SortInput) {
    searchMovies(search: $search, pagination: $pagination, sort: $sort) {
      movies {
        id
        fileId
        title
        moviePlot
        content
        director
        writer
        stars
        imdbRating
        popu
        genre
        subgenre
        language
        productionHouse
        source
        country
        awards
        year
        modifiedTime
        folderPath
        fileName
        url
        contentType
        limitedTo
        restrictedTo
        createdAt
        updatedAt
      }
      totalCount
      page
      pageSize
      totalPages
      hasNext
      hasPrevious
    }
  }
`

const ADVANCED_SEARCH_MOVIES_QUERY = gql`
  query AdvancedSearchMovies($search: AdvancedSearchInput!) {
    advancedSearchMovies(search: $search) {
      movies {
        id
        fileId
        title
        moviePlot
        content
        director
        writer
        stars
        imdbRating
        popu
        genre
        subgenre
        language
        productionHouse
        source
        country
        awards
        year
        modifiedTime
        folderPath
        fileName
        url
        contentType
        limitedTo
        restrictedTo
        createdAt
        updatedAt
      }
      totalCount
      page
      pageSize
      totalPages
      hasNext
      hasPrevious
      facets {
        field
        values {
          value
          count
        }
      }
      searchTimeMs
    }
  }
`

const GET_MOVIE_BY_ID_QUERY = gql`
  query GetMovieById($id: String!) {
    getMovieById(id: $id) {
      id
      fileId
      title
      moviePlot
      content
      director
      writer
      stars
      imdbRating
      popu
      genre
      subgenre
      language
      productionHouse
      source
      country
      awards
      year
      modifiedTime
      folderPath
      fileName
      url
      contentType
      limitedTo
      restrictedTo
      createdAt
      updatedAt
    }
  }
`

const GET_FILTER_OPTIONS_QUERY = gql`
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
`

const GET_SEARCH_STATS_QUERY = gql`
  query GetSearchStats {
    getSearchStats {
      totalMovies
      searchTimeMs
      indexSizeMb
      lastUpdated
    }
  }
`

const GET_DASHBOARD_STATS_QUERY = gql`
  query GetDashboardStats {
    getDashboardStats {
      totalMovies
      averageRating
      topGenre
      latestYear
      top5Genres {
        name
        count
      }
      yearlyStats {
        year
        count
        topGenres
        topMovies
        averageRating
      }
      topRatedMovies {
        title
        year
        genre
        rating
        director
      }
    }
  }
`

const GET_SEARCH_SUGGESTIONS_QUERY = gql`
  query GetSearchSuggestions($query: String!, $limit: Int) {
    getSearchSuggestions(query: $query, limit: $limit) {
      titles
      genres
      directors
      actors
    }
  }
`

// API functions
export const searchMovies = async (searchInput, paginationInput, sortInput) => {
  try {
    const variables = {
      search: searchInput,
      pagination: paginationInput,
      sort: sortInput
    }

    const data = await request(API_URL, SEARCH_MOVIES_QUERY, variables)
    return data.searchMovies
  } catch (error) {
    console.error('Search movies error:', error)
    throw new Error(error.response?.errors?.[0]?.message || 'Search failed')
  }
}

export const advancedSearchMovies = async (searchInput) => {
  try {
    const variables = {
      search: searchInput
    }

    const data = await request(API_URL, ADVANCED_SEARCH_MOVIES_QUERY, variables)
    return data.advancedSearchMovies
  } catch (error) {
    console.error('Advanced search movies error:', error)
    throw new Error(error.response?.errors?.[0]?.message || 'Advanced search failed')
  }
}

export const getMovieById = async (id) => {
  try {
    const data = await request(API_URL, GET_MOVIE_BY_ID_QUERY, { id })
    return data.getMovieById
  } catch (error) {
    console.error('Get movie by ID error:', error)
    throw new Error(error.response?.errors?.[0]?.message || 'Failed to get movie')
  }
}

export const getFilterOptions = async () => {
  try {
    const data = await request(API_URL, GET_FILTER_OPTIONS_QUERY)
    return data.getFilterOptions
  } catch (error) {
    console.error('Get filter options error:', error)
    throw new Error(error.response?.errors?.[0]?.message || 'Failed to get filter options')
  }
}

export const getSearchStats = async () => {
  try {
    const data = await request(API_URL, GET_SEARCH_STATS_QUERY)
    return data.getSearchStats
  } catch (error) {
    console.error('Get search stats error:', error)
    throw new Error(error.response?.errors?.[0]?.message || 'Failed to get search stats')
  }
}

export const getSearchSuggestions = async (query, limit = 5) => {
  try {
    const data = await request(API_URL, GET_SEARCH_SUGGESTIONS_QUERY, { query, limit })
    return data.getSearchSuggestions
  } catch (error) {
    console.error('Get search suggestions error:', error)
    throw new Error(error.response?.errors?.[0]?.message || 'Failed to get suggestions')
  }
}

export const getDashboardStats = async () => {
  try {
    const data = await request(API_URL, GET_DASHBOARD_STATS_QUERY)
    return data.getDashboardStats
  } catch (error) {
    console.error('Get dashboard stats error:', error)
    throw new Error(error.response?.errors?.[0]?.message || 'Failed to get dashboard stats')
  }
}

// CRUD Mutations
const CREATE_MOVIE_MUTATION = gql`
  mutation CreateMovie($movieData: MovieInput!) {
    createMovie(movieData: $movieData) {
      success
      message
      id
    }
  }
`

const UPDATE_MOVIE_MUTATION = gql`
  mutation UpdateMovie($movieId: String!, $movieData: MovieInput!) {
    updateMovie(movieId: $movieId, movieData: $movieData) {
      success
      message
      id
    }
  }
`

const DELETE_MOVIE_MUTATION = gql`
  mutation DeleteMovie($movieId: String!) {
    deleteMovie(movieId: $movieId) {
      success
      message
      id
    }
  }
`

const GET_MOVIE_QUERY = gql`
  query GetMovie($movieId: String!) {
    getMovie(movieId: $movieId) {
      success
      message
      id
      movie {
        id
        title
        imdbRating
        language
        country
        stars
        director
        writer
        popu
        productionHouse
        movie
        moviePlot
        awards
        content
        genre
        subgenre
        year
        source
        fileId
        folderPath
        modifiedTime
        fileName
        url
        source
        contentType
        limitedTo
        restrictedTo
        createdAt
        updatedAt
      }
    }
  }
`

// CRUD API functions
export const createMovie = async (movieData) => {
  try {
    const data = await request(API_URL, CREATE_MOVIE_MUTATION, { movieData })
    return data.createMovie
  } catch (error) {
    console.error('Error creating movie:', error)
    throw error
  }
}

export const updateMovie = async (movieId, movieData) => {
  try {
    const data = await request(API_URL, UPDATE_MOVIE_MUTATION, { movieId, movieData })
    return data.updateMovie
  } catch (error) {
    console.error('Error updating movie:', error)
    throw error
  }
}

export const deleteMovie = async (movieId) => {
  try {
    const data = await request(API_URL, DELETE_MOVIE_MUTATION, { movieId })
    return data.deleteMovie
  } catch (error) {
    console.error('Error deleting movie:', error)
    throw error
  }
}

export const getMovie = async (movieId) => {
  try {
    const data = await request(API_URL, GET_MOVIE_QUERY, { movieId })
    return data.getMovie
  } catch (error) {
    console.error('Error getting movie:', error)
    throw error
  }
}
