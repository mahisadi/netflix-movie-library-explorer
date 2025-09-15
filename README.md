# Netflix Movie Library Explorer

A comprehensive movie discovery and management platform that provides advanced search capabilities, content curation tools, and analytics insights for movie enthusiasts and content managers.

## Overview

The Netflix Movie Library Explorer is a full-stack application that combines modern web technologies with powerful search capabilities to create an intuitive movie browsing and management experience. The platform features a sophisticated search engine, real-time analytics, and seamless integration with Google Drive for data storage.

## Key Features

### Search & Discovery
- **Advanced Search**: Full-text search across movie titles, directors, plots, and metadata
- **Faceted Filtering**: Filter by genre, year, rating, country, and language
- **Smart Suggestions**: RedisSearch-powered relevance scoring and suggestions
- **Pagination**: Efficient handling of large movie collections

### Content Management
- **Movie Library**: Comprehensive database of 250+ movies with detailed metadata
- **CRUD Operations**: Create, read, update, and delete movie records
- **Bulk Operations**: Efficient batch processing for large datasets
- **Data Validation**: Robust data integrity and validation

### Analytics & Insights
- **Dashboard Statistics**: Real-time metrics on movie collections
- **Genre Analysis**: Distribution and trending analysis by genre
- **Yearly Trends**: Movie release patterns and popularity over time
- **User Analytics**: Page views, search patterns, and user behavior tracking

### Data Integration
- **Google Drive Integration**: Seamless data storage and retrieval from Google Drive
- **OAuth2.0 Authentication**: Secure access to Google Drive APIs
- **Automated Ingestion**: Batch processing of movie data from JSON files
- **Data Synchronization**: Real-time sync between Google Drive and local cache

## Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **GraphQL**: Flexible API query language with Strawberry GraphQL
- **Redis**: In-memory data store with RedisSearch for full-text search
- **RedisTimeSeries**: Time-series data for analytics
- **Google Drive API**: Cloud storage integration

### Frontend
- **Vue.js 3**: Progressive JavaScript framework
- **Vite**: Fast build tool and development server
- **Pinia**: State management for Vue applications
- **Chart.js**: Data visualization and analytics charts
- **Tailwind CSS**: Utility-first CSS framework

### Infrastructure
- **Docker**: Containerized Redis Stack deployment
- **Python Virtual Environment**: Isolated dependency management
- **Node.js**: JavaScript runtime for frontend development

## Architecture

### Data Flow
1. **Data Ingestion**: Movies are stored in Google Drive as JSON files in nested folder structures
2. **Processing**: Connector service processes and cleanses data from Google Drive
3. **Indexing**: RedisSearch creates searchable indexes with full-text capabilities
4. **API Layer**: FastAPI serves GraphQL endpoints for data access
5. **Frontend**: Vue.js application consumes APIs and provides user interface

### Database Design
- **Redis DB 0**: RedisSearch for movie data and search indexes
- **Redis DB 1**: App Insights for user analytics and metrics
- **Schema**: Optimized for search performance with sortable fields

## Project Structure

```
netflix-movie-library-explorer/
├── READ_ME.md                           # Project overview
├── LOCAL_RUN_BOOK.md                    # Detailed setup guide
├── requirements.txt                     # Python dependencies
├── docker-compose.yml                   # Redis Stack configuration
├── netflix-movie-library-connector/     # Data ingestion service
│   ├── connectors/                      # Google Drive connector
│   ├── services/                        # Redis and Google Drive services
│   └── utils/                          # Configuration and utilities
├── netflix-movie-library-service/       # FastAPI backend
│   ├── api/                            # GraphQL API implementation
│   ├── services/                       # Business logic services
│   └── storage/                        # Logs and data storage
├── netflix-movie-library-ui/           # Vue.js frontend
│   ├── src/                            # Source code
│   │   ├── components/                 # Reusable Vue components
│   │   ├── views/                      # Page components
│   │   ├── stores/                     # Pinia state management
│   │   └── services/                   # API service layer
│   └── public/                         # Static assets
└── local_infrastructure/               # Setup scripts and sample data
    ├── sample_data.json                # Movie database
    └── setup scripts                   # Redis and system setup
```

## Getting Started

### Quick Start
1. **Clone the repository**
2. **Follow the setup guide**: See [LOCAL_RUN_BOOK.md](LOCAL_RUN_BOOK.md) for detailed instructions
3. **Start services**: Redis, API, and UI services
4. **Access the application**: Visit http://localhost:3000

### Prerequisites
- Python 3.8+
- Node.js 16+
- Docker and Docker Compose
- Google Drive API credentials

## API Documentation

### GraphQL Endpoint
- **URL**: `http://localhost:8000/graphql/`
- **Method**: POST
- **Content-Type**: `application/json`

### Key Queries
- `advancedSearchMovies`: Search and filter movies with pagination
- `getDashboardStats`: Retrieve analytics and statistics
- Support for complex filtering by genre, year, rating, and more

For detailed API documentation with sample requests and responses, see the [GraphQL API Documentation](LOCAL_RUN_BOOK.md#13-graphql-api-documentation-for-technical-employees) section in LOCAL_RUN_BOOK.md.

## Features in Detail

### Search Capabilities
- **Text Search**: Search across movie titles, directors, plots, and cast
- **Field-Specific Search**: Target specific fields using RedisSearch syntax
- **Range Queries**: Filter by year ranges, rating ranges, etc.
- **Combined Filters**: Multiple criteria in single queries
- **Sorting**: Sort by relevance, year, rating, or timestamps

### Data Management
- **Automated Ingestion**: Batch processing from Google Drive
- **Data Cleansing**: Automatic genre extraction and data normalization
- **Duplicate Handling**: Smart duplicate detection and resolution
- **Version Control**: Track data changes and updates

### User Experience
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Real-time Updates**: Live data synchronization
- **Intuitive Navigation**: Clear information architecture
- **Performance Optimized**: Fast loading and smooth interactions

## Development

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Standards
- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use ESLint configuration
- **Vue.js**: Follow Vue.js style guide
- **Documentation**: Update relevant documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For setup issues, feature requests, or bug reports:
1. Check the [LOCAL_RUN_BOOK.md](LOCAL_RUN_BOOK.md) troubleshooting section
2. Review service logs for error details
3. Verify all prerequisites are met
4. Ensure all services are running correctly

---

**Version**: 1.0.0  
**Last Updated**: September 2025  
**Maintainer**: Netflix Movie Library Explorer Team
