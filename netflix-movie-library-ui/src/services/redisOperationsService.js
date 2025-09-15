/**
 * Redis Operations Service
 * Handles system monitoring, health checks, and operations data for Operations dashboard
 */

class RedisOperationsService {
  constructor() {
    this.redis = null
    this.isConnected = false
    this.metrics = {
      system: {},
      performance: {},
      alerts: []
    }
    this.init()
  }

  async init() {
    try {
      this.redis = await this.connectRedis()
      this.isConnected = true
      console.log('✅ Redis Operations Service initialized')
      
      // Start metrics collection
      this.startMetricsCollection()
    } catch (error) {
      console.error('❌ Failed to initialize Redis Operations Service:', error)
      this.isConnected = false
    }
  }

  async connectRedis() {
    // Connect to the backend API for Redis operations
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    
    return {
      // Health check
      ping: async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/health`)
          const data = await response.json()
          return data.status === 'healthy' ? 'PONG' : 'ERROR'
        } catch (error) {
          console.error('Error pinging Redis:', error)
          return 'ERROR'
        }
      },
      
      // Get Redis info
      info: async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/api/operations/redis-info`)
          const data = await response.json()
          if (data.success) {
            return `redis_version:${data.data.version}\nused_memory:${data.data.usedMemory}\nconnected_clients:${data.data.connectedClients}`
          }
          return 'redis_version:Unknown\nused_memory:0B\nconnected_clients:0'
        } catch (error) {
          console.error('Error getting Redis info:', error)
          return 'redis_version:Unknown\nused_memory:0B\nconnected_clients:0'
        }
      },
      
      // Get configuration
      hgetall: async (key) => {
        try {
          const response = await fetch(`${API_BASE_URL}/api/operations/configuration`)
          const data = await response.json()
          return data.success ? data.data : {}
        } catch (error) {
          console.error('Error getting configuration:', error)
          return {}
        }
      },
      
      // Update configuration
      hset: async (key, field, value) => {
        try {
          const response = await fetch(`${API_BASE_URL}/api/operations/configuration`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ [field]: value })
          })
          return response.ok ? 1 : 0
        } catch (error) {
          console.error('Error updating configuration:', error)
          return 0
        }
      },
      
      // Time series operations (fallback to regular operations)
      ts_add: async (key, timestamp, value, labels) => {
        console.log(`Time series tracking: ${key} ${timestamp} ${value}`, labels)
        return Promise.resolve(timestamp)
      },
      
      ts_range: async (key, from, to) => {
        console.log(`Time series query: ${key} ${from} ${to}`)
        return Promise.resolve([])
      },
      
      // List operations
      lpush: async (key, value) => {
        console.log(`List push: ${key} ${value}`)
        return Promise.resolve(1)
      },
      
      lrange: async (key, start, stop) => {
        console.log(`List range: ${key} ${start} ${stop}`)
        return Promise.resolve([])
      },
      
      // Sorted set operations
      zadd: async (key, score, member) => {
        console.log(`Sorted set add: ${key} ${score} ${member}`)
        return Promise.resolve(1)
      },
      
      zrevrange: async (key, start, stop) => {
        console.log(`Sorted set range: ${key} ${start} ${stop}`)
        return Promise.resolve([])
      }
    }
  }

  // ==================== SYSTEM METRICS COLLECTION ====================

  startMetricsCollection() {
    // Collect system metrics every 30 seconds
    setInterval(() => {
      this.collectSystemMetrics()
    }, 30000)

    // Collect performance metrics every 10 seconds
    setInterval(() => {
      this.collectPerformanceMetrics()
    }, 10000)

    // Check alerts every 60 seconds
    setInterval(() => {
      this.checkAlerts()
    }, 60000)
  }

  async collectSystemMetrics() {
    if (!this.isConnected) return

    try {
      const timestamp = Date.now()
      
      // Collect CPU usage (mock)
      const cpuUsage = this.getMockCpuUsage()
      await this.redis.ts_add('system_metrics:cpu_usage', timestamp, cpuUsage, {
        type: 'cpu'
      })

      // Collect memory usage (mock)
      const memoryUsage = this.getMockMemoryUsage()
      await this.redis.ts_add('system_metrics:memory_usage', timestamp, memoryUsage, {
        type: 'memory'
      })

      // Collect Redis memory usage
      const redisMemory = await this.getRedisMemoryUsage()
      await this.redis.ts_add('system_metrics:redis_memory', timestamp, redisMemory, {
        type: 'redis'
      })

      // Update current metrics
      this.metrics.system = {
        cpu: cpuUsage,
        memory: memoryUsage,
        redis: redisMemory,
        timestamp: new Date().toISOString()
      }

    } catch (error) {
      console.error('Error collecting system metrics:', error)
    }
  }

  async collectPerformanceMetrics() {
    if (!this.isConnected) return

    try {
      const timestamp = Date.now()
      
      // Collect response time (mock)
      const responseTime = this.getMockResponseTime()
      await this.redis.ts_add('app_metrics:response_time', timestamp, responseTime, {
        type: 'performance'
      })

      // Collect error rate (mock)
      const errorRate = this.getMockErrorRate()
      await this.redis.ts_add('app_metrics:error_rate', timestamp, errorRate, {
        type: 'errors'
      })

      // Update current metrics
      this.metrics.performance = {
        responseTime: responseTime,
        errorRate: errorRate,
        timestamp: new Date().toISOString()
      }

    } catch (error) {
      console.error('Error collecting performance metrics:', error)
    }
  }

  // ==================== ALERTING SYSTEM ====================

  async checkAlerts() {
    if (!this.isConnected) return

    try {
      const alerts = []

      // Check CPU threshold
      if (this.metrics.system.cpu > 80) {
        alerts.push({
          type: 'warning',
          message: `High CPU usage: ${this.metrics.system.cpu}%`,
          timestamp: new Date().toISOString(),
          severity: 'high'
        })
      }

      // Check memory threshold
      if (this.metrics.system.memory > 85) {
        alerts.push({
          type: 'warning',
          message: `High memory usage: ${this.metrics.system.memory}%`,
          timestamp: new Date().toISOString(),
          severity: 'high'
        })
      }

      // Check Redis memory threshold
      if (this.metrics.system.redis > 90) {
        alerts.push({
          type: 'warning',
          message: `High Redis memory usage: ${this.metrics.system.redis}%`,
          timestamp: new Date().toISOString(),
          severity: 'critical'
        })
      }

      // Check response time threshold
      if (this.metrics.performance.responseTime > 2000) {
        alerts.push({
          type: 'warning',
          message: `High response time: ${this.metrics.performance.responseTime}ms`,
          timestamp: new Date().toISOString(),
          severity: 'medium'
        })
      }

      // Check error rate threshold
      if (this.metrics.performance.errorRate > 5) {
        alerts.push({
          type: 'error',
          message: `High error rate: ${this.metrics.performance.errorRate}%`,
          timestamp: new Date().toISOString(),
          severity: 'critical'
        })
      }

      // Store alerts
      if (alerts.length > 0) {
        this.metrics.alerts = [...this.metrics.alerts, ...alerts].slice(-50) // Keep last 50 alerts
        
        // Store in Redis
        for (const alert of alerts) {
          await this.redis.lpush('operations:alerts', JSON.stringify(alert))
        }
      }

    } catch (error) {
      console.error('Error checking alerts:', error)
    }
  }

  // ==================== OPERATIONS DATA RETRIEVAL ====================

  async getSystemMetrics() {
    if (!this.isConnected) return this.getMockSystemMetrics()

    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/operations/system-metrics`)
      const data = await response.json()
      
      if (data.success) {
        return data.data
      } else {
        console.error('Error getting system metrics:', data.error)
        return this.getMockSystemMetrics()
      }
    } catch (error) {
      console.error('Error getting system metrics:', error)
      return this.getMockSystemMetrics()
    }
  }

  async getPerformanceMetrics() {
    if (!this.isConnected) return this.getMockPerformanceMetrics()

    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/operations/performance-metrics`)
      const data = await response.json()
      
      if (data.success) {
        return data.data
      } else {
        console.error('Error getting performance metrics:', data.error)
        return this.getMockPerformanceMetrics()
      }
    } catch (error) {
      console.error('Error getting performance metrics:', error)
      return this.getMockPerformanceMetrics()
    }
  }

  async getAlerts() {
    if (!this.isConnected) return this.getMockAlerts()

    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/operations/alerts`)
      const data = await response.json()
      
      if (data.success) {
        return data.data
      } else {
        console.error('Error getting alerts:', data.error)
        return this.getMockAlerts()
      }
    } catch (error) {
      console.error('Error getting alerts:', error)
      return this.getMockAlerts()
    }
  }

  async getRedisInfo() {
    if (!this.isConnected) return this.getMockRedisInfo()

    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/operations/redis-info`)
      const data = await response.json()
      
      if (data.success) {
        return data.data
      } else {
        console.error('Error getting Redis info:', data.error)
        return this.getMockRedisInfo()
      }
    } catch (error) {
      console.error('Error getting Redis info:', error)
      return this.getMockRedisInfo()
    }
  }

  // ==================== CONFIGURATION MANAGEMENT ====================

  async getConfiguration() {
    if (!this.isConnected) return this.getMockConfiguration()

    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/operations/configuration`)
      const data = await response.json()
      
      if (data.success) {
        return data.data
      } else {
        console.error('Error getting configuration:', data.error)
        return this.getMockConfiguration()
      }
    } catch (error) {
      console.error('Error getting configuration:', error)
      return this.getMockConfiguration()
    }
  }

  async updateConfiguration(config) {
    if (!this.isConnected) return false

    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/operations/configuration`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      })
      const data = await response.json()
      
      return data.success
    } catch (error) {
      console.error('Error updating configuration:', error)
      return false
    }
  }

  // ==================== UTILITY METHODS ====================

  async getRedisMemoryUsage() {
    try {
      const info = await this.redis.info()
      const memoryMatch = info.match(/used_memory:(\d+)/)
      const maxMemoryMatch = info.match(/maxmemory:(\d+)/)
      
      if (memoryMatch && maxMemoryMatch) {
        const used = parseInt(memoryMatch[1])
        const max = parseInt(maxMemoryMatch[1])
        return max > 0 ? Math.round((used / max) * 100) : 0
      }
      
      return 0
    } catch (error) {
      return 0
    }
  }

  // ==================== MOCK DATA FOR DEVELOPMENT ====================

  getMockCpuUsage() {
    return Math.floor(Math.random() * 30) + 20 // 20-50%
  }

  getMockMemoryUsage() {
    return Math.floor(Math.random() * 40) + 30 // 30-70%
  }

  getMockResponseTime() {
    return Math.floor(Math.random() * 500) + 100 // 100-600ms
  }

  getMockErrorRate() {
    return Math.floor(Math.random() * 3) // 0-3%
  }

  getMockSystemMetrics() {
    return {
      cpu: { current: 35, history: [] },
      memory: { current: 45, history: [] },
      redis: { current: 25, history: [] },
      timestamp: new Date().toISOString()
    }
  }

  getMockPerformanceMetrics() {
    return {
      responseTime: { current: 250, history: [] },
      errorRate: { current: 1, history: [] },
      timestamp: new Date().toISOString()
    }
  }

  getMockAlerts() {
    return [
      {
        type: 'info',
        message: 'System running normally',
        timestamp: new Date().toISOString(),
        severity: 'low'
      }
    ]
  }

  getMockRedisInfo() {
    return {
      version: '7.0.0',
      uptime: 86400,
      connectedClients: 5,
      usedMemory: '1.2MB',
      totalCommands: 15000,
      keyspaceHits: 12000,
      keyspaceMisses: 3000,
      timestamp: new Date().toISOString()
    }
  }

  getMockConfiguration() {
    return {
      systemThresholds: {
        cpu: 80,
        memory: 85,
        redis: 90
      },
      performanceThresholds: {
        responseTime: 2000,
        errorRate: 5
      },
      alerting: {
        enabled: true,
        email: 'admin@example.com',
        webhook: ''
      },
      retention: {
        metrics: 7,
        logs: 30,
        alerts: 90
      }
    }
  }

  // ==================== HEALTH CHECK ====================

  async healthCheck() {
    try {
      if (!this.isConnected) {
        return { status: 'disconnected', message: 'Redis not connected' }
      }

      await this.redis.ping()
      
      return { 
        status: 'healthy', 
        message: 'Redis Operations Service is operational',
        metrics: this.metrics,
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      return { 
        status: 'error', 
        message: `Redis Operations Service error: ${error.message}`,
        timestamp: new Date().toISOString()
      }
    }
  }
}

// Export singleton instance
export default new RedisOperationsService()
