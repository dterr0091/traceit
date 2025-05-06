# Trace Backend

Backend API service for Trace - a tool that identifies the earliest verifiable origin of text, image, audio, or video content.

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker and Docker Compose (optional)

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on the template:
```bash
cp .env.template .env
# Edit .env with your configuration
```

4. Start PostgreSQL and Redis (if not using Docker):
```bash
# Install PostgreSQL and Redis on your system
# Create a database named 'traceit'
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

### Docker Development

1. Create a `.env` file based on the template:
```bash
cp .env.template .env
# Edit .env with your configuration
```

2. Build and start the containers:
```bash
docker-compose up -d
```

3. Access the API at http://localhost:8000

## API Documentation

Once running, access the interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/           # API routes
│   │   └── v1/        # API version 1 endpoints
│   ├── core/          # Core application code
│   ├── db/            # Database connection and queries
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   └── utils/         # Utility functions
├── tests/             # Tests
├── .env               # Environment variables (create from .env.template)
├── .env.template      # Environment variables template
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker configuration
└── docker-compose.yml # Docker Compose configuration
```

## Credits System

- Light request (URL/text): 1 credit
- Heavy request (image/audio): 3 credits
- Video request: 8 credits (paid tiers only)

## External APIs Used

- OpenAI API
- Perplexity Sonar API
- Brave Search API
- TinEye API (for image searches)
- ACRCloud API (for audio fingerprinting)
- RunPod API (for GPU batch processing) 