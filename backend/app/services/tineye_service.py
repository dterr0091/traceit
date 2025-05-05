import os
import requests
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..utils.bloom_filter import BloomFilter

logger = logging.getLogger(__name__)

class TinEyeService:
    """Service for interacting with TinEye API for reverse image search"""
    
    TINEYE_API_KEY = os.getenv("TINEYE_API_KEY")
    TINEYE_API_URL = "https://api.tineye.com/rest/"
    TINEYE_BATCH_API_URL = "https://api.tineye.com/rest/search_batch/"
    
    # In-memory queue for batch processing
    _batch_queue = []
    _bloom_filter = None
    
    @classmethod
    def initialize_bloom_filter(cls):
        """Initialize Bloom filter for deduplication"""
        if cls._bloom_filter is None:
            # Initialize with capacity for ~10,000 items with 0.1% false positive rate
            cls._bloom_filter = BloomFilter(capacity=10000, error_rate=0.001)
    
    @classmethod
    def add_to_batch(cls, image_data: bytes, image_hash: str) -> bool:
        """
        Add an image to the batch queue for TinEye processing
        
        Args:
            image_data: Binary image data
            image_hash: Hash of the image for deduplication
            
        Returns:
            bool: True if added to queue, False if duplicate
        """
        cls.initialize_bloom_filter()
        
        # Check if this image hash is already in our filter
        if cls._bloom_filter.check(image_hash):
            logger.info(f"Skipping duplicate image with hash {image_hash}")
            return False
        
        # Add to bloom filter and batch queue
        cls._bloom_filter.add(image_hash)
        cls._batch_queue.append({
            "image_data": image_data,
            "image_hash": image_hash,
            "added_at": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Added image with hash {image_hash} to TinEye batch queue. Queue size: {len(cls._batch_queue)}")
        return True
    
    @classmethod
    async def process_batch(cls) -> Dict[str, Any]:
        """
        Process the current batch of images with TinEye
        Should be called hourly via a scheduled task
        
        Returns:
            Dict with processing results
        """
        if not cls.TINEYE_API_KEY:
            raise ValueError("TINEYE_API_KEY environment variable not set")
        
        if not cls._batch_queue:
            logger.info("TinEye batch queue is empty, nothing to process")
            return {"status": "empty", "processed": 0}
        
        # Take the current batch and reset the queue
        current_batch = cls._batch_queue.copy()
        cls._batch_queue = []
        
        logger.info(f"Processing TinEye batch with {len(current_batch)} images")
        
        try:
            # Prepare batch for TinEye API
            files = []
            for idx, item in enumerate(current_batch):
                files.append(
                    ('images[]', (f'image_{idx}.jpg', item["image_data"], 'image/jpeg'))
                )
            
            # Add authentication
            params = {
                "api_key": cls.TINEYE_API_KEY
            }
            
            # Submit batch to TinEye
            response = requests.post(
                cls.TINEYE_BATCH_API_URL,
                params=params,
                files=files
            )
            response.raise_for_status()
            
            batch_result = response.json()
            
            # Store batch results for later retrieval
            # In a real implementation, this would store in a database
            batch_id = batch_result.get("batch_id", "unknown")
            
            return {
                "status": "success",
                "processed": len(current_batch),
                "batch_id": batch_id,
                "results": batch_result
            }
            
        except Exception as e:
            logger.error(f"Error processing TinEye batch: {str(e)}")
            # Put items back in queue for retry
            cls._batch_queue.extend(current_batch)
            return {
                "status": "error",
                "error": str(e),
                "processed": 0
            }
    
    @staticmethod
    async def check_batch_results(batch_id: str) -> Dict[str, Any]:
        """
        Check the results of a TinEye batch
        
        Args:
            batch_id: The batch ID to check
            
        Returns:
            Dict with batch results
        """
        if not TinEyeService.TINEYE_API_KEY:
            raise ValueError("TINEYE_API_KEY environment variable not set")
        
        params = {
            "api_key": TinEyeService.TINEYE_API_KEY
        }
        
        try:
            response = requests.get(
                f"{TinEyeService.TINEYE_BATCH_API_URL}{batch_id}",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error checking TinEye batch results: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def extract_origins(tineye_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract origin information from TinEye results
        
        Args:
            tineye_results: Raw results from TinEye API
            
        Returns:
            List of origin objects with normalized structure
        """
        origins = []
        
        if "matches" not in tineye_results or not tineye_results["matches"]:
            return origins
        
        for match in tineye_results["matches"]:
            try:
                # Extract relevant information from TinEye match
                origin = {
                    "url": match.get("backlink", ""),
                    "title": match.get("domain", ""),  # TinEye often doesn't provide titles
                    "source": "tineye",
                    "timestamp": match.get("crawl_date", ""),
                    "similarity": float(match.get("score", 0)) / 100.0,  # Normalize to 0-1
                    "confidence": min(float(match.get("score", 0)) / 100.0, 1.0),
                    "metadata": {
                        "domain": match.get("domain", ""),
                        "width": match.get("width", 0),
                        "height": match.get("height", 0),
                        "image_url": match.get("image_url", "")
                    }
                }
                origins.append(origin)
            except Exception as e:
                logger.error(f"Error processing TinEye match: {str(e)}")
                continue
        
        # Sort by score (highest first)
        origins.sort(key=lambda x: x["similarity"], reverse=True)
        
        return origins[:10]  # Limit to top 10 results 