import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from ..models.vector import ContentEmbedding
import hashlib
from typing import List, Dict, Any, Optional
import json

class VectorService:
    @staticmethod
    def get_embedding(text: str) -> List[float]:
        """
        Get embedding for text (mock implementation)
        In a real implementation, this would call an embedding model API
        
        Args:
            text: The text to embed
            
        Returns:
            Embedding vector (1536 dimensions for OpenAI embeddings)
        """
        # This is a placeholder. In production, use a real embedding model
        # Like OpenAI's text-embedding-3-small or similar
        # For now, we'll create a random vector normalized to unit length
        rng = np.random.RandomState(int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32))
        embedding = rng.randn(1536)
        embedding = embedding / np.linalg.norm(embedding)
        return embedding.tolist()
    
    @staticmethod
    def compute_content_hash(content: str) -> str:
        """
        Compute SHA-256 hash for content
        
        Args:
            content: The content to hash
            
        Returns:
            SHA-256 hash as hex string
        """
        return hashlib.sha256(content.encode()).hexdigest()
    
    @staticmethod
    def store_embedding(
        db: Session, 
        content: str, 
        content_type: str,
        embedding: Optional[List[float]] = None,
        source_url: Optional[str] = None,
        channel_id: Optional[str] = None,
        timestamp = None,
        engagement_score: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ContentEmbedding:
        """
        Store content embedding in database
        
        Args:
            db: Database session
            content: Raw content
            content_type: Type of content (text, image, audio, video)
            embedding: Optional pre-computed embedding
            source_url: Source URL
            channel_id: Channel/creator ID
            timestamp: Publication timestamp
            engagement_score: Engagement score
            metadata: Additional metadata
            
        Returns:
            Created ContentEmbedding object
        """
        # Generate hash
        content_hash = VectorService.compute_content_hash(content)
        
        # Check if content already exists
        existing = db.query(ContentEmbedding).filter(ContentEmbedding.content_hash == content_hash).first()
        if existing:
            return existing
        
        # Generate embedding if not provided
        if embedding is None:
            embedding = VectorService.get_embedding(content)
        
        # Create new embedding
        content_embedding = ContentEmbedding(
            content_hash=content_hash,
            content_type=content_type,
            embedding=embedding,
            raw_text=content if content_type == "text" else None,
            source_url=source_url,
            channel_id=channel_id,
            timestamp=timestamp,
            engagement_score=engagement_score,
            metadata=metadata
        )
        
        db.add(content_embedding)
        db.commit()
        db.refresh(content_embedding)
        
        return content_embedding
    
    @staticmethod
    def search_similar_content(
        db: Session, 
        query: str, 
        limit: int = 5, 
        similarity_threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Search for similar content using vector similarity
        
        Args:
            db: Database session
            query: Search query
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of similar content with similarity scores
        """
        # Generate query embedding
        query_embedding = VectorService.get_embedding(query)
        
        # Perform vector search
        # pgvector provides the <-> operator for L2 distance and <=> for cosine distance
        # Lower value means more similar for L2, higher means more similar for cosine
        results = (
            db.query(
                ContentEmbedding,
                func.cos_similarity(ContentEmbedding.embedding, query_embedding).label("similarity")
            )
            .filter(func.cos_similarity(ContentEmbedding.embedding, query_embedding) >= similarity_threshold)
            .order_by(text("similarity DESC"))
            .limit(limit)
            .all()
        )
        
        # Format results
        formatted_results = []
        for content, similarity in results:
            formatted_results.append({
                "content_hash": content.content_hash,
                "content_type": content.content_type,
                "raw_text": content.raw_text,
                "source_url": content.source_url,
                "channel_id": content.channel_id,
                "timestamp": content.timestamp.isoformat() if content.timestamp else None,
                "engagement_score": content.engagement_score,
                "metadata": content.metadata,
                "similarity": float(similarity)
            })
            
        return formatted_results 