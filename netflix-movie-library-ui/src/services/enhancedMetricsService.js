/**
 * Enhanced Metrics Service with Pinia Integration
 * Comprehensive tracking across all pages with charts support
 */

import { useUserStore } from '@/stores/userStore'
import { useSearchStore } from '@/stores/searchStore'

class EnhancedMetricsService {
  constructor() {
    this.apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    this.sessionId = this.generateSessionId()
    this.userId = this.getUserId()
    this.chartColors = {
      primary: '#4a90e2',
      secondary: '#7b68ee',
      success: '#20b2aa',
      warning: '#ffa500',
      info: '#ff69b4',
      light: '#32cd32',
      dark: '#9370db'
    }
  }

  generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
  }

  getUserId() {
    let userId = localStorage.getItem('movie_library_user_id')
    if (!userId) {
      userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
      localStorage.setItem('movie_library_user_id', userId)
    }
    return userId
  }

  // Generate UUID v4
  generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0
      const v = c === 'x' ? r : (r & 0x3 | 0x8)
      return v.toString(16)
    })
  }

  // Get user info from Pinia store using store helper methods
  getUserInfo() {
    let userStore = null
    let userProfile = null
    let email = null
    let firstName = null
    let lastName = null
    let country = null
    let city = null
    let state = null
    let timezone = null
    let timezoneOffset = null
    let nationality = null
    let registeredDate = null
    let accountAge = null
    let gender = null
    let profilePicture = null
    
    try {
      userStore = useUserStore()
      userProfile = userStore.user
      
      console.log('Pinia User Data (Full):', userProfile)
      
      if (userProfile) {
        // Use Pinia store helper methods for consistent data extraction
        const fullName = userStore.getUserFullName()
        const initials = userStore.getUserInitials()
        const location = userStore.getUserLocation()
        
        // Extract individual components (no fallback values)
        firstName = userProfile.name?.first
        lastName = userProfile.name?.last
        country = userProfile.location?.country
        city = userProfile.location?.city
        state = userProfile.location?.state
        timezone = userProfile.location?.timezone?.description
        timezoneOffset = userProfile.location?.timezone?.offset
        nationality = userProfile.nat
        gender = userProfile.gender
        email = userProfile.email
        registeredDate = userProfile.registered?.date
        accountAge = userProfile.registered?.age
        profilePicture = userProfile.picture?.medium
        
        // Ensure country is always a full name, not a code
        country = this.normalizeCountryName(country)
        
        console.log('Successfully extracted user data using Pinia store methods:', {
          fullName,
          initials,
          location,
          hasUserProfile: !!userProfile
        })
      } else {
        console.log('No user profile found in Pinia store')
      }
      
      console.log('Enhanced User Info:', {
        firstName,
        lastName,
        country,
        city,
        state,
        timezone,
        timezoneOffset,
        nationality,
        gender,
        email,
        registeredDate,
        accountAge,
        profilePicture,
        hasUserProfile: !!userProfile
      })
      
    } catch (error) {
      console.warn('Pinia store not available:', error)
    }
    
    // Generate unique record ID combining UUID and email
    const recordId = this.generateUUID()
    const uniqueRecordId = `${recordId}:${email}`
    
    return {
      // Unique identifiers
      recordid: recordId,
      uniqueRecordId: uniqueRecordId,
      email: email,
      
      // Basic user info (using Pinia store methods when available)
      firstName: firstName,
      lastName: lastName,
      fullName: userStore ? userStore.getUserFullName() : `${firstName} ${lastName}`.trim(),
      initials: userStore ? userStore.getUserInitials() : `${firstName[0]}${lastName[0]}`.toUpperCase(),
      location: userStore ? userStore.getUserLocation() : `${city}, ${country}`,
      
      // Location info
      country: country,
      city: city,
      state: state,
      timezone: timezone,
      timezoneOffset: timezoneOffset,
      nationality: nationality,
      
      // Contact info
      email: email,
      
      // Registration info
      registeredDate: registeredDate,
      accountAge: accountAge,
      
      // Additional context
      gender: gender,
      profilePicture: profilePicture,
      
      // Enhanced user context for analytics
      userContext: {
        // Pinia store methods
        fullName: userStore ? userStore.getUserFullName() : `${firstName} ${lastName}`.trim(),
        initials: userStore ? userStore.getUserInitials() : `${firstName[0]}${lastName[0]}`.toUpperCase(),
        location: userStore ? userStore.getUserLocation() : `${city}, ${country}`,
        
        // Detailed user info
        firstName: firstName,
        lastName: lastName,
        country: country,
        city: city,
        state: state,
        timezone: timezone,
        timezoneOffset: timezoneOffset,
        nationality: nationality,
        gender: gender,
        email: email,
        registeredDate: registeredDate,
        accountAge: accountAge,
        profilePicture: profilePicture,
        
        // Store reference
        hasUserStore: !!userStore,
        hasUserProfile: !!userProfile
      },
      
      // Legacy format for backward compatibility
      userProfile: {
        first_name: firstName,
        last_name: lastName,
        country: country,
        city: city,
        state: state,
        timezone: timezone,
        timezone_offset: timezoneOffset,
        nationality: nationality,
        gender: gender,
        email: email,
        registered_date: registeredDate,
        account_age: accountAge,
        profile_picture: profilePicture
      }
    }
  }

  // Get country name from country code
  getCountryNameFromCode(code) {
    const countryMap = {
      'US': 'United States',
      'GB': 'United Kingdom',
      'CA': 'Canada',
      'AU': 'Australia',
      'DE': 'Germany',
      'FR': 'France',
      'ES': 'Spain',
      'IT': 'Italy',
      'JP': 'Japan',
      'KR': 'South Korea',
      'CN': 'China',
      'IN': 'India',
      'BR': 'Brazil',
      'MX': 'Mexico',
      'RU': 'Russia',
      'NL': 'Netherlands',
      'SE': 'Sweden',
      'NO': 'Norway',
      'DK': 'Denmark',
      'FI': 'Finland'
    }
    return countryMap[code] || code
  }

  // Normalize country name to ensure it's always a full name, not a code
  normalizeCountryName(country) {
    if (!country) return null
    
    // If it's already a full name, return as is
    const fullNames = [
      'United States', 'United Kingdom', 'Canada', 'Australia', 'Germany', 'France',
      'Spain', 'Italy', 'Japan', 'South Korea', 'China', 'India', 'Brazil', 'Mexico',
      'Russia', 'Netherlands', 'Sweden', 'Norway', 'Denmark', 'Finland', 'New Zealand'
    ]
    
    if (fullNames.includes(country)) {
      return country
    }
    
    // If it's a country code, convert to full name
    return this.getCountryNameFromCode(country)
  }

  // Enhanced tracking with Pinia context and UUID + email combination
  async trackUserAction(action, metadata = {}) {
    try {
      const userInfo = this.getUserInfo()
      const currentUrl = window.location.href
      const previousUrl = document.referrer || null
      const visitPage = this.getPageName(currentUrl)
      
      const payload = {
        // Basic tracking data - only page, activity, and country
        page: visitPage,
        activity: action,
        user_country: userInfo.country,
        
        // Metadata
        metadata: {
          timestamp: new Date().toISOString(),
          current_url: currentUrl,
          previous_url: previousUrl,
          session_id: this.sessionId,
          ...metadata
        }
      }

      console.log('🎯 UI → Service: Tracking User Action', {
        action,
        metadata,
        userInfo: {
          uniqueRecordId: userInfo.uniqueRecordId,
          email: userInfo.email,
          country: userInfo.country,
          sessionId: this.sessionId
        },
        payload
      })

      // Send to backend
      this.sendToBackend('/api/analytics/track/page-activity', payload)
      
      // Store locally
      this.storeLocalMetric('user_action', payload)

    } catch (error) {
      console.warn('Failed to track user action:', error)
    }
  }

  // Search tracking with enhanced user context and UUID + email combination
  async trackSearch(query, resultsCount, filters = {}, searchType = 'text') {
    try {
      const userInfo = this.getUserInfo()
      const currentUrl = window.location.href
      const previousUrl = document.referrer || null
      const visitPage = this.getPageName(currentUrl)
      
      const payload = {
        // Search data - simplified to only essential info
        query: query,
        results_count: resultsCount,
        search_type: searchType,
        filters: filters,
        country: userInfo.country,
        
        // Metadata
        metadata: {
          timestamp: new Date().toISOString(),
          visit_page: visitPage,
          current_url: currentUrl,
          previous_url: previousUrl,
          activity: 'searching',
          session_id: this.sessionId,
          has_filters: Object.keys(filters).length > 0,
          filter_count: Object.keys(filters).length
        }
      }

      console.log('UI → Service: Tracking Search', {
        query,
        resultsCount,
        searchType,
        filters,
        country: userInfo.country,
        payload
      })

      this.sendToBackend('/api/analytics/track/search', payload)
      this.storeLocalMetric('search_query', payload)

    } catch (error) {
      console.warn('Failed to track search:', error)
    }
  }

  // Library operations tracking
  async trackLibraryOperation(operation, movieData = {}, metadata = {}) {
    try {
      const userInfo = this.getUserInfo()
      
      const payload = {
        operation, // 'create', 'edit', 'delete', 'view', 'sort', 'filter'
        country: userInfo.country,
        movie_data: {
          movie_id: movieData.id,
          movie_title: movieData.title,
          movie_genre: movieData.genre,
          movie_year: movieData.year
        },
        metadata: {
          ...metadata,
          timestamp: new Date().toISOString(),
          url: window.location.href
        }
      }

      console.log('UI → Service: Tracking Library Operation', {
        operation,
        movieData,
        metadata,
        country: userInfo.country,
        payload
      })

      this.sendToBackend('/api/analytics/track/page-activity', payload)
      this.storeLocalMetric('library_operation', payload)

    } catch (error) {
      console.warn('Failed to track library operation:', error)
    }
  }

  // Sorting tracking
  async trackSorting(sortField, sortDirection, context = 'library') {
    try {
      const userInfo = this.getUserInfo()
      
      const payload = {
        sort_field: sortField,
        sort_direction: sortDirection,
        context, // 'library', 'home', 'insights'
        country: userInfo.country,
        metadata: {
          timestamp: new Date().toISOString(),
          url: window.location.href
        }
      }

      console.log('UI → Service: Tracking Sorting', {
        sortField,
        sortDirection,
        context,
        country: userInfo.country,
        payload
      })

      this.sendToBackend('/api/analytics/track/page-activity', payload)
      this.storeLocalMetric('sorting', payload)

    } catch (error) {
      console.warn('Failed to track sorting:', error)
    }
  }

  // Filter tracking
  async trackFilter(filterType, filterValue, action = 'apply') {
    try {
      const userInfo = this.getUserInfo()
      
      const payload = {
        filter_type: filterType,
        filter_value: filterValue,
        action, // 'apply', 'remove', 'clear_all'
        country: userInfo.country,
        metadata: {
          timestamp: new Date().toISOString(),
          url: window.location.href
        }
      }

      console.log('UI → Service: Tracking Filter', {
        filterType,
        filterValue,
        action,
        country: userInfo.country,
        payload
      })

      this.sendToBackend('/api/analytics/track/page-activity', payload)
      this.storeLocalMetric('filter', payload)

    } catch (error) {
      console.warn('Failed to track filter:', error)
    }
  }

  // Simplified page view tracking - only country data
  async trackPageView(page, metadata = {}) {
    try {
      console.log('trackPageView called:', { page, metadata })
      const userInfo = this.getUserInfo()
      console.log('User info retrieved:', userInfo)
      
      const payload = {
        // Basic tracking data - only page and country
        page: page,
        country: userInfo.country,
        
        // Minimal metadata
        metadata: {
          ...metadata,
          timestamp: new Date().toISOString(),
          url: window.location.href,
          referrer: document.referrer,
          session_id: this.sessionId
        }
      }

      console.log('UI → Service: Tracking Page View (Simplified)', {
        page,
        country: userInfo.country
      })

      console.log('Sending page view to backend:', payload)
      this.sendToBackend('/api/analytics/track/page-view', payload)
      this.storeLocalMetric('page_view', payload)

    } catch (error) {
      console.warn('Failed to track page view:', error)
    }
  }

  // Send to backend (fire and forget)
  async sendToBackend(endpoint, payload) {
    try {
      console.log('UI → API: Sending to Backend', {
        endpoint: `${this.apiBaseUrl}${endpoint}`,
        payload,
        timestamp: new Date().toISOString()
      })

      const response = await fetch(`${this.apiBaseUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      })

      if (response.ok) {
        console.log('API Response: Success', {
          endpoint,
          status: response.status,
          statusText: response.statusText
        })
      } else {
        console.warn('⚠️ API Response: Error', {
          endpoint,
          status: response.status,
          statusText: response.statusText
        })
      }
    } catch (error) {
      console.error(' API Error: Failed to send metrics to backend', {
        endpoint,
        error: error.message,
        payload
      })
    }
  }

  // Store locally for offline tracking
  storeLocalMetric(type, data) {
    try {
      const key = `movie_library_metrics_${type}`
      const existing = JSON.parse(localStorage.getItem(key) || '[]')
      existing.push(data)
      
      // Keep only last 100 entries per type
      if (existing.length > 100) {
        existing.splice(0, existing.length - 100)
      }
      
      localStorage.setItem(key, JSON.stringify(existing))
    } catch (error) {
      console.warn('Failed to store local metric:', error)
    }
  }

  // Get metrics data for charts
  async getMetricsData(days = 7) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/analytics/summary`)
      if (response.ok) {
        return await response.json()
      }
    } catch (error) {
      console.error('Failed to get metrics data:', error)
    }
    return null
  }

  // Get global metrics for insights
  async getGlobalMetrics(days = 7) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/analytics/summary`)
      if (response.ok) {
        return await response.json()
      }
    } catch (error) {
      console.error('Failed to get global metrics:', error)
    }
    return null
  }

  // Get activity data grouped by type
  async getActivityData(days = 7) {
    try {
      const metrics = await this.getMetricsData(days)
      if (!metrics) {
        console.log('No metrics data found, returning empty structure')
        return {
          searches: {},
          actions: {},
          library_operations: {},
          page_views: {},
          sorting: {},
          filters: {}
        }
      }

      // Group activities by type
      const activities = {
        searches: metrics.searches || [],
        actions: metrics.actions || [],
        library_operations: metrics.library_operations || [],
        page_views: metrics.page_views || [],
        sorting: metrics.sorting || [],
        filters: metrics.filters || []
      }

      console.log('Raw activities data:', activities)

      // Group by same activity
      const groupedActivities = {}
      Object.keys(activities).forEach(type => {
        groupedActivities[type] = this.groupByActivity(activities[type])
      })

      console.log('Grouped activities:', groupedActivities)
      return groupedActivities
    } catch (error) {
      console.error('Failed to get activity data:', error)
      return {
        searches: {},
        actions: {},
        library_operations: {},
        page_views: {},
        sorting: {},
        filters: {}
      }
    }
  }

  // Group activities by same action/query
  groupByActivity(activities) {
    const grouped = {}
    activities.forEach(activity => {
      const key = activity.action || activity.query || activity.operation || 'unknown'
      if (!grouped[key]) {
        grouped[key] = {
          count: 0,
          activities: [],
          first_seen: activity.timestamp,
          last_seen: activity.timestamp
        }
      }
      grouped[key].count++
      grouped[key].activities.push(activity)
      if (activity.timestamp < grouped[key].first_seen) {
        grouped[key].first_seen = activity.timestamp
      }
      if (activity.timestamp > grouped[key].last_seen) {
        grouped[key].last_seen = activity.timestamp
      }
    })
    return grouped
  }

  // Chart configuration helpers
  getChartConfig(type, data, options = {}) {
    const baseConfig = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: '#fff',
            font: {
              size: 12
            }
          }
        }
      }
    }

    switch (type) {
      case 'pie':
        return {
          type: 'pie',
          data: {
            labels: data.labels,
            datasets: [{
              data: data.values,
              backgroundColor: this.getPieColors(data.labels.length),
              borderColor: '#333',
              borderWidth: 1
            }]
          },
          options: {
            ...baseConfig,
            plugins: {
              ...baseConfig.plugins,
              legend: {
                ...baseConfig.plugins.legend,
                labels: {
                  ...baseConfig.plugins.legend.labels,
                  generateLabels: function(chart) {
                    const data = chart.data
                    if (data.labels.length && data.datasets.length) {
                      return data.labels.map((label, i) => {
                        const value = data.datasets[0].data[i]
                        return {
                          text: `${label}: ${value}`,
                          fillStyle: data.datasets[0].backgroundColor[i],
                          strokeStyle: data.datasets[0].borderColor,
                          lineWidth: data.datasets[0].borderWidth,
                          hidden: false,
                          index: i
                        }
                      })
                    }
                    return []
                  }
                }
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    const label = context.label || ''
                    const value = context.parsed || 0
                    return `${label}: ${value} visits`
                  }
                }
              }
            },
            ...options
          }
        }

      case 'bar':
        return {
          type: 'bar',
          data: {
            labels: data.labels,
            datasets: [{
              label: data.label || 'Count',
              data: data.values,
              backgroundColor: this.chartColors.primary,
              borderColor: this.chartColors.secondary,
              borderWidth: 1
            }]
          },
          options: {
            ...baseConfig,
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  color: '#fff'
                },
                grid: {
                  color: '#333'
                }
              },
              x: {
                ticks: {
                  color: '#fff'
                },
                grid: {
                  color: '#333'
                }
              }
            },
            ...options
          }
        }

      case 'line':
        return {
          type: 'line',
          data: {
            labels: data.labels,
            datasets: [{
              label: data.label || 'Count',
              data: data.values,
              borderColor: this.chartColors.primary,
              backgroundColor: this.chartColors.primary + '20',
              tension: 0.4,
              fill: true
            }]
          },
          options: {
            ...baseConfig,
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  color: '#fff'
                },
                grid: {
                  color: '#333'
                }
              },
              x: {
                ticks: {
                  color: '#fff'
                },
                grid: {
                  color: '#333'
                }
              }
            },
            ...options
          }
        }

      default:
        return baseConfig
    }
  }

  getPieColors(count) {
    const colors = [
      this.chartColors.primary,
      this.chartColors.secondary,
      this.chartColors.success,
      this.chartColors.warning,
      this.chartColors.info,
      this.chartColors.light
    ]
    
    const result = []
    for (let i = 0; i < count; i++) {
      result.push(colors[i % colors.length])
    }
    
    console.log(`Generated ${count} pie colors:`, result)
    return result
  }

  // Initialize enhanced tracking
  init() {
    // Track initial page view immediately (without waiting for user data)
    this.trackCurrentPageView()

    // Track navigation changes
    window.addEventListener('popstate', () => {
      this.trackCurrentPageView()
    })

    // Track visibility changes
    document.addEventListener('visibilitychange', () => {
      const currentPage = window.location.pathname
      if (document.visibilityState === 'visible') {
        this.trackUserAction('page_visible', { page: currentPage })
      } else {
        this.trackUserAction('page_hidden', { page: currentPage })
      }
    })

    // Track errors
    window.addEventListener('error', (event) => {
      this.trackUserAction('javascript_error', {
        error_message: event.message,
        error_filename: event.filename,
        error_line: event.lineno,
        error_column: event.colno
      })
    })

    console.log('Enhanced metrics tracking initialized')
  }


  trackCurrentPageView() {
    const page = window.location.pathname
    const pageName = this.getPageName(page)
    this.trackPageView(page, { 
      page_name: pageName,
      full_url: window.location.href,
      referrer: document.referrer
    })
  }

  getPageName(path) {
    // Extract just the pathname if a full URL is passed
    const pathname = path.startsWith('http') ? new URL(path).pathname : path
    
    const pageMap = {
      '/': 'Home',
      '/home': 'Home',
      '/app/library': 'Library',
      '/app/insights': 'Insights'
    }
    
    const pageName = pageMap[pathname] || null
    console.log('Page Name Detection:', { path, pathname, pageName })
    return pageName
  }
}

// Create global instance
const enhancedMetricsService = new EnhancedMetricsService()

// Export the service but don't auto-initialize
// Initialization will be handled when Pinia is available
export default enhancedMetricsService
export { enhancedMetricsService }
