<template>
  <div class="metrics-dashboard">
    <div class="dashboard-header">
      <h2>📊 Analytics Dashboard</h2>
      <p>User metrics and system performance</p>
    </div>

    <!-- Metrics Overview -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon">👥</div>
        <div class="metric-content">
          <div class="metric-number">{{ userMetrics.total_actions || 0 }}</div>
          <div class="metric-label">User Actions</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">🔍</div>
        <div class="metric-content">
          <div class="metric-number">{{ userMetrics.total_searches || 0 }}</div>
          <div class="metric-label">Search Queries</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">📄</div>
        <div class="metric-content">
          <div class="metric-number">{{ userMetrics.total_page_views || 0 }}</div>
          <div class="metric-label">Page Views</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">🔌</div>
        <div class="metric-content">
          <div class="metric-number">{{ userMetrics.total_api_calls || 0 }}</div>
          <div class="metric-label">API Calls</div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="activity-section">
      <h3>Recent Activity</h3>
      <div class="activity-list">
        <div 
          v-for="action in recentActions" 
          :key="action.timestamp" 
          class="activity-item"
        >
          <div class="activity-icon">{{ getActionIcon(action.action) }}</div>
          <div class="activity-content">
            <div class="activity-action">{{ formatAction(action.action) }}</div>
            <div class="activity-time">{{ formatTime(action.datetime) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Popular Queries -->
    <div class="queries-section" v-if="popularQueries.length > 0">
      <h3>Popular Search Queries</h3>
      <div class="queries-list">
        <div 
          v-for="query in popularQueries" 
          :key="query.query" 
          class="query-item"
        >
          <span class="query-text">{{ query.query }}</span>
          <span class="query-count">{{ query.count }} searches</span>
        </div>
      </div>
    </div>

    <!-- System Logs -->
    <div class="logs-section">
      <h3>System Logs</h3>
      <div class="logs-controls">
        <select v-model="selectedLogLevel" @change="loadLogs" class="log-filter">
          <option value="">All Levels</option>
          <option value="error">Errors</option>
          <option value="warning">Warnings</option>
          <option value="info">Info</option>
        </select>
        <button @click="loadLogs" class="btn btn-secondary">Refresh</button>
      </div>
      <div class="logs-list">
        <div 
          v-for="log in systemLogs" 
          :key="log.timestamp" 
          class="log-item"
          :class="`log-${log.level.toLowerCase()}`"
        >
          <div class="log-level">{{ log.level }}</div>
          <div class="log-content">
            <div class="log-message">{{ log.message }}</div>
            <div class="log-meta">
              <span class="log-component">{{ log.component }}</span>
              <span class="log-time">{{ formatTime(log.datetime) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import metricsService from '@/services/metricsService'

export default {
  name: 'MetricsDashboard',
  setup() {
    const userMetrics = ref({})
    const recentActions = ref([])
    const popularQueries = ref([])
    const systemLogs = ref([])
    const selectedLogLevel = ref('')
    const loading = ref(false)

    const loadUserMetrics = async () => {
      try {
        const userId = localStorage.getItem('movie_library_user_id')
        if (!userId) return

        const response = await fetch(`http://localhost:8000/metrics/user/${userId}?days=7`)
        if (response.ok) {
          const data = await response.json()
          userMetrics.value = data.summary || {}
          recentActions.value = data.actions?.slice(-10) || []
        }
      } catch (error) {
        console.error('Failed to load user metrics:', error)
      }
    }

    const loadGlobalMetrics = async () => {
      try {
        const response = await fetch('http://localhost:8000/metrics/global?days=7')
        if (response.ok) {
          const data = await response.json()
          popularQueries.value = data.popular_queries || []
        }
      } catch (error) {
        console.error('Failed to load global metrics:', error)
      }
    }

    const loadLogs = async () => {
      try {
        loading.value = true
        const level = selectedLogLevel.value ? `&level=${selectedLogLevel.value}` : ''
        const response = await fetch(`http://localhost:8000/metrics/logs?hours=24&limit=50${level}`)
        if (response.ok) {
          const data = await response.json()
          systemLogs.value = data.logs || []
        }
      } catch (error) {
        console.error('Failed to load logs:', error)
      } finally {
        loading.value = false
      }
    }

    const getActionIcon = (action) => {
      const icons = {
        'search': '🔍',
        'view_movie': '👁️',
        'edit_movie': '✏️',
        'create_movie': '➕',
        'delete_movie': '🗑️',
        'navigate': '🧭',
        'change_filter': '🔧',
        'change_sort': '📊',
        'page_visible': '👀',
        'page_hidden': '🙈'
      }
      return icons[action] || '📝'
    }

    const formatAction = (action) => {
      return action.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }

    const formatTime = (datetime) => {
      return new Date(datetime).toLocaleString()
    }

    onMounted(() => {
      loadUserMetrics()
      loadGlobalMetrics()
      loadLogs()
    })

    return {
      userMetrics,
      recentActions,
      popularQueries,
      systemLogs,
      selectedLogLevel,
      loading,
      loadLogs,
      getActionIcon,
      formatAction,
      formatTime
    }
  }
}
</script>

<style scoped>
.metrics-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background: #0a0a0a;
  color: #fff;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 3rem;
}

.dashboard-header h2 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  color: #fff;
}

.dashboard-header p {
  color: #999;
  font-size: 1.1rem;
  margin: 0;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.metric-card {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
}

.metric-card:hover {
  border-color: #e50914;
  transform: translateY(-2px);
}

.metric-icon {
  font-size: 2rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #2a2a2a;
  border-radius: 50%;
}

.metric-content {
  flex: 1;
}

.metric-number {
  font-size: 2rem;
  font-weight: 700;
  color: #e50914;
  margin: 0;
}

.metric-label {
  color: #999;
  font-size: 0.9rem;
  margin: 0.25rem 0 0 0;
}

.activity-section,
.queries-section,
.logs-section {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.activity-section h3,
.queries-section h3,
.logs-section h3 {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.activity-list {
  max-height: 300px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid #333;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  font-size: 1.2rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #2a2a2a;
  border-radius: 50%;
}

.activity-content {
  flex: 1;
}

.activity-action {
  font-weight: 500;
  color: #fff;
  margin: 0;
}

.activity-time {
  color: #999;
  font-size: 0.8rem;
  margin: 0.25rem 0 0 0;
}

.queries-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.query-item {
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 20px;
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.query-text {
  color: #fff;
  font-weight: 500;
}

.query-count {
  color: #999;
  font-size: 0.8rem;
}

.logs-controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  align-items: center;
}

.log-filter {
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 6px;
  color: #fff;
  padding: 0.5rem;
  font-size: 0.9rem;
}

.logs-list {
  max-height: 400px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid #333;
}

.log-item:last-child {
  border-bottom: none;
}

.log-level {
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  min-width: 60px;
  text-align: center;
}

.log-error .log-level {
  background: #dc3545;
  color: #fff;
}

.log-warning .log-level {
  background: #ffc107;
  color: #000;
}

.log-info .log-level {
  background: #17a2b8;
  color: #fff;
}

.log-debug .log-level {
  background: #6c757d;
  color: #fff;
}

.log-content {
  flex: 1;
}

.log-message {
  color: #fff;
  margin: 0;
}

.log-meta {
  display: flex;
  gap: 1rem;
  margin: 0.25rem 0 0 0;
  font-size: 0.8rem;
  color: #999;
}

.btn {
  background: #e50914;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn:hover {
  background: #b8070f;
}

.btn-secondary {
  background: #6c757d;
}

.btn-secondary:hover {
  background: #545b62;
}

@media (max-width: 768px) {
  .metrics-dashboard {
    padding: 1rem;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .metric-card {
    padding: 1rem;
  }
  
  .metric-icon {
    width: 50px;
    height: 50px;
    font-size: 1.5rem;
  }
  
  .metric-number {
    font-size: 1.5rem;
  }
}
</style>
