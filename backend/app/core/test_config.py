import os
from dotenv import load_dotenv

# Load test environment variables
load_dotenv(".env.test", override=True)

# Test database configuration - uses SQLite in-memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Test configuration settings
TEST_CONFIG = {
    "TESTING": True,
    "REDIS_URL": os.getenv("REDIS_URL", "redis://localhost:6379/1"),
    "JWT_SECRET_KEY": "test_secret_key",
    "JWT_ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
    "PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY", ""),
    "BRAVE_API_KEY": os.getenv("BRAVE_API_KEY", ""),
    "TINEYE_API_KEY": os.getenv("TINEYE_API_KEY", ""),
}

# Set environment variables for testing
for key, value in TEST_CONFIG.items():
    os.environ[key] = str(value) 