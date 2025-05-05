from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    # Perplexity API Configuration
    PERPLEXITY_API_KEY: str = os.getenv("PERPLEXITY_API_KEY", "")
    
    # API Configuration
    API_VERSION: str = "v1"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Validate API keys
settings = Settings()
print(f"API KEY!!! { settings.OPENAI_API_KEY}")
if not settings.OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required. Please set it in your .env file.")
if not settings.PERPLEXITY_API_KEY:
    raise ValueError("PERPLEXITY_API_KEY is required. Please set it in your .env file.") 