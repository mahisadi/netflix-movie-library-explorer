/**
 * Redis Analytics Service
 * Handles real-time analytics data collection and retrieval for Insights dashboard
 */

class RedisAnalyticsService {
  constructor() {
    this.redis = null
    this.isConnected = false
    // Don't call init() here - it will be called explicitly
  }

  async init() {
    console.log('Redis Analytics Service init() called')
    try {
      // Initialize Redis connection
      this.redis = await this.connectRedis()
      this.isConnected = true
      console.log('Redis Analytics Service initialized, isConnected:', this.isConnected)
    } catch (error) {
      console.error('Failed to initialize Redis Analytics Service:', error)
      this.isConnected = false
    }
  }

  async connectRedis() {
    // Connect to the backend API for Redis operations
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    
    return {
      // Page views tracking
      hincrby: async (key, field, increment) => {
        try {
          const response = await fetch(`${API_BASE_URL}/api/analytics/track/page-view`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ page: field, country: 'Unknown' })
          })
          return response.ok ? increment : 0
        } catch (error) {
          console.error('Error tracking page view:', error)
          return 0
        }
      },
      
      // Get page views data - simplified to avoid phantom data
      hgetall: async (key) => {
        try {
          console.log('hgetall called with key:', key)
          // Only return page views data for page_views keys
          if (key.includes('page_views')) {
            const response = await fetch(`${API_BASE_URL}/api/analytics/page-views`)
            const data = await response.json()
            return data.success ? data.data : {}
          }
          // Return empty for other keys to prevent phantom data
          return {}
        } catch (error) {
          console.error('Error getting data:', error)
          return {}
        }
      },
      
      // Search tracking
      zadd: async (key, score, member) => {
        try {
          const response = await fetch(`${API_BASE_URL}/api/analytics/track/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              query: member, 
              results_count: score, 
              country: 'Unknown' 
            })
          })
          return response.ok ? 1 : 0
        } catch (error) {
          console.error('Error tracking search:', error)
          return 0
        }
      },
      
      // Get search rankings
      zrevrange: async (key, start, stop) => {
        try {
          const response = await fetch(`${API_BASE_URL}/api/analytics/search-activities`)
          const data = await response.json()
          if (data.success) {
            return Object.keys(data.data).slice(start, stop + 1)
          }
          return []
        } catch (error) {
          console.error('Error getting search rankings:', error)
          return []
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
      }
    }
  }

  // ==================== PAGE VIEWS TRACKING ====================

  /**
   * Track page view with country information
   */
  async trackPageView(page, userCountry = 'Unknown') {
    if (!this.isConnected) return

    const today = this.getTodayString()
    const month = this.getMonthString()

    try {
      // Increment daily page views
      await this.redis.hincrby(`page_views:daily:${today}`, page, 1)
      
      // Increment monthly country distribution
      await this.redis.hincrby(`user_countries:monthly:${month}`, userCountry, 1)
      
      // Add to time series for real-time analytics
      await this.redis.ts_add('user_activity:page_views', '*', 1, {
        page: page,
        country: userCountry
      })

      console.log(`Tracked page view: ${page} from ${userCountry}`)
    } catch (error) {
      console.error('Error tracking page view:', error)
    }
  }

  /**
   * Get page views data for Insights dashboard
   */
  async getPageViewsData() {
    console.log('getPageViewsData called, isConnected:', this.isConnected)
    if (!this.isConnected) {
      console.log(' Service not connected, returning empty data')
      return {}
    }

    try {
      // Call the page views API directly
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      console.log(' Fetching page views from:', `${API_BASE_URL}/api/analytics/page-views`)
      const response = await fetch(`${API_BASE_URL}/api/analytics/page-views`)
      console.log(' Page views response status:', response.status)
      const data = await response.json()
      console.log('Page views data received:', data)
      
      if (data.success) {
        // The API already returns data in the correct format
        console.log('Page views data success, returning:', data.data)
        return data.data
      }
      
      console.log('Page views API returned success: false')
      return {}
    } catch (error) {
      console.error(' Error getting page views data:', error)
      return {}
    }
  }

  // ==================== SEARCH ACTIVITIES TRACKING ====================

  /**
   * Track search query with results count
   */
  async trackSearchQuery(query, resultsCount) {
    if (!this.isConnected) return

    const today = this.getTodayString()

    try {
      // Increment search frequency
      await this.redis.hincrby(`search_activities:daily:${today}`, query, 1)
      
      // Add to search rankings (sorted set)
      await this.redis.zadd(`search_rankings:daily:${today}`, resultsCount, query)
      
      // Add to time series
      await this.redis.ts_add('user_activity:search_queries', '*', 1, {
        query: query,
        results: resultsCount
      })

      console.log(` Tracked search: "${query}" with ${resultsCount} results`)
    } catch (error) {
      console.error('Error tracking search query:', error)
    }
  }

  /**
   * Get search activities data for Insights dashboard
   */
  async getSearchActivitiesData() {
    console.log(' getSearchActivitiesData called, isConnected:', this.isConnected)
    if (!this.isConnected) {
      console.log(' Service not connected, returning empty data')
      return {}
    }

    try {
      // Call the search activities API directly
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      console.log(' Fetching search activities from:', `${API_BASE_URL}/api/analytics/search-activities`)
      const response = await fetch(`${API_BASE_URL}/api/analytics/search-activities`)
      console.log(' Search activities response status:', response.status)
      const data = await response.json()
      console.log(' Search activities data received:', data)
      
      if (data.success) {
        // The API already returns data in the correct format
        console.log(' Search activities data success, returning:', data.data)
        return data.data
      }
      
      console.log(' Search activities API returned success: false')
      return {}
    } catch (error) {
      console.error(' Error getting search activities data:', error)
      return {}
    }
  }

  // ==================== USER COUNTRIES TRACKING ====================

  /**
   * Track user country for analytics
   */
  async trackUserCountry(country) {
    if (!this.isConnected) return

    const month = this.getMonthString()

    try {
      // Increment country count
      await this.redis.hincrby(`user_countries:monthly:${month}`, country, 1)
      
      // Add to country rankings
      await this.redis.zadd(`country_rankings:monthly:${month}`, 1, country)
      
      // Add to time series
      await this.redis.ts_add('user_activity:country_distribution', '*', 1, {
        country: country
      })

      console.log(` Tracked user country: ${country}`)
    } catch (error) {
      console.error('Error tracking user country:', error)
    }
  }

  /**
   * Get user countries data for Insights dashboard
   */
  async getUserCountriesData() {
    console.log(' getUserCountriesData called, isConnected:', this.isConnected)
    if (!this.isConnected) return {}

    try {
      // Call the user countries API directly
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      console.log(' Fetching from:', `${API_BASE_URL}/api/analytics/user-countries`)
      const response = await fetch(`${API_BASE_URL}/api/analytics/user-countries`)
      console.log(' Response status:', response.status)
      const data = await response.json()
      console.log(' Response data:', data)
      
      if (data.success) {
        // The API already returns data in the correct format
        console.log(' Returning data.data:', data.data)
        return data.data
      }
      
      console.log(' API returned success: false')
      return {}
    } catch (error) {
      console.error('Error getting user countries data:', error)
      return {}
    }
  }

  // ==================== PAGE ACTIVITIES TRACKING ====================

  /**
   * Track page activity (clicks, interactions, etc.)
   */
  async trackPageActivity(page, activity, userCountry = 'Unknown') {
    if (!this.isConnected) return

    try {
      // Call the page activity tracking API directly
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/analytics/track/page-activity`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          page: page,
          activity: activity,
          user_country: userCountry
        })
      })

      if (response.ok) {
        console.log(` Tracked page activity: ${page} - ${activity}`)
      } else {
        console.error('Failed to track page activity')
      }
    } catch (error) {
      console.error('Error tracking page activity:', error)
    }
  }

  /**
   * Get page activities data for Insights dashboard
   */
  async getPageActivitiesData() {
    if (!this.isConnected) return []

    try {
      // Call the page activities API directly
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/analytics/page-activities`)
      const data = await response.json()
      
      if (data.success) {
        // The API already returns data in the correct format
        return data.data
      }
      
      return []
    } catch (error) {
      console.error('Error getting page activities data:', error)
      return []
    }
  }

  // ==================== UTILITY METHODS ====================

  getTodayString() {
    return new Date().toISOString().split('T')[0] // YYYY-MM-DD
  }

  getMonthString() {
    const now = new Date()
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}` // YYYY-MM
  }

  // ==================== FALLBACK DATA (NO MOCK DATA) ====================

  // ==================== HEALTH CHECK ====================

  async healthCheck() {
    try {
      if (!this.isConnected) {
        return { status: 'disconnected', message: 'Redis not connected' }
      }

      // Test Redis connection
      await this.redis.ping()
      
      return { 
        status: 'healthy', 
        message: 'Redis Analytics Service is operational',
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      return { 
        status: 'error', 
        message: `Redis Analytics Service error: ${error.message}`,
        timestamp: new Date().toISOString()
      }
    }
  }
}

// Export singleton instance
export default new RedisAnalyticsService()
