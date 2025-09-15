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
import { useUserStore } from '../stores/userStore'
import { enhancedMetricsService } from '../services/enhancedMetricsService.js'
import NmleSearchBar from '../components/NmleSearchBar.vue'
import NmleMovieResults from '../components/NmleMovieResults.vue'

const searchStore = useSearchStore()
const userStore = useUserStore()
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

onMounted(async () => {
  // Ensure user store is initialized
  if (!userStore.user) {
    console.log(' User store not ready, fetching user...')
    await userStore.fetchRandomUser()
  }
  
  // Track page view on mount
  console.log(' Home page mounted, tracking page view')
  enhancedMetricsService.trackPageView('/home', {
    page_name: 'Home',
    full_url: window.location.href,
    referrer: document.referrer,
    navigation_type: 'mount'
  })
  
  // Load dashboard data
  await loadDashboardData()
})

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
