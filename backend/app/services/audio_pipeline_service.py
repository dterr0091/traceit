import os
import logging
import asyncio
from typing import Dict, Optional, Union, List, Any
from uuid import uuid4

from ..services.whisper_service import WhisperService
from ..services.redis_service import RedisService
from ..services.vector_service import VectorService
from ..services.router_service import RouterService
from ..utils.file_utils import delete_file_if_exists

logger = logging.getLogger(__name__)

class AudioPipelineService:
    """
    Service for processing audio through the Trace pipeline.
    Identifies the earliest verifiable origin of audio content.
    """
    
    def __init__(self):
        """Initialize the audio pipeline with required services."""
        self.whisper_service = WhisperService()
        self.redis_service = RedisService()
        self.vector_service = VectorService()
        self.router_service = RouterService()
    
    async def process_audio(self, file_path: str = None, url: str = None, 
                           job_id: str = None) -> Dict[str, Any]:
        """
        Process audio through the Trace pipeline.
        
        Args:
            file_path: Path to local audio file
            url: URL to audio file
            job_id: Optional job ID for existing search bundle
            
        Returns:
            Dict containing processing results
        """
        if not file_path and not url:
            return {"error": "Either file_path or url must be provided"}
            
        job_id = job_id or str(uuid4())
        temp_file = None
        
        try:
            # Download file if URL provided
            if url and not file_path:
                temp_file = await self.whisper_service.download_audio_from_url(url)
                if not temp_file:
                    return {"error": f"Failed to download audio from URL: {url}"}
                file_path = temp_file
            
            # Check cache for this audio file hash
            file_hash = await self._get_audio_hash(file_path)
            cached_result = await self.redis_service.get(f"audio:{file_hash}")
            
            if cached_result:
                logger.info(f"Cache hit for audio hash: {file_hash}")
                return {
                    "job_id": job_id,
                    "result": cached_result,
                    "from_cache": True
                }
                
            # Process audio with Whisper
            whisper_result = await self.whisper_service.process_audio_file(file_path)
            
            # Different processing paths based on content type
            if whisper_result.get("content_type") == "music":
                # For music, use fingerprint data to find origin
                origin_result = await self._find_music_origin(
                    whisper_result.get("fingerprint", {}),
                    file_hash
                )
            else:
                # For speech, use transcription to find origin
                transcription = whisper_result.get("transcription", {}).get("text", "")
                origin_result = await self._find_speech_origin(transcription, file_hash)
            
            # Combine results
            result = {
                "job_id": job_id,
                "content_type": whisper_result.get("content_type"),
                "transcription": whisper_result.get("transcription", {}).get("text", ""),
                "origin": origin_result,
                "confidence": origin_result.get("confidence", 0),
            }
            
            # Cache result
            await self.redis_service.set(
                f"audio:{file_hash}", 
                result,
                expire_seconds=60*60*24*30  # 30 days
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in audio pipeline: {str(e)}")
            return {
                "job_id": job_id,
                "error": str(e)
            }
        finally:
            # Clean up temp file if created
            if temp_file:
                delete_file_if_exists(temp_file)
    
    async def _get_audio_hash(self, file_path: str) -> str:
        """
        Generate a perceptual hash for the audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            String hash representing the audio content
        """
        # For simplicity, we'll use a file hash here
        # In a production system, you would want to use a proper audio
        # fingerprinting algorithm for perceptual hashing
        import hashlib
        
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    async def _find_music_origin(self, fingerprint_data: Dict, file_hash: str) -> Dict:
        """
        Find the origin of music audio using fingerprint data.
        
        Args:
            fingerprint_data: ACRCloud fingerprint results
            file_hash: Hash of the audio file
            
        Returns:
            Dict containing origin information
        """
        # Extract music metadata
        music_info = fingerprint_data.get("metadata", {}).get("music", [{}])[0]
        title = music_info.get("title", "")
        artist = music_info.get("artist", "")
        
        if not title or not artist:
            return {
                "found": False,
                "confidence": 0,
                "message": "Insufficient music metadata"
            }
        
        # Use the Router service to find the origin
        # This will query local vector DB and optionally Perplexity
        search_query = f"music {title} by {artist}"
        router_result = await self.router_service.query(
            query=search_query,
            artifact_hash=file_hash,
            artifact_type="audio"
        )
        
        return {
            "found": router_result.get("hits", []) != [],
            "confidence": router_result.get("confidence", 0),
            "hits": router_result.get("hits", []),
            "metadata": {
                "title": title,
                "artist": artist,
                "album": music_info.get("album", ""),
                "release_date": music_info.get("release_date", "")
            }
        }
    
    async def _find_speech_origin(self, transcription: str, file_hash: str) -> Dict:
        """
        Find the origin of speech audio using transcription.
        
        Args:
            transcription: Text transcription from Whisper
            file_hash: Hash of the audio file
            
        Returns:
            Dict containing origin information
        """
        if not transcription or len(transcription) < 10:
            return {
                "found": False,
                "confidence": 0,
                "message": "Insufficient transcription text"
            }
        
        # Use the Router service to find the origin
        # This will query local vector DB and optionally Perplexity
        router_result = await self.router_service.query(
            query=transcription[:500],  # Use first 500 chars
            artifact_hash=file_hash,
            artifact_type="audio"
        )
        
        return {
            "found": router_result.get("hits", []) != [],
            "confidence": router_result.get("confidence", 0),
            "hits": router_result.get("hits", [])
        } 