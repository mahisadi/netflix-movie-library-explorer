<template>
  <div class="insights-page">
    <div class="container">
      <!-- Header Section -->
      <div class="insights-header-section">
        <div class="header-content">
          <h1 class="page-title">
            <span class="title-icon">📊</span>
            Insights & Analytics
          </h1>
          <p class="page-description">Comprehensive metrics and system monitoring</p>
        </div>

        <!-- Tab Navigation -->
        <div class="tab-navigation">
          <button 
            @click="activeTab = 'metrics'" 
            class="tab-button"
            :class="{ active: activeTab === 'metrics' }"
          >
            📈 Metrics
          </button>
          <button 
            @click="activeTab = 'operations'" 
            class="tab-button"
            :class="{ active: activeTab === 'operations' }"
          >
            🔧 Operations
          </button>
        </div>
      </div>

    <!-- Main Content Grid - Only show for Metrics tab -->
    <div v-if="activeTab === 'metrics'" class="main-content-grid">
      <!-- Left Half (50%) -->
      <div class="left-half">
        <!-- Top 25% - Page Views Cards -->
        <div class="page-views-section">
          <!-- All Page Views Card -->
          <div class="playing-card">
            <div class="card-header">
              <h3>All Page Views</h3>
              <div class="card-icon">📊</div>
            </div>
            <div class="card-content">
              <div class="stat-row">
                <span class="stat-label">Home:</span>
                <span class="stat-value">{{ allPageViews.Home }}</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">Library:</span>
                <span class="stat-value">{{ allPageViews.Library }}</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">Insights:</span>
                <span class="stat-value">{{ allPageViews.Insights }}</span>
              </div>
            </div>
          </div>

          <!-- Unique Page Views Card -->
          <div class="playing-card">
            <div class="card-header">
              <h3>Unique Page Views</h3>
              <div class="card-icon">👥</div>
            </div>
            <div class="card-content">
              <div class="stat-row">
                <span class="stat-label">Home:</span>
                <span class="stat-value">{{ uniquePageViews.Home }}</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">Library:</span>
                <span class="stat-value">{{ uniquePageViews.Library }}</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">Insights:</span>
                <span class="stat-value">{{ uniquePageViews.Insights }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Bottom 75% - Employee Country Chart -->
        <div class="employee-country-section">
          <div class="metric-card">
            <div class="card-header">
              <h3>Employee's Country</h3>
              <div class="card-icon">🌍</div>
            </div>
            <div class="chart-wrapper">
              <canvas ref="userCountryChart"></canvas>
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
                  <tr v-for="([query, data], index) in paginatedSearchActivities" :key="query">
                    <td class="query-cell">{{ query }}</td>
                    <td class="count-cell">{{ data.resultsCount }}</td>
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

    <!-- Operations Tab Content -->
    <div v-if="activeTab === 'operations'" class="operations-content">
      <div class="operations-placeholder">
        <div class="placeholder-icon">🔧</div>
        <h3>Operations Dashboard</h3>
        <p>System operations and monitoring tools will be displayed here.</p>
        <div class="operations-features">
          <div class="feature-item">
            <span class="feature-icon">⚙️</span>
            <span>System Configuration</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">📊</span>
            <span>Performance Monitoring</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">🔍</span>
            <span>Log Analysis</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">🚨</span>
            <span>Alert Management</span>
          </div>
        </div>
      </div>
    </div>

    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import enhancedMetricsService from '@/services/enhancedMetricsService'
import Chart from 'chart.js/auto'

export default {
  name: 'Insights',
  setup() {
    const activeTab = ref('metrics')
    const userCountryChart = ref(null)

    // Mock data for page views
    const allPageViews = ref({
      'Home': 45,
      'Library': 32,
      'Insights': 18
    })

    const uniquePageViews = ref({
      'Home': 12,
      'Library': 8,
      'Insights': 5
    })

    // Mock data for user countries (expanded for testing responsive behavior)
    const userCountries = ref({
      'United States': 25,
      'Canada': 15,
      'United Kingdom': 12,
      'Germany': 8,
      'Australia': 6,
      'France': 4,
      'Japan': 3,
      'Brazil': 2,
      'India': 1,
      'Spain': 3,
      'Italy': 2,
      'Netherlands': 2,
      'Sweden': 1,
      'Norway': 1,
      'Denmark': 1,
      'Finland': 1,
      'Poland': 1,
      'Czech Republic': 1,
      'Hungary': 1,
      'Portugal': 1
    })

    // Mock data for search activities (expanded for testing)
    const searchActivities = ref({
      'inception': { resultsCount: 5 },
      'blade runner': { resultsCount: 3 },
      'gone girl': { resultsCount: 2 },
      'hereditary': { resultsCount: 1 },
      'matrix': { resultsCount: 4 },
      'interstellar': { resultsCount: 3 },
      'avatar': { resultsCount: 2 },
      'titanic': { resultsCount: 1 },
      'joker': { resultsCount: 3 },
      'parasite': { resultsCount: 2 }
    })

    // Mock data for page activities (expanded for testing)
    const pageActivities = ref([
      {
        visit_page: 'Home',
        activity: 'page_view',
        user_profile: { country: 'United States' }
      },
      {
        visit_page: 'Library',
        activity: 'sorting',
        user_profile: { country: 'Canada' }
      },
      {
        visit_page: 'Insights',
        activity: 'click_navigation',
        user_profile: { country: 'United Kingdom' }
      },
      {
        visit_page: 'Home',
        activity: 'search',
        user_profile: { country: 'Germany' }
      },
      {
        visit_page: 'Library',
        activity: 'filter',
        user_profile: { country: 'Australia' }
      },
      {
        visit_page: 'Insights',
        activity: 'chart_interaction',
        user_profile: { country: 'France' }
      },
      {
        visit_page: 'Home',
        activity: 'movie_click',
        user_profile: { country: 'Japan' }
      },
      {
        visit_page: 'Library',
        activity: 'sort_by_year',
        user_profile: { country: 'Brazil' }
      }
    ])

    // Pagination state
    const searchActivitiesPage = ref(1)
    const pageActivitiesPage = ref(1)
    const itemsPerPage = 5

    // Computed properties for paginated data
    const paginatedSearchActivities = computed(() => {
      const entries = Object.entries(searchActivities.value)
      const start = (searchActivitiesPage.value - 1) * itemsPerPage
      const end = start + itemsPerPage
      return entries.slice(start, end)
    })

    const paginatedPageActivities = computed(() => {
      const start = (pageActivitiesPage.value - 1) * itemsPerPage
      const end = start + itemsPerPage
      return pageActivities.value.slice(start, end)
    })

    // Pagination methods
    const totalSearchPages = computed(() => 
      Math.ceil(Object.keys(searchActivities.value).length / itemsPerPage)
    )

    const totalPageActivitiesPages = computed(() => 
      Math.ceil(pageActivities.value.length / itemsPerPage)
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
      if (!userCountryChart.value) return

      const data = userCountries.value
      const labels = Object.keys(data)
      const values = Object.values(data)
      
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
            label: 'Employees',
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
                    return `${label}: ${value} employees (${percentage}%) - ${othersCount} countries`
                  }
                  
                  return `${label}: ${value} employees (${percentage}%)`
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
                maxTicksLimit: 8
              }
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

      new Chart(userCountryChart.value, config)
    }

    onMounted(() => {
      // Track page view
      enhancedMetricsService.trackPageView('/home/insights', {
        tab: activeTab.value
      })
      
      // Create chart after component is mounted
      setTimeout(() => {
        createUserCountryChart()
      }, 100)
    })

    return {
      activeTab,
      allPageViews,
      uniquePageViews,
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
      goToPageActivitiesPage
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
  gap: 1rem;
}

/* Right Half (50%) */
.right-half {
  display: flex;
  flex-direction: column;
  gap: 1rem;
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
  color: #e50914;
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

/* Operations Tab Content */
.operations-content {
  padding: 2rem 0;
  min-height: 60vh;
}

.operations-placeholder {
  text-align: center;
  padding: 3rem 2rem;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  border-radius: 12px;
  border: 1px solid #333;
  max-width: 600px;
  margin: 0 auto;
}

.placeholder-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.8;
}

.operations-placeholder h3 {
  color: #fff;
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.operations-placeholder p {
  color: #ccc;
  margin-bottom: 2rem;
  font-size: 0.9rem;
}

.operations-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 2rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.feature-item:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(229, 9, 20, 0.3);
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 1.2rem;
}

.feature-item span:last-child {
  color: #fff;
  font-weight: 500;
  font-size: 0.9rem;
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

.metrics-tab,
.operations-tab {
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
    gap: 0.75rem;
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
