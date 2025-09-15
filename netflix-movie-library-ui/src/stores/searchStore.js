import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { searchMovies, advancedSearchMovies, getFilterOptions, getSearchStats, getDashboardStats } from '../api/movieApi'
import enhancedMetricsService from '../services/enhancedMetricsService'

export const useSearchStore = defineStore('search', () => {
  // State
  const movies = ref([])
  const loading = ref(false)
  const error = ref(null)
  const searchQuery = ref('')
  const hasSearched = ref(false)
  const filters = ref({
    genre: '',
    subgenre: '',
    yearFrom: null,
    yearTo: null,
    ratingMin: null,
    ratingMax: null,
    language: '',
    country: ''
  })
  const pagination = ref({
    page: 1,
    pageSize: 20,
    totalCount: 0,
    totalPages: 0,
    hasNext: false,
    hasPrevious: false
  })
  const sortOptions = ref({
    field: 'relevance',
    direction: 'desc'
  })
  const filterOptions = ref({
    genres: [],
    subgenres: [],
    languages: [],
    countries: [],
    years: [],
    productionHouses: []
  })
  
  // Advanced search state
  const facets = ref([])
  const searchTimeMs = ref(0)
  const useAdvancedSearch = ref(false)
  const stats = ref({
    totalMovies: 0,
    searchTimeMs: 0,
    indexSizeMb: 0,
    lastUpdated: ''
  })
  const dashboardStats = ref({
    totalMovies: 0,
    averageRating: 0.0,
    topGenre: 'Unknown',
    latestYear: 0,
    top5Genres: [],
    yearlyStats: [],
    topRatedMovies: []
  })
  
  // Top-rated movies sorting state
  const topRatedSort = ref({
    field: 'rating',
    direction: 'desc'
  })

  // Getters
  const hasResults = computed(() => movies.value.length > 0)
  const isEmpty = computed(() => !loading.value && movies.value.length === 0)
  const currentPage = computed(() => pagination.value.page)
  const totalPages = computed(() => pagination.value.totalPages)
  
  // Sorted top-rated movies
  const sortedTopRatedMovies = computed(() => {
    const movies = dashboardStats.value.topRatedMovies || []
    const { field, direction } = topRatedSort.value
    
    return [...movies].sort((a, b) => {
      let aVal = a[field]
      let bVal = b[field]
      
      // Handle string comparison
      if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase()
        bVal = bVal.toLowerCase()
      }
      
      if (direction === 'asc') {
        return aVal > bVal ? 1 : aVal < bVal ? -1 : 0
      } else {
        return aVal < bVal ? 1 : aVal > bVal ? -1 : 0
      }
    })
  })

  // Actions
  const setSearchQuery = (query) => {
    searchQuery.value = query
  }

  const setFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
  }

  const setSortOptions = (options) => {
    sortOptions.value = { ...sortOptions.value, ...options }
  }

  const setPagination = (newPagination) => {
    pagination.value = { ...pagination.value, ...newPagination }
  }

  const clearFilters = () => {
    filters.value = {
      genre: '',
      subgenre: '',
      yearFrom: null,
      yearTo: null,
      ratingMin: null,
      ratingMax: null,
      language: '',
      country: ''
    }
  }

  const clearSearch = () => {
    searchQuery.value = ''
    movies.value = []
    hasSearched.value = false
    error.value = null
    clearFilters()
  }

  const search = async (resetPagination = true) => {
    if (resetPagination) {
      pagination.value.page = 1
    }

    loading.value = true
    error.value = null
    hasSearched.value = true

    try {
      if (useAdvancedSearch.value) {
        await advancedSearch()
      } else {
        await basicSearch()
      }
    } catch (err) {
      error.value = err.message || 'Search failed'
      movies.value = []
    } finally {
      loading.value = false
    }
  }

  const basicSearch = async () => {
    const searchInput = {
      query: searchQuery.value,
      ...filters.value
    }

    const paginationInput = {
      page: pagination.value.page,
      pageSize: pagination.value.pageSize
    }

    const sortInput = {
      field: sortOptions.value.field,
      direction: sortOptions.value.direction
    }

    const result = await searchMovies(searchInput, paginationInput, sortInput)
    
    movies.value = result.movies || []
    pagination.value = {
      page: result.page || 1,
      pageSize: result.pageSize || 20,
      totalCount: result.totalCount || 0,
      totalPages: result.totalPages || 0,
      hasNext: result.hasNext || false,
      hasPrevious: result.hasPrevious || false
    }

    // Track search metrics only if there's a search query
    if (searchQuery.value && searchQuery.value.trim()) {
      enhancedMetricsService.trackSearch(
        searchQuery.value,
        result.totalCount || 0,
        filters.value,
        'text'
      )
    }
  }

  const advancedSearch = async () => {
    // Build advanced search filters
    const advancedFilters = {}
    
    // TAG field filters
    if (filters.value.genre) {
      advancedFilters.genres = [filters.value.genre]
    }
    if (filters.value.subgenre) {
      advancedFilters.subgenres = [filters.value.subgenre]
    }
    if (filters.value.language) {
      advancedFilters.languages = [filters.value.language]
    }
    if (filters.value.productionHouse) {
      advancedFilters.productionHouses = [filters.value.productionHouse]
    }
    
    // NUMERIC range filters
    if (filters.value.yearFrom || filters.value.yearTo) {
      advancedFilters.yearRange = {
        minYear: filters.value.yearFrom,
        maxYear: filters.value.yearTo
      }
    }
    if (filters.value.ratingMin || filters.value.ratingMax) {
      advancedFilters.ratingRange = {
        minRating: filters.value.ratingMin,
        maxRating: filters.value.ratingMax
      }
    }

    const searchInput = {
      query: searchQuery.value || '*',
      filters: Object.keys(advancedFilters).length > 0 ? advancedFilters : null,
      page: pagination.value.page,
      pageSize: pagination.value.pageSize,
      sortField: sortOptions.value.field,
      sortDirection: sortOptions.value.direction,
      includeFacets: true
    }

    const result = await advancedSearchMovies(searchInput)
    
    movies.value = result.movies || []
    facets.value = result.facets || []
    searchTimeMs.value = result.searchTimeMs || 0
    
    pagination.value = {
      page: result.page || 1,
      pageSize: result.pageSize || 20,
      totalCount: result.totalCount || 0,
      totalPages: result.totalPages || 0,
      hasNext: result.hasNext || false,
      hasPrevious: result.hasPrevious || false
    }

    // Track search metrics only if there's a search query
    if (searchQuery.value && searchQuery.value.trim()) {
      enhancedMetricsService.trackSearch(
        searchQuery.value,
        result.totalCount || 0,
        filters.value,
        'advanced'
      )
    }
  }

  const loadFilterOptions = async () => {
    try {
      const options = await getFilterOptions()
      filterOptions.value = options
    } catch (err) {
      console.error('Failed to load filter options:', err)
    }
  }

  const loadStats = async () => {
    try {
      const statsData = await getSearchStats()
      stats.value = statsData
    } catch (err) {
      console.error('Failed to load stats:', err)
    }
  }

  const loadDashboardStats = async (page = 1, pageSize = 10, sortField = 'year', sortDirection = 'asc') => {
    try {
      const dashboardData = await getDashboardStats(page, pageSize, sortField, sortDirection)
      dashboardStats.value = dashboardData
    } catch (err) {
      console.error('Failed to load dashboard stats:', err)
    }
  }

  const nextPage = async () => {
    if (pagination.value.hasNext) {
      pagination.value.page += 1
      await search(false)
    }
  }

  const previousPage = async () => {
    if (pagination.value.hasPrevious) {
      pagination.value.page -= 1
      await search(false)
    }
  }

  const goToPage = async (page) => {
    if (page >= 1 && page <= pagination.value.totalPages) {
      pagination.value.page = page
      await search(false)
    }
  }
  
  // Top-rated movies sorting
  const sortTopRatedMovies = (field) => {
    if (topRatedSort.value.field === field) {
      // Toggle direction if same field
      topRatedSort.value.direction = topRatedSort.value.direction === 'asc' ? 'desc' : 'asc'
    } else {
      // New field, default to descending
      topRatedSort.value.field = field
      topRatedSort.value.direction = 'desc'
    }
  }

  return {
    // State
    movies,
    loading,
    error,
    searchQuery,
    hasSearched,
    filters,
    pagination,
    sortOptions,
    filterOptions,
    stats,
    dashboardStats,
    topRatedSort,
    facets,
    searchTimeMs,
    useAdvancedSearch,
    
    // Getters
    hasResults,
    isEmpty,
    currentPage,
    totalPages,
    sortedTopRatedMovies,
    
    // Actions
    setSearchQuery,
    setFilters,
    setSortOptions,
    setPagination,
    clearFilters,
    clearSearch,
    search,
    basicSearch,
    advancedSearch,
    loadFilterOptions,
    loadStats,
    loadDashboardStats,
    nextPage,
    previousPage,
    goToPage,
    sortTopRatedMovies
  }
})
