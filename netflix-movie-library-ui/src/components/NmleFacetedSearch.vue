<template>
  <div class="nmle-faceted-search" v-if="facets && facets.length > 0">
    <div class="facets-container">
      <h3 class="facets-title">Filter by</h3>
      
      <div v-for="facet in facets" :key="facet.field" class="facet-group">
        <h4 class="facet-label">{{ formatFacetLabel(facet.field) }}</h4>
        <div class="facet-values">
          <label 
            v-for="value in facet.values.slice(0, 10)" 
            :key="value.value" 
            class="facet-item"
          >
            <input 
              type="checkbox" 
              :value="value.value"
              :checked="isSelected(facet.field, value.value)"
              @change="handleFacetChange(facet.field, value.value, $event.target.checked)"
              class="facet-checkbox"
            />
            <span class="facet-value">{{ value.value }}</span>
            <span class="facet-count">({{ value.count }})</span>
          </label>
        </div>
      </div>
      
      <button @click="clearAllFacets" class="clear-facets-btn">
        Clear All Filters
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useSearchStore } from '../stores/searchStore'

const searchStore = useSearchStore()

const props = defineProps({
  facets: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['facet-change'])

const selectedFacets = computed(() => {
  const facets = {}
  if (searchStore.filters.genre) facets.genre = [searchStore.filters.genre]
  if (searchStore.filters.subgenre) facets.subgenre = [searchStore.filters.subgenre]
  if (searchStore.filters.language) facets.language = [searchStore.filters.language]
  if (searchStore.filters.productionHouse) facets.productionHouse = [searchStore.filters.productionHouse]
  return facets
})

const formatFacetLabel = (field) => {
  const labels = {
    'genre': 'Genre',
    'subgenre': 'Subgenre', 
    'language': 'Language',
    'production_house': 'Production House'
  }
  return labels[field] || field
}

const isSelected = (field, value) => {
  const fieldMap = {
    'genre': 'genre',
    'subgenre': 'subgenre',
    'language': 'language', 
    'production_house': 'productionHouse'
  }
  const filterField = fieldMap[field]
  return searchStore.filters[filterField] === value
}

const handleFacetChange = (field, value, checked) => {
  const fieldMap = {
    'genre': 'genre',
    'subgenre': 'subgenre',
    'language': 'language',
    'production_house': 'productionHouse'
  }
  
  const filterField = fieldMap[field]
  const newFilters = { ...searchStore.filters }
  
  if (checked) {
    newFilters[filterField] = value
  } else {
    newFilters[filterField] = ''
  }
  
  searchStore.setFilters(newFilters)
  emit('facet-change', newFilters)
}

const clearAllFacets = () => {
  searchStore.clearFilters()
  emit('facet-change', {})
}
</script>

<style scoped>
.nmle-faceted-search {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.facets-container {
  max-height: 400px;
  overflow-y: auto;
}

.facets-title {
  color: #fff;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #333;
}

.facet-group {
  margin-bottom: 1.5rem;
}

.facet-label {
  color: #ccc;
  font-size: 0.9rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  text-transform: capitalize;
}

.facet-values {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.facet-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0;
  cursor: pointer;
  color: #ccc;
  font-size: 0.85rem;
}

.facet-item:hover {
  color: #fff;
}

.facet-checkbox {
  margin: 0;
  accent-color: #e50914;
}

.facet-value {
  flex: 1;
}

.facet-count {
  color: #999;
  font-size: 0.8rem;
}

.clear-facets-btn {
  background: #e50914;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  margin-top: 1rem;
  width: 100%;
  transition: background-color 0.2s ease;
}

.clear-facets-btn:hover {
  background: #d40813;
}

/* Scrollbar styling */
.facets-container::-webkit-scrollbar {
  width: 6px;
}

.facets-container::-webkit-scrollbar-track {
  background: #333;
  border-radius: 3px;
}

.facets-container::-webkit-scrollbar-thumb {
  background: #666;
  border-radius: 3px;
}

.facets-container::-webkit-scrollbar-thumb:hover {
  background: #888;
}
</style>
