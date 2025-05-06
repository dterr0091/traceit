import os
import logging
import asyncio
import hashlib
from typing import Dict, List, Any, Optional, Union, Tuple
from uuid import uuid4

from ..services.ffmpeg_service import FFmpegService
from ..services.runpod_service import RunPodService
from ..services.audio_pipeline_service import AudioPipelineService
from ..services.redis_service import RedisService
from ..services.vector_service import VectorService
from ..services.router_service import RouterService
from ..services.credit_service import CreditService
from ..services.lineage_service import LineageService
from ..utils.file_utils import delete_file_if_exists, upload_to_storage

logger = logging.getLogger(__name__)

class VideoPipelineService:
    """
    Service for processing videos through the Trace pipeline.
    Identifies the earliest verifiable origin of video content, handling
    both audio and visual components, including composite video detection.
    """
    
    def __init__(self):
        """Initialize the video pipeline with required services."""
        self.ffmpeg_service = FFmpegService()
        self.runpod_service = RunPodService()
        self.audio_pipeline = AudioPipelineService()
        self.redis_service = RedisService()
        self.vector_service = VectorService()
        self.router_service = RouterService()
        self.credit_service = CreditService()
        self.lineage_service = LineageService()
        
        # Similarity threshold for matching frames
        self.clip_similarity_threshold = 0.20
    
    async def process_video(self, 
                          file_path: str = None, 
                          url: str = None,
                          job_id: str = None) -> Dict[str, Any]:
        """
        Process a video through the Trace pipeline.
        
        Args:
            file_path: Path to local video file
            url: URL to video file
            job_id: Optional job ID for tracking
            
        Returns:
            Dict containing processing results
        """
        if not file_path and not url:
            return {"error": "Either file_path or url must be provided"}
            
        job_id = job_id or str(uuid4())
        temp_files = []
        
        try:
            # Download file if URL provided
            if url and not file_path:
                file_path = await self.ffmpeg_service.download_video(url)
                if not file_path:
                    return {"error": f"Failed to download video from URL: {url}"}
                temp_files.append(file_path)
            
            # Get video metadata
            metadata = await self.ffmpeg_service.get_video_metadata(file_path)
            
            # Check cache for this video
            video_hash = await self._get_video_hash(file_path)
            cached_result = await self.redis_service.get(f"video:{video_hash}")
            
            if cached_result:
                logger.info(f"Cache hit for video hash: {video_hash}")
                return {
                    "job_id": job_id,
                    "result": cached_result,
                    "from_cache": True
                }
            
            # Process and return initial response (we'll process video frames asynchronously)
            initial_response = {
                "job_id": job_id,
                "status": "processing",
                "metadata": metadata,
                "hash": video_hash
            }
            
            # Start audio processing first (faster)
            audio_task = asyncio.create_task(self._process_audio_track(file_path, job_id))
            
            # Start keyframe extraction and processing
            visual_task = asyncio.create_task(self._process_visual_frames(file_path, job_id))
            
            # Wait for both tasks to complete
            audio_result, visual_result = await asyncio.gather(audio_task, visual_task)
            
            # Detect if this is a composite video
            is_composite = await self._check_if_composite(audio_result, visual_result)
            
            # Prepare final result
            result = {
                "job_id": job_id,
                "metadata": metadata,
                "origins": {
                    "audio": audio_result.get("origin") if audio_result else None,
                    "visual": visual_result.get("origin") if visual_result else None
                },
                "is_composite": is_composite,
                "confidence": {
                    "audio": audio_result.get("confidence", 0) if audio_result else 0,
                    "visual": visual_result.get("confidence", 0) if visual_result else 0
                },
                "hash": video_hash
            }
            
            # Store in lineage service for tracking
            if audio_result or visual_result:
                await self.lineage_service.store_origin(
                    artifact_id=video_hash,
                    artifact_type="video",
                    origin_data=None,  # No single origin for composite videos
                    is_composite=is_composite,
                    audio_origin=audio_result.get("origin") if audio_result else None,
                    visual_origin=visual_result.get("origin") if visual_result else None
                )
            
            # Cache the result
            await self.redis_service.set(
                f"video:{video_hash}", 
                result,
                expire_seconds=60*60*24*90  # 90 days
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in video pipeline: {str(e)}")
            return {
                "job_id": job_id,
                "error": str(e)
            }
        finally:
            # Clean up temp files
            for temp_file in temp_files:
                delete_file_if_exists(temp_file)
    
    async def _process_audio_track(self, 
                                  video_path: str, 
                                  job_id: str) -> Dict[str, Any]:
        """
        Extract and process the audio track from a video.
        
        Args:
            video_path: Path to the video file
            job_id: Job ID for tracking
            
        Returns:
            Dict containing audio processing results
        """
        try:
            # Extract audio from video
            audio_path = await self.ffmpeg_service.extract_audio(video_path)
            if not audio_path:
                return {"error": "No audio track found in video"}
            
            # Process the audio file using existing audio pipeline
            audio_result = await self.audio_pipeline.process_audio(
                file_path=audio_path,
                job_id=job_id
            )
            
            # Clean up temp audio file
            delete_file_if_exists(audio_path)
            
            return audio_result
            
        except Exception as e:
            logger.error(f"Error processing audio track: {str(e)}")
            return {"error": str(e)}
    
    async def _process_visual_frames(self, 
                                    video_path: str, 
                                    job_id: str) -> Dict[str, Any]:
        """
        Extract and process keyframes from a video.
        
        Args:
            video_path: Path to the video file
            job_id: Job ID for tracking
            
        Returns:
            Dict containing visual processing results
        """
        frame_paths = []
        
        try:
            # Extract 3 keyframes (start, middle, end)
            frame_paths = await self.ffmpeg_service.extract_keyframes(video_path)
            if not frame_paths:
                return {"error": "Failed to extract frames from video"}
            
            # Upload frames to storage to get URLs for RunPod
            frame_urls = []
            for frame_path in frame_paths:
                url = await upload_to_storage(frame_path)
                if url:
                    frame_urls.append(url)
            
            if not frame_urls:
                return {"error": "Failed to upload frames for processing"}
            
            # Submit batch job to RunPod for CLIP embeddings
            batch_job = await self.runpod_service.submit_clip_embedding_job(
                image_urls=frame_urls,
                job_id=job_id
            )
            
            if not batch_job.get("success", False):
                return {
                    "error": "Failed to submit GPU batch job",
                    "details": batch_job.get("error")
                }
            
            # Wait for RunPod job to complete (with timeout)
            job_result = await self.runpod_service.wait_for_completion(
                runpod_job_id=batch_job.get("runpod_job_id"),
                timeout_seconds=300
            )
            
            if not job_result.get("success", False):
                return {
                    "error": "GPU batch job failed or timed out",
                    "details": job_result.get("error")
                }
            
            # Process embeddings from RunPod result
            embeddings = job_result.get("output", {}).get("embeddings", [])
            if not embeddings:
                return {"error": "No embeddings returned from GPU job"}
            
            # Search for visual origins using the frame embeddings
            visual_origins = await self._find_visual_origins(embeddings, job_id)
            
            # Use majority voting to determine final visual origin
            combined_origin = await self._combine_frame_origins(visual_origins)
            
            return combined_origin
            
        except Exception as e:
            logger.error(f"Error processing visual frames: {str(e)}")
            return {"error": str(e)}
        finally:
            # Clean up temp frame files
            for frame_path in frame_paths:
                delete_file_if_exists(frame_path)
    
    async def _find_visual_origins(self, 
                                  embeddings: List[Dict], 
                                  job_id: str) -> List[Dict]:
        """
        Find origins for each frame using vector search.
        
        Args:
            embeddings: List of CLIP embeddings for frames
            job_id: Job ID for tracking
            
        Returns:
            List of origin results for each frame
        """
        visual_origins = []
        
        for i, embedding in enumerate(embeddings):
            # Use the vector service to search for similar images
            vector_result = await self.vector_service.search_by_embedding(
                embedding=embedding,
                table="image_embeddings",
                top_k=3
            )
            
            # Record frame origin with similarity scores
            visual_origins.append({
                "frame_index": i,
                "hits": vector_result.get("hits", []),
                "confidence": vector_result.get("confidence", 0)
            })
        
        return visual_origins
    
    async def _combine_frame_origins(self, frame_origins: List[Dict]) -> Dict[str, Any]:
        """
        Combine results from multiple frames using majority voting.
        
        Args:
            frame_origins: List of origin results for each frame
            
        Returns:
            Dict containing combined origin result
        """
        # Count origin sources by channel ID
        channel_counts = {}
        channel_confidence = {}
        all_hits = []
        
        for origin in frame_origins:
            hits = origin.get("hits", [])
            all_hits.extend(hits)
            
            for hit in hits:
                channel_id = hit.get("channel_id")
                if channel_id:
                    channel_counts[channel_id] = channel_counts.get(channel_id, 0) + 1
                    
                    # Use max confidence for each channel
                    current_conf = channel_confidence.get(channel_id, 0)
                    hit_conf = hit.get("confidence", 0)
                    channel_confidence[channel_id] = max(current_conf, hit_conf)
        
        # Find the channel with the most matches
        best_channel = None
        best_count = 0
        
        for channel_id, count in channel_counts.items():
            if count > best_count:
                best_count = count
                best_channel = channel_id
        
        # If no strong match, return low confidence
        if best_count < 2:
            return {
                "origin": {
                    "found": False,
                    "confidence": 0,
                    "message": "No consistent visual origin found across frames"
                },
                "confidence": 0
            }
        
        # Find the best hit for this channel
        best_hit = None
        for hit in all_hits:
            if hit.get("channel_id") == best_channel:
                if not best_hit or hit.get("confidence", 0) > best_hit.get("confidence", 0):
                    best_hit = hit
        
        return {
            "origin": {
                "found": True,
                "confidence": channel_confidence.get(best_channel, 0),
                "hit": best_hit,
                "matching_frames": best_count
            },
            "confidence": channel_confidence.get(best_channel, 0)
        }
    
    async def _check_if_composite(self, 
                                 audio_result: Dict[str, Any], 
                                 visual_result: Dict[str, Any]) -> bool:
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
    
    async def _get_video_hash(self, file_path: str) -> str:
        """
        Generate a perceptual hash for the video file.
        For simplicity, we'll use the first frame + audio hash combination.
        
        Args:
            file_path: Path to the video file
            
        Returns:
            String hash representing the video content
        """
        # Extract the first frame
        frames = await self.ffmpeg_service.extract_keyframes(
            file_path, 
            frame_positions=[0]
        )
        
        if not frames:
            # Fallback to file hash if frame extraction fails
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        
        # Hash the first frame
        frame_hash = hashlib.md5()
        with open(frames[0], "rb") as f:
            frame_hash.update(f.read())
        
        # Extract part of the audio for hashing
        audio_path = await self.ffmpeg_service.extract_audio(file_path)
        audio_hash = ""
        
        if audio_path:
            # Get first 30 seconds of audio
            audio_hash_md5 = hashlib.md5()
            with open(audio_path, "rb") as f:
                audio_hash_md5.update(f.read(1024 * 1024))  # Read up to 1MB
            audio_hash = audio_hash_md5.hexdigest()
            delete_file_if_exists(audio_path)
        
        # Clean up the frame
        delete_file_if_exists(frames[0])
        
        # Combine hashes
        combined = f"{frame_hash.hexdigest()}:{audio_hash}"
        final_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        return final_hash 

    async def process_video_with_progress(self,
                                         file_path: str = None,
                                         url: str = None,
                                         job_id: str = None,
                                         user_id: str = None) -> Dict[str, Any]:
        """
        Process a video with progress tracking for SSE.
        
        Args:
            file_path: Path to local video file
            url: URL to video file
            job_id: Optional job ID for tracking
            user_id: User ID for credit deduction
            
        Returns:
            Dict containing processing results
        """
        if not file_path and not url:
            return {"error": "Either file_path or url must be provided"}
            
        job_id = job_id or str(uuid4())
        temp_files = []
        
        try:
            # Initialize progress
            await self._update_progress(job_id, "starting", "Initializing video processing", 0)
            
            # Download file if URL provided
            if url and not file_path:
                await self._update_progress(job_id, "downloading", "Downloading video from URL", 5)
                file_path = await self.ffmpeg_service.download_video(url)
                if not file_path:
                    await self._update_progress(job_id, "error", "Failed to download video from URL", 0)
                    return {"error": f"Failed to download video from URL: {url}"}
                temp_files.append(file_path)
            
            # Get video metadata
            await self._update_progress(job_id, "metadata", "Extracting video metadata", 10)
            metadata = await self.ffmpeg_service.get_video_metadata(file_path)
            
            # Calculate video hash for cache lookup
            await self._update_progress(job_id, "hashing", "Calculating video hash", 15)
            video_hash = await self._get_video_hash(file_path)
            
            # Check cache
            cached_result = await self.redis_service.get_cache(f"video:{video_hash}")
            if cached_result:
                logger.info(f"Cache hit for video hash: {video_hash}")
                await self._update_progress(job_id, "complete", "Retrieved from cache", 100)
                
                # Store the final result
                await self.redis_service.set_cache(
                    f"video_result:{job_id}", 
                    cached_result,
                    ttl_days=1  # Short TTL for job results
                )
                
                return {
                    "job_id": job_id,
                    "result": cached_result,
                    "from_cache": True
                }
            
            # Start audio processing
            await self._update_progress(job_id, "audio_processing", "Processing audio track", 20)
            audio_result = await self._process_audio_track(file_path, job_id)
            
            # Update progress
            if audio_result.get("error"):
                await self._update_progress(job_id, "audio_warning", f"Audio processing issue: {audio_result.get('error')}", 35)
            else:
                await self._update_progress(job_id, "audio_complete", "Audio processing complete", 40)
            
            # Start frame extraction
            await self._update_progress(job_id, "extracting_frames", "Extracting video frames", 45)
            frame_paths = await self.ffmpeg_service.extract_keyframes(file_path)
            if not frame_paths:
                await self._update_progress(job_id, "error", "Failed to extract frames from video", 45)
                return {"error": "Failed to extract frames from video"}
                
            # Upload frames
            await self._update_progress(job_id, "uploading_frames", "Uploading frames for analysis", 50)
            frame_urls = []
            for frame_path in frame_paths:
                url = await upload_to_storage(frame_path)
                if url:
                    frame_urls.append(url)
            
            if not frame_urls:
                await self._update_progress(job_id, "error", "Failed to upload frames for processing", 50)
                return {"error": "Failed to upload frames for processing"}
            
            # Submit GPU job
            await self._update_progress(job_id, "gpu_job_submit", "Submitting GPU job for frame analysis", 55)
            batch_job = await self.runpod_service.submit_clip_embedding_job(frame_urls, job_id)
            
            if not batch_job.get("success", False):
                await self._update_progress(job_id, "error", "Failed to submit GPU batch job", 55)
                return {
                    "error": "Failed to submit GPU batch job",
                    "details": batch_job.get("error")
                }
            
            # Wait for GPU job
            await self._update_progress(job_id, "gpu_job_processing", "Processing frames with GPU (this may take a minute)", 60)
            
            # Poll for job completion with progress updates
            runpod_job_id = batch_job.get("runpod_job_id")
            job_complete = False
            timeout = 300  # 5 minutes
            start_time = asyncio.get_event_loop().time()
            
            while not job_complete and asyncio.get_event_loop().time() - start_time < timeout:
                job_status = await self.runpod_service.get_job_status(runpod_job_id)
                
                if job_status.get("status") == "COMPLETED":
                    job_complete = True
                elif job_status.get("status") == "FAILED":
                    await self._update_progress(job_id, "error", "GPU job failed", 60)
                    return {"error": "GPU batch job failed"}
                else:
                    # Update progress based on RunPod status
                    status_text = job_status.get("status", "PENDING")
                    progress = 60
                    if status_text == "IN_PROGRESS":
                        progress = 65
                    elif status_text == "IN_QUEUE":
                        progress = 62
                        
                    await self._update_progress(job_id, "gpu_job_" + status_text.lower(), f"GPU job status: {status_text}", progress)
                    await asyncio.sleep(3)  # Poll every 3 seconds
            
            if not job_complete:
                await self._update_progress(job_id, "error", "GPU job timed out", 65)
                return {"error": "GPU batch job timed out"}
            
            # Get job result
            await self._update_progress(job_id, "getting_gpu_results", "Retrieving GPU analysis results", 70)
            job_result = await self.runpod_service.get_job_output(runpod_job_id)
            
            if not job_result.get("success", False):
                await self._update_progress(job_id, "error", "Failed to get GPU job results", 70)
                return {
                    "error": "Failed to get GPU job results",
                    "details": job_result.get("error")
                }
            
            # Process embeddings
            await self._update_progress(job_id, "processing_embeddings", "Processing frame embeddings", 75)
            embeddings = job_result.get("output", {}).get("embeddings", [])
            if not embeddings:
                await self._update_progress(job_id, "error", "No embeddings returned from GPU job", 75)
                return {"error": "No embeddings returned from GPU job"}
            
            # Find visual origins
            await self._update_progress(job_id, "finding_visual_origins", "Searching for visual origins", 80)
            visual_origins = await self._find_visual_origins(embeddings, job_id)
            
            # Combine frame origins
            await self._update_progress(job_id, "combining_origins", "Determining primary visual origin", 85)
            visual_result = await self._combine_frame_origins(visual_origins)
            
            # Check for composite
            await self._update_progress(job_id, "checking_composite", "Checking if video is composite", 90)
            is_composite = await self._check_if_composite(audio_result, visual_result)
            
            # Prepare final result
            await self._update_progress(job_id, "preparing_result", "Preparing final result", 95)
            result = {
                "job_id": job_id,
                "metadata": metadata,
                "origins": {
                    "audio": audio_result.get("origin") if audio_result and not audio_result.get("error") else None,
                    "visual": visual_result.get("origin") if visual_result and not visual_result.get("error") else None
                },
                "is_composite": is_composite,
                "confidence": {
                    "audio": audio_result.get("confidence", 0) if audio_result and not audio_result.get("error") else 0,
                    "visual": visual_result.get("confidence", 0) if visual_result and not visual_result.get("error") else 0
                },
                "hash": video_hash
            }
            
            # Store in lineage service
            if audio_result or visual_result:
                await self.lineage_service.store_origin(
                    artifact_id=video_hash,
                    artifact_type="video",
                    origin_data=None,  # No single origin for composite videos
                    is_composite=is_composite,
                    audio_origin=audio_result.get("origin") if audio_result and not audio_result.get("error") else None,
                    visual_origin=visual_result.get("origin") if visual_result and not visual_result.get("error") else None
                )
            
            # Cache the result
            await self.redis_service.set_cache(
                f"video:{video_hash}", 
                result,
                ttl_days=90  # 90 days
            )
            
            # Store the final result for this job
            await self.redis_service.set_cache(
                f"video_result:{job_id}", 
                result,
                ttl_days=1  # Short TTL for job results
            )
            
            # Deduct credits if user_id provided
            if user_id:
                await self.credit_service.deduct_credits(user_id, 8, f"Video processing: {job_id}")
            
            await self._update_progress(job_id, "complete", "Processing complete", 100)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in video pipeline: {str(e)}")
            await self._update_progress(job_id, "error", f"Error: {str(e)}", 0)
            return {
                "job_id": job_id,
                "error": str(e)
            }
        finally:
            # Clean up temp files
            for temp_file in temp_files:
                delete_file_if_exists(temp_file)
    
    async def _update_progress(self, 
                              job_id: str, 
                              status: str, 
                              message: str, 
                              percent: int) -> None:
        """
        Update processing progress for a job. This information is used for SSE.
        
        Args:
            job_id: The job ID
            status: Current status code
            message: Human-readable progress message
            percent: Progress percentage (0-100)
        """
        progress = {
            "job_id": job_id,
            "status": status,
            "message": message,
            "percent": percent,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        logger.info(f"Job {job_id} progress: {status} - {message} ({percent}%)")
        
        # Store in Redis for SSE endpoint to retrieve
        await self.redis_service.set_cache(
            f"video_progress:{job_id}", 
            progress,
            ttl_days=1  # 24 hours TTL
        ) 