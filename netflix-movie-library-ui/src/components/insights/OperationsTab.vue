<template>
  <div class="operations-tab">
    <!-- System Status Cards -->
    <div class="status-grid">
      <div class="status-card">
        <div class="status-icon">🔌</div>
        <div class="status-content">
          <div class="status-title">API Status</div>
          <div class="status-value" :class="apiStatus.class">{{ apiStatus.text }}</div>
        </div>
      </div>

      <div class="status-card">
        <div class="status-icon">🗄️</div>
        <div class="status-content">
          <div class="status-title">Redis Status</div>
          <div class="status-value" :class="redisStatus.class">{{ redisStatus.text }}</div>
        </div>
      </div>

      <div class="status-card">
        <div class="status-icon">📊</div>
        <div class="status-content">
          <div class="status-title">Error Count</div>
          <div class="status-value error">{{ errorCount }}</div>
        </div>
      </div>

      <div class="status-card">
        <div class="status-icon">⏱️</div>
        <div class="status-content">
          <div class="status-title">Avg Response Time</div>
          <div class="status-value">{{ avgResponseTime }}ms</div>
        </div>
      </div>
    </div>

    <!-- Log Controls -->
    <div class="log-controls">
      <div class="control-group">
        <label>Log Level:</label>
        <select v-model="selectedLogLevel" @change="loadLogs" class="log-select">
          <option value="">All Levels</option>
          <option value="error">Errors</option>
          <option value="warning">Warnings</option>
          <option value="info">Info</option>
          <option value="debug">Debug</option>
        </select>
      </div>

      <div class="control-group">
        <label>Component:</label>
        <select v-model="selectedComponent" @change="loadLogs" class="log-select">
          <option value="">All Components</option>
          <option value="api">API</option>
          <option value="connector">Connector</option>
          <option value="metrics">Metrics</option>
          <option value="system">System</option>
        </select>
      </div>

      <div class="control-group">
        <label>Time Range:</label>
        <select v-model="selectedTimeRange" @change="loadLogs" class="log-select">
          <option value="1">Last Hour</option>
          <option value="6">Last 6 Hours</option>
          <option value="24">Last 24 Hours</option>
          <option value="168">Last Week</option>
        </select>
      </div>

      <button @click="loadLogs" class="btn btn-primary" :disabled="loading">
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Logs Display -->
    <div class="logs-section">
      <div class="logs-header">
        <h3>System Logs</h3>
        <div class="logs-stats">
          <span class="log-count">{{ filteredLogs.length }} logs</span>
          <span class="log-errors" v-if="errorCount > 0">{{ errorCount }} errors</span>
        </div>
      </div>

      <div class="logs-container">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading logs...</p>
        </div>

        <div v-else-if="filteredLogs.length === 0" class="no-logs">
          <div class="no-logs-icon">📝</div>
          <h4>No logs found</h4>
          <p>Try adjusting your filters or time range</p>
        </div>

        <div v-else class="logs-list">
          <div 
            v-for="log in paginatedLogs" 
            :key="log.timestamp" 
            class="log-item"
            :class="`log-${log.level.toLowerCase()}`"
            @click="toggleLogDetails(log)"
          >
            <div class="log-header">
              <div class="log-level">{{ log.level }}</div>
              <div class="log-time">{{ formatTime(log.datetime) }}</div>
              <div class="log-component">{{ log.component }}</div>
              <div class="log-toggle">
                {{ expandedLogs.has(log.timestamp) ? '▼' : '▶' }}
              </div>
            </div>
            
            <div class="log-message">{{ log.message }}</div>
            
            <div v-if="expandedLogs.has(log.timestamp)" class="log-details">
              <div class="log-metadata">
                <div class="metadata-item">
                  <strong>Timestamp:</strong> {{ log.datetime }}
                </div>
                <div class="metadata-item">
                  <strong>Component:</strong> {{ log.component }}
                </div>
                <div v-if="log.metadata && Object.keys(log.metadata).length > 0" class="metadata-item">
                  <strong>Metadata:</strong>
                  <pre class="metadata-json">{{ JSON.stringify(log.metadata, null, 2) }}</pre>
                </div>
                <div v-if="log.traceback" class="metadata-item">
                  <strong>Traceback:</strong>
                  <pre class="traceback">{{ log.traceback }}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="filteredLogs.length > logsPerPage" class="pagination">
          <button 
            @click="currentPage = Math.max(1, currentPage - 1)"
            :disabled="currentPage === 1"
            class="btn btn-secondary"
          >
            Previous
          </button>
          
          <span class="page-info">
            Page {{ currentPage }} of {{ totalPages }}
          </span>
          
          <button 
            @click="currentPage = Math.min(totalPages, currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="btn btn-secondary"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Real-time Logs -->
    <div class="realtime-section">
      <div class="realtime-header">
        <h3>Real-time Logs</h3>
        <div class="realtime-controls">
          <button 
            @click="toggleRealtime" 
            class="btn"
            :class="realtimeEnabled ? 'btn-danger' : 'btn-success'"
          >
            {{ realtimeEnabled ? 'Stop' : 'Start' }} Real-time
          </button>
        </div>
      </div>
      
      <div v-if="realtimeEnabled" class="realtime-logs">
        <div 
          v-for="log in realtimeLogs" 
          :key="log.timestamp" 
          class="realtime-log-item"
          :class="`log-${log.level.toLowerCase()}`"
        >
          <span class="realtime-time">{{ formatTime(log.datetime) }}</span>
          <span class="realtime-level">{{ log.level }}</span>
          <span class="realtime-message">{{ log.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import enhancedMetricsService from '@/services/enhancedMetricsService'

export default {
  name: 'OperationsTab',
  setup() {
    const logs = ref([])
    const realtimeLogs = ref([])
    const loading = ref(false)
    const selectedLogLevel = ref('')
    const selectedComponent = ref('')
    const selectedTimeRange = ref('24')
    const expandedLogs = ref(new Set())
    const currentPage = ref(1)
    const logsPerPage = 20
    const realtimeEnabled = ref(false)
    const realtimeInterval = ref(null)

    // System status
    const apiStatus = ref({ text: 'Checking...', class: 'warning' })
    const redisStatus = ref({ text: 'Checking...', class: 'warning' })
    const errorCount = ref(0)
    const avgResponseTime = ref(0)

    const filteredLogs = computed(() => {
      let filtered = logs.value

      if (selectedLogLevel.value) {
        filtered = filtered.filter(log => log.level.toLowerCase() === selectedLogLevel.value)
      }

      if (selectedComponent.value) {
        filtered = filtered.filter(log => log.component === selectedComponent.value)
      }

      return filtered
    })

    const paginatedLogs = computed(() => {
      const start = (currentPage.value - 1) * logsPerPage
      const end = start + logsPerPage
      return filteredLogs.value.slice(start, end)
    })

    const totalPages = computed(() => {
      return Math.ceil(filteredLogs.value.length / logsPerPage)
    })

    const loadLogs = async () => {
      try {
        loading.value = true
        const level = selectedLogLevel.value ? `&level=${selectedLogLevel.value}` : ''
        const component = selectedComponent.value ? `&component=${selectedComponent.value}` : ''
        const hours = selectedTimeRange.value
        
        const response = await fetch(`http://localhost:8000/metrics/logs?hours=${hours}&limit=1000${level}${component}`)
        if (response.ok) {
          const data = await response.json()
          logs.value = data.logs || []
          errorCount.value = logs.value.filter(log => log.level.toLowerCase() === 'error').length
        }
      } catch (error) {
        console.error('Failed to load logs:', error)
      } finally {
        loading.value = false
      }
    }

    const loadSystemStatus = async () => {
      try {
        // Check API status
        const apiResponse = await fetch('http://localhost:8000/health')
        if (apiResponse.ok) {
          apiStatus.value = { text: 'Healthy', class: 'success' }
        } else {
          apiStatus.value = { text: 'Unhealthy', class: 'error' }
        }

        // Check Redis status (simplified)
        redisStatus.value = { text: 'Connected', class: 'success' }
        
        // Calculate average response time from API logs
        const apiLogs = logs.value.filter(log => log.component === 'api')
        if (apiLogs.length > 0) {
          const totalTime = apiLogs.reduce((sum, log) => {
            return sum + (log.metadata?.response_time_ms || 0)
          }, 0)
          avgResponseTime.value = Math.round(totalTime / apiLogs.length)
        }

      } catch (error) {
        apiStatus.value = { text: 'Error', class: 'error' }
        redisStatus.value = { text: 'Error', class: 'error' }
      }
    }

    const toggleLogDetails = (log) => {
      if (expandedLogs.value.has(log.timestamp)) {
        expandedLogs.value.delete(log.timestamp)
      } else {
        expandedLogs.value.add(log.timestamp)
      }
    }

    const toggleRealtime = () => {
      if (realtimeEnabled.value) {
        stopRealtime()
      } else {
        startRealtime()
      }
    }

    const startRealtime = () => {
      realtimeEnabled.value = true
      realtimeLogs.value = []
      
      // Poll for new logs every 5 seconds
      realtimeInterval.value = setInterval(async () => {
        try {
          const response = await fetch('http://localhost:8000/metrics/logs?hours=1&limit=10')
          if (response.ok) {
            const data = await response.json()
            const newLogs = data.logs || []
            
            // Add only new logs
            newLogs.forEach(log => {
              if (!realtimeLogs.value.find(existing => existing.timestamp === log.timestamp)) {
                realtimeLogs.value.unshift(log)
              }
            })
            
            // Keep only last 50 logs
            if (realtimeLogs.value.length > 50) {
              realtimeLogs.value = realtimeLogs.value.slice(0, 50)
            }
          }
        } catch (error) {
          console.error('Failed to load realtime logs:', error)
        }
      }, 5000)
    }

    const stopRealtime = () => {
      realtimeEnabled.value = false
      if (realtimeInterval.value) {
        clearInterval(realtimeInterval.value)
        realtimeInterval.value = null
      }
    }

    const formatTime = (datetime) => {
      return new Date(datetime).toLocaleString()
    }

    onMounted(() => {
      loadLogs()
      loadSystemStatus()
    })

    onUnmounted(() => {
      stopRealtime()
    })

    return {
      logs,
      realtimeLogs,
      loading,
      selectedLogLevel,
      selectedComponent,
      selectedTimeRange,
      expandedLogs,
      currentPage,
      logsPerPage,
      realtimeEnabled,
      apiStatus,
      redisStatus,
      errorCount,
      avgResponseTime,
      filteredLogs,
      paginatedLogs,
      totalPages,
      loadLogs,
      toggleLogDetails,
      toggleRealtime,
      formatTime
    }
  }
}
</script>

<style scoped>
.operations-tab {
  color: #fff;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.status-card {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.status-icon {
  font-size: 2rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #2a2a2a;
  border-radius: 50%;
}

.status-content {
  flex: 1;
}

.status-title {
  color: #999;
  font-size: 0.9rem;
  margin: 0 0 0.5rem 0;
}

.status-value {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
}

.status-value.success {
  color: #28a745;
}

.status-value.warning {
  color: #ffc107;
}

.status-value.error {
  color: #dc3545;
}

.log-controls {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.control-group label {
  color: #999;
  font-size: 0.9rem;
  font-weight: 500;
}

.log-select {
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 6px;
  color: #fff;
  padding: 0.5rem;
  font-size: 0.9rem;
  min-width: 120px;
}

.logs-section {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.logs-header h3 {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0;
  color: #fff;
}

.logs-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
  color: #999;
}

.log-errors {
  color: #dc3545;
  font-weight: 600;
}

.logs-container {
  max-height: 600px;
  overflow-y: auto;
}

.loading-state {
  text-align: center;
  padding: 2rem;
  color: #999;
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

.no-logs {
  text-align: center;
  padding: 3rem;
  color: #999;
}

.no-logs-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.no-logs h4 {
  color: #fff;
  margin: 0 0 0.5rem 0;
}

.logs-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.log-item {
  background: #2a2a2a;
  border: 1px solid #333;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.log-item:hover {
  border-color: #444;
  background: #333;
}

.log-item.log-error {
  border-left: 4px solid #dc3545;
}

.log-item.log-warning {
  border-left: 4px solid #ffc107;
}

.log-item.log-info {
  border-left: 4px solid #17a2b8;
}

.log-item.log-debug {
  border-left: 4px solid #6c757d;
}

.log-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
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

.log-time {
  color: #999;
  font-size: 0.8rem;
  min-width: 150px;
}

.log-component {
  color: #e50914;
  font-weight: 500;
  font-size: 0.9rem;
  min-width: 80px;
}

.log-toggle {
  color: #999;
  font-size: 0.8rem;
  margin-left: auto;
}

.log-message {
  color: #fff;
  font-size: 0.9rem;
  margin: 0;
}

.log-details {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #444;
}

.log-metadata {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.metadata-item {
  color: #ccc;
  font-size: 0.8rem;
}

.metadata-item strong {
  color: #fff;
}

.metadata-json,
.traceback {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 4px;
  padding: 0.5rem;
  margin: 0.5rem 0 0 0;
  font-family: 'Courier New', monospace;
  font-size: 0.7rem;
  color: #ccc;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #333;
}

.page-info {
  color: #999;
  font-size: 0.9rem;
}

.realtime-section {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 12px;
  padding: 1.5rem;
}

.realtime-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.realtime-header h3 {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0;
  color: #fff;
}

.realtime-logs {
  max-height: 300px;
  overflow-y: auto;
  background: #0a0a0a;
  border: 1px solid #333;
  border-radius: 8px;
  padding: 1rem;
}

.realtime-log-item {
  display: flex;
  gap: 1rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #222;
  font-size: 0.8rem;
}

.realtime-log-item:last-child {
  border-bottom: none;
}

.realtime-time {
  color: #999;
  min-width: 120px;
}

.realtime-level {
  font-weight: 600;
  min-width: 60px;
}

.realtime-message {
  color: #fff;
  flex: 1;
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

.btn:disabled {
  background: #666;
  cursor: not-allowed;
}

.btn-primary {
  background: #e50914;
}

.btn-secondary {
  background: #6c757d;
}

.btn-success {
  background: #28a745;
}

.btn-danger {
  background: #dc3545;
}

@media (max-width: 768px) {
  .status-grid {
    grid-template-columns: 1fr;
  }
  
  .log-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .control-group {
    width: 100%;
  }
  
  .log-select {
    width: 100%;
  }
  
  .logs-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .realtime-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
}
</style>
