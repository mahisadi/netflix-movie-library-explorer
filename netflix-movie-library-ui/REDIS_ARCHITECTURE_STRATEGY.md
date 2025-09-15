# Redis Architecture Strategy for Search, Insights & Operations

## 🎯 **Overview**
Comprehensive Redis data architecture to support Search, Insights, and Operations with real-time capabilities, analytics, and monitoring.

## 📊 **Current State Analysis**

### ✅ **What's Working**
- Redis Stack deployed with RedisSearch
- Basic movie search functionality
- Simple key-value caching
- Docker Compose setup

### ❌ **What's Missing**
- Structured analytics data storage
- Real-time metrics collection
- Operations monitoring layer
- Data retention policies
- Performance optimization

## 🏗️ **Proposed Redis Architecture**

### **Database Separation Strategy**
```
DB 0: Search Data (Movies, Content)
DB 1: Analytics & Insights
DB 2: Operations & Monitoring
DB 3: Cache & Sessions
DB 4: Metrics & Counters
DB 5: Logs & Events
```

## 🔍 **1. Search Data Layer (DB 0)**

### **RedisSearch Indexes**
```python
# Movies Index
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

# Content Index (for other content types)
FT.CREATE content_index ON HASH PREFIX 1 content: SCHEMA
    title TEXT SORTABLE
    type TAG SORTABLE
    category TAG SORTABLE
    tags TAG
    content TEXT
    metadata JSON
    created_at NUMERIC SORTABLE
```

### **Search Optimization**
- **Faceted Search**: Genre, year, rating filters
- **Fuzzy Matching**: Typo tolerance
- **Auto-complete**: Search suggestions
- **Relevance Scoring**: Custom scoring algorithms

## 📈 **2. Analytics & Insights Layer (DB 1)**

### **Data Structures**

#### **Time-Series Data**
```python
# User Activity Tracking
TS.CREATE user_activity:page_views 
    RETENTION 90d 
    LABELS type page_views

TS.CREATE user_activity:search_queries 
    RETENTION 30d 
    LABELS type search

TS.CREATE user_activity:country_distribution 
    RETENTION 180d 
    LABELS type geography

# Search Analytics
TS.CREATE search_analytics:query_frequency 
    RETENTION 30d 
    LABELS type frequency

TS.CREATE search_analytics:result_counts 
    RETENTION 30d 
    LABELS type results
```

#### **Hash Structures for Aggregated Data**
```python
# Page Views Aggregation
HSET page_views:daily:2024-01-15 
    home 45 
    library 32 
    insights 5

# Search Activities
HSET search_activities:daily:2024-01-15 
    inception 5 
    blade_runner 3 
    gone_girl 2

# User Countries
HSET user_countries:monthly:2024-01 
    "United States" 25 
    "Canada" 15 
    "United Kingdom" 12
```

#### **Sorted Sets for Rankings**
```python
# Top Search Terms
ZADD search_rankings:daily:2024-01-15 
    5 inception 
    3 blade_runner 
    2 gone_girl

# Top Countries
ZADD country_rankings:monthly:2024-01 
    25 "United States" 
    15 "Canada" 
    12 "United Kingdom"
```

### **Real-Time Analytics Pipeline**
```python
class AnalyticsPipeline:
    def track_page_view(self, page: str, user_country: str):
        # Increment counters
        self.redis.hincrby(f"page_views:daily:{today}", page, 1)
        self.redis.hincrby(f"user_countries:monthly:{month}", user_country, 1)
        
        # Add to time series
        self.redis.ts_add("user_activity:page_views", "*", 1, 
                         labels={"page": page, "country": user_country})
    
    def track_search(self, query: str, result_count: int):
        # Track search frequency
        self.redis.hincrby(f"search_activities:daily:{today}", query, 1)
        self.redis.zincrby(f"search_rankings:daily:{today}", 1, query)
        
        # Time series data
        self.redis.ts_add("user_activity:search_queries", "*", 1,
                         labels={"query": query, "results": result_count})
```

## ⚙️ **3. Operations & Monitoring Layer (DB 2)**

### **System Health Monitoring**
```python
# System Metrics
TS.CREATE system_metrics:cpu_usage 
    RETENTION 7d 
    LABELS type cpu

TS.CREATE system_metrics:memory_usage 
    RETENTION 7d 
    LABELS type memory

TS.CREATE system_metrics:redis_memory 
    RETENTION 7d 
    LABELS type redis

# Application Metrics
TS.CREATE app_metrics:response_time 
    RETENTION 3d 
    LABELS type performance

TS.CREATE app_metrics:error_rate 
    RETENTION 7d 
    LABELS type errors
```

### **Alerting System**
```python
# Alert Rules Storage
HSET alert_rules:system 
    cpu_threshold 80 
    memory_threshold 85 
    redis_threshold 90

HSET alert_rules:performance 
    response_time_threshold 2000 
    error_rate_threshold 5
```

### **Log Aggregation**
```python
# Structured Logs
LPUSH logs:application:2024-01-15 
    '{"level":"INFO","message":"Search completed","query":"inception","results":5,"timestamp":"2024-01-15T10:30:00Z"}'

LPUSH logs:errors:2024-01-15 
    '{"level":"ERROR","message":"Database connection failed","error":"Connection timeout","timestamp":"2024-01-15T10:35:00Z"}'
```

## 🚀 **4. Implementation Strategy**

### **Phase 1: Analytics Foundation (Week 1-2)**
1. **Set up Time-Series structures**
2. **Implement basic tracking functions**
3. **Create analytics aggregation jobs**
4. **Build Insights dashboard data layer**

### **Phase 2: Operations Monitoring (Week 3-4)**
1. **System metrics collection**
2. **Health check endpoints**
3. **Alerting system setup**
4. **Operations dashboard data**

### **Phase 3: Performance Optimization (Week 5-6)**
1. **Search performance tuning**
2. **Caching strategies**
3. **Data retention policies**
4. **Memory optimization**

## 📋 **Data Retention Policies**

### **Search Data**
- **Movies**: Permanent (with versioning)
- **Search Index**: Permanent
- **Search Cache**: 24 hours

### **Analytics Data**
- **Page Views**: 90 days
- **Search Queries**: 30 days
- **User Countries**: 180 days
- **Aggregated Stats**: 1 year

### **Operations Data**
- **System Metrics**: 7 days
- **Application Logs**: 30 days
- **Error Logs**: 90 days
- **Performance Data**: 14 days

## 🔧 **Redis Configuration**

### **Memory Optimization**
```redis
# Redis.conf optimizations
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000

# Time-series specific
TS.CREATE ... RETENTION 30d COMPRESSION COMPRESSED
```

### **Performance Tuning**
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

## 📊 **Monitoring & Alerting**

### **Key Metrics to Track**
1. **Search Performance**
   - Query response time
   - Index size
   - Cache hit ratio

2. **Analytics Accuracy**
   - Data freshness
   - Aggregation completeness
   - Time-series data integrity

3. **Operations Health**
   - Redis memory usage
   - Connection count
   - Error rates

### **Alerting Rules**
```python
# Example alerting logic
def check_system_health():
    cpu_usage = get_cpu_usage()
    memory_usage = get_memory_usage()
    
    if cpu_usage > 80:
        send_alert("High CPU usage", cpu_usage)
    
    if memory_usage > 85:
        send_alert("High memory usage", memory_usage)
```

## 🎯 **Benefits of This Architecture**

### **Performance**
- **Sub-millisecond** search responses
- **Real-time** analytics updates
- **Efficient** memory usage with TTL

### **Scalability**
- **Horizontal scaling** with Redis Cluster
- **Data partitioning** by database
- **Load balancing** capabilities

### **Reliability**
- **Data persistence** with RDB/AOF
- **Backup strategies** for critical data
- **Health monitoring** and alerting

### **Maintainability**
- **Clear separation** of concerns
- **Structured data** organization
- **Comprehensive monitoring**

## 🚀 **Next Steps**

1. **Review and approve** this architecture
2. **Set up Redis databases** with proper separation
3. **Implement analytics pipeline** for Insights
4. **Create operations monitoring** for Operations tab
5. **Optimize search performance** with RedisSearch
6. **Set up monitoring and alerting**

This architecture provides a solid foundation for scalable, performant, and maintainable data management across all three domains.
