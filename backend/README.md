# Trace Backend

## Overview
Backend service for Trace - a platform that identifies the earliest verifiable origin of text, image, audio, or video content.

This implementation covers the first milestone of the project:
- Authentication system
- Credit metering
- pgvector search
- Redis cache
- Perplexity router

## Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL database with pgvector extension
- Redis server
- Perplexity API key

### Setup

1. Create a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`:
```
# PostgreSQL Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/traceit

# Auth
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_URL=redis://localhost:6379

# Perplexity API
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# Server
HOST=0.0.0.0
PORT=8000
```

4. Setup PostgreSQL with pgvector extension:
```sql 
CREATE DATABASE traceit;
CREATE EXTENSION IF NOT EXISTS vector;
```

5. Run the server:
```
python run.py
```

The API will be available at http://localhost:8000/ with documentation at http://localhost:8000/docs

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/token` - Login and get access token
- `GET /auth/me` - Get current user info

### Credits
- `GET /credits/balance` - Get credit balance
- `POST /credits/add` - Add credits
- `GET /credits/transactions` - Get transaction history
- `GET /credits/searches` - Get search history

### Search
- `POST /search/text` - Search for text origin
- `POST /search/url` - Search for URL content origin
- `GET /search/status/{job_id}` - Get search job status

## Architecture
- **Authentication**: JWT-based auth with password hashing
- **Database**: PostgreSQL with pgvector for vector similarity search
- **Caching**: Redis for caching Perplexity results and search results
- **API**: FastAPI for high-performance async API
- **Routing**: Smart router that uses local search first, falls back to Perplexity API when needed 