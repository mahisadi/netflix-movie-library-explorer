<template>
  <div class="insights-page">
    <div class="container">
      <!-- Header Section -->
      <div class="insights-header-section">
        <div class="header-content">
          <h1 class="page-title">
            <span class="title-icon"></span>
            Insights & Analytics
          </h1>
          <p class="page-description">Comprehensive metrics and system monitoring</p>
        </div>

        <!-- Tab Navigation -->
        <div class="tab-navigation">
          <button 
            @click="handleTabChange('metrics')" 
            class="tab-button"
            :class="{ active: activeTab === 'metrics' }"
          >
            📈 Metrics
          </button>
        </div>
      </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading insights data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Oops! Something went wrong</h3>
      <p>We're sorry for the inconvenience. We're having trouble loading the insights data right now.</p>
      <div class="error-details">
        <p><strong>Error:</strong> {{ error }}</p>
      </div>
      <div class="error-actions">
        <button @click="loadAnalyticsData" class="retry-btn">Try Again</button>
        <button @click="error = null" class="dismiss-btn">Dismiss</button>
      </div>
    </div>

    <!-- Main Content Grid - Only show for Metrics tab -->
    <div v-else-if="activeTab === 'metrics'" class="main-content-grid">
      <!-- Left Half (50%) -->
      <div class="left-half">
        <!-- Top 25% - Page Views Cards -->
        <div class="page-views-section">
          <!-- All Page Views Card -->
          <div class="playing-card">
            <div class="card-header">
              <h3>All Page Views</h3>
              <div class="card-icon"></div>
            </div>
            <div class="card-content">
              <div v-if="!allPageViews || Object.keys(allPageViews).length === 0" class="no-data-small">
                No data available
              </div>
              <template v-else>
                <div class="stat-row">
                  <span class="stat-label">Home:</span>
                  <span class="stat-value">{{ allPageViews.Home || 0 }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">Library:</span>
                  <span class="stat-value">{{ allPageViews.Library || 0 }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">Insights:</span>
                  <span class="stat-value">{{ allPageViews.Insights || 0 }}</span>
                </div>
              </template>
            </div>
          </div>

          <!-- Unique Page Views Card -->
          <div class="playing-card">
            <div class="card-header">
              <h3>Unique Page Views</h3>
              <div class="card-icon">👥</div>
            </div>
            <div class="card-content">
              <div v-if="!uniquePageViews || Object.keys(uniquePageViews).length === 0" class="no-data-small">
                No data available
              </div>
              <template v-else>
                <div class="stat-row">
                  <span class="stat-label">Home:</span>
                  <span class="stat-value">{{ uniquePageViews.Home || 0 }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">Library:</span>
                  <span class="stat-value">{{ uniquePageViews.Library || 0 }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">Insights:</span>
                  <span class="stat-value">{{ uniquePageViews.Insights || 0 }}</span>
                </div>
              </template>
            </div>
          </div>
        </div>

        <!-- Bottom 75% - Employee Country Chart -->
        <div class="employee-country-section">
          <div class="metric-card">
            <div class="card-header">
              <h3>User Countries</h3>
              <div class="card-icon"></div>
            </div>
            <div v-if="!userCountries || Object.keys(userCountries).length === 0" class="no-data-chart">
              <div class="no-data-icon"></div>
              <p>No country data available</p>
            </div>
            <div v-else class="chart-container">
              <div class="chart-wrapper">
                <canvas ref="userCountryChart"></canvas>
              </div>
              <!-- Fallback text display -->
              <div class="chart-fallback" v-if="false">
                <div class="country-list">
                  <div v-for="(count, country) in userCountries" :key="country" class="country-item">
                    <span class="country-name">{{ country }}</span>
                    <span class="country-count">{{ count }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Half (50%) -->
      <div class="right-half">
        <!-- Top 50% - Search Activities -->
        <div class="search-activities-section">
          <div class="metric-card">
            <div class="card-header">
              <h3>Search Activities</h3>
              <div class="card-icon">🔍</div>
            </div>
            <div class="table-wrapper">
              <table class="search-activities-table">
                <thead>
                  <tr>
                    <th>Search Term</th>
                    <th>Results Found</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="index in 8" :key="index">
                    <td v-if="paginatedSearchActivities[index - 1]" class="query-cell">
                      {{ paginatedSearchActivities[index - 1][0] }}
                    </td>
                    <td v-else class="query-cell empty-cell"></td>
                    
                    <td v-if="paginatedSearchActivities[index - 1]" class="count-cell">
                      {{ paginatedSearchActivities[index - 1][1].resultsCount }}
                    </td>
                    <td v-else class="count-cell empty-cell"></td>
                  </tr>
                  <tr v-if="paginatedSearchActivities.length === 0">
                    <td colspan="2" class="no-data">No search activities found</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!-- Pagination Controls -->
            <div class="pagination-controls" v-if="totalSearchPages > 1">
              <button 
                @click="goToSearchPage(searchActivitiesPage - 1)"
                :disabled="searchActivitiesPage === 1"
                class="pagination-btn"
              >
                ←
              </button>
              <span class="pagination-info">
                {{ searchActivitiesPage }} / {{ totalSearchPages }}
              </span>
              <button 
                @click="goToSearchPage(searchActivitiesPage + 1)"
                :disabled="searchActivitiesPage === totalSearchPages"
                class="pagination-btn"
              >
                →
              </button>
            </div>
          </div>
        </div>

        <!-- Bottom 50% - Page Activities -->
        <div class="page-activities-section">
          <div class="metric-card">
            <div class="card-header">
              <h3>Page Activities</h3>
              <div class="card-icon">📋</div>
            </div>
            <div class="table-wrapper">
              <table class="page-activities-table">
                <thead>
                  <tr>
                    <th>Visit Page</th>
                    <th>Activity</th>
                    <th>Country</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(activity, index) in paginatedPageActivities" :key="index">
                    <td class="page-cell">{{ activity.visit_page }}</td>
                    <td class="activity-cell">{{ activity.activity }}</td>
                    <td class="country-cell">{{ activity.user_profile?.country || 'Unknown' }}</td>
                  </tr>
                  <tr v-if="paginatedPageActivities.length === 0">
                    <td colspan="3" class="no-data">No page activities found</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!-- Pagination Controls -->
            <div class="pagination-controls" v-if="totalPageActivitiesPages > 1">
              <button 
                @click="goToPageActivitiesPage(pageActivitiesPage - 1)"
                :disabled="pageActivitiesPage === 1"
                class="pagination-btn"
              >
                ←
              </button>
              <span class="pagination-info">
                {{ pageActivitiesPage }} / {{ totalPageActivitiesPages }}
              </span>
              <button 
                @click="goToPageActivitiesPage(pageActivitiesPage + 1)"
                :disabled="pageActivitiesPage === totalPageActivitiesPages"
                class="pagination-btn"
              >
                →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>


    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, nextTick } from 'vue'
import enhancedMetricsService from '@/services/enhancedMetricsService'
import redisAnalyticsService from '@/services/redisAnalyticsService'
import Chart from 'chart.js/auto'

export default {
  name: 'Insights',
  setup() {
    const activeTab = ref('metrics')
    const userCountryChart = ref(null)
    const loading = ref(false)
    const error = ref(null)

    // Real data from APIs
    const allPageViews = ref({})
    const uniquePageViews = ref({})
    const userCountries = ref({})
    const searchActivities = ref({})
    const pageActivities = ref([])


    // Pagination state
    const searchActivitiesPage = ref(1)
    const pageActivitiesPage = ref(1)
    const itemsPerPage = 5

    // Data loading functions
    const loadAnalyticsData = async () => {
      try {
        loading.value = true
        error.value = null

        // Load page views data
        const pageViewsData = await redisAnalyticsService.getPageViewsData()
        allPageViews.value = pageViewsData || {}
        uniquePageViews.value = pageViewsData || {} // For now, same as all page views

        // Load user countries data
        console.log(' Loading user countries data...')
        const countriesData = await redisAnalyticsService.getUserCountriesData()
        console.log(' User countries data received:', countriesData)
        userCountries.value = countriesData || {}
        console.log(' User countries value set to:', userCountries.value)

        // Load search activities data
        const searchData = await redisAnalyticsService.getSearchActivitiesData()
        searchActivities.value = searchData || {}

        // Load page activities data
        const activitiesData = await redisAnalyticsService.getPageActivitiesData()
        pageActivities.value = activitiesData || []

        console.log(' Analytics data loaded successfully')
      } catch (err) {
        console.error(' Error loading analytics data:', err)
        error.value = 'Failed to load analytics data. Please check your connection and try again.'
        
        // Set fallback empty data to prevent further errors
        allPageViews.value = {}
        uniquePageViews.value = {}
        userCountries.value = {}
        searchActivities.value = {}
        pageActivities.value = []
      } finally {
        loading.value = false
      }
    }


    // Computed properties for paginated data
    const paginatedSearchActivities = computed(() => {
      if (!searchActivities.value) return []
      const entries = Object.entries(searchActivities.value)
      const start = (searchActivitiesPage.value - 1) * itemsPerPage
      const end = start + itemsPerPage
      return entries.slice(start, end)
    })

    const paginatedPageActivities = computed(() => {
      if (!pageActivities.value) return []
      const start = (pageActivitiesPage.value - 1) * itemsPerPage
      const end = start + itemsPerPage
      return pageActivities.value.slice(start, end)
    })

    // Pagination methods
    const totalSearchPages = computed(() => 
      Math.ceil((searchActivities.value ? Object.keys(searchActivities.value).length : 0) / itemsPerPage)
    )

    const totalPageActivitiesPages = computed(() => 
      Math.ceil((pageActivities.value ? pageActivities.value.length : 0) / itemsPerPage)
    )

    const goToSearchPage = (page) => {
      if (page >= 1 && page <= totalSearchPages.value) {
        searchActivitiesPage.value = page
      }
    }

    const goToPageActivitiesPage = (page) => {
      if (page >= 1 && page <= totalPageActivitiesPages.value) {
        pageActivitiesPage.value = page
      }
    }

    // Chart creation method
    const createUserCountryChart = () => {
      if (!userCountryChart.value) {
        console.log(' Chart canvas not found')
        return
      }

      const data = userCountries.value
      console.log(' User Countries Data:', data)
      
      if (!data || Object.keys(data).length === 0) {
        console.log(' No user countries data available')
        return
      }

      const labels = Object.keys(data)
      const values = Object.values(data)
      console.log(' Chart Labels:', labels)
      console.log(' Chart Values:', values)
      
      // Generate colors dynamically for any number of countries
      const generateColors = (count) => {
        const baseColors = [
          '#e50914', // Netflix Red
          '#4a90e2', // Blue
          '#20b2aa', // Teal
          '#ffa500', // Orange
          '#ff69b4', // Pink
          '#32cd32', // Green
          '#ff1493', // Deep Pink
          '#00ced1', // Dark Turquoise
          '#ffd700', // Gold
          '#da70d6'  // Orchid
        ]
        
        const colors = []
        for (let i = 0; i < count; i++) {
          colors.push(baseColors[i % baseColors.length])
        }
        return colors
      }
      
      // Sort data by value for better visualization
      const sortedData = labels
        .map((label, index) => ({
          label,
          value: values[index]
        }))
        .sort((a, b) => b.value - a.value)

      // Limit to top 10 countries to maintain consistent chart size
      const maxCountries = 10
      const limitedData = sortedData.slice(0, maxCountries)
      
      // If there are more than 10 countries, add "Others" category
      if (sortedData.length > maxCountries) {
        const othersValue = sortedData.slice(maxCountries).reduce((sum, item) => sum + item.value, 0)
        limitedData.push({
          label: 'Others',
          value: othersValue
        })
      }

      const sortedLabels = limitedData.map(item => item.label)
      const sortedValues = limitedData.map(item => item.value)

      // Generate colors with special handling for "Others"
      const backgroundColor = sortedLabels.map((label, index) => {
        if (label === 'Others') {
          return 'rgba(128, 128, 128, 0.8)' // Gray for Others
        }
        return generateColors(sortedLabels.length)[index]
      })

      const borderColor = sortedLabels.map((label, index) => {
        if (label === 'Others') {
          return '#808080' // Gray border for Others
        }
        return '#fff'
      })

      const config = {
        type: 'bar',
        data: {
          labels: sortedLabels,
          datasets: [{
            label: 'Users',
            data: sortedValues,
            backgroundColor: backgroundColor,
            borderColor: borderColor,
            borderWidth: 1,
            borderRadius: 4,
            borderSkipped: false
          }]
        },
        options: {
          indexAxis: 'y', // Horizontal bar chart
          responsive: true,
          maintainAspectRatio: false,
          layout: {
            padding: {
              top: 10,
              bottom: 10,
              left: 10,
              right: 10
            }
          },
          plugins: {
            legend: {
              display: false // Hide legend since labels are on the axis
            },
            tooltip: {
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              titleColor: '#fff',
              bodyColor: '#fff',
              borderColor: '#e50914',
              borderWidth: 1,
              callbacks: {
                label: function(context) {
                  const label = context.label || ''
                  const value = context.parsed.x || 0
                  const total = sortedValues.reduce((sum, val) => sum + val, 0)
                  const percentage = ((value / total) * 100).toFixed(1)
                  
                  if (label === 'Others') {
                    const originalTotal = values.reduce((sum, val) => sum + val, 0)
                    const othersCount = sortedData.length - maxCountries
                    return `${label}: ${value} users (${percentage}%) - ${othersCount} countries`
                  }
                  
                  return `${label}: ${value} users (${percentage}%)`
                }
              }
            }
          },
          scales: {
            x: {
              beginAtZero: true,
              grid: {
                color: 'rgba(255, 255, 255, 0.1)',
                drawBorder: false
              },
              ticks: {
                color: '#ffffff',
                font: {
                  size: 10,
                  weight: 'bold'
                },
                maxTicksLimit: 8,
                stepSize: (() => {
                  const maxValue = Math.max(...sortedValues)
                  if (maxValue <= 10) return 1
                  if (maxValue <= 100) return 10
                  if (maxValue <= 500) return 25
                  if (maxValue <= 1000) return 50
                  return 100
                })(),
                callback: function(value) {
                  return value
                }
              },
              max: (() => {
                const maxValue = Math.max(...sortedValues)
                if (maxValue <= 10) return 10
                if (maxValue <= 100) return 100
                if (maxValue <= 500) return 500
                if (maxValue <= 1000) return 1000
                return Math.ceil(maxValue / 100) * 100
              })()
            },
            y: {
              grid: {
                display: false
              },
              ticks: {
                color: '#ffffff',
                font: {
                  size: 9,
                  weight: 'bold'
                },
                maxTicksLimit: 10
              }
            }
          },
          animation: {
            duration: 1000,
            easing: 'easeInOutQuart'
          }
        }
      }

      try {
        // Destroy existing chart if it exists
        if (userCountryChart.value.chart) {
          userCountryChart.value.chart.destroy()
        }
        
        console.log('🎨 Creating chart with config:', config)
        const chart = new Chart(userCountryChart.value, config)
        userCountryChart.value.chart = chart
        console.log(' Chart created successfully')
      } catch (error) {
        console.error(' Error creating chart:', error)
      }
    }

    onMounted(async () => {
      console.log(' Insights component mounted')
      
      // Initialize services
      console.log(' Initializing services...')
      await redisAnalyticsService.init()
      console.log(' Services initialized')
      
      // Insights page tracking removed - only track Home and Library pages
      
      // Load initial data
      console.log(' Loading analytics data...')
      await loadAnalyticsData()
      
      // Create chart after data is loaded and DOM is updated
      await nextTick()
      setTimeout(() => {
        createUserCountryChart()
      }, 200)
    })

    // Watch for tab changes to load appropriate data
    const handleTabChange = async (tab) => {
      activeTab.value = tab
      if (tab === 'metrics') {
        await loadAnalyticsData()
        await nextTick()
        setTimeout(() => {
          createUserCountryChart()
        }, 200)
      }
    }

    return {
      activeTab,
      loading,
      error,
      allPageViews,
      uniquePageViews,
      userCountries,
      userCountryChart,
      searchActivities,
      pageActivities,
      paginatedSearchActivities,
      paginatedPageActivities,
      searchActivitiesPage,
      pageActivitiesPage,
      totalSearchPages,
      totalPageActivitiesPages,
      goToSearchPage,
      goToPageActivitiesPage,
      handleTabChange
    }
  }
}
</script>

<style scoped>
.insights-page {
  padding: 2rem 0;
  background: linear-gradient(180deg, #141414 0%, #000000 100%);
  min-height: 100vh;
}

/* Header Section Layout */
.insights-header-section {
  margin-bottom: 1rem;
}

.header-content {
  text-align: left;
  margin-bottom: 0.5rem;
}

.page-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0 0 0.25rem 0;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.title-icon {
  font-size: 1rem;
}

.page-description {
  color: #999;
  font-size: 0.75rem;
  margin: 0;
}

/* Main Content Grid Layout */
.main-content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
  height: calc(100vh - 300px);
  min-height: 500px;
}

/* Left Half (50%) */
.left-half {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Right Half (50%) */
.right-half {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Page Views Section (Top 25% of left half) */
.page-views-section {
  display: flex;
  flex-direction: row;
  gap: 0.75rem;
  height: 25%;
  min-height: 120px;
}

/* Employee Country Section (Bottom 75% of left half) */
.employee-country-section {
  flex: 1;
  height: 75%;
}

/* Search Activities Section (Top 50% of right half) */
.search-activities-section {
  height: 50%;
}

/* Page Activities Section (Bottom 50% of right half) */
.page-activities-section {
  height: 50%;
}

/* Metric Card Styles */
.metric-card {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  border: 1px solid #333;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  height: 100%;
}

.metric-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.metric-card .card-header h3 {
  color: #fff;
  font-size: 0.9rem;
  font-weight: 600;
  margin: 0;
}

.metric-card .card-icon {
  font-size: 1rem;
}

.metric-card .chart-wrapper {
  position: relative;
  height: 280px;
  width: 100%;
  max-height: 280px;
  min-height: 200px;
}

.metric-card .chart-wrapper canvas {
  width: 100% !important;
  height: 100% !important;
}

.chart-container {
  position: relative;
  height: 280px;
  width: 100%;
}

.chart-fallback {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.country-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
  padding: 1rem;
}

.country-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  border-left: 3px solid #e50914;
}

.country-name {
  color: #fff;
  font-weight: 600;
}

.country-count {
  color: #e50914;
  font-weight: 700;
  background: rgba(229, 9, 20, 0.2);
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

/* Playing Card Styles */
.playing-card {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  border: 1px solid #333;
  border-radius: 8px;
  padding: 0.75rem;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  flex: 1;
  height: fit-content;
  position: relative;
  overflow: hidden;
}

.playing-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #e50914, #ff6b6b, #e50914);
}

.playing-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.playing-card .card-header h3 {
  color: #fff;
  font-size: 0.85rem;
  font-weight: 600;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.playing-card .card-icon {
  font-size: 1.1rem;
  opacity: 0.8;
}

.playing-card .card-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.playing-card .stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.playing-card .stat-row:last-child {
  border-bottom: none;
}

.playing-card .stat-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #ccc;
  text-transform: capitalize;
}

.playing-card .stat-value {
  font-size: 0.9rem;
  font-weight: 700;
  background: rgba(229, 9, 20, 0.15);
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  border: 1px solid rgba(229, 9, 20, 0.3);
  min-width: 30px;
  text-align: center;
}

/* Table Styles */
.table-wrapper {
  height: calc(100% - 60px);
  overflow-y: auto;
  overflow-x: hidden;
  border-radius: 4px;
}

.table-wrapper::-webkit-scrollbar {
  width: 6px;
}

.table-wrapper::-webkit-scrollbar-track {
  background: #222;
  border-radius: 3px;
}

.table-wrapper::-webkit-scrollbar-thumb {
  background: #555;
  border-radius: 3px;
}

.table-wrapper::-webkit-scrollbar-thumb:hover {
  background: #777;
}

.search-activities-table,
.page-activities-table {
  width: 100%;
  border-collapse: collapse;
  height: 100%;
}

.search-activities-table th,
.search-activities-table td,
.page-activities-table th,
.page-activities-table td {
  padding: 0.4rem 0.5rem;
  text-align: left;
  border-bottom: 1px solid #333;
}

.search-activities-table th,
.page-activities-table th {
  background: #2a2a2a;
  color: #fff;
  font-weight: 600;
  font-size: 0.75rem;
  position: sticky;
  top: 0;
  padding: 0.4rem 0.5rem;
}

.search-activities-table td,
.page-activities-table td {
  color: #ccc;
  font-size: 0.75rem;
}

.empty-cell {
  color: #666 !important;
  font-style: italic;
}

.query-cell {
  font-weight: 500;
  color: #e50914;
}

.count-cell {
  text-align: center;
  font-weight: 600;
  color: #4a90e2;
}

.page-cell {
  font-weight: 500;
  color: #4a90e2;
}

.activity-cell {
  color: #20b2aa;
  text-transform: capitalize;
}

.country-cell {
  color: #ffa500;
}

.no-data {
  text-align: center;
  color: #666;
  font-style: italic;
  padding: 2rem;
}

.no-data-small {
  text-align: center;
  color: #666;
  font-style: italic;
  padding: 1rem;
  font-size: 0.8rem;
}

.no-data-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 280px;
  color: #666;
}

.no-data-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  opacity: 0.5;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #999;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #333;
  border-top: 4px solid #e50914;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.8;
}

.error-state h3 {
  color: #fff;
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
}

.error-state p {
  color: #ccc;
  margin: 0 0 1rem 0;
  font-size: 1rem;
  line-height: 1.5;
}

.error-details {
  background: rgba(220, 53, 69, 0.1);
  border: 1px solid rgba(220, 53, 69, 0.3);
  border-radius: 6px;
  padding: 1rem;
  margin: 1rem 0;
  text-align: left;
}

.error-details p {
  margin: 0;
  color: #ff6b6b;
  font-size: 0.9rem;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 1.5rem;
}

.retry-btn {
  background: #e50914;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.75rem 1.5rem;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.retry-btn:hover {
  background: #b8070f;
  transform: translateY(-1px);
}

.dismiss-btn {
  background: #6c757d;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.75rem 1.5rem;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.dismiss-btn:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

/* Pagination Controls */
.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-top: 1px solid #333;
  background: rgba(0, 0, 0, 0.2);
}

.pagination-btn {
  background: #333;
  border: 1px solid #555;
  color: #fff;
  padding: 0.4rem 0.6rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s ease;
  min-width: 32px;
}

.pagination-btn:hover:not(:disabled) {
  background: #555;
  border-color: #777;
}

.pagination-btn:disabled {
  background: #222;
  border-color: #333;
  color: #666;
  cursor: not-allowed;
  opacity: 0.5;
}

.pagination-info {
  color: #ccc;
  font-size: 0.75rem;
  font-weight: 500;
  min-width: 60px;
  text-align: center;
}

.tab-navigation {
  display: flex;
  justify-content: flex-start;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
}

.tab-button {
  background: transparent;
  border: 1px solid #333;
  color: #999;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tab-button:hover {
  border-color: #e50914;
  color: #fff;
  background: #1a1a1a;
}

.tab-button.active {
  background: #e50914;
  border-color: #e50914;
  color: #fff;
}

.tab-content {
  min-height: 600px;
}

.metrics-tab {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 1024px) {
  .main-content-grid {
    grid-template-columns: 1fr;
    height: auto;
    min-height: 400px;
  }
  
  .left-half,
  .right-half {
    height: auto;
  }
  
  .page-views-section {
    height: auto;
    min-height: 100px;
  }
  
  .employee-country-section {
    height: 250px;
  }
  
  .search-activities-section,
  .page-activities-section {
    height: 200px;
  }
}

@media (max-width: 768px) {
  .insights-page {
    padding: 1rem 0;
  }
  
  .insights-header-section {
    flex-direction: column;
    gap: 1rem;
  }
  
  .page-title {
    font-size: 1.5rem;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .title-icon {
    font-size: 1.2rem;
  }
  
  .tab-navigation {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .tab-button {
    width: auto;
    min-width: 120px;
    justify-content: flex-start;
  }
  
  .main-content-grid {
    grid-template-columns: 1fr;
    height: auto;
    gap: 1.5rem;
  }
  
  .page-views-section {
    flex-direction: row;
    gap: 0.5rem;
    height: auto;
    min-height: 100px;
  }
  
  .employee-country-section {
    height: 250px;
  }
  
  .search-activities-section,
  .page-activities-section {
    height: 200px;
  }
  
  .playing-card {
    flex: 1;
    padding: 0.75rem;
  }
  
  .playing-card .card-header h3 {
    font-size: 0.75rem;
  }
  
  .playing-card .stat-label {
    font-size: 0.7rem;
  }
  
  .playing-card .stat-value {
    font-size: 0.8rem;
    padding: 0.15rem 0.4rem;
  }
}
</style>
