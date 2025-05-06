import logging
import hashlib
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from .brave_search_service import BraveSearchService
from .tineye_service import TinEyeService
from .redis_service import RedisService

logger = logging.getLogger(__name__)

class ImageSearchService:
    """Service that combines Brave Search and TinEye for reverse image search"""
    
    @staticmethod
    def compute_image_hash(image_data: bytes) -> str:
        """
        Compute SHA-256 hash of image data (to be replaced with perceptual hash)
        
        Args:
            image_data: Binary image data
            
        Returns:
            str: Hash of the image
        """
        # In a production system, this would be a perceptual hash
        # For now, we'll use SHA-256 for simplicity
        return hashlib.sha256(image_data).hexdigest()
    
    @staticmethod
    async def search_image(db: Session, image_data: bytes) -> Dict[str, Any]:
        """
        Perform reverse image search using Brave Search with TinEye fallback
        
        Args:
            db: Database session
            image_data: Binary image data
            
        Returns:
            Dict containing search results
        """
        # Compute image hash for caching and deduplication
        image_hash = ImageSearchService.compute_image_hash(image_data)
        
        # Check cache first
        cache_key = f"image_search:{image_hash}"
        cached_result = await RedisService.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for image {image_hash}")
            return cached_result
        
        # Start with Brave Search
        logger.info(f"Performing Brave Search for image {image_hash}")
        brave_results = await BraveSearchService.reverse_image_search(image_data)
        
        origins = BraveSearchService.extract_origins(brave_results)
        
        # TinEye fallback temporarily disabled
        # If Brave results aren't good enough, enqueue the image for TinEye batch processing
        # if not origins or len(origins) < 3 or max(origin.get("confidence", 0) for origin in origins) < 0.8:
        #     logger.info(f"Adding image {image_hash} to TinEye batch queue")
        #     TinEyeService.add_to_batch(image_data, image_hash)
        
        # Calculate confidence score based on number and quality of results
        confidence = 0.0
        if origins:
            # Get average confidence of top 3 results, weighted by position
            weights = [0.6, 0.3, 0.1]  # Top result gets 60% weight, second gets 30%, third gets 10%
            top_origins = origins[:3]
            confidence_sum = sum(
                weights[i] * origin.get("confidence", 0) 
                for i, origin in enumerate(top_origins)
            )
            confidence = confidence_sum / sum(weights[:len(top_origins)])
        
        # Prepare result
        result = {
            "query_hash": image_hash,
            "results": brave_results.get("results", []),
            "origins": origins,
            "confidence": confidence,
            "source": "brave_search"
        }
        
        # Cache result
        await RedisService.set(cache_key, result, expire_seconds=86400 * 30)  # 30 days TTL
        
        return result
    
    @staticmethod
    async def get_tineye_results(image_hash: str, batch_id: str) -> Dict[str, Any]:
        """
        Get TinEye results for a specific image
        
        Args:
            image_hash: Hash of the image
            batch_id: TinEye batch ID
            
        Returns:
            Dict containing TinEye results
        """
        # This would typically check a database to find the TinEye results for this image
        # For now, we'll just fetch the batch results
        batch_results = await TinEyeService.check_batch_results(batch_id)
        
        # Extract origins from TinEye results
        tineye_origins = TinEyeService.extract_origins(batch_results)
        
        # Prepare result
        result = {
            "query_hash": image_hash,
            "results": batch_results.get("matches", []),
            "origins": tineye_origins,
            "confidence": max(origin.get("confidence", 0) for origin in tineye_origins) if tineye_origins else 0.0,
            "source": "tineye"
        }
        
        # Update cache with TinEye results
        cache_key = f"image_search:{image_hash}"
        await RedisService.set(cache_key, result, expire_seconds=86400 * 90)  # 90 days TTL
        
        return result 