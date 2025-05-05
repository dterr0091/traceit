import os
import tempfile
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, List

import httpx
import whisper
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class WhisperService:
    """
    Service for transcribing audio using Whisper tiny-en model on CPU.
    Also handles fallback to ACRCloud for music fingerprinting.
    """
    
    def __init__(self):
        """Initialize the Whisper model with tiny-en for CPU usage."""
        # Load model only when needed to save memory
        self._model = None
        self.model_name = "tiny.en"
        
    @property
    def model(self):
        """Lazy loading of the Whisper model."""
        if self._model is None:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self._model = whisper.load_model(self.model_name)
        return self._model
    
    async def process_audio_file(self, file_path: str) -> Dict:
        """
        Process an audio file using Whisper for transcription and ACRCloud fallback.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dict containing transcription and fingerprint results
        """
        transcription = self.transcribe_audio(file_path)
        
        # If transcription is mostly music (low speech confidence), use ACRCloud
        if transcription.get("is_music", False):
            fingerprint_result = await self.get_music_fingerprint(file_path)
            if fingerprint_result:
                return {
                    "transcription": transcription,
                    "fingerprint": fingerprint_result,
                    "content_type": "music"
                }
        
        return {
            "transcription": transcription,
            "content_type": "speech"
        }
    
    def transcribe_audio(self, file_path: str) -> Dict:
        """
        Transcribe audio using Whisper.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dict containing transcription results
        """
        try:
            # Transcribe with Whisper
            result = self.model.transcribe(file_path)
            
            # Determine if this is likely music based on segments analysis
            segments = result.get("segments", [])
            is_music = self._is_likely_music(segments)
            
            return {
                "text": result.get("text", ""),
                "segments": self._format_segments(segments),
                "is_music": is_music,
                "language": result.get("language", "en")
            }
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return {"error": str(e)}
    
    def _format_segments(self, segments: List) -> List[Dict]:
        """Format segments for API response."""
        return [
            {
                "start": segment.get("start", 0),
                "end": segment.get("end", 0),
                "text": segment.get("text", ""),
                "confidence": segment.get("confidence", 0)
            }
            for segment in segments
        ]
    
    def _is_likely_music(self, segments: List) -> bool:
        """
        Determine if audio is likely music based on segment analysis.
        
        Args:
            segments: List of segments from Whisper transcription
            
        Returns:
            Boolean indicating if the audio is likely music
        """
        if not segments:
            return False
            
        # If few segments with long pauses, likely music
        if len(segments) < 3 and any(s.get("end", 0) - s.get("start", 0) > 10 for s in segments):
            return True
            
        # If average confidence is very low, likely music
        avg_confidence = sum(s.get("confidence", 0) for s in segments) / len(segments)
        if avg_confidence < 0.4:
            return True
            
        return False
    
    async def get_music_fingerprint(self, file_path: str) -> Optional[Dict]:
        """
        Get music fingerprint using ACRCloud API.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dict containing fingerprint results or None if failed
        """
        # This is a placeholder - implement actual ACRCloud API integration
        # In a real implementation, you would:
        # 1. Read the ACRCloud API key from environment variables
        # 2. Send the audio file to ACRCloud API
        # 3. Process and return the results
        
        try:
            # Placeholder for ACRCloud API call
            # In production, replace with actual API call
            logger.info(f"Would send {file_path} to ACRCloud API for fingerprinting")
            
            # Simulate ACRCloud response - replace with actual implementation
            return {
                "status": "success",
                "metadata": {
                    "music": [{
                        "title": "Example Song",
                        "artist": "Example Artist",
                        "album": "Example Album",
                        "release_date": "2023-01-01",
                        "confidence": 0.85
                    }]
                }
            }
        except Exception as e:
            logger.error(f"Error getting music fingerprint: {str(e)}")
            return None
    
    async def download_audio_from_url(self, url: str) -> Optional[str]:
        """
        Download audio from URL to a temporary file.
        
        Args:
            url: URL of the audio file
            
        Returns:
            Path to the downloaded file or None if download failed
        """
        try:
            # Create temp file with appropriate extension
            suffix = Path(url).suffix or ".mp3"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Download file
            async with httpx.AsyncClient() as client:
                async with client.stream("GET", url) as response:
                    response.raise_for_status()
                    with open(temp_path, 'wb') as f:
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)
            
            return temp_path
        except Exception as e:
            logger.error(f"Error downloading audio from URL {url}: {str(e)}")
            return None 