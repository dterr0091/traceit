from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # API Configuration
    API_VERSION: str = "v1"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings() 