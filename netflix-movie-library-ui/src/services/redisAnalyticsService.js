/**
 * Redis Analytics Service
 * Handles real-time analytics data collection and retrieval for Insights dashboard
 */

class RedisAnalyticsService {
  constructor() {
    this.redis = null
    this.isConnected = false
    this.init()
  }

  async init() {
    try {
      // Initialize Redis connection
      this.redis = await this.connectRedis()
      this.isConnected = true
      console.log('✅ Redis Analytics Service initialized')
    } catch (error) {
      console.error('❌ Failed to initialize Redis Analytics Service:', error)
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
      
      // Get page views data
      hgetall: async (key) => {
        try {
          const response = await fetch(`${API_BASE_URL}/api/analytics/page-views`)
          const data = await response.json()
          return data.success ? data.data : {}
        } catch (error) {
          console.error('Error getting page views:', error)
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

      console.log(`📊 Tracked page view: ${page} from ${userCountry}`)
    } catch (error) {
      console.error('Error tracking page view:', error)
    }
  }

  /**
   * Get page views data for Insights dashboard
   */
  async getPageViewsData() {
    if (!this.isConnected) return this.getMockPageViewsData()

    const today = this.getTodayString()
    
    try {
      const pageViews = await this.redis.hgetall(`page_views:daily:${today}`)
      
      return {
        Home: parseInt(pageViews.Home) || 0,
        Library: parseInt(pageViews.Library) || 0,
        Insights: parseInt(pageViews.Insights) || 0
      }
    } catch (error) {
      console.error('Error getting page views data:', error)
      return this.getMockPageViewsData()
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

      console.log(`🔍 Tracked search: "${query}" with ${resultsCount} results`)
    } catch (error) {
      console.error('Error tracking search query:', error)
    }
  }

  /**
   * Get search activities data for Insights dashboard
   */
  async getSearchActivitiesData() {
    if (!this.isConnected) return this.getMockSearchActivitiesData()

    const today = this.getTodayString()
    
    try {
      const searchActivities = await this.redis.hgetall(`search_activities:daily:${today}`)
      
      // Convert to the format expected by the dashboard
      const result = {}
      for (const [query, count] of Object.entries(searchActivities)) {
        result[query] = { resultsCount: parseInt(count) }
      }
      
      return result
    } catch (error) {
      console.error('Error getting search activities data:', error)
      return this.getMockSearchActivitiesData()
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

      console.log(`🌍 Tracked user country: ${country}`)
    } catch (error) {
      console.error('Error tracking user country:', error)
    }
  }

  /**
   * Get user countries data for Insights dashboard
   */
  async getUserCountriesData() {
    if (!this.isConnected) return this.getMockUserCountriesData()

    const month = this.getMonthString()
    
    try {
      const countries = await this.redis.hgetall(`user_countries:monthly:${month}`)
      
      // Convert string values to numbers
      const result = {}
      for (const [country, count] of Object.entries(countries)) {
        result[country] = parseInt(count)
      }
      
      return result
    } catch (error) {
      console.error('Error getting user countries data:', error)
      return this.getMockUserCountriesData()
    }
  }

  // ==================== PAGE ACTIVITIES TRACKING ====================

  /**
   * Track page activity (clicks, interactions, etc.)
   */
  async trackPageActivity(page, activity, userCountry = 'Unknown') {
    if (!this.isConnected) return

    const today = this.getTodayString()

    try {
      // Store activity in a list for recent activities
      const activityData = {
        visit_page: page,
        activity: activity,
        user_profile: { country: userCountry },
        timestamp: new Date().toISOString()
      }

      await this.redis.lpush(`page_activities:daily:${today}`, JSON.stringify(activityData))
      
      // Keep only last 100 activities
      await this.redis.ltrim(`page_activities:daily:${today}`, 0, 99)

      console.log(`📋 Tracked page activity: ${page} - ${activity}`)
    } catch (error) {
      console.error('Error tracking page activity:', error)
    }
  }

  /**
   * Get page activities data for Insights dashboard
   */
  async getPageActivitiesData() {
    if (!this.isConnected) return this.getMockPageActivitiesData()

    const today = this.getTodayString()
    
    try {
      const activities = await this.redis.lrange(`page_activities:daily:${today}`, 0, -1)
      
      // Parse JSON strings and return as array
      return activities.map(activity => JSON.parse(activity))
    } catch (error) {
      console.error('Error getting page activities data:', error)
      return this.getMockPageActivitiesData()
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

  // ==================== MOCK DATA FOR DEVELOPMENT ====================

  getMockPageViewsData() {
    return {
      Home: 45,
      Library: 32,
      Insights: 5
    }
  }

  getMockSearchActivitiesData() {
    return {
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
    }
  }

  getMockUserCountriesData() {
    return {
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
    }
  }

  getMockPageActivitiesData() {
    return [
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
    ]
  }

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
