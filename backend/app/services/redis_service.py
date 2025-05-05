import json
import redis
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class RedisService:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = redis.from_url(self.redis_url)
        
    def set_cache(self, key, value, ttl_days=30):
        """
        Store value in Redis cache with TTL
        
        Args:
            key: Cache key (typically content hash)
            value: Value to store (will be JSON serialized)
            ttl_days: Time to live in days
        """
        # Serialize dict/list to JSON string
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
            
        # Set with TTL
        self.redis_client.set(key, value, ex=timedelta(days=ttl_days).total_seconds())
        
    def get_cache(self, key):
        """
        Retrieve value from Redis cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        value = self.redis_client.get(key)
        
        # Return None if key doesn't exist
        if value is None:
            return None
            
        # Try to parse as JSON
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            # Return as-is if not JSON
            return value
            
    def delete_cache(self, key):
        """Delete cache entry"""
        self.redis_client.delete(key)
        
    def exists(self, key):
        """Check if key exists in cache"""
        return self.redis_client.exists(key) > 0

# Initialize singleton
redis_service = RedisService() 