<template>
  <div class="nmle-movie-results">
    <div class="container">
      <!-- Stats Section - Hidden for now -->
      <!-- <div class="stats-section" v-if="stats.totalMovies > 0">
        <div class="stats-card">
          <div class="stat-item">
            <span class="stat-number">{{ stats.totalMovies.toLocaleString() }}</span>
            <span class="stat-label">Total Movies</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ pagination.totalCount.toLocaleString() }}</span>
            <span class="stat-label">Search Results</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ stats.searchTimeMs }}ms</span>
            <span class="stat-label">Search Time</span>
          </div>
        </div>
      </div> -->

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Searching movies...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <div class="error-card">
          <h3>Search Error</h3>
          <p>{{ error }}</p>
          <button @click="retrySearch" class="btn btn-primary">Try Again</button>
        </div>
      </div>

      <!-- No Results Found -->
      <div v-else-if="isEmpty && hasSearched" class="no-results-state">
        <div class="no-results-card">
          <div class="no-results-icon">🔍</div>
          <h3>No Results Found</h3>
          <p>We couldn't find any movies matching "{{ searchQuery }}"</p>
          <div class="no-results-suggestions">
            <p>Try:</p>
            <ul>
              <li>Checking your spelling</li>
              <li>Using different keywords</li>
              <li>Broadening your search terms</li>
              <li>Removing filters</li>
            </ul>
          </div>
          <button @click="clearSearch" class="btn btn-primary">Clear Search</button>
        </div>
      </div>

      <!-- Default Movie Dashboard -->
      <div v-else-if="!hasSearched" class="movie-dashboard">
        <div class="dashboard-header">
          <h2>Movie Collection Dashboard</h2>
          <p>Overview of your movie library</p>
        </div>
        
        <!-- Top Statistics Cards -->
        <div class="top-stats-grid">
          <div class="stat-card">
            <div class="stat-icon">🎬</div>
            <div class="stat-content">
              <div class="stat-number">{{ totalMovieCount }}</div>
              <div class="stat-label">Total Movies</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon">🏷️</div>
            <div class="stat-content">
              <div class="stat-number">{{ totalGenresCount }}</div>
              <div class="stat-label">Total Genres</div>
            </div>
          </div>
        </div>
        
        <!-- Top 5 Genres Section -->
        <div class="genres-section">
          <h3>Top 5 Genres</h3>
          <div class="genres-cards">
            <div 
              v-for="(genre, index) in top5Genres" 
              :key="genre.name" 
              class="genre-card"
              :class="`rank-${index + 1}`"
            >
              <div class="genre-card-header">
                <div class="genre-rank-badge">{{ index + 1 }}</div>
                <div class="genre-icon">{{ getGenreIcon(genre.name) }}</div>
              </div>
              <div class="genre-card-content">
                <div class="genre-name">{{ genre.name }}</div>
                <div class="genre-count">{{ genre.count }} movie{{ genre.count !== 1 ? 's' : '' }}</div>
                <div class="genre-percentage">{{ getGenrePercentage(genre.count) }}%</div>
              </div>
              <div class="genre-card-footer">
                <div class="genre-progress-bar">
                  <div 
                    class="genre-progress-fill" 
                    :style="{ width: `${getGenrePercentage(genre.count)}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Top-Rated Movies Section -->
        <div class="top-rated-section">
          <h3>Top-Rated Movies</h3>
          <div class="top-rated-table-container">
            <table class="top-rated-table">
              <thead>
                <tr>
                  <th 
                    class="sortable" 
                    :class="{ active: topRatedSort.field === 'rating', [topRatedSort.direction]: topRatedSort.field === 'rating' }"
                    @click="sortTopRatedMovies('rating')"
                  >
                    Rating
                    <span class="sort-arrow" v-if="topRatedSort.field === 'rating'">
                      {{ topRatedSort.direction === 'asc' ? '↑' : '↓' }}
                    </span>
                  </th>
                  <th 
                    class="sortable" 
                    :class="{ active: topRatedSort.field === 'title', [topRatedSort.direction]: topRatedSort.field === 'title' }"
                    @click="sortTopRatedMovies('title')"
                  >
                    Title
                    <span class="sort-arrow" v-if="topRatedSort.field === 'title'">
                      {{ topRatedSort.direction === 'asc' ? '↑' : '↓' }}
                    </span>
                  </th>
                  <th 
                    class="sortable mobile-hidden" 
                    :class="{ active: topRatedSort.field === 'year', [topRatedSort.direction]: topRatedSort.field === 'year' }"
                    @click="sortTopRatedMovies('year')"
                  >
                    Year
                    <span class="sort-arrow" v-if="topRatedSort.field === 'year'">
                      {{ topRatedSort.direction === 'asc' ? '↑' : '↓' }}
                    </span>
                  </th>
                  <th 
                    class="sortable mobile-hidden" 
                    :class="{ active: topRatedSort.field === 'genre', [topRatedSort.direction]: topRatedSort.field === 'genre' }"
                    @click="sortTopRatedMovies('genre')"
                  >
                    Genre
                    <span class="sort-arrow" v-if="topRatedSort.field === 'genre'">
                      {{ topRatedSort.direction === 'asc' ? '↑' : '↓' }}
                    </span>
                  </th>
                  <th 
                    class="sortable mobile-hidden" 
                    :class="{ active: topRatedSort.field === 'director', [topRatedSort.direction]: topRatedSort.field === 'director' }"
                    @click="sortTopRatedMovies('director')"
                  >
                    Director
                    <span class="sort-arrow" v-if="topRatedSort.field === 'director'">
                      {{ topRatedSort.direction === 'asc' ? '↑' : '↓' }}
                    </span>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="movie in sortedTopRatedMovies" :key="movie.title" class="top-rated-row">
                  <td class="rating-cell">
                    <div class="rating-display">
                      <span class="rating-number">{{ movie.rating }}</span>
                      <span class="rating-stars">⭐</span>
                    </div>
                  </td>
                  <td class="title-cell">{{ movie.title }}</td>
                  <td class="year-cell mobile-hidden">{{ movie.year }}</td>
                  <td class="genre-cell mobile-hidden">
                    <span class="genre-tag">{{ movie.genre }}</span>
                  </td>
                  <td class="director-cell mobile-hidden">{{ movie.director }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- Yearly Breakdown Table -->
        <div class="yearly-section">
          <div class="yearly-table-container">
            <h3>Movies by Year</h3>
            <table class="yearly-table">
              <thead>
                <tr>
                  <th>Year</th>
                  <th>Count</th>
                  <th class="mobile-hidden">Genres</th>
                  <th class="mobile-hidden">Top Movies</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="yearData in yearlyStats" :key="yearData.year" class="year-row">
                  <td class="year-cell">{{ yearData.year }}</td>
                  <td class="count-cell">{{ yearData.count }}</td>
                  <td class="genres-cell mobile-hidden">
                    <div class="genre-tags">
                      <span 
                        v-for="genre in yearData.topGenres" 
                        :key="genre" 
                        class="genre-tag"
                      >
                        {{ genre }}
                      </span>
                    </div>
                  </td>
                  <td class="movies-cell mobile-hidden">
                    <div class="movie-list">
                      <span 
                        v-for="movie in yearData.topMovies" 
                        :key="movie" 
                        class="movie-item"
                      >
                        {{ movie }}
                      </span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- Dashboard actions removed -->
      </div>

      <!-- Results -->
      <div v-else-if="hasSearched" class="results-section">
        <div class="results-header">
          <h2>Search Results ({{ movies.length }})</h2>
          <div class="results-info" v-if="movies.length > 0">
            Showing {{ movies.length > 0 ? 1 : 0 }} - 
            {{ movies.length }} 
            of {{ movies.length }} movies
          </div>
        </div>

        <!-- No Results Found -->
        <div v-if="movies.length === 0" class="no-results-state">
          <div class="no-results-card">
            <div class="no-results-icon">🔍</div>
            <h3>No Results Found</h3>
            <p>We couldn't find any movies matching "{{ searchQuery }}"</p>
            <div class="no-results-suggestions">
              <p>Try:</p>
              <ul>
                <li>Checking your spelling</li>
                <li>Using different keywords</li>
                <li>Broadening your search terms</li>
                <li>Removing filters</li>
              </ul>
            </div>
            <button @click="clearSearch" class="btn btn-primary">Clear Search</button>
          </div>
        </div>

        <!-- Movies Grid -->
        <div v-else class="movies-grid">
          <div v-for="movie in movies" :key="movie.id" class="movie-card">
            <div class="movie-poster">
              <div class="poster-placeholder">
                <span>{{ movie.title.charAt(0) }}</span>
              </div>
              <div class="movie-rating" v-if="movie.imdbRating > 0">
                ⭐ {{ movie.imdbRating }}
              </div>
            </div>
            
            <div class="movie-info">
              <h3 class="movie-title">{{ movie.title }}</h3>
              <p class="movie-year" v-if="movie.year">{{ movie.year }}</p>
              
              <div class="movie-meta">
                <span class="movie-genre" v-if="movie.genre">{{ movie.genre }}</span>
                <span class="movie-subgenre" v-if="movie.subgenre">{{ movie.subgenre }}</span>
              </div>
              
              <div class="movie-details">
                <p v-if="movie.director" class="movie-director">
                  <strong>Director:</strong> {{ movie.director }}
                </p>
                <p v-if="movie.stars && movie.stars.length" class="movie-stars">
                  <strong>Cast:</strong> {{ movie.stars.slice(0, 3).join(', ') }}
                  <span v-if="movie.stars.length > 3">...</span>
                </p>
                <p v-if="movie.country" class="movie-country">
                  <strong>Country:</strong> {{ movie.country }}
                </p>
                <p v-if="movie.language" class="movie-language">
                  <strong>Language:</strong> {{ movie.language }}
                </p>
                <p v-if="movie.productionHouse" class="movie-production">
                  <strong>Production:</strong> {{ movie.productionHouse }}
                </p>
                <p v-if="movie.fileId" class="movie-file-id">
                  <strong>ID:</strong> {{ movie.fileId.substring(0, 12) }}...
                </p>
              </div>
              
              <p v-if="movie.moviePlot" class="movie-plot">
                {{ movie.moviePlot.substring(0, 150) }}
                <span v-if="movie.moviePlot.length > 150">...</span>
              </p>
              
              <div class="movie-actions">
                <button @click="viewMovie(movie)" class="btn btn-primary btn-sm">
                  View Details
                </button>
                <a v-if="movie.url" :href="movie.url" target="_blank" class="btn btn-secondary btn-sm">
                  Open Source
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

        <!-- Pagination -->
        <div class="pagination" v-if="pagination.totalPages > 1">
          <button 
            @click="previousPage" 
            :disabled="!pagination.hasPrevious"
            class="btn btn-secondary"
          >
            Previous
          </button>
          
          <div class="page-numbers">
            <button
              v-for="page in visiblePages"
              :key="page"
              @click="goToPage(page)"
              :class="['page-btn', { active: page === pagination.page }]"
            >
              {{ page }}
            </button>
          </div>
          
          <button 
            @click="nextPage" 
            :disabled="!pagination.hasNext"
            class="btn btn-secondary"
          >
            Next
          </button>
        </div>
      </div>
    </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useSearchStore } from '../stores/searchStore'

const searchStore = useSearchStore()

// Computed properties
const movies = computed(() => searchStore.movies)
const loading = computed(() => searchStore.loading)
const error = computed(() => searchStore.error)
const isEmpty = computed(() => searchStore.isEmpty)
const hasResults = computed(() => searchStore.hasResults)
const pagination = computed(() => searchStore.pagination)
const stats = computed(() => searchStore.stats)
const searchQuery = computed(() => searchStore.searchQuery)
const hasSearched = computed(() => searchStore.hasSearched)

// Real yearly stats data from API
const yearlyStats = computed(() => searchStore.dashboardStats.yearlyStats || [])

// Dashboard statistics from real API data
const totalMovieCount = computed(() => searchStore.dashboardStats.totalMovies || 0)

const totalGenresCount = computed(() => {
  const genres = searchStore.dashboardStats.top5Genres || []
  return genres.length
})

const top5Genres = computed(() => searchStore.dashboardStats.top5Genres || [])

// Top-rated movies
const sortedTopRatedMovies = computed(() => searchStore.sortedTopRatedMovies)
const topRatedSort = computed(() => searchStore.topRatedSort)

// Pagination helpers
const visiblePages = computed(() => {
  const current = pagination.value.page
  const total = pagination.value.totalPages
  const pages = []
  
  const start = Math.max(1, current - 2)
  const end = Math.min(total, current + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// Methods
const retrySearch = async () => {
  await searchStore.search()
}

const clearSearch = () => {
  searchStore.clearSearch()
}

// Top-rated movies sorting
const sortTopRatedMovies = (field) => {
  searchStore.sortTopRatedMovies(field)
}

// Genre helper methods
const getGenreIcon = (genreName) => {
  const icons = {
    'thriller': '🎭',
    'action': '💥',
    'biography': '📚',
    'sci-fi': '🚀',
    'supernatural': '👻',
    'horror': '🦇',
    'drama': '🎬',
    'comedy': '😂',
    'romance': '💕',
    'crime': '🔍',
    'adventure': '🗺️',
    'mystery': '🔍'
  }
  return icons[genreName.toLowerCase()] || '🎬'
}

const getGenrePercentage = (count) => {
  const maxCount = top5Genres.value[0]?.count || 1
  return Math.round((count / maxCount) * 100)
}

// Load dashboard stats when component mounts
onMounted(async () => {
  await searchStore.loadDashboardStats()
})

const viewMovie = (movie) => {
  // TODO: Implement movie detail modal or page
  console.log('View movie:', movie)
}

const previousPage = async () => {
  await searchStore.previousPage()
}

const nextPage = async () => {
  await searchStore.nextPage()
}

const goToPage = async (page) => {
  await searchStore.goToPage(page)
}
</script>

<style scoped>
.nmle-movie-results {
  padding: 2rem 0;
  background: linear-gradient(180deg, #141414 0%, #000000 100%);
}

.stats-section {
  margin-bottom: 2rem;
}

.stats-card {
  background: linear-gradient(135deg, #e50914 0%, #f40612 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 12px;
  display: flex;
  justify-content: space-around;
  text-align: center;
  box-shadow: 0 4px 12px rgba(229, 9, 20, 0.3);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.error-card,
.empty-card {
  background: #222;
  color: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  border: 1px solid #333;
  max-width: 400px;
}

.no-results-state {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 4rem 2rem;
  min-height: 400px;
}

.no-results-card {
  background: #222;
  color: #fff;
  padding: 3rem;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.7);
  border: 1px solid #333;
  max-width: 500px;
  text-align: center;
}

.no-results-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.7;
}

.no-results-card h3 {
  color: #ffffff;
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.no-results-card p {
  color: #b3b3b3;
  font-size: 1.1rem;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.no-results-suggestions {
  background: #1a1a1a;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  text-align: left;
}

.no-results-suggestions p {
  color: #e5e5e5;
  font-weight: 600;
  margin-bottom: 1rem;
  text-align: center;
}

.no-results-suggestions ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.no-results-suggestions li {
  color: #b3b3b3;
  padding: 0.5rem 0;
  padding-left: 1.5rem;
  position: relative;
}

.no-results-suggestions li::before {
  content: "•";
  color: #e50914;
  position: absolute;
  left: 0;
  font-weight: bold;
}

.movie-dashboard {
  margin-top: 2rem;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 2rem;
}

.dashboard-header h2 {
  color: #ffffff;
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.dashboard-header p {
  color: #999;
  font-size: 1rem;
  margin: 0;
}

.top-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.7);
  border-color: #555;
  background: #2a2a2a;
}

.stat-icon {
  font-size: 2rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #333;
  border-radius: 50%;
  color: #e5e5e5;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #e5e5e5;
  margin-bottom: 0.25rem;
}

.stat-label {
  color: #b3b3b3;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.genres-section {
  margin-bottom: 3rem;
}

.genres-section h3 {
  color: #ffffff;
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
}

.genres-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.genre-card {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  border: 1px solid #333;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.genre-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(229, 9, 20, 0.3);
  border-color: #e50914;
}

.genre-card.rank-1:hover {
  box-shadow: 0 8px 25px rgba(255, 215, 0, 0.4);
  border-color: #ffd700;
}

.genre-card.rank-2:hover {
  box-shadow: 0 8px 25px rgba(192, 192, 192, 0.4);
  border-color: #c0c0c0;
}

.genre-card.rank-3:hover {
  box-shadow: 0 8px 25px rgba(205, 127, 50, 0.4);
  border-color: #cd7f32;
}

.genre-card.rank-4:hover {
  box-shadow: 0 8px 25px rgba(74, 144, 226, 0.4);
  border-color: #4a90e2;
}

.genre-card.rank-5:hover {
  box-shadow: 0 8px 25px rgba(123, 104, 238, 0.4);
  border-color: #7b68ee;
}

.genre-card.rank-1 {
  border-color: #ffd700;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  box-shadow: 0 2px 8px rgba(255, 215, 0, 0.2);
}

.genre-card.rank-2 {
  border-color: #c0c0c0;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  box-shadow: 0 2px 8px rgba(192, 192, 192, 0.2);
}

.genre-card.rank-3 {
  border-color: #cd7f32;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  box-shadow: 0 2px 8px rgba(205, 127, 50, 0.2);
}

.genre-card.rank-4 {
  border-color: #4a90e2;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  box-shadow: 0 2px 8px rgba(74, 144, 226, 0.2);
}

.genre-card.rank-5 {
  border-color: #7b68ee;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  box-shadow: 0 2px 8px rgba(123, 104, 238, 0.2);
}

.genre-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.genre-rank-badge {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #e50914 0%, #b8070f 100%);
  color: #ffffff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
  box-shadow: 0 2px 8px rgba(229, 9, 20, 0.4);
}

.genre-card.rank-1 .genre-rank-badge {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #000;
  box-shadow: 0 2px 8px rgba(255, 215, 0, 0.4);
}

.genre-card.rank-2 .genre-rank-badge {
  background: linear-gradient(135deg, #c0c0c0 0%, #e0e0e0 100%);
  color: #000;
  box-shadow: 0 2px 8px rgba(192, 192, 192, 0.4);
}

.genre-card.rank-3 .genre-rank-badge {
  background: linear-gradient(135deg, #cd7f32 0%, #daa520 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(205, 127, 50, 0.4);
}

.genre-icon {
  font-size: 1.5rem;
  opacity: 0.8;
}

.genre-card-content {
  text-align: center;
  margin-bottom: 1rem;
}

.genre-name {
  color: #ffffff;
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  text-transform: capitalize;
}

.genre-count {
  color: #ccc;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.genre-percentage {
  color: #e50914;
  font-size: 0.8rem;
  font-weight: 600;
}

.genre-card-footer {
  margin-top: auto;
}

.genre-progress-bar {
  width: 100%;
  height: 6px;
  background: #333;
  border-radius: 3px;
  overflow: hidden;
}

.genre-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #e50914 0%, #f40612 100%);
  border-radius: 3px;
  transition: width 0.6s ease;
}

.genre-card.rank-1 .genre-progress-fill {
  background: linear-gradient(90deg, #ffd700 0%, #ffed4e 100%);
}

.genre-card.rank-2 .genre-progress-fill {
  background: linear-gradient(90deg, #c0c0c0 0%, #e0e0e0 100%);
}

.genre-card.rank-3 .genre-progress-fill {
  background: linear-gradient(90deg, #cd7f32 0%, #daa520 100%);
}

.yearly-section {
  margin-bottom: 3rem;
  padding-top: 2rem;
}

.yearly-table-container h3 {
  color: #fff;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.yearly-table-container h3::before {
  content: "📅";
  font-size: 1.2rem;
}

.yearly-table-container {
  background: #222;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border: 1px solid #333;
  overflow-x: auto;
}

.yearly-table {
  width: 100%;
  border-collapse: collapse;
  color: #fff;
}

.yearly-table th {
  background: #e50914;
  color: #fff;
  padding: 1rem;
  text-align: left;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.9rem;
}

.yearly-table td {
  padding: 1rem;
  border-bottom: 1px solid #333;
  vertical-align: top;
}

.year-row:hover {
  background-color: rgba(229, 9, 20, 0.1);
}

.year-cell {
  font-weight: 700;
  font-size: 1.1rem;
  color: #e50914;
  width: 120px;
  min-width: 120px;
}

.count-cell {
  font-weight: 600;
  font-size: 1.2rem;
  color: #ffffff;
}

.genres-cell {
  min-width: 150px;
}

.genre-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.genre-tag {
  background: #e50914;
  color: #ffffff;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.movies-cell {
  min-width: 200px;
}

.movie-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.movie-item {
  color: #e5e5e5;
  font-size: 0.9rem;
  padding: 0.25rem 0;
  border-bottom: 1px solid #333;
}

.movie-item:last-child {
  border-bottom: none;
}

.dashboard-actions {
  text-align: center;
}

.results-section {
  margin-top: 2rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.results-header h2 {
  color: #ffffff;
  margin: 0;
  font-size: 1.8rem;
  font-weight: 700;
}

.results-info {
  color: #999;
  font-size: 0.9rem;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.movie-card {
  background: #222;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  border: 1px solid #333;
  overflow: hidden;
  transition: all 0.3s ease;
}

.movie-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.7);
  border-color: #e50914;
}

.movie-poster {
  position: relative;
  height: 200px;
  background: linear-gradient(45deg, #333, #555);
  display: flex;
  align-items: center;
  justify-content: center;
}

.poster-placeholder {
  width: 80px;
  height: 80px;
  background: #e50914;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(229, 9, 20, 0.3);
}

.movie-rating {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.movie-info {
  padding: 1.5rem;
}

.movie-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #ffffff;
  margin: 0 0 0.5rem 0;
  line-height: 1.3;
}

.movie-year {
  color: #999;
  font-size: 0.9rem;
  margin: 0 0 1rem 0;
}

.movie-meta {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.movie-genre,
.movie-subgenre {
  background: #e50914;
  color: #ffffff;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.movie-details {
  margin-bottom: 1rem;
}

.movie-details p {
  margin: 0.25rem 0;
  font-size: 0.9rem;
  color: #e5e5e5;
}

.movie-plot {
  color: #999;
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 1.5rem;
}

.movie-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.8rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 3rem;
}

.page-numbers {
  display: flex;
  gap: 0.5rem;
}

.page-btn {
  padding: 8px 12px;
  border: 1px solid #333;
  background: #222;
  color: #e5e5e5;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-btn:hover {
  background: #333;
  color: #fff;
}

.page-btn.active {
  background: #e50914;
  color: white;
  border-color: #e50914;
}

/* Mobile responsive utilities - columns hidden only on very small mobile screens */

@media (max-width: 480px) {
  .mobile-hidden {
    display: none;
  }
  
  .stats-card {
    flex-direction: column;
    gap: 1rem;
  }
  
  .results-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .movies-grid {
    grid-template-columns: 1fr;
  }
  
  .pagination {
    flex-wrap: wrap;
  }
  
  .top-stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
  }
  
  .stat-card {
    padding: 1rem;
  }
  
  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 1.5rem;
  }
  
  .stat-number {
    font-size: 1.5rem;
  }
  
  .genre-bar {
    width: 150px;
  }
  
  .yearly-table-container {
    padding: 1rem;
  }
  
  .yearly-table th,
  .yearly-table td {
    padding: 0.75rem 0.5rem;
    font-size: 0.9rem;
  }
  
  .yearly-table th {
    font-size: 0.8rem;
  }
  
  .genre-tags {
    gap: 0.25rem;
  }
  
  .genre-tag {
    font-size: 0.7rem;
    padding: 0.2rem 0.5rem;
  }
  
  .movie-item {
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .top-stats-grid {
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
  }
  
  .stat-card {
    padding: 0.75rem;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 1.2rem;
  }
  
  .stat-number {
    font-size: 1.2rem;
  }
  
  .genre-bar {
    width: 100px;
  }
  
  .yearly-table th,
  .yearly-table td {
    padding: 0.5rem 0.25rem;
    font-size: 0.8rem;
  }
  
  .yearly-table th {
    font-size: 0.7rem;
  }
  
  .dashboard-header h2 {
    font-size: 1.5rem;
  }
  
  .dashboard-header p {
    font-size: 0.9rem;
  }
  
  .no-results-card {
    padding: 2rem;
    margin: 1rem;
  }
  
  .no-results-icon {
    font-size: 3rem;
  }
  
  .no-results-card h3 {
    font-size: 1.5rem;
  }
  
  .no-results-card p {
    font-size: 1rem;
  }
}

/* Top-Rated Movies Section */
.top-rated-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  border-radius: 12px;
  border: 1px solid #333;
}

.top-rated-section h3 {
  color: #fff;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.top-rated-section h3::before {
  content: "⭐";
  font-size: 1.2rem;
}

.top-rated-table-container {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #444;
}

.top-rated-table {
  width: 100%;
  border-collapse: collapse;
  background: #1a1a1a;
  color: #fff;
}

.top-rated-table thead {
  background: linear-gradient(135deg, #e50914 0%, #b8070f 100%);
  color: #fff;
}

.top-rated-table th {
  padding: 1rem 0.75rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #b8070f;
  position: relative;
}

.top-rated-table th.sortable {
  cursor: pointer;
  user-select: none;
  transition: all 0.2s ease;
  position: relative;
}

.top-rated-table th.sortable:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-1px);
}

.top-rated-table th.sortable.active {
  background: rgba(255, 255, 255, 0.2);
}

.sort-arrow {
  margin-left: 0.5rem;
  font-size: 0.8rem;
  opacity: 0.8;
}

.top-rated-table tbody tr {
  border-bottom: 1px solid #333;
  transition: background-color 0.2s ease;
}

.top-rated-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.05);
}

.top-rated-table tbody tr:last-child {
  border-bottom: none;
}

.top-rated-table td {
  padding: 1rem 0.75rem;
  font-size: 0.9rem;
  vertical-align: middle;
}

.rating-cell {
  text-align: center;
  width: 100px;
}

.rating-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #000;
  padding: 0.25rem 0.5rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.85rem;
}

.rating-number {
  font-weight: 700;
}

.rating-stars {
  font-size: 0.8rem;
  color: #ff4757;
  filter: drop-shadow(0 0 5px rgba(255, 71, 87, 0.6));
}

.title-cell {
  font-weight: 600;
  color: #fff;
  font-size: 1rem;
}

.year-cell {
  text-align: center;
  color: #ccc;
  font-weight: 500;
  width: 120px;
  min-width: 120px;
}

.genre-cell {
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
}

.genre-tag {
  display: inline-block;
  background: linear-gradient(135deg, #e50914 0%, #b8070f 100%);
  color: #fff;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: capitalize;
  text-align: center;
  min-width: 80px;
  justify-content: center;
}

.director-cell {
  color: #ccc;
  font-style: italic;
}

/* Responsive design for top-rated table */
@media (max-width: 1024px) {
  .top-rated-section {
    margin-top: 1.5rem;
    padding: 1rem;
  }
  
  .top-rated-section h3 {
    font-size: 1.25rem;
  }
  
  .top-rated-table th,
  .top-rated-table td {
    padding: 0.75rem 0.5rem;
    font-size: 0.8rem;
  }
  
  .rating-display {
    padding: 0.2rem 0.4rem;
    font-size: 0.75rem;
  }
  
  .title-cell {
    font-size: 0.9rem;
  }
  
  .genre-tag {
    padding: 0.2rem 0.5rem;
    font-size: 0.7rem;
    min-width: 60px;
  }
  
  .genre-cell {
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .year-cell {
    width: 100px;
    min-width: 100px;
  }
  
  .genres-cards {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
  }
  
  .genre-card {
    padding: 1rem;
  }
  
  .genre-name {
    font-size: 1rem;
  }
  
  .genre-icon {
    font-size: 1.2rem;
  }
  
  .genre-rank-badge {
    width: 28px;
    height: 28px;
    font-size: 0.8rem;
  }
}

/* New movie details styling */
.movie-production {
  font-size: 0.85rem;
  color: #ccc;
  margin: 0.25rem 0;
}

.movie-file-id {
  font-size: 0.75rem;
  color: #999;
  margin: 0.25rem 0;
  font-family: monospace;
}
</style>
