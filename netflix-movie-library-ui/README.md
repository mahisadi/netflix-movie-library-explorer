# Movie Library Explorer

A modern Vue.js 3 application for exploring and searching through movie collections with powerful filtering and search capabilities.

## Features

- 🔍 **Advanced Search**: Full-text search across movie titles, actors, directors, and plots
- 🎯 **Smart Filtering**: Filter by genre, subgenre, year range, rating, language, and country
- 📊 **Real-time Stats**: View collection statistics and search performance metrics
- 🎨 **Modern UI**: Clean, responsive design with smooth animations
- ⚡ **Fast Performance**: Optimized with Vue.js 3 Composition API and Pinia state management
- 🔗 **GraphQL API**: Type-safe API integration with our backend service

## Technology Stack

- **Frontend**: Vue.js 3 with Composition API
- **State Management**: Pinia
- **Build Tool**: Vite
- **API**: GraphQL with graphql-request
- **Styling**: CSS3 with modern features
- **Backend**: FastAPI + GraphQL + RedisSearch

## Project Structure

```
movie-library-explorer/
├── src/
│   ├── components/          # Vue components with nmle- prefix
│   │   ├── NmleHeader.vue
│   │   ├── NmleFooter.vue
│   │   ├── NmleSearchBar.vue
│   │   └── NmleMovieResults.vue
│   ├── stores/              # Pinia stores
│   │   └── searchStore.js
│   ├── api/                 # API service layer
│   │   └── movieApi.js
│   ├── assets/              # Static assets
│   ├── App.vue              # Main app component
│   ├── main.js              # App entry point
│   └── style.css            # Global styles
├── public/                  # Public assets
├── index.html               # HTML template
├── vite.config.js           # Vite configuration
└── package.json             # Dependencies and scripts
```

## Getting Started

### Prerequisites

- Node.js 18+ (recommended: 20+)
- npm or yarn
- Backend API running on http://localhost:8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to http://localhost:3000

### Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## API Integration

The application connects to our GraphQL API service layer running on `http://localhost:8000`. Make sure the backend service is running before starting the frontend.

### Available GraphQL Operations

- `searchMovies` - Search movies with filters and pagination
- `getMovieById` - Get individual movie details
- `getFilterOptions` - Get available filter values
- `getSearchStats` - Get collection statistics
- `getSearchSuggestions` - Get search suggestions

## Component Architecture

### NmleHeader
- Application header with navigation
- Branding and main navigation links

### NmleFooter
- Application footer with information
- Technology stack and feature highlights

### NmleSearchBar
- Main search interface
- Advanced filtering options
- Sort and pagination controls

### NmleMovieResults
- Movie results display
- Grid layout with movie cards
- Pagination controls
- Loading and error states

## State Management

The application uses Pinia for state management with a centralized `searchStore` that handles:

- Search query and filters
- Movie results and pagination
- Loading and error states
- Filter options and statistics

## Styling

The application uses modern CSS with:
- CSS Grid and Flexbox for layouts
- CSS Custom Properties for theming
- Responsive design principles
- Smooth animations and transitions

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

### Code Organization

- Components follow the `nmle-` prefix convention
- All components use Vue 3 Composition API
- State management is centralized in Pinia stores
- API calls are abstracted in service modules

## Contributing

1. Follow the existing code style and naming conventions
2. Use the `nmle-` prefix for all components
3. Write clean, maintainable code
4. Test your changes thoroughly

## License

This project is part of the Enterprise Search Connectors suite.
