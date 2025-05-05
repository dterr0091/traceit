import math
import hashlib
from typing import List

class BloomFilter:
    """
    Simple Bloom filter implementation for image hash deduplication
    """
    
    def __init__(self, capacity: int = 10000, error_rate: float = 0.001):
        """
        Initialize a new Bloom filter
        
        Args:
            capacity: Expected number of elements to be added
            error_rate: Desired false positive rate
        """
        self.capacity = capacity
        self.error_rate = error_rate
        
        # Calculate optimal filter size and number of hash functions
        self.size = self._get_size(capacity, error_rate)
        self.hash_count = self._get_hash_count(self.size, capacity)
        
        # Initialize bit array
        self.bit_array = [False] * self.size
    
    def _get_size(self, n: int, p: float) -> int:
        """
        Calculate optimal bit array size
        
        Args:
            n: Capacity
            p: Error rate
            
        Returns:
            int: Optimal size in bits
        """
        m = -(n * math.log(p)) / (math.log(2) ** 2)
        return int(m)
    
    def _get_hash_count(self, m: int, n: int) -> int:
        """
        Calculate optimal number of hash functions
        
        Args:
            m: Filter size in bits
            n: Capacity
            
        Returns:
            int: Optimal number of hash functions
        """
        k = (m / n) * math.log(2)
        return int(k)
    
    def _get_hash_values(self, item: str) -> List[int]:
        """
        Generate hash values for an item
        
        Args:
            item: String to hash
            
        Returns:
            List of hash values
        """
        # Use different salts for different hash functions
        hash_values = []
        for i in range(self.hash_count):
            salt = f"salt_{i}"
            hash_input = f"{salt}_{item}"
            hash_hex = hashlib.md5(hash_input.encode()).hexdigest()
            hash_int = int(hash_hex, 16)
            hash_values.append(hash_int % self.size)
        
        return hash_values
    
    def add(self, item: str) -> None:
        """
        Add an item to the filter
        
        Args:
            item: String to add
        """
        for bit_position in self._get_hash_values(item):
            self.bit_array[bit_position] = True
    
    def check(self, item: str) -> bool:
        """
        Check if an item might be in the filter
        
        Args:
            item: String to check
            
        Returns:
            bool: True if the item might be in the filter, False if definitely not
        """
        for bit_position in self._get_hash_values(item):
            if not self.bit_array[bit_position]:
                return False
        return True 