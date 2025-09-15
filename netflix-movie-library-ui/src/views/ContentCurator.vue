<template>
  <div class="content-curator">
    <!-- Header Section -->
    <div class="curator-header">
      <div class="header-content">
        <h1 class="page-title">
          <span class="title-icon">🎬</span>
          Manage Movie Library
        </h1>
        <p class="page-description">Manage your movie library with full CRUD operations</p>
      </div>
      <div class="header-actions">
        <button 
          @click="openAddModal" 
          class="btn btn-primary add-movie-btn"
        >
          <span class="btn-icon">+</span>
          Add Movie
        </button>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="curator-controls">
      <div class="search-section">
        <div class="search-input-wrapper">
          <input
            v-model="searchQuery"
            @input="handleSearch"
            type="text"
            placeholder="Search movies..."
            class="search-input"
          />
          <button 
            v-if="searchQuery" 
            @click="clearSearch" 
            class="clear-btn"
          >
            ✕
          </button>
        </div>
      </div>
      
      <div class="filter-section desktop-only">
        <select v-model="selectedGenre" @change="applyFilters" class="filter-select">
          <option value="">All Genres</option>
          <option v-for="genre in availableGenres" :key="genre" :value="genre">
            {{ genre }}
          </option>
        </select>

        <select v-model="selectedYear" @change="applyFilters" class="filter-select">
          <option value="">All Years</option>
          <option v-for="year in availableYears" :key="year" :value="year">
            {{ year }}
          </option>
        </select>
      </div>
    </div>

    <!-- Movies Grid -->
    <div class="movies-grid-container">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading movies...</p>
      </div>

      <div v-else-if="filteredMovies.length === 0" class="empty-state">
        <div class="empty-icon">🎭</div>
        <h3>No movies found</h3>
        <p v-if="searchQuery || selectedGenre || selectedYear">
          Try adjusting your search criteria
        </p>
        <p v-else>
          Start by adding your first movie!
        </p>
      </div>

      <div v-else class="movies-table-container">
        <table class="movies-table">
          <thead>
            <tr>
              <th @click="handleSort('title')" class="sortable-header">
                Title {{ getSortIcon('title') }}
              </th>
              <th @click="handleSort('country')" class="sortable-header mobile-hidden">
                Country {{ getSortIcon('country') }}
              </th>
              <th @click="handleSort('year')" class="sortable-header mobile-hidden">
                Year {{ getSortIcon('year') }}
              </th>
              <th @click="handleSort('genre')" class="sortable-header mobile-hidden">
                Genre {{ getSortIcon('genre') }}
              </th>
              <th class="actions-header mobile-hidden">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="movie in paginatedMovies" 
              :key="movie.id" 
              class="movie-row"
              @click="openEditModal(movie)"
            >
              <td class="title-cell">
                <div class="movie-title">{{ movie.title }}</div>
                <div class="movie-details">
                  <span class="rating-display">
                    <span class="rating-number">{{ movie.imdbRating }}</span>
                    <span class="rating-star">⭐</span>
                  </span>
                  <span class="subgenre-tag" v-if="movie.subgenre && movie.subgenre !== 'unknown'">
                    {{ movie.subgenre }}
                  </span>
                  <span class="file-id-tag" v-if="movie.fileId">
                    ID: {{ movie.fileId.substring(0, 8) }}...
                  </span>
                </div>
              </td>
              <td class="country-cell mobile-hidden">{{ movie.country || 'N/A' }}</td>
              <td class="year-cell mobile-hidden">{{ movie.year }}</td>
              <td class="genre-cell mobile-hidden">
                <span class="genre-tag">{{ movie.genre }}</span>
              </td>
              <td class="actions-cell mobile-hidden">
                <div class="movie-actions">
                  <button 
                    @click.stop="openEditModal(movie)" 
                    class="action-btn edit-btn"
                    title="Edit Movie"
                  >
                    ✏️
                  </button>
                  <button 
                    @click.stop="confirmDelete(movie)" 
                    class="action-btn delete-btn"
                    title="Delete Movie"
                  >
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <button 
        @click="goToPage(currentPage - 1)" 
        :disabled="currentPage === 1"
        class="pagination-btn"
      >
        ← Previous
      </button>
      
      <span class="pagination-info">
        Page {{ currentPage }} of {{ totalPages }}
        ({{ filteredMovies.length }} movies)
      </span>
      
      <button 
        @click="goToPage(currentPage + 1)" 
        :disabled="currentPage === totalPages"
        class="pagination-btn"
      >
        Next →
      </button>
    </div>

    <!-- Add/Edit Movie Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ isEditing ? 'Edit Movie' : 'Add New Movie' }}</h2>
          <button @click="closeModal" class="modal-close">✕</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="saveMovie" class="movie-form">
            <div class="form-row">
              <div class="form-group">
                <label for="title">Title *</label>
                <input 
                  v-model="formData.title" 
                  type="text" 
                  id="title" 
                  required 
                  class="form-input"
                  autocomplete="off"
                />
              </div>
              
              <div class="form-group">
                <label for="year">Year *</label>
                <input 
                  v-model.number="formData.year" 
                  type="number" 
                  id="year" 
                  required 
                  min="1900" 
                  max="2030"
                  class="form-input"
                  autocomplete="off"
                />
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="genre">Genre *</label>
                <select v-model="formData.genre" id="genre" required class="form-select">
                  <option value="">Select Genre</option>
                  <option v-for="genre in availableGenres" :key="genre" :value="genre">
                    {{ genre }}
                  </option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="subgenre">Sub-genre</label>
                <input 
                  v-model="formData.subgenre" 
                  type="text" 
                  id="subgenre" 
                  class="form-input"
                  autocomplete="off"
                />
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="director">Director *</label>
                <input 
                  v-model="formData.director" 
                  type="text" 
                  id="director" 
                  required 
                  class="form-input"
                  autocomplete="off"
                />
              </div>
              
              <div class="form-group">
                <label for="imdbRating">IMDB Rating</label>
                <input 
                  v-model.number="formData.imdbRating" 
                  type="number" 
                  id="imdbRating" 
                  min="0" 
                  max="10" 
                  step="0.1"
                  class="form-input"
                  autocomplete="off"
                />
              </div>
            </div>
            
            <div class="form-group">
              <label for="stars">Stars (comma-separated)</label>
              <input 
                v-model="formData.stars" 
                type="text" 
                id="stars" 
                placeholder="Leonardo DiCaprio, Marion Cotillard, Tom Hardy"
                class="form-input"
                autocomplete="off"
              />
            </div>
            
            <div class="form-group">
              <label for="writer">Writer</label>
              <input 
                v-model="formData.writer" 
                type="text" 
                id="writer" 
                class="form-input"
                autocomplete="off"
              />
            </div>
            
            <div class="form-group">
              <label for="moviePlot">Plot Summary</label>
              <textarea 
                v-model="formData.moviePlot" 
                id="moviePlot" 
                rows="3"
                class="form-textarea"
                autocomplete="off"
              ></textarea>
            </div>
            
            <div class="form-group">
              <label for="content">Content (for search)</label>
              <textarea 
                v-model="formData.content" 
                id="content" 
                rows="3"
                placeholder="Additional content for search indexing..."
                class="form-textarea"
                autocomplete="off"
              ></textarea>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="language">Language</label>
              <input 
                v-model="formData.language" 
                type="text" 
                id="language" 
                class="form-input"
                autocomplete="off"
              />
              </div>
              
              <div class="form-group">
                <label for="country">Country</label>
              <input 
                v-model="formData.country" 
                type="text" 
                id="country" 
                class="form-input"
                autocomplete="off"
              />
              </div>
            </div>
            
            <div class="form-group">
              <label for="awards">Awards (comma-separated)</label>
              <input 
                v-model="formData.awards" 
                type="text" 
                id="awards" 
                placeholder="Oscar for Best Picture, Golden Globe for Best Director"
                class="form-input"
                autocomplete="off"
              />
            </div>
            
            <div class="form-group">
              <label for="productionHouse">Production House</label>
              <input 
                v-model="formData.productionHouse" 
                type="text" 
                id="productionHouse" 
                placeholder="Warner Bros. Pictures, Universal Pictures"
                class="form-input"
                autocomplete="off"
              />
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="limitedTo">Limited To</label>
                <input 
                  v-model="formData.limitedTo" 
                  type="text" 
                  id="limitedTo" 
                  placeholder="Access scope (e.g., department, team)"
                  class="form-input"
                  autocomplete="off"
                />
              </div>
              
              <div class="form-group">
                <label for="restrictedTo">Restricted To</label>
                <input 
                  v-model="formData.restrictedTo" 
                  type="text" 
                  id="restrictedTo" 
                  placeholder="Restriction scope (e.g., confidential, internal)"
                  class="form-input"
                  autocomplete="off"
                />
              </div>
            </div>
          </form>
        </div>
        
        <div class="modal-footer">
          <button @click="closeModal" class="btn btn-secondary">
            Cancel
          </button>
          <button 
            @click="saveMovie" 
            :disabled="saving"
            class="btn btn-primary"
          >
            <span v-if="saving" class="spinner-small"></span>
            {{ isEditing ? 'Update Movie' : 'Add Movie' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal-content delete-modal" @click.stop>
        <div class="modal-header">
          <h2>Confirm Delete</h2>
          <button @click="closeDeleteModal" class="modal-close">✕</button>
        </div>
        
        <div class="modal-body">
          <p>Are you sure you want to delete <strong>{{ movieToDelete?.title }}</strong>?</p>
          <p class="warning-text">This action cannot be undone.</p>
        </div>
        
        <div class="modal-footer">
          <button @click="closeDeleteModal" class="btn btn-secondary">
            Cancel
          </button>
          <button 
            @click="performDelete" 
            :disabled="deleting"
            class="btn btn-danger"
          >
            <span v-if="deleting" class="spinner-small"></span>
            Delete Movie
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useSearchStore } from '@/stores/searchStore'
import { 
  createMovie, 
  updateMovie, 
  deleteMovie, 
  getMovie 
} from '@/api/movieApi'
import enhancedMetricsService from '@/services/enhancedMetricsService'

export default {
  name: 'ContentCurator',
  setup() {
    const searchStore = useSearchStore()
    
    // Reactive data
    const movies = ref([])
    const loading = ref(false)
    const saving = ref(false)
    const deleting = ref(false)
    const searchQuery = ref('')
    const selectedGenre = ref('')
    const selectedYear = ref('')
    const showModal = ref(false)
    const showDeleteModal = ref(false)
    const isEditing = ref(false)
    const movieToDelete = ref(null)
    const currentEditingMovie = ref(null)
    const currentPage = ref(1)
    const pageSize = ref(12)
    const sortField = ref('updatedAt')
    const sortDirection = ref('desc')
    
    // Form data
    const formData = ref({
      title: '',
      year: new Date().getFullYear(),
      genre: '',
      subgenre: '',
      director: '',
      stars: '',
      writer: '',
      content: '',
      moviePlot: '',
      awards: '',
      imdbRating: 0.0,
      language: 'English',
      country: '',
      productionHouse: '',
      limitedTo: '',
      restrictedTo: ''
    })
    
    // Computed properties
    const availableGenres = computed(() => {
      const genres = new Set()
      movies.value.forEach(movie => {
        if (movie.genre && movie.genre !== 'unknown') {
          genres.add(movie.genre)
        }
      })
      return Array.from(genres).sort()
    })
    
    const availableYears = computed(() => {
      const years = new Set()
      movies.value.forEach(movie => {
        if (movie.year && movie.year > 1900) {
          years.add(movie.year)
        }
      })
      return Array.from(years).sort((a, b) => b - a)
    })
    
    const filteredMovies = computed(() => {
      let filtered = movies.value
      
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(movie => 
          movie.title.toLowerCase().includes(query) ||
          movie.director.toLowerCase().includes(query) ||
          (movie.stars && movie.stars.some(star => 
            star.toLowerCase().includes(query)
          )) ||
          movie.moviePlot.toLowerCase().includes(query)
        )
      }
      
      if (selectedGenre.value) {
        filtered = filtered.filter(movie => movie.genre === selectedGenre.value)
      }
      
      if (selectedYear.value) {
        filtered = filtered.filter(movie => movie.year === selectedYear.value)
      }
      
      // Apply sorting
      filtered.sort((a, b) => {
        let aValue = a[sortField.value]
        let bValue = b[sortField.value]
        
        // Handle different data types
        if (sortField.value === 'year' || sortField.value === 'imdbRating') {
          aValue = Number(aValue) || 0
          bValue = Number(bValue) || 0
        } else if (sortField.value === 'createdAt' || sortField.value === 'updatedAt') {
          // Handle timestamp fields - convert to numbers for comparison
          aValue = Number(aValue) || 0
          bValue = Number(bValue) || 0
        } else {
          aValue = String(aValue || '').toLowerCase()
          bValue = String(bValue || '').toLowerCase()
        }
        
        if (sortDirection.value === 'asc') {
          return aValue > bValue ? 1 : aValue < bValue ? -1 : 0
        } else {
          return aValue < bValue ? 1 : aValue > bValue ? -1 : 0
        }
      })
      
      return filtered
    })
    
    const totalPages = computed(() => 
      Math.ceil(filteredMovies.value.length / pageSize.value)
    )
    
    const paginatedMovies = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredMovies.value.slice(start, end)
    })
    
    // Methods
    const loadMovies = async () => {
      loading.value = true
      try {
        // Enable advanced search for better filtering
        searchStore.useAdvancedSearch = true
        
        // Use the existing search functionality to get all movies
        await searchStore.search('', {
          page: 1,
          pageSize: 1000 // Get all movies for curation
        })
        movies.value = searchStore.movies || []
      } catch (error) {
        console.error('Error loading movies:', error)
      } finally {
        loading.value = false
      }
    }
    
    const handleSearch = () => {
      currentPage.value = 1
    }
    
    const clearSearch = () => {
      searchQuery.value = ''
      selectedGenre.value = ''
      selectedYear.value = ''
      currentPage.value = 1
    }
    
    const applyFilters = () => {
      currentPage.value = 1
    }
    
    const goToPage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
      }
    }
    
    const handleSort = (field) => {
      if (sortField.value === field) {
        // Toggle direction if same field
        sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
      } else {
        // New field, default to ascending
        sortField.value = field
        sortDirection.value = 'asc'
      }
      
      // Track sorting metrics
      enhancedMetricsService.trackSorting(field, sortDirection.value, 'library')
      
      // Reset to first page when sorting
      currentPage.value = 1
    }
    
    const getSortIcon = (field) => {
      if (sortField.value !== field) return '↕️'
      return sortDirection.value === 'asc' ? '↑' : '↓'
    }
    
    const truncateText = (text, length) => {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    }
    
    const openAddModal = () => {
      isEditing.value = false
      currentEditingMovie.value = null // Clear any previous editing movie
      formData.value = {
        title: '',
        year: new Date().getFullYear(),
        genre: '',
        subgenre: '',
        director: '',
        stars: '',
        writer: '',
        content: '',
        moviePlot: '',
        awards: '',
        imdbRating: 0.0,
        language: 'English',
        country: '',
        productionHouse: '',
        limitedTo: '',
        restrictedTo: ''
      }
      showModal.value = true
    }
    
    const openEditModal = (movie) => {
      isEditing.value = true
      currentEditingMovie.value = movie // Store the current movie being edited
      formData.value = {
        title: movie.title || '',
        year: movie.year || new Date().getFullYear(),
        genre: movie.genre || '',
        subgenre: movie.subgenre || '',
        director: movie.director || '',
        stars: Array.isArray(movie.stars) ? movie.stars.join(', ') : (movie.stars || ''),
        writer: movie.writer || '',
        content: movie.content || '',
        moviePlot: movie.moviePlot || '',
        awards: Array.isArray(movie.awards) ? movie.awards.join(', ') : (movie.awards || ''),
        imdbRating: movie.imdbRating || 0.0,
        language: movie.language || 'English',
        country: movie.country || '',
        productionHouse: movie.productionHouse || '',
        limitedTo: movie.limitedTo || '',
        restrictedTo: movie.restrictedTo || ''
      }
      showModal.value = true
    }
    
    const closeModal = () => {
      showModal.value = false
      isEditing.value = false
      currentEditingMovie.value = null
    }
    
    const saveMovie = async () => {
      saving.value = true
      try {
        const movieData = {
          title: formData.value.title,
          year: formData.value.year,
          genre: formData.value.genre,
          subgenre: formData.value.subgenre,
          director: formData.value.director,
          stars: formData.value.stars,
          writer: formData.value.writer,
          content: formData.value.content,
          moviePlot: formData.value.moviePlot,
          awards: formData.value.awards,
          imdbRating: formData.value.imdbRating,
          language: formData.value.language,
          country: formData.value.country,
          productionHouse: formData.value.productionHouse,
          limitedTo: formData.value.limitedTo,
          restrictedTo: formData.value.restrictedTo
        }
        
        let result
        if (isEditing.value) {
          // Update existing movie - use the stored movie ID (should be movie: prefixed)
          if (currentEditingMovie.value && currentEditingMovie.value.id) {
            // Ensure the ID has the movie: prefix
            const movieId = currentEditingMovie.value.id.startsWith('movie:') 
              ? currentEditingMovie.value.id 
              : `movie:${currentEditingMovie.value.id}`
            result = await updateMovie(movieId, movieData)
          } else {
            throw new Error('Movie ID not found for update')
          }
        } else {
          // Create new movie
          result = await createMovie(movieData)
        }
        
        if (result.success) {
          // Track library operation
          const operation = isEditing.value ? 'edit' : 'create'
          enhancedMetricsService.trackLibraryOperation(operation, {
            id: result.movie?.id || currentEditingMovie.value?.id,
            title: movieData.title,
            genre: movieData.genre,
            year: movieData.year
          })
          
          closeModal()
          await loadMovies() // Reload the list
        } else {
          alert(`Error: ${result.message}`)
        }
      } catch (error) {
        console.error('Error saving movie:', error)
        alert(`Error saving movie: ${error.message}`)
      } finally {
        saving.value = false
      }
    }
    
    const confirmDelete = (movie) => {
      movieToDelete.value = movie
      showDeleteModal.value = true
    }
    
    const closeDeleteModal = () => {
      showDeleteModal.value = false
      movieToDelete.value = null
    }
    
    const performDelete = async () => {
      if (!movieToDelete.value) return
      
      deleting.value = true
      try {
        // Ensure the ID has the movie: prefix
        const movieId = movieToDelete.value.id.startsWith('movie:') 
          ? movieToDelete.value.id 
          : `movie:${movieToDelete.value.id}`
        
        const result = await deleteMovie(movieId)
        
        if (result.success) {
          // Track library operation
          enhancedMetricsService.trackLibraryOperation('delete', {
            id: movieToDelete.value.id,
            title: movieToDelete.value.title,
            genre: movieToDelete.value.genre,
            year: movieToDelete.value.year
          })
          
          closeDeleteModal()
          await loadMovies() // Reload the list
        } else {
          alert(`Error: ${result.message}`)
        }
      } catch (error) {
        console.error('Error deleting movie:', error)
        alert(`Error deleting movie: ${error.message}`)
      } finally {
        deleting.value = false
      }
    }
    
    // Lifecycle
    onMounted(() => {
      loadMovies()
    })
    
    return {
      movies,
      loading,
      saving,
      deleting,
      searchQuery,
      selectedGenre,
      selectedYear,
      showModal,
      showDeleteModal,
      isEditing,
      movieToDelete,
      currentPage,
      pageSize,
      formData,
      availableGenres,
      availableYears,
      filteredMovies,
      totalPages,
      paginatedMovies,
      loadMovies,
      handleSearch,
      clearSearch,
      applyFilters,
      goToPage,
      handleSort,
      getSortIcon,
      truncateText,
      openAddModal,
      openEditModal,
      closeModal,
      saveMovie,
      confirmDelete,
      closeDeleteModal,
      performDelete
    }
  }
}
</script>

<style scoped>
.content-curator {
  min-height: 100vh;
  background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 100%);
  color: #ffffff;
  padding: 2rem;
  padding-left: 8rem;
  padding-right: 8rem;
  max-width: 1400px;
  margin: 0 auto;
}

.curator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #333;
}

.header-content .page-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.title-icon {
  font-size: 1.5rem;
}

.page-description {
  color: #ccc;
  margin: 0.5rem 0 0 0;
  font-size: 1.1rem;
}

.add-movie-btn {
  background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.add-movie-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(74, 144, 226, 0.3);
}

.curator-controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.search-section {
  flex: 1;
  min-width: 300px;
}

.search-input-wrapper {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem;
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 8px;
  color: white;
  font-size: 1rem;
}

.search-input:focus {
  outline: none;
  border-color: #e50914;
  box-shadow: 0 0 0 2px rgba(229, 9, 20, 0.2);
}

.clear-btn {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 0.25rem;
}

.filter-section {
  display: flex;
  gap: 0.5rem;
}

.filter-select {
  padding: 0.75rem;
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  min-width: 150px;
}

.movies-grid-container {
  margin-bottom: 2rem;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #333;
  border-top: 4px solid #e50914;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state .empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: #ccc;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #999;
}

.movies-table-container {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 2rem;
}

.movies-table {
  width: 100%;
  border-collapse: collapse;
  background: #1a1a1a;
}

.movies-table thead {
  background: #2a2a2a;
}

.movies-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #fff;
  border-bottom: 1px solid #333;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.movies-table th:nth-child(1) {
  width: 30%;
  text-align: left;
}

.movies-table th:nth-child(2),
.movies-table th:nth-child(3),
.movies-table th:nth-child(4),
.movies-table th:nth-child(5) {
  text-align: center;
}

.sortable-header {
  cursor: pointer;
  user-select: none;
  transition: all 0.2s ease;
  position: relative;
}

.sortable-header:hover {
  background: #333;
  color: #fff;
}

.actions-header {
  cursor: default;
}

.movies-table td {
  padding: 1rem;
  border-bottom: 1px solid #333;
  vertical-align: top;
}

.movie-row {
  cursor: pointer;
  transition: all 0.2s ease;
}

.movie-row:hover {
  background: #2a2a2a;
}

.movie-row:last-child td {
  border-bottom: none;
}

.title-cell {
  width: 30%;
}

.movie-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #fff;
  margin-bottom: 0.5rem;
}

.movie-details {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.25rem;
}

.rating-display {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: #2a2a2a;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-size: 0.85rem;
}

.rating-number {
  font-weight: 600;
  color: #ffd700;
}

.rating-star {
  font-size: 0.8rem;
}

.subgenre-tag {
  background: #333;
  color: #ccc;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.file-id-tag {
  background: #1a1a1a;
  color: #999;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 400;
  font-family: monospace;
}

.country-cell {
  width: 17.5%;
  text-align: center;
  color: #ccc;
  font-size: 0.9rem;
  font-weight: 500;
}

.year-cell {
  width: 17.5%;
  text-align: center;
  color: #ccc;
  font-weight: 500;
  font-size: 1rem;
}

.genre-cell {
  width: 17.5%;
  text-align: center;
}

.genre-tag {
  background: #2a2a2a;
  color: #ccc;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  font-size: 0.9rem;
  display: inline-block;
  font-weight: 500;
}

.actions-cell {
  width: 17.5%;
  text-align: center;
}

.movie-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.action-btn {
  background: none;
  border: 1px solid #444;
  color: #ccc;
  padding: 0.4rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.edit-btn:hover {
  background: #2a2a2a;
  border-color: #4a90e2;
  color: #4a90e2;
}

.delete-btn:hover {
  background: #2a2a2a;
  border-color: #dc3545;
  color: #dc3545;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.pagination-btn {
  background: #2a2a2a;
  border: 1px solid #444;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: #3a3a3a;
  border-color: #e50914;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  color: #ccc;
  font-size: 0.875rem;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 12px;
  width: 95%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #333;
}

.modal-header h2 {
  margin: 0;
  color: #fff;
}

.modal-close {
  background: none;
  border: none;
  color: #999;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.25rem;
}

.modal-body {
  padding: 1.5rem;
}

.movie-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  color: #ccc;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-input, .form-select, .form-textarea {
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 6px;
  color: white;
  padding: 0.75rem;
  font-size: 1rem;
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  outline: none;
  border-color: #e50914;
  box-shadow: 0 0 0 2px rgba(229, 9, 20, 0.2);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #333;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3);
}

.btn-secondary {
  background: #2a2a2a;
  color: #ccc;
  border: 1px solid #444;
}

.btn-secondary:hover {
  background: #3a3a3a;
}

.btn-danger {
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.delete-modal .modal-body {
  text-align: center;
}

.warning-text {
  color: #e50914;
  font-weight: 600;
  margin-top: 0.5rem;
}

/* Responsive Design */
@media (max-width: 900px) {
  .page-title {
    font-size: 1.1rem;
  }
  
  .title-icon {
    font-size: 0.9rem;
  }
  
  .page-description {
    font-size: 0.8rem;
  }
}

@media (max-width: 768px) {
  .content-curator {
    padding: 1rem;
  }
  
  .curator-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .page-title {
    font-size: 1rem;
  }
  
  .title-icon {
    font-size: 0.8rem;
  }
  
  .page-description {
    font-size: 0.75rem;
  }
  
  .curator-controls {
    flex-direction: column;
  }
  
  .desktop-only {
    display: none;
  }
  
  .mobile-hidden {
    display: none;
  }
  
  .search-section {
    min-width: auto;
  }
  
  .movies-table-container {
    overflow-x: auto;
  }
  
  .movies-table {
    min-width: 100%;
  }
  
  .movies-table th,
  .movies-table td {
    padding: 0.75rem 0.5rem;
    font-size: 0.85rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    margin: 1rem;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 0.9rem;
  }
  
  .title-icon {
    font-size: 0.7rem;
  }
  
  .page-description {
    font-size: 0.7rem;
  }
  
  .movies-table th,
  .movies-table td {
    padding: 0.5rem 0.25rem;
    font-size: 0.8rem;
  }
  
  .movie-actions {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .action-btn {
    width: 28px;
    height: 28px;
    font-size: 0.8rem;
  }
}
</style>
