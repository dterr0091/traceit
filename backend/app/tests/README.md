# Testing the Search Functionality

This directory contains tests for the search functionality of the Trace application.

## Setup for Testing

### 1. Database Configuration

By default, the tests use SQLite in-memory database. This is configured in `app/core/test_config.py`.

### 2. Environment Variables

Create a `.env.test` file in the backend directory with the following content:

```
# Test environment configuration
SQLALCHEMY_DATABASE_URL=sqlite:///:memory:
REDIS_URL=redis://localhost:6379/1
JWT_SECRET_KEY=test_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PERPLEXITY_API_KEY=test_perplexity_key
BRAVE_API_KEY=test_brave_key
TINEYE_API_KEY=test_tineye_key
TESTING=true
```

### 3. Fix Database Configuration

The main application uses a database configuration that requires a valid database URL. For testing, we need to modify this behavior.

Replace the content of `app/models/db.py` with the content from `app/models/db.py.fixed`. This version includes a fallback to SQLite in-memory database when no database URL is provided.

```
cp app/models/db.py.fixed app/models/db.py
```

## Running Tests

### Individual Tests

Run an individual test file using pytest:

```
pytest -xvs app/tests/test_text_search.py
```

### All Tests

Run all tests:

```
pytest -xvs app/tests/
```

## The Minimal Test

For a quick test of the search functionality without relying on the full application configuration, use the `minimal_test.py` script:

```
python minimal_test.py
```

This script sets up a minimal environment with SQLite in-memory database and tests the search flow.

## Test Files

- `test_text_search.py`: Tests the RouterService search functionality
- `test_db_config.py`: Tests the database configuration
- `test_search_endpoint.py`: Tests the search endpoints with FastAPI TestClient
- `conftest.py`: Pytest configuration with fixtures for database and client

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues, make sure the `SQLALCHEMY_DATABASE_URL` environment variable is set correctly. 

For local testing, you can use SQLite:

```
export SQLALCHEMY_DATABASE_URL=sqlite:///:memory:
```

### Redis Connection Issues

Tests that use Redis caching may fail if Redis is not available. Mock Redis or use a test Redis instance. 