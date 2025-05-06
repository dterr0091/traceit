import unittest
import asyncio
from unittest.mock import patch, MagicMock
import os
import sys

# Add the parent directory to sys.path to import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, app_dir)

# Remove the import we're not using
# from services.video_pipeline_service import VideoPipelineService

class MockLineageService:
    async def store_origin(self, **kwargs):
        return {"success": True}

class MockService:
    async def set(self, key, value, expire_seconds=None):
        return None
        
    async def get(self, key):
        return None
        
    async def extract_audio(self, path):
        return "temp_audio.mp3"
        
    async def get_video_metadata(self, path):
        return {"duration": 60, "has_audio": True}
        
    async def extract_keyframes(self, path, frame_positions=None):
        return ["frame1.jpg", "frame2.jpg", "frame3.jpg"]

# Simple mock for testing the _check_if_composite method
class TestCompositeChecker:
    def __init__(self):
        self.clip_similarity_threshold = 0.20
        
    async def _check_if_composite(self, audio_result, visual_result):
        """
        Determine if a video is a composite (audio and visuals from different sources).
        
        Args:
            audio_result: Audio processing result
            visual_result: Visual processing result
            
        Returns:
            True if the video is a composite, False otherwise
        """
        # If either component has no origin, it's not a confirmed composite
        if not audio_result or not visual_result:
            return False
        
        audio_origin = audio_result.get("origin", {})
        visual_origin = visual_result.get("origin", {})
        
        # Both must have found origins
        if not audio_origin.get("found", False) or not visual_origin.get("found", False):
            return False
            
        # Check if audio and visual have different channel IDs
        audio_channel = audio_origin.get("hit", {}).get("channel_id")
        visual_channel = visual_origin.get("hit", {}).get("channel_id")
        
        if not audio_channel or not visual_channel:
            return False
            
        # If channels are different and visual match is strong (2+ frames),
        # it's likely a composite video
        return (audio_channel != visual_channel and 
                visual_origin.get("matching_frames", 0) >= 2)

class TestCompositeMediaChecker(unittest.TestCase):
    """Tests for the composite media checker functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.checker = TestCompositeChecker()
    
    def test_check_if_composite_true(self):
        """Test that _check_if_composite returns True for composite videos."""
        # Create mock results
        audio_result = {
            "origin": {
                "found": True,
                "confidence": 0.85,
                "hit": {
                    "channel_id": "channel_A",
                    "url": "https://example.com/audio_origin",
                    "title": "Original Audio",
                    "timestamp": "2023-01-01T00:00:00Z"
                }
            }
        }
        
        visual_result = {
            "origin": {
                "found": True,
                "confidence": 0.92,
                "matching_frames": 3,
                "hit": {
                    "channel_id": "channel_B",
                    "url": "https://example.com/visual_origin",
                    "title": "Original Video",
                    "timestamp": "2022-06-01T00:00:00Z"
                }
            }
        }
        
        # Run the check
        result = asyncio.run(self.checker._check_if_composite(audio_result, visual_result))
        
        # Assert result
        self.assertTrue(result, "Should identify as composite when audio and visual have different channels")
    
    def test_check_if_composite_false_same_channel(self):
        """Test that _check_if_composite returns False for original videos (same channel)."""
        # Create mock results with same channel ID
        audio_result = {
            "origin": {
                "found": True,
                "confidence": 0.85,
                "hit": {
                    "channel_id": "channel_A",
                    "url": "https://example.com/origin",
                    "title": "Original Content",
                    "timestamp": "2023-01-01T00:00:00Z"
                }
            }
        }
        
        visual_result = {
            "origin": {
                "found": True,
                "confidence": 0.92,
                "matching_frames": 3,
                "hit": {
                    "channel_id": "channel_A",  # Same channel ID
                    "url": "https://example.com/origin",
                    "title": "Original Content",
                    "timestamp": "2023-01-01T00:00:00Z"
                }
            }
        }
        
        # Run the check
        result = asyncio.run(self.checker._check_if_composite(audio_result, visual_result))
        
        # Assert result
        self.assertFalse(result, "Should not identify as composite when audio and visual have the same channel")
    
    def test_check_if_composite_false_low_frames(self):
        """Test that _check_if_composite returns False when matching frames is low."""
        # Create mock results with different channels but only 1 matching frame
        audio_result = {
            "origin": {
                "found": True,
                "confidence": 0.85,
                "hit": {
                    "channel_id": "channel_A",
                    "url": "https://example.com/audio_origin",
                    "title": "Original Audio",
                    "timestamp": "2023-01-01T00:00:00Z"
                }
            }
        }
        
        visual_result = {
            "origin": {
                "found": True,
                "confidence": 0.92,
                "matching_frames": 1,  # Only 1 matching frame
                "hit": {
                    "channel_id": "channel_B",
                    "url": "https://example.com/visual_origin",
                    "title": "Original Video",
                    "timestamp": "2022-06-01T00:00:00Z"
                }
            }
        }
        
        # Run the check
        result = asyncio.run(self.checker._check_if_composite(audio_result, visual_result))
        
        # Assert result
        self.assertFalse(result, "Should not identify as composite when matching frames is less than 2")
    
    def test_check_if_composite_false_missing_data(self):
        """Test that _check_if_composite returns False when data is missing."""
        # Test with missing audio origin
        result1 = asyncio.run(self.checker._check_if_composite(None, {"origin": {"found": True}}))
        self.assertFalse(result1, "Should not identify as composite when audio origin is missing")
        
        # Test with missing visual origin
        result2 = asyncio.run(self.checker._check_if_composite({"origin": {"found": True}}, None))
        self.assertFalse(result2, "Should not identify as composite when visual origin is missing")
        
        # Test with origins not found
        result3 = asyncio.run(self.checker._check_if_composite(
            {"origin": {"found": False}},
            {"origin": {"found": False}}
        ))
        self.assertFalse(result3, "Should not identify as composite when origins not found")
        
        # Test with missing channel IDs
        result4 = asyncio.run(self.checker._check_if_composite(
            {"origin": {"found": True, "hit": {}}},
            {"origin": {"found": True, "hit": {}, "matching_frames": 3}}
        ))
        self.assertFalse(result4, "Should not identify as composite when channel IDs are missing")

if __name__ == '__main__':
    unittest.main() 