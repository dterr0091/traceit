import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.brave_search_service import BraveSearchService
from app.services.tineye_service import TinEyeService
from app.services.scheduler_service import SchedulerService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def test_brave_search():
    """Test Brave Search API"""
    logger.info("Testing Brave Search API")
    
    # Load a test image
    test_image_path = "test_data/test_image.jpg"
    
    if not os.path.exists(test_image_path):
        logger.error(f"Test image not found at {test_image_path}")
        return
    
    with open(test_image_path, "rb") as f:
        image_data = f.read()
    
    # Perform reverse image search
    results = await BraveSearchService.reverse_image_search(image_data)
    
    logger.info(f"Brave Search API returned {len(results.get('results', []))} results")
    
    # Extract origins
    origins = BraveSearchService.extract_origins(results)
    logger.info(f"Extracted {len(origins)} origins")
    
    for i, origin in enumerate(origins[:3]):
        logger.info(f"Origin {i+1}: {origin['url']} (confidence: {origin['confidence']})")
    
    return origins

async def test_tineye_batch():
    """Test TinEye batch processing"""
    logger.info("Testing TinEye batch processing")
    
    # Initialize the bloom filter
    TinEyeService.initialize_bloom_filter()
    
    # Load test images
    test_image_dir = "test_data"
    test_images = []
    
    if not os.path.exists(test_image_dir):
        logger.error(f"Test image directory not found at {test_image_dir}")
        return
    
    for filename in os.listdir(test_image_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            file_path = os.path.join(test_image_dir, filename)
            with open(file_path, "rb") as f:
                image_data = f.read()
                image_hash = f"test_{filename}"
                test_images.append((image_data, image_hash))
    
    if not test_images:
        logger.error("No test images found")
        return
    
    # Add images to the batch queue
    for image_data, image_hash in test_images:
        added = TinEyeService.add_to_batch(image_data, image_hash)
        logger.info(f"Added image {image_hash} to batch: {added}")
    
    # Process the batch
    batch_result = await TinEyeService.process_batch()
    logger.info(f"Batch processing result: {batch_result}")
    
    # Check the batch results if available
    if batch_result.get("status") == "success" and "batch_id" in batch_result:
        batch_id = batch_result["batch_id"]
        logger.info(f"Checking results for batch {batch_id}")
        
        results = await TinEyeService.check_batch_results(batch_id)
        logger.info(f"Batch results: {results}")
    
    return batch_result

async def test_scheduler():
    """Test the scheduler"""
    logger.info("Testing scheduler")
    
    # Start the scheduler
    await SchedulerService.start()
    logger.info("Scheduler started")
    
    # Wait for a bit
    logger.info("Waiting for 10 seconds...")
    await asyncio.sleep(10)
    
    # Force run TinEye batch
    result = await SchedulerService.force_run_tineye_batch()
    logger.info(f"Forced TinEye batch result: {result}")
    
    # Stop the scheduler
    await SchedulerService.stop()
    logger.info("Scheduler stopped")
    
    return result

async def main():
    """Run all tests"""
    logger.info("Starting image search tests")
    
    # Create test data directory if it doesn't exist
    test_data_dir = "test_data"
    os.makedirs(test_data_dir, exist_ok=True)
    
    # Test if we have API keys
    brave_key = os.getenv("BRAVE_API_KEY")
    tineye_key = os.getenv("TINEYE_API_KEY")
    
    if not brave_key:
        logger.warning("BRAVE_API_KEY not set. Brave Search tests will fail.")
    
    if not tineye_key:
        logger.warning("TINEYE_API_KEY not set. TinEye tests will fail.")
    
    # Run tests if we have API keys
    if brave_key:
        try:
            await test_brave_search()
        except Exception as e:
            logger.error(f"Error in Brave Search test: {str(e)}")
    
    if tineye_key:
        try:
            await test_tineye_batch()
        except Exception as e:
            logger.error(f"Error in TinEye batch test: {str(e)}")
    
    # Test scheduler regardless of API keys
    try:
        await test_scheduler()
    except Exception as e:
        logger.error(f"Error in scheduler test: {str(e)}")
    
    logger.info("All tests completed")

if __name__ == "__main__":
    asyncio.run(main()) 