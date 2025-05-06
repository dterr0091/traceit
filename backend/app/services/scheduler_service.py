import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from .tineye_service import TinEyeService
from .lineage_service import LineageService

logger = logging.getLogger(__name__)

class SchedulerService:
    """Service for scheduling background tasks"""
    
    _running = False
    _tineye_last_run = 0
    _lineage_graph_last_run = 0
    _lineage_service = None
    
    @classmethod
    async def start(cls):
        """Start the scheduler"""
        if cls._running:
            logger.warning("Scheduler is already running")
            return
        
        cls._running = True
        cls._lineage_service = LineageService()
        asyncio.create_task(cls._run_scheduler())
        logger.info("Scheduler started")
    
    @classmethod
    async def stop(cls):
        """Stop the scheduler"""
        cls._running = False
        logger.info("Scheduler stopped")
    
    @classmethod
    async def _run_scheduler(cls):
        """Main scheduler loop"""
        while cls._running:
            try:
                current_time = time.time()
                
                # Check if it's time to run TinEye batch
                if current_time - cls._tineye_last_run >= 3600:  # 1 hour interval
                    await cls._run_tineye_batch()
                    cls._tineye_last_run = current_time
                
                # Check if it's time to run lineage graph update
                # Run once per day (24 hours = 86400 seconds)
                if current_time - cls._lineage_graph_last_run >= 86400:
                    await cls._run_lineage_graph_update()
                    cls._lineage_graph_last_run = current_time
                
                # Sleep for a bit to avoid busy waiting
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying
    
    @classmethod
    async def _run_tineye_batch(cls) -> Dict[str, Any]:
        """Run TinEye batch processing"""
        logger.info(f"Running scheduled TinEye batch processing at {datetime.utcnow().isoformat()}")
        try:
            result = await TinEyeService.process_batch()
            logger.info(f"TinEye batch processing completed: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in TinEye batch processing: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    @classmethod
    async def _run_lineage_graph_update(cls) -> Dict[str, Any]:
        """Run nightly lineage graph update to build multi-hop relationships"""
        logger.info(f"Running scheduled lineage graph update at {datetime.utcnow().isoformat()}")
        
        if not cls._lineage_service or not cls._lineage_service.neo4j_enabled:
            logger.warning("Neo4j is not enabled - skipping lineage graph update")
            return {"status": "skipped", "reason": "Neo4j not enabled"}
        
        try:
            result = await cls._lineage_service.build_multi_hop_graph()
            logger.info(f"Lineage graph update completed: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in lineage graph update: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    @classmethod
    async def force_run_tineye_batch(cls) -> Dict[str, Any]:
        """Manually force a TinEye batch run"""
        cls._tineye_last_run = time.time()  # Update the last run time
        return await cls._run_tineye_batch() 
        
    @classmethod
    async def force_run_lineage_graph_update(cls) -> Dict[str, Any]:
        """Manually force a lineage graph update"""
        if not cls._lineage_service:
            cls._lineage_service = LineageService()
        cls._lineage_graph_last_run = time.time()  # Update the last run time
        return await cls._run_lineage_graph_update() 