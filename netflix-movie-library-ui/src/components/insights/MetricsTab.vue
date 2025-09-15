<template>
  <div class="metrics-tab">
    <!-- Search Activities Section -->
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
              <tr v-for="(data, query) in searchActivities" :key="query">
                <td class="query-cell">{{ query }}</td>
                <td class="count-cell">{{ data.resultsCount }}</td>
              </tr>
              <tr v-if="Object.keys(searchActivities).length === 0">
                <td colspan="2" class="no-data">No search activities found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Page Activities Table -->
    <div class="page-activities-section">
      <h3>Page Activities</h3>
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
            <tr v-for="(activity, index) in pageActivities" :key="index">
              <td class="page-cell">{{ activity.visit_page }}</td>
              <td class="activity-cell">{{ activity.activity }}</td>
              <td class="country-cell">{{ activity.user_profile?.country || 'Unknown' }}</td>
            </tr>
            <tr v-if="pageActivities.length === 0">
              <td colspan="3" class="no-data">No page activities found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { enhancedMetricsService } from '../../services/enhancedMetricsService.js'
import Chart from 'chart.js/auto'

// No chart refs needed in this component

// Mock data for demonstration
const mockMetricsData = ref({
  userCountries: {
    'United States': 25,
    'Canada': 15,
    'United Kingdom': 12,
    'Germany': 8,
    'Australia': 6,
    'France': 4,
    'Japan': 3,
    'Brazil': 2,
    'India': 1
  },
  searchActivities: {
    'inception': { resultsCount: 5 },
    'blade runner': { resultsCount: 3 },
    'gone girl': { resultsCount: 2 },
    'hereditary': { resultsCount: 1 }
  },
  pageActivities: [
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
    }
  ]
})

// Computed properties
const pageActivities = computed(() => mockMetricsData.value.pageActivities)
const searchActivities = computed(() => mockMetricsData.value.searchActivities)

// No chart creation needed in this component
</script>

<style scoped>
.metrics-tab {
  padding: 0.5rem;
  color: #fff;
}

/* Search Activities Section */
.search-activities-section {
  margin-bottom: 1rem;
}

.metric-card {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  border: 1px solid #333;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-header h3 {
  color: #fff;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
}

.card-icon {
  font-size: 1.5rem;
}

.chart-wrapper {
  position: relative;
  height: 200px;
  width: 100%;
  margin-bottom: 0.5rem;
}

/* Specific styling for bar charts */
.metric-card:nth-child(2) .chart-wrapper {
  height: 220px; /* Extra height for horizontal bar chart */
}

/* Search Activities Table */
.search-activities-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 0.5rem;
}

.search-activities-table th,
.search-activities-table td {
  padding: 0.5rem;
  text-align: left;
  border-bottom: 1px solid #333;
}

.search-activities-table th {
  background: #2a2a2a;
  color: #fff;
  font-weight: 600;
  font-size: 0.9rem;
}

.search-activities-table td {
  color: #ccc;
  font-size: 0.85rem;
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

/* Page Activities Section */
.page-activities-section {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  border: 1px solid #333;
  border-radius: 8px;
  padding: 1rem;
  margin-top: 0.5rem;
}

.page-activities-section h3 {
  color: #fff;
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.75rem 0;
}

.page-activities-table {
  width: 100%;
  border-collapse: collapse;
}

.page-activities-table th,
.page-activities-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #333;
}

.page-activities-table th {
  background: #2a2a2a;
  color: #fff;
  font-weight: 600;
  font-size: 0.9rem;
}

.page-activities-table td {
  color: #ccc;
  font-size: 0.85rem;
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

/* Chart Legend Styling */
.metric-card canvas {
  max-height: 200px;
}

/* Ensure legends are visible */
.metric-card .chart-wrapper {
  padding-bottom: 2rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .metric-card {
    padding: 1rem;
  }
  
  .page-activities-section {
    padding: 1rem;
  }
  
  .page-activities-table th,
  .page-activities-table td {
    padding: 0.5rem;
    font-size: 0.8rem;
  }
}
</style>