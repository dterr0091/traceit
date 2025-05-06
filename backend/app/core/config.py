import os
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Server settings
    ENV: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Auth
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str
    REDIS_TTL_DAYS: int = 30

    # External APIs
    OPENAI_API_KEY: str
    PERPLEXITY_API_KEY: str
    BRAVE_SEARCH_API_KEY: str = ""
    TINEYE_API_KEY: str = ""
    ACRCLOUD_ACCESS_KEY: str = ""
    ACRCLOUD_SECRET_KEY: str = ""
    DIFFBOT_API_KEY: str = ""

    # Storage
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET_NAME: str = "traceit-files"
    AWS_REGION: str = "us-west-2"

    # GPU Services
    RUNPOD_API_KEY: str = ""

    # Graph Database
    NEO4J_URI: str = ""
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = ""

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID_BASIC: str = ""
    STRIPE_PRICE_ID_PRO: str = ""

    # Notifications
    EMAIL_FROM: str = "noreply@traceit.app"
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # Cost Limits
    MAX_FREE_TIER_CREDITS: int = 50
    DEFAULT_PAID_TIER_CREDITS: int = 500
    GPU_BATCH_SIZE: int = 3


settings = Settings() 