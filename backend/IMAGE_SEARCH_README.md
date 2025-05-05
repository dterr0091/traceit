# Image Reverse Search Flow

This document explains the implementation of the image reverse search functionality in the Trace project.

## Overview

The image reverse search flow uses two main services:

1. **Brave Search API** - Primary image search service (real-time)
2. **TinEye API** - Secondary/fallback service (batch processing)

The system is designed to:
- Use Brave Search API for immediate results
- Queue images for TinEye batch processing if Brave Search results are insufficient
- Process TinEye batches hourly to reduce API costs
- Deduplicate images using a Bloom filter
- Cache results to minimize API calls

## API Endpoints

### `/search/image`

Upload an image to search for its origin.

**Request:**
- `POST /search/image`
- Authentication: JWT token required
- Content-Type: `multipart/form-data`
- Body: Image file

**Response:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "query_hash": "abc123...",
  "query_type": "heavy",
  "perplexity_used": false,
  "credits_used": 3,
  "results": [...],
  "origins": [
    {
      "url": "https://example.com/image.jpg",
      "title": "Example Image",
      "source": "brave_search",
      "timestamp": "2023-06-15T12:00:00Z",
      "similarity": 0.95,
      "confidence": 0.90,
      "metadata": {
        "domain": "example.com",
        "width": 800,
        "height": 600,
        "alt_text": "Example image description"
      }
    },
    ...
  ],
  "confidence": 0.85
}
```

### Admin Endpoints

#### `/search/tineye-batch/{batch_id}`

Get the status/results of a TinEye batch job.

**Request:**
- `GET /search/tineye-batch/{batch_id}`
- Authentication: Admin JWT token required
- Path parameter: `batch_id` - TinEye batch ID

**Response:**
```json
{
  "batch_id": "tineye_batch_123",
  "status": "completed",
  "matches": [...],
  ...
}
```

#### `/search/tineye-batch/run`

Manually trigger a TinEye batch processing job.

**Request:**
- `POST /search/tineye-batch/run`
- Authentication: Admin JWT token required

**Response:**
```json
{
  "status": "success",
  "processed": 5,
  "batch_id": "tineye_batch_456"
}
```

## Scheduled Tasks

- TinEye batch processing runs hourly
- The scheduler is initialized when the FastAPI app starts
- The scheduler uses a class-based approach for simplicity

## Environment Variables

The following environment variables need to be set:

- `BRAVE_API_KEY` - API key for Brave Search
- `TINEYE_API_KEY` - API key for TinEye API

## Testing

A test script is provided at `test_image_search.py` that can be used to test:

1. Brave Search API functionality
2. TinEye batch processing
3. The scheduler

To run the tests:

```bash
cd backend
python test_image_search.py
```

Note: You'll need to have valid API keys set in your environment variables and at least one test image in the `test_data` directory.

## Architecture

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Image Input │───▶│ Brave Search API │───▶│ Return Results │
└─────────────┘    └──────────────────┘    └─────────────────┘
       │                     │                      ▲
       │                     ▼                      │
       │             ┌──────────────┐               │
       │             │ Good results?│───Yes────────▶│
       │             └──────────────┘               │
       │                     │                      │
       │                     No                     │
       │                     ▼                      │
       │            ┌────────────────┐              │
       └───────────▶│ TinEye Batch   │──────────────┘
                    │ (Hourly)       │
                    └────────────────┘
```

## Integration with Existing Code

- The image search functionality is integrated with the existing credit system
- The same authentication and authorization mechanisms are used
- Results follow the same format as other search types but with image-specific fields 