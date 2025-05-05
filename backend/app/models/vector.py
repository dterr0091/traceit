from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from .db import Base

class ContentEmbedding(Base):
    __tablename__ = "content_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    content_hash = Column(String, unique=True, index=True)  # SHA-256 hash for text, perceptual hash for media
    content_type = Column(String)  # text, image, audio, video
    embedding = Column(Vector(1536))  # Dimension depends on the embedding model used
    raw_text = Column(Text, nullable=True)  # Optional storage of the text for text content
    source_url = Column(String, nullable=True)
    channel_id = Column(String, nullable=True)  # For identifying content creator/channel
    timestamp = Column(DateTime(timezone=True), nullable=True)  # Original publication timestamp
    engagement_score = Column(Float, default=0.0)  # Popularity/engagement metric
    metadata = Column(JSONB, nullable=True)  # Additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
class CacheEntry(Base):
    __tablename__ = "cache_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    query_hash = Column(String, index=True)  # Hash of the query for cache lookup
    results = Column(JSONB)  # Cached search results
    perplexity_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))  # TTL for cache entries 