<template>
  <div class="home">
    <nmle-search-bar />
    <nmle-movie-results />
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useSearchStore } from '../stores/searchStore'
import NmleSearchBar from '../components/NmleSearchBar.vue'
import NmleMovieResults from '../components/NmleMovieResults.vue'

const searchStore = useSearchStore()
const route = useRoute()

const loadDashboardData = async () => {
  // Clear any existing search state and load dashboard data
  searchStore.clearSearch()
  await Promise.all([
    searchStore.loadFilterOptions(),
    searchStore.loadStats(),
    searchStore.loadDashboardStats()
  ])
}

onMounted(loadDashboardData)

// Watch for route changes to reset state when navigating to home
watch(() => route.path, (newPath) => {
  if (newPath === '/home') {
    loadDashboardData()
  }
})
</script>

<style scoped>
.home {
  min-height: 100vh;
}
</style>
