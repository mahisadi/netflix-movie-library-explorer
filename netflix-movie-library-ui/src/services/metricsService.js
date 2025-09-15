/**
 * Frontend Metrics Service
 * Tracks user interactions and sends them to the backend
 */

class MetricsService {
  constructor() {
    this.apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    this.sessionId = this.generateSessionId()
    this.userId = this.getUserId()
  }

  generateSessionId() {
    // Generate a unique session ID
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
  }

  getUserId() {
    // Try to get user ID from localStorage or generate anonymous
    let userId = localStorage.getItem('movie_library_user_id')
    if (!userId) {
      userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
      localStorage.setItem('movie_library_user_id', userId)
    }
    return userId
  }

  async trackUserAction(action, metadata = {}) {
    try {
      const payload = {
        action,
        user_id: this.userId,
        session_id: this.sessionId,
        metadata: {
          ...metadata,
          timestamp: new Date().toISOString(),
          url: window.location.href,
          user_agent: navigator.userAgent
        }
      }

      // Send to backend (fire and forget)
      fetch(`${this.apiBaseUrl}/metrics/track-action`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      }).catch(error => {
        console.warn('Failed to track user action:', error)
      })

      // Also store locally for offline tracking
      this.storeLocalMetric('user_action', payload)

    } catch (error) {
      console.warn('Failed to track user action:', error)
    }
  }

  async trackSearchQuery(query, resultsCount, filters = {}) {
    try {
      const payload = {
        query,
        results_count: resultsCount,
        user_id: this.userId,
        session_id: this.sessionId,
        filters,
        metadata: {
          timestamp: new Date().toISOString(),
          url: window.location.href
        }
      }

      // Send to backend
      fetch(`${this.apiBaseUrl}/metrics/track-search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      }).catch(error => {
        console.warn('Failed to track search query:', error)
      })

      // Store locally
      this.storeLocalMetric('search_query', payload)

    } catch (error) {
      console.warn('Failed to track search query:', error)
    }
  }

  async trackPageView(page, metadata = {}) {
    try {
      const payload = {
        page,
        user_id: this.userId,
        session_id: this.sessionId,
        metadata: {
          ...metadata,
          timestamp: new Date().toISOString(),
          url: window.location.href,
          referrer: document.referrer
        }
      }

      // Send to backend
      fetch(`${this.apiBaseUrl}/metrics/track-page-view`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      }).catch(error => {
        console.warn('Failed to track page view:', error)
      })

      // Store locally
      this.storeLocalMetric('page_view', payload)

    } catch (error) {
      console.warn('Failed to track page view:', error)
    }
  }

  async trackApiCall(endpoint, method, statusCode, responseTime, metadata = {}) {
    try {
      const payload = {
        endpoint,
        method,
        status_code: statusCode,
        response_time_ms: responseTime,
        user_id: this.userId,
        session_id: this.sessionId,
        metadata: {
          ...metadata,
          timestamp: new Date().toISOString()
        }
      }

      // Send to backend
      fetch(`${this.apiBaseUrl}/metrics/track-api-call`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      }).catch(error => {
        console.warn('Failed to track API call:', error)
      })

      // Store locally
      this.storeLocalMetric('api_call', payload)

    } catch (error) {
      console.warn('Failed to track API call:', error)
    }
  }

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

  // Convenience methods for common actions
  trackSearch(query, resultsCount, filters = {}) {
    this.trackUserAction('search', { query, resultsCount, filters })
    this.trackSearchQuery(query, resultsCount, filters)
  }

  trackMovieView(movieId, movieTitle) {
    this.trackUserAction('view_movie', { movie_id: movieId, movie_title: movieTitle })
  }

  trackMovieEdit(movieId, movieTitle) {
    this.trackUserAction('edit_movie', { movie_id: movieId, movie_title: movieTitle })
  }

  trackMovieCreate(movieTitle) {
    this.trackUserAction('create_movie', { movie_title: movieTitle })
  }

  trackMovieDelete(movieId, movieTitle) {
    this.trackUserAction('delete_movie', { movie_id: movieId, movie_title: movieTitle })
  }

  trackFilterChange(filterType, filterValue) {
    this.trackUserAction('change_filter', { filter_type: filterType, filter_value: filterValue })
  }

  trackSortChange(sortField, sortDirection) {
    this.trackUserAction('change_sort', { sort_field: sortField, sort_direction: sortDirection })
  }

  trackNavigation(fromPage, toPage) {
    this.trackUserAction('navigate', { from_page: fromPage, to_page: toPage })
  }

  // Track page views automatically
  trackCurrentPageView() {
    const page = window.location.pathname
    this.trackPageView(page)
  }

  // Initialize tracking
  init() {
    // Track initial page view
    this.trackCurrentPageView()

    // Track navigation changes
    window.addEventListener('popstate', () => {
      this.trackCurrentPageView()
    })

    // Track visibility changes (user engagement)
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') {
        this.trackUserAction('page_visible')
      } else {
        this.trackUserAction('page_hidden')
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

    console.log(' Metrics tracking initialized')
  }
}

// Create global instance
const metricsService = new MetricsService()

// Auto-initialize
metricsService.init()

export default metricsService
