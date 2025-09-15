# netflix-movie-library-service

This service provides a GraphQL API for searching and filtering movie data
stored in RedisSearch. It acts as a service layer between the UI and the
data layer (RedisSearch)


# Tech Stack
* FastAPI + GraphQL



# local run python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload