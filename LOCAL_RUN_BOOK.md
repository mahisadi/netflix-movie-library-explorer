# Netflix Movie Library Explorer - Local Run Book

This document provides step-by-step instructions for setting up and running the Netflix Movie Library Explorer application locally.

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Docker and Docker Compose
- Google Drive API credentials

## 1. Google Drive API Setup

### 1.1 Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable the Google Drive API

### 1.2 Create OAuth2.0 Credentials
1. Navigate to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Desktop application" as application type
4. Name your OAuth client (e.g., "Netflix Movie Library Explorer")
5. Click "Create" and download the JSON file
6. Rename the downloaded file to `credentials.json` and place it in the project root

### 1.3 Configure OAuth2.0 Consent Screen
1. Navigate to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type and click "Create"
3. Fill in the required fields:
   - App name: "Netflix Movie Library Explorer"
   - User support email: Your email
   - Developer contact information: Your email
4. Add scopes:
   - `https://www.googleapis.com/auth/drive.readonly`
   - `https://www.googleapis.com/auth/drive.file`
5. Add test users (your Google account email)
6. Save and continue through all steps

### 1.4 First-Time Authentication Setup
1. Run the authentication command to generate token:
```bash
cd netflix-movie-library-connector
python -c "
from services.google_drive_service import GoogleDriveService
service = GoogleDriveService()
if not service.is_authenticated():
    print('Please complete OAuth2.0 authentication in your browser')
    service._authenticate_oauth2()
else:
    print('Already authenticated')
"
```

2. This will open your browser for OAuth2.0 consent
3. Grant permissions to the application
4. The token will be automatically saved for future use

### 1.5 Configure Google Drive Folder
1. Create a folder in your Google Drive for the movie data
2. Note the folder ID from the URL (e.g., `1Z-Bqt69UgrGkwo0ArjHaNrA7uUmUm2r6`)
3. Update the folder ID in `netflix-movie-library-connector/utils/config.py`:
```python
GOOGLE_DRIVE_FOLDER_NAME = "1Z-Bqt69UgrGkwo0ArjHaNrA7uUmUm2r6"  # Your folder ID
```

### 1.6 Token Management
- OAuth2.0 tokens are automatically saved in `token.json` in the project root
- Tokens expire after 1 hour and are automatically refreshed
- If authentication fails, delete `token.json` and re-run the authentication command
- Never commit `token.json` to version control (it's already in `.gitignore`)

## 2. Python Environment Setup

### 2.1 Create Virtual Environment
```bash
# Navigate to project root
cd /Users/mahiprimer/projects/netflix-movie-library-explorer

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### 2.2 Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt
```

## 3. Docker and Redis Setup

### 3.1 Start Redis Stack Container
```bash
# Start Redis Stack with Docker Compose
docker-compose up -d redis-stack

# Verify Redis is running
docker ps | grep redis
```

### 3.2 Verify Redis Connection
```bash
# Test Redis connection
docker exec -it redis-search redis-cli ping
# Should return: PONG
```

## 4. Mock Data Ingestion to Google Drive

### 4.1 Prepare Sample Data
The sample data is located in:
```
local_infrastructure/sample_data.json
```

### 4.2 Ingest Data to Google Drive
```bash
# Navigate to source data setup folder
cd netflix-movie-library-connector/source-data-setup

# Run the ingestion script
python ingest_sample_data_to_google_drive.py
```

This script will:
- Create nested folder structure in Google Drive
- Upload JSON files with random folder organization
- Organize movies by genre/subgenre/year structure

## 5. Data Fetching from Google Drive

### 5.1 Run the Connector
```bash
# Navigate to connector directory
cd netflix-movie-library-connector

# Run the connector to fetch data from Google Drive
python main.py google_drive --recreate-index
```

This command will:
- Connect to Google Drive
- Fetch all JSON files from the configured folder
- Process and cleanse the data
- Index all records into RedisSearch
- Create searchable index with proper schema

### 5.2 Verify Data Ingestion
```bash
# Check Redis document count
curl -s http://localhost:8000/health
```

Expected output should show 253+ documents in RedisSearch.

## 6. API Service Setup

### 6.1 Start the API Service
```bash
# Navigate to API service directory
cd netflix-movie-library-service

# Start the FastAPI service
python run_api_service.py
```

The API will be available at: `http://localhost:8000`

### 6.2 Verify API Health
```bash
# Check API health endpoint
curl http://localhost:8000/health

# Test GraphQL endpoint
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "query { advancedSearchMovies(search: { query: \"*\", page: 1, pageSize: 5 }) { movies { id title year } totalCount } }"}'
```

## 7. UI Service Setup

### 7.1 Install UI Dependencies
```bash
# Navigate to UI directory
cd netflix-movie-library-ui

# Install Node.js dependencies
npm install
```

### 7.2 Start the UI Service
```bash
# Start the development server
npm run dev
```

The UI will be available at: `http://localhost:3000`

## 8. Application URLs and Features

### 8.1 Home Page
- **URL**: `http://localhost:3000/home`
- **Description**: Main dashboard with movie statistics and "Movies by Year" section
- **Features**:
  - Search functionality
  - Dashboard statistics
  - Top movies by year
  - Genre distribution

### 8.2 Library Page
- **URL**: `http://localhost:3000/app/library`
- **Description**: Movie content curation and management
- **Features**:
  - Browse all movies
  - Advanced filtering by genre, year, rating
  - Sorting capabilities
  - Pagination
  - CRUD operations for movie records

### 8.3 Insights Page
- **URL**: `http://localhost:3000/app/insights`
- **Description**: Metrics dashboard and analytics
- **Features**:
  - Page view analytics
  - Search activity tracking
  - User country statistics
  - Real-time metrics visualization
- **Note**: Some features still in development

## 9. Troubleshooting

### 9.1 Common Issues

**Redis Connection Failed**
```bash
# Restart Redis container
docker-compose restart redis-stack

# Check Redis logs
docker logs redis-search
```

**Google Drive Authentication Error**
- Verify `credentials.json` is in project root
- Check OAuth2.0 consent screen is properly configured
- Ensure Google Drive API is enabled
- Re-run authentication command if token expires:
```bash
cd netflix-movie-library-connector
python -c "
from services.google_drive_service import GoogleDriveService
service = GoogleDriveService()
service._authenticate_oauth2()
"
```
- Verify you're added as a test user in OAuth consent screen

**API Service Not Starting**
```bash
# Check if port 8000 is available
lsof -i :8000

# Kill process if needed
kill -9 <PID>
```

**UI Not Loading**
```bash
# Check if port 3000 is available
lsof -i :3000

# Clear npm cache
npm cache clean --force
```

### 9.2 Data Issues

**No Movies Showing**
```bash
# Re-run the connector
cd netflix-movie-library-connector
python main.py google_drive --recreate-index
```

**Search Not Working**
```bash
# Check Redis index
docker exec -it redis-search redis-cli FT.INFO movie_library
```

## 10. Development Workflow

### 10.1 Making Changes
1. Make code changes
2. Restart affected services
3. Test functionality
4. Check logs for errors

### 10.2 Adding New Movies
1. Add JSON files to Google Drive folder
2. Run connector: `python main.py google_drive`
3. Verify data in UI

### 10.3 Updating Configuration
- Update `netflix-movie-library-connector/utils/config.py` for connector settings
- Update `netflix-movie-library-service/api/config.py` for API settings
- Restart services after configuration changes

## 11. Service Management

### 11.1 Starting All Services
```bash
# Terminal 1: Redis
docker-compose up -d redis-stack

# Terminal 2: API
cd netflix-movie-library-service && python run_api_service.py

# Terminal 3: UI
cd netflix-movie-library-ui && npm run dev
```

### 11.2 Stopping Services
```bash
# Stop UI (Ctrl+C in terminal)
# Stop API (Ctrl+C in terminal)
# Stop Redis
docker-compose down
```

## 12. File Structure

```
netflix-movie-library-explorer/
├── LOCAL_RUN_BOOK.md                    # This file
├── requirements.txt                      # Python dependencies
├── docker-compose.yml                   # Docker configuration
├── credentials.json                     # Google Drive API credentials
├── netflix-movie-library-connector/    # Data ingestion service
├── netflix-movie-library-service/       # FastAPI backend
├── netflix-movie-library-ui/            # Vue.js frontend
└── local_infrastructure/                # Setup and sample data
```

## 13. GraphQL API Documentation (For Technical Employees)

### 13.1 API Endpoint
- **GraphQL URL**: `http://localhost:8000/graphql/`
- **Method**: POST
- **Content-Type**: `application/json`

### 13.2 Available Queries

#### 13.2.1 Search Movies by Director Name
**Purpose**: Search for movies by director name using text search across all fields
**Query**: `advancedSearchMovies`

**Sample Request**:
```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query SearchMovies($search: AdvancedSearchInput!) { advancedSearchMovies(search: $search) { movies { id title year director imdbRating genre } totalCount } }",
    "variables": {
      "search": {
        "query": "Nolan",
        "page": 1,
        "pageSize": 2
      }
    }
  }'
```

**Sample Response**:
```json
{
  "data": {
    "advancedSearchMovies": {
      "movies": [
        {
          "id": "movie:1c13vVyhekcmnJAWLz5yKCxqxaykOAhdm",
          "title": "Oppenheimer",
          "year": 2023,
          "director": "Christopher Nolan",
          "imdbRating": 8.5,
          "genre": "Biographical"
        },
        {
          "id": "movie:1w_rrkKfv-B3IaaZK7M7egr3pHbL3XzAq",
          "title": "Inception",
          "year": 2010,
          "director": "Christopher Nolan",
          "imdbRating": 8.8,
          "genre": "Thriller"
        }
      ],
      "totalCount": 5
    }
  }
}
```

#### 13.2.2 Dashboard Statistics
**Query**: `getDashboardStats`

**Sample Request**:
```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query GetDashboardStats($page: Int, $pageSize: Int, $sortField: String, $sortDirection: String) { getDashboardStats(page: $page, pageSize: $pageSize, sortField: $sortField, sortDirection: $sortDirection) { totalMovies totalGenres top5Genres yearlyStats { year movieCount topMovies { title rating } genreStats { genre count } } yearlyPagination { page pageSize totalPages totalCount hasNext hasPrevious } } }",
    "variables": {
      "page": 1,
      "pageSize": 5,
      "sortField": "year",
      "sortDirection": "desc"
    }
  }'
```

**Sample Response**:
```json
{
  "data": {
    "getDashboardStats": {
      "totalMovies": 253,
      "totalGenres": 15,
      "top5Genres": [
        {"genre": "Drama", "count": 45},
        {"genre": "Action", "count": 38},
        {"genre": "Thriller", "count": 32},
        {"genre": "Comedy", "count": 28},
        {"genre": "Sci-Fi", "count": 25}
      ],
      "yearlyStats": [
        {
          "year": 2023,
          "movieCount": 12,
          "topMovies": [
            {"title": "Oppenheimer", "rating": 8.5},
            {"title": "Spider-Man: Across the Spider-Verse", "rating": 8.6},
            {"title": "Guardians of the Galaxy Vol. 3", "rating": 8.0}
          ],
          "genreStats": [
            {"genre": "Biographical", "count": 3},
            {"genre": "Action", "count": 4},
            {"genre": "Animation", "count": 2}
          ]
        },
        {
          "year": 2022,
          "movieCount": 18,
          "topMovies": [
            {"title": "Top Gun: Maverick", "rating": 8.3},
            {"title": "The Batman", "rating": 7.8},
            {"title": "Everything Everywhere All at Once", "rating": 8.1}
          ],
          "genreStats": [
            {"genre": "Action", "count": 6},
            {"genre": "Drama", "count": 5},
            {"genre": "Sci-Fi", "count": 4}
          ]
        }
      ],
      "yearlyPagination": {
        "page": 1,
        "pageSize": 5,
        "totalPages": 12,
        "totalCount": 60,
        "hasNext": true,
        "hasPrevious": false
      }
    }
  }
}
```

#### 13.2.3 Filter Movies by Genre
**Purpose**: Filter movies by specific genre using RedisSearch field syntax
**Query**: `advancedSearchMovies`

**Sample Request**:
```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query SearchByGenre { advancedSearchMovies(search: { query: \"@genre:Sci-Fi\", page: 1, pageSize: 2 }) { movies { id title year director imdbRating genre subgenre } totalCount } }"
  }'
```

**Sample Response**:
```json
{
  "data": {
    "advancedSearchMovies": {
      "movies": [
        {
          "id": "movie:123lRuc1R_qcbbIITlSxEaNgNqURm1nFt",
          "title": "Blade Runner 2049",
          "year": 2017,
          "director": "Denis Villeneuve",
          "imdbRating": 8.0,
          "genre": "Sci-Fi",
          "subgenre": "Cyberpunk"
        },
        {
          "id": "movie:1w_rrkKfv-B3IaaZK7M7egr3pHbL3XzAq",
          "title": "Inception",
          "year": 2010,
          "director": "Christopher Nolan",
          "imdbRating": 8.8,
          "genre": "Sci-Fi",
          "subgenre": "Sci-Fi Thriller"
        }
      ],
      "totalCount": 25
    }
  }
}
```

#### 13.2.4 Filter Movies by Minimum Rating
**Purpose**: Find movies with IMDB rating above a specific threshold
**Query**: `advancedSearchMovies`

**Sample Request**:
```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query SearchByRating { advancedSearchMovies(search: { query: \"@imdbRating:[8.5 10.0]\", page: 1, pageSize: 2 }) { movies { id title year director imdbRating genre } totalCount } }"
  }'
```

**Sample Response**:
```json
{
  "data": {
    "advancedSearchMovies": {
      "movies": [
        {
          "id": "movie:1c39nOsmEoLjo2sC4We0g_1rB9wpjYLTh",
          "title": "The Dark Knight",
          "year": 2008,
          "director": "Christopher Nolan",
          "imdbRating": 9.0,
          "genre": "Action"
        },
        {
          "id": "movie:1w_rrkKfv-B3IaaZK7M7egr3pHbL3XzAq",
          "title": "Inception",
          "year": 2010,
          "director": "Christopher Nolan",
          "imdbRating": 8.8,
          "genre": "Sci-Fi"
        }
      ],
      "totalCount": 12
    }
  }
}
```

#### 13.2.5 Filter Movies by Year Range
**Purpose**: Find movies released within a specific year range
**Query**: `advancedSearchMovies`

**Sample Request**:
```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query SearchByYear { advancedSearchMovies(search: { query: \"@year:[2020 2023]\", page: 1, pageSize: 2 }) { movies { id title year director imdbRating genre } totalCount } }"
  }'
```

**Sample Response**:
```json
{
  "data": {
    "advancedSearchMovies": {
      "movies": [
        {
          "id": "movie:1c13vVyhekcmnJAWLz5yKCxqxaykOAhdm",
          "title": "Oppenheimer",
          "year": 2023,
          "director": "Christopher Nolan",
          "imdbRating": 8.5,
          "genre": "Biographical"
        },
        {
          "id": "movie:1zE20o_EvrQKFr-GOxl20BPSmKxBY080E",
          "title": "Parasite",
          "year": 2019,
          "director": "Bong Joon Ho",
          "imdbRating": 8.6,
          "genre": "Thriller"
        }
      ],
      "totalCount": 18
    }
  }
}
```

### 13.3 Input Types

#### 13.3.1 AdvancedSearchInput
```graphql
input AdvancedSearchInput {
  query: String!                    # Search query (supports RedisSearch syntax)
  page: Int = 1                     # Page number (1-based)
  pageSize: Int = 20                # Items per page
  maxPageSize: Int = 1000          # Maximum allowed page size
  sortField: String = "relevance"   # Sort field: "year", "imdbRating", "modified_timestamp", "relevance"
  sortDirection: String = "desc"    # Sort direction: "asc" or "desc"
}
```

#### 13.3.2 Supported Search Syntax
- **Basic text search**: `"Nolan"` - searches in title, director, plot
- **Field-specific search**: `"@title:Inception"` - searches only in title field
- **Genre search**: `"@genre:Sci-Fi"` - searches specific genre
- **Year range**: `"@year:[2010 2020]"` - movies between 2010-2020
- **Rating filter**: `"@imdbRating:[8.0 10.0]"` - movies with rating 8.0+
- **Combined queries**: `"@genre:Action @year:[2015 2023]"` - Action movies from 2015-2023

### 13.4 Response Types

#### 13.4 Movie Type
```graphql
type Movie {
  id: String!              # Unique movie identifier
  title: String!          # Movie title
  year: Int!              # Release year
  director: String!        # Director name
  imdbRating: Float!      # IMDB rating (0.0-10.0)
  genre: String!          # Primary genre
  subgenre: String!       # Sub-genre
  stars: [String!]!       # List of main actors
  country: String!        # Production countries
  language: String!        # Primary language
  moviePlot: String!      # Movie synopsis
  awards: [String!]!      # Awards and nominations
  createdTimestamp: Int!  # Unix timestamp when created
  updatedTimestamp: Int!  # Unix timestamp when last updated
}
```

### 13.5 Error Handling

**Sample Error Response**:
```json
{
  "data": null,
  "errors": [
    {
      "message": "Cannot query field 'invalidField' on type 'Movie'",
      "locations": [{"line": 1, "column": 45}],
      "extensions": {
        "code": "GRAPHQL_VALIDATION_FAILED"
      }
    }
  ]
}
```

### 13.6 Performance Considerations

- **Pagination**: Always use pagination for large result sets
- **Field Selection**: Only request fields you need to reduce payload size
- **Caching**: Responses are cached for 5 minutes
- **Rate Limiting**: No rate limits currently implemented
- **Indexing**: All text fields are indexed for fast search

### 13.7 Testing the API

**Health Check**:
```bash
curl http://localhost:8000/health
```

**GraphQL Playground**: Visit `http://localhost:8000/docs` for interactive GraphQL playground

## 14. Support

For issues or questions:
1. Check the troubleshooting section
2. Review service logs
3. Verify all prerequisites are met
4. Ensure all services are running correctly

---

**Last Updated**: September 2025
**Version**: 1.0.0
