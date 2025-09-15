# Redis Implementation Plan for Search, Insights & Operations

## 🎯 **Implementation Overview**

This plan outlines the step-by-step implementation of Redis-based data architecture for the Movie Library Explorer's Search, Insights, and Operations functionality.

## 📋 **Phase 1: Foundation Setup (Week 1)**

### **1.1 Redis Infrastructure**
```bash
# Update docker-compose.yml
services:
  redis:
    image: redis/redis-stack:latest
    container_name: redis-movie-explorer
    ports:
      - "6379:6379"
      - "8001:8001"  # RedisInsight
    volumes:
      - redis_data:/data
    environment:
      - REDIS_PASSWORD=${REDIS_PASSWORD:-}
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    restart: unless-stopped
```

### **1.2 Database Structure**
```python
# Database separation
DB 0: Search Data (Movies, Content)
DB 1: Analytics & Insights  
DB 2: Operations & Monitoring
DB 3: Cache & Sessions
DB 4: Metrics & Counters
DB 5: Logs & Events
```

### **1.3 RedisSearch Indexes**
```python
# Create movie search index
FT.CREATE movies_index ON HASH PREFIX 1 movie: SCHEMA
    title TEXT SORTABLE
    genre TAG SORTABLE
    subgenre TAG SORTABLE
    year NUMERIC SORTABLE
    rating NUMERIC SORTABLE
    language TAG SORTABLE
    country TAG SORTABLE
    plot TEXT
    director TEXT
    cast TEXT
    created_at NUMERIC SORTABLE
    updated_at NUMERIC SORTABLE
```

## 📊 **Phase 2: Analytics Implementation (Week 2)**

### **2.1 Integrate Analytics Service**
```javascript
// Update Insights.vue to use Redis Analytics Service
import redisAnalyticsService from '@/services/redisAnalyticsService'

// Replace mock data with real Redis data
const loadAnalyticsData = async () => {
  try {
    const [pageViews, searchActivities, userCountries, pageActivities] = await Promise.all([
      redisAnalyticsService.getPageViewsData(),
      redisAnalyticsService.getSearchActivitiesData(),
      redisAnalyticsService.getUserCountriesData(),
      redisAnalyticsService.getPageActivitiesData()
    ])
    
    allPageViews.value = pageViews
    searchActivities.value = searchActivities
    userCountries.value = userCountries
    pageActivities.value = pageActivities
  } catch (error) {
    console.error('Failed to load analytics data:', error)
  }
}
```

### **2.2 Real-Time Tracking**
```javascript
// Add tracking to search functionality
const search = async (resetPagination = true) => {
  // ... existing search logic ...
  
  // Track search analytics
  await redisAnalyticsService.trackSearchQuery(
    searchQuery.value,
    result.totalCount || 0
  )
}

// Add page view tracking
const trackPageView = async (page) => {
  const userCountry = getUserCountry() // Get from user profile
  await redisAnalyticsService.trackPageView(page, userCountry)
}
```

### **2.3 Data Structures**
```python
# Time-series data for real-time analytics
TS.CREATE user_activity:page_views RETENTION 90d LABELS type page_views
TS.CREATE user_activity:search_queries RETENTION 30d LABELS type search
TS.CREATE user_activity:country_distribution RETENTION 180d LABELS type geography

# Hash structures for aggregated data
HSET page_views:daily:2024-01-15 home 45 library 32 insights 5
HSET search_activities:daily:2024-01-15 inception 5 blade_runner 3
HSET user_countries:monthly:2024-01 "United States" 25 "Canada" 15
```

## ⚙️ **Phase 3: Operations Implementation (Week 3)**

### **3.1 Integrate Operations Service**
```javascript
// Update Operations tab content
import redisOperationsService from '@/services/redisOperationsService'

// Replace placeholder with real operations data
const loadOperationsData = async () => {
  try {
    const [systemMetrics, performanceMetrics, alerts, redisInfo, config] = await Promise.all([
      redisOperationsService.getSystemMetrics(),
      redisOperationsService.getPerformanceMetrics(),
      redisOperationsService.getAlerts(),
      redisOperationsService.getRedisInfo(),
      redisOperationsService.getConfiguration()
    ])
    
    operationsData.value = {
      system: systemMetrics,
      performance: performanceMetrics,
      alerts: alerts,
      redis: redisInfo,
      configuration: config
    }
  } catch (error) {
    console.error('Failed to load operations data:', error)
  }
}
```

### **3.2 System Monitoring**
```python
# System metrics collection
TS.CREATE system_metrics:cpu_usage RETENTION 7d LABELS type cpu
TS.CREATE system_metrics:memory_usage RETENTION 7d LABELS type memory
TS.CREATE system_metrics:redis_memory RETENTION 7d LABELS type redis

# Performance metrics
TS.CREATE app_metrics:response_time RETENTION 3d LABELS type performance
TS.CREATE app_metrics:error_rate RETENTION 7d LABELS type errors
```

### **3.3 Alerting System**
```python
# Alert configuration
HSET operations:configuration 
    cpu_threshold 80 
    memory_threshold 85 
    redis_threshold 90
    response_time_threshold 2000
    error_rate_threshold 5

# Alert storage
LPUSH operations:alerts '{"type":"warning","message":"High CPU usage","timestamp":"2024-01-15T10:30:00Z","severity":"high"}'
```

## 🔍 **Phase 4: Search Optimization (Week 4)**

### **4.1 Enhanced Search Features**
```python
# Add fuzzy matching and auto-complete
FT.CREATE movies_suggestions ON HASH PREFIX 1 suggestion: SCHEMA
    title TEXT PHONETIC "dm:en"
    genre TAG
    year NUMERIC

# Search with suggestions
FT.SUGGET movies_suggestions "inc" FUZZY 2 MAX 5
```

### **4.2 Search Analytics**
```python
# Track search performance
TS.CREATE search_analytics:query_frequency RETENTION 30d LABELS type frequency
TS.CREATE search_analytics:result_counts RETENTION 30d LABELS type results
TS.CREATE search_analytics:response_times RETENTION 7d LABELS type performance
```

### **4.3 Caching Strategy**
```python
# Cache popular searches
SETEX search_cache:popular:inception 3600 '{"movies":[...],"totalCount":5}'

# Cache filter options
SETEX filter_cache:genres 1800 '["action","comedy","drama"]'
SETEX filter_cache:years 1800 '[1990,1991,1992,...]'
```

## 📈 **Phase 5: Performance & Monitoring (Week 5)**

### **5.1 Performance Optimization**
```python
# Connection pooling
redis_pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    max_connections=20,
    retry_on_timeout=True
)

# Pipeline for batch operations
pipe = redis.pipeline()
for operation in operations:
    pipe.execute_command(operation)
pipe.execute()
```

### **5.2 Data Retention Policies**
```python
# Automatic cleanup
EXPIRE page_views:daily:* 90d
EXPIRE search_activities:daily:* 30d
EXPIRE user_countries:monthly:* 180d
EXPIRE operations:alerts 90d
```

### **5.3 Health Monitoring**
```javascript
// Health check endpoint
app.get('/health/redis', async (req, res) => {
  try {
    const analyticsHealth = await redisAnalyticsService.healthCheck()
    const operationsHealth = await redisOperationsService.healthCheck()
    
    res.json({
      status: 'healthy',
      services: {
        analytics: analyticsHealth,
        operations: operationsHealth
      },
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    res.status(500).json({
      status: 'unhealthy',
      error: error.message,
      timestamp: new Date().toISOString()
    })
  }
})
```

## 🚀 **Implementation Steps**

### **Step 1: Environment Setup**
```bash
# Install Redis Stack
docker-compose up -d redis

# Install RedisInsight for monitoring
# Access at http://localhost:8001
```

### **Step 2: Update Frontend Services**
```javascript
// Update package.json dependencies
{
  "redis": "^4.6.0",
  "ioredis": "^5.3.0"
}

// Install dependencies
npm install redis ioredis
```

### **Step 3: Backend API Integration**
```python
# Create Redis API endpoints
@app.get("/api/analytics/page-views")
async def get_page_views():
    return await redis_analytics_service.get_page_views_data()

@app.get("/api/operations/system-metrics")
async def get_system_metrics():
    return await redis_operations_service.get_system_metrics()
```

### **Step 4: Data Migration**
```python
# Migrate existing data to Redis
def migrate_movie_data():
    movies = get_existing_movies()
    for movie in movies:
        redis_search_service.index_document(movie.id, movie.data)
```

### **Step 5: Testing & Validation**
```javascript
// Test analytics tracking
await redisAnalyticsService.trackPageView('Home', 'United States')
const data = await redisAnalyticsService.getPageViewsData()
console.log('Page views:', data)

// Test operations monitoring
const health = await redisOperationsService.healthCheck()
console.log('Operations health:', health)
```

## 📊 **Expected Benefits**

### **Performance Improvements**
- **Search Response Time**: < 50ms (from current ~200ms)
- **Analytics Data**: Real-time updates
- **Operations Monitoring**: Sub-second metrics collection

### **Scalability**
- **Concurrent Users**: Support 1000+ simultaneous users
- **Data Volume**: Handle millions of movies and analytics events
- **Memory Usage**: Optimized with TTL and compression

### **Reliability**
- **Data Persistence**: RDB + AOF backup
- **Health Monitoring**: Automated alerts and recovery
- **Error Handling**: Graceful degradation

## 🔧 **Configuration Files**

### **Redis Configuration**
```redis
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec
```

### **Environment Variables**
```bash
# .env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_password
REDIS_DB=0
REDISEARCH_INDEX_NAME=movies_index
REDISEARCH_PREFIX=movie:
```

## 📋 **Monitoring Dashboard**

### **RedisInsight Integration**
- **Real-time monitoring** of Redis performance
- **Memory usage** and key distribution
- **Query analysis** and optimization
- **Alert configuration** and management

### **Custom Operations Dashboard**
- **System metrics** visualization
- **Performance trends** analysis
- **Alert management** interface
- **Configuration management** panel

This implementation plan provides a comprehensive roadmap for integrating Redis across all three domains while maintaining performance, scalability, and reliability.
