<template>
  <div class="nmle-search-bar">
    <div class="container">
      <div class="search-container">
        <div class="search-input-group">
          <div class="search-input-wrapper">
            <input
              v-model="searchQuery"
              @keyup.enter="handleSearch"
              @input="handleInput"
              type="text"
              placeholder="Search movies by title, actor, director, plot, writer, or awards..."
              class="search-input"
            />
            <button 
              v-if="searchQuery" 
              @click="handleClear" 
              class="clear-button"
              type="button"
            >
              ✕
            </button>
          </div>
          <button @click="handleSearch" class="search-button" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            <span v-else>Search</span>
          </button>
        </div>
        
        <div class="filters-section" v-if="showFilters">
          <div class="filters-row">
            <select v-model="filters.genre" @change="handleFilterChange" class="filter-select">
              <option value="">All Genres</option>
              <option v-for="genre in filterOptions.genres" :key="genre" :value="genre">
                {{ genre }}
              </option>
            </select>
            
            <select v-model="filters.subgenre" @change="handleFilterChange" class="filter-select">
              <option value="">All Subgenres</option>
              <option v-for="subgenre in filterOptions.subgenres" :key="subgenre" :value="subgenre">
                {{ subgenre }}
              </option>
            </select>
            
            <select v-model="filters.language" @change="handleFilterChange" class="filter-select">
              <option value="">All Languages</option>
              <option v-for="language in filterOptions.languages" :key="language" :value="language">
                {{ language }}
              </option>
            </select>
            
            <select v-model="sortOptions.field" @change="handleSortChange" class="filter-select">
              <option value="relevance">Sort by Relevance</option>
              <option value="title">Sort by Title</option>
              <option value="imdb_rating">Sort by Rating</option>
              <option value="year">Sort by Year</option>
            </select>
          </div>
          
          <div class="filters-row">
            <div class="range-inputs">
              <label>Year Range:</label>
              <input
                v-model.number="filters.yearFrom"
                @change="handleFilterChange"
                type="number"
                placeholder="From"
                class="range-input"
                min="1900"
                :max="new Date().getFullYear()"
              />
              <span>-</span>
              <input
                v-model.number="filters.yearTo"
                @change="handleFilterChange"
                type="number"
                placeholder="To"
                class="range-input"
                min="1900"
                :max="new Date().getFullYear()"
              />
            </div>
            
            <div class="range-inputs">
              <label>Rating Range:</label>
              <input
                v-model.number="filters.ratingMin"
                @change="handleFilterChange"
                type="number"
                placeholder="Min"
                class="range-input"
                min="0"
                max="10"
                step="0.1"
              />
              <span>-</span>
              <input
                v-model.number="filters.ratingMin"
                @change="handleFilterChange"
                type="number"
                placeholder="Max"
                class="range-input"
                min="0"
                max="10"
                step="0.1"
              />
            </div>
            
            <button @click="clearFilters" class="btn btn-secondary">
              Clear Filters
            </button>
          </div>
        </div>
        
        <div class="search-actions" style="display: none;">
          <button @click="toggleFilters" class="btn btn-secondary">
            {{ showFilters ? 'Hide' : 'Show' }} Filters
          </button>
        </div>
      </div>
      
      <!-- Faceted Search -->
      <NmleFacetedSearch 
        v-if="facets && facets.length > 0"
        :facets="facets"
        @facet-change="handleFacetChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useSearchStore } from '../stores/searchStore'
import NmleFacetedSearch from './NmleFacetedSearch.vue'

const searchStore = useSearchStore()

// Local state
const searchQuery = ref('')
const showFilters = ref(false)

// Computed
const filters = computed(() => searchStore.filters)
const sortOptions = computed(() => searchStore.sortOptions)
const filterOptions = computed(() => searchStore.filterOptions)
const loading = computed(() => searchStore.loading)
const facets = computed(() => searchStore.facets)

// Methods
const handleInput = async () => {
  searchStore.setSearchQuery(searchQuery.value)
  
  // If input is empty, clear search and return to dashboard
  if (!searchQuery.value.trim()) {
    searchStore.clearSearch()
  }
}

const handleSearch = async () => {
  // Enable advanced search for better filtering
  searchStore.useAdvancedSearch = true
  await searchStore.search()
}

const handleClear = () => {
  searchStore.clearSearch()
}

const handleFilterChange = async () => {
  searchStore.setFilters(filters.value)
  await searchStore.search()
}

const handleSortChange = async () => {
  searchStore.setSortOptions(sortOptions.value)
  await searchStore.search()
}

const clearFilters = async () => {
  searchStore.clearFilters()
  await searchStore.search()
}

const handleFacetChange = (newFilters) => {
  // Trigger search with new filters
  searchStore.search()
}

const toggleFilters = () => {
  showFilters.value = !showFilters.value
}

// Watch for external changes
watch(() => searchStore.searchQuery, (newValue) => {
  searchQuery.value = newValue
  
  // If search query is cleared externally, ensure we're in dashboard mode
  if (!newValue.trim()) {
    searchStore.clearSearch()
  }
})
</script>

<style scoped>
.nmle-search-bar {
  padding: 3rem 0;
}

.search-container {
  max-width: 800px;
  margin: 0 auto;
}

.search-input-group {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.search-input-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.search-input {
  width: 100%;
  padding: 16px 20px;
  padding-right: 50px;
  border: 2px solid #333;
  border-radius: 8px;
  font-size: 18px;
  background-color: #333;
  color: #fff;
  transition: all 0.3s ease;
}

.clear-button {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #999;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.clear-button:hover {
  background-color: #555;
  color: #fff;
  transform: translateY(-50%) scale(1.1);
}

.search-input:focus {
  outline: none;
  border-color: #e50914;
  box-shadow: 0 0 0 3px rgba(229, 9, 20, 0.3);
  background-color: #444;
}

.search-input::placeholder {
  color: #999;
}

.search-button {
  padding: 16px 32px;
  background: #e50914;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
  box-shadow: 0 4px 12px rgba(229, 9, 20, 0.3);
}

.search-button:hover:not(:disabled) {
  background: #f40612;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(229, 9, 20, 0.4);
}

.search-button:disabled {
  background: #666;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.filters-section {
  background: #222;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  border: 1px solid #333;
}

.filters-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.filters-row:last-child {
  margin-bottom: 0;
}

.filter-select {
  padding: 10px 14px;
  border: 1px solid #333;
  border-radius: 4px;
  background: #333;
  color: #fff;
  min-width: 150px;
  transition: all 0.3s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #e50914;
  background: #444;
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.range-inputs label {
  font-weight: 500;
  color: #e5e5e5;
  white-space: nowrap;
}

.range-input {
  width: 80px;
  padding: 8px 10px;
  border: 1px solid #333;
  border-radius: 4px;
  background: #333;
  color: #fff;
  text-align: center;
  transition: all 0.3s ease;
}

.range-input:focus {
  outline: none;
  border-color: #e50914;
  background: #444;
}

.search-actions {
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .search-input-group {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .search-input-wrapper {
    width: 100%;
  }
  
  .search-input {
    padding: 12px 16px;
    padding-right: 45px;
    font-size: 16px;
  }
  
  .search-button {
    padding: 12px 24px;
    font-size: 14px;
    letter-spacing: 0.3px;
  }
  
  .clear-button {
    right: 8px;
    width: 24px;
    height: 24px;
    font-size: 16px;
  }
  
  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-select {
    min-width: auto;
  }
  
  .range-inputs {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .search-input {
    padding: 10px 14px;
    padding-right: 40px;
    font-size: 14px;
  }
  
  .search-button {
    padding: 10px 20px;
    font-size: 13px;
    letter-spacing: 0.2px;
  }
  
  .clear-button {
    right: 6px;
    width: 22px;
    height: 22px;
    font-size: 14px;
  }
  
  .search-input-group {
    gap: 0.5rem;
  }
}
</style>
