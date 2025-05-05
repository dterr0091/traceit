import os
import json
import logging
import httpx
import asyncio
from typing import Dict, List, Any, Optional, Union
from uuid import uuid4

logger = logging.getLogger(__name__)

class RunPodService:
    """
    Service for interacting with RunPod GPU batch infrastructure.
    Handles submission and retrieval of GPU batch processing jobs.
    """
    
    def __init__(self):
        """Initialize the RunPod service with API credentials."""
        self.api_key = os.getenv("RUNPOD_API_KEY")
        self.api_url = "https://api.runpod.io/v2"
        self.endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")
        
        if not self.api_key:
            logger.warning("RUNPOD_API_KEY not set. RunPod service will not function properly.")
        
        if not self.endpoint_id:
            logger.warning("RUNPOD_ENDPOINT_ID not set. RunPod service will not function properly.")
    
    async def submit_clip_embedding_job(self, 
                                       image_urls: List[str], 
                                       job_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Submit a CLIP embedding job to RunPod.
        
        Args:
            image_urls: List of image URLs to process
            job_id: Optional job ID for tracking
            
        Returns:
            Dict containing job submission results
        """
        if not self.api_key or not self.endpoint_id:
            return {"error": "RunPod API credentials not configured"}
        
        job_id = job_id or str(uuid4())
        
        try:
            payload = {
                "input": {
                    "images": image_urls,
                    "job_id": job_id
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.api_url}/{self.endpoint_id}/run"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code != 200:
                    logger.error(f"RunPod API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"RunPod API error: {response.status_code}",
                        "details": response.text
                    }
                
                result = response.json()
                return {
                    "success": True,
                    "runpod_job_id": result.get("id"),
                    "job_id": job_id,
                    "status": "submitted"
                }
                
        except Exception as e:
            logger.error(f"Error submitting RunPod job: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "job_id": job_id
            }
    
    async def get_job_status(self, runpod_job_id: str) -> Dict[str, Any]:
        """
        Check the status of a RunPod job.
        
        Args:
            runpod_job_id: The RunPod job ID to check
            
        Returns:
            Dict containing job status
        """
        if not self.api_key or not self.endpoint_id:
            return {"error": "RunPod API credentials not configured"}
        
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            url = f"{self.api_url}/{self.endpoint_id}/status/{runpod_job_id}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code != 200:
                    logger.error(f"RunPod API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"RunPod API error: {response.status_code}",
                        "details": response.text
                    }
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Error checking RunPod job status: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_job_result(self, runpod_job_id: str) -> Dict[str, Any]:
        """
        Get the results of a completed RunPod job.
        
        Args:
            runpod_job_id: The RunPod job ID to retrieve
            
        Returns:
            Dict containing job results
        """
        if not self.api_key or not self.endpoint_id:
            return {"error": "RunPod API credentials not configured"}
        
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            url = f"{self.api_url}/{self.endpoint_id}/output/{runpod_job_id}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code != 200:
                    logger.error(f"RunPod API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"RunPod API error: {response.status_code}",
                        "details": response.text
                    }
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Error retrieving RunPod job results: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def wait_for_completion(self, 
                                 runpod_job_id: str, 
                                 timeout_seconds: int = 300,
                                 check_interval: int = 5) -> Dict[str, Any]:
        """
        Wait for a RunPod job to complete with timeout.
        
        Args:
            runpod_job_id: The RunPod job ID to wait for
            timeout_seconds: Maximum time to wait (in seconds)
            check_interval: How often to check status (in seconds)
            
        Returns:
            Dict containing final job result or timeout error
        """
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout_seconds:
            status = await self.get_job_status(runpod_job_id)
            
            if not status.get("success", False):
                return status
            
            if status.get("status") == "COMPLETED":
                return await self.get_job_result(runpod_job_id)
            
            if status.get("status") in ["FAILED", "CANCELLED"]:
                return {
                    "success": False,
                    "error": f"Job {status.get('status')}",
                    "details": status
                }
            
            # Wait before checking again
            await asyncio.sleep(check_interval)
        
        return {
            "success": False,
            "error": f"Timeout after {timeout_seconds} seconds",
            "job_id": runpod_job_id
        } 