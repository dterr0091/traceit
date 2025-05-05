from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
import hashlib
from .vector_service import VectorService
from .perplexity_service import perplexity_service
from .redis_service import redis_service
import json

class RouterService:
    @staticmethod
    async def search(
        db: Session,
        query: str,
        query_type: str = "light",
        force_perplexity: bool = False
    ) -> Dict[str, Any]:
        """
        Smart router that decides whether to use local pgvector search or Perplexity API
        
        Args:
            db: Database session
            query: Search query
            query_type: Type of query (light, heavy, video)
            force_perplexity: Force using Perplexity API regardless of local results
            
        Returns:
            Combined search results with origin information
        """
        # Generate query hash for caching
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        cache_key = f"search:{query_hash}"
        
        # Check cache first
        cached_result = redis_service.get_cache(cache_key)
        if cached_result:
            return cached_result
        
        # Step 1: Try pgvector search first
        local_results = VectorService.search_similar_content(
            db=db,
            query=query,
            limit=5,
            similarity_threshold=0.7
        )
        
        # Initialize response
        response = {
            "query": query,
            "query_type": query_type,
            "query_hash": query_hash,
            "perplexity_used": False,
            "results": [],
            "origins": [],
            "confidence": 0.0
        }
        
        # Step 2: Determine if we need Perplexity
        # Use Perplexity if local results have < 3 hits or max similarity < 0.80
        need_perplexity = force_perplexity or len(local_results) < 3
        
        if not need_perplexity and local_results:
            max_similarity = max(result["similarity"] for result in local_results)
            need_perplexity = max_similarity < 0.80
        
        # Step 3: If needed, call Perplexity API
        perplexity_results = []
        if need_perplexity:
            perplexity_data = await perplexity_service.search(query, cache_key=f"perplexity:{query_hash}")
            
            # Process Perplexity results
            if perplexity_data and "results" in perplexity_data:
                perplexity_results = perplexity_data["results"]
                response["perplexity_used"] = True
        
        # Step 4: Merge and rank results
        all_results = []
        
        # Add local results
        for result in local_results:
            all_results.append({
                "source": "local",
                "content_hash": result["content_hash"],
                "content_type": result["content_type"],
                "text": result["raw_text"],
                "url": result["source_url"],
                "timestamp": result["timestamp"],
                "similarity": result["similarity"],
                "engagement": result["engagement_score"],
                "channel_id": result["channel_id"],
                "score": result["similarity"] * (1 + 0.2 * result["engagement_score"])
            })
        
        # Add Perplexity results
        for result in perplexity_results:
            # Extract data from Perplexity result
            url = result.get("url", "")
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            
            # Calculate a score (example formula)
            # In practice, you'd want to normalize and weight these properly
            relevance = result.get("relevance_score", 0.5)
            freshness = result.get("freshness_score", 0.5)
            score = 0.6 * relevance + 0.4 * freshness
            
            all_results.append({
                "source": "perplexity",
                "text": f"{title}\n{snippet}",
                "url": url,
                "timestamp": result.get("published_date"),
                "similarity": relevance,
                "engagement": result.get("engagement_score", 0),
                "channel_id": result.get("domain"),
                "score": score
            })
            
            # Store this result in our vector database for future searches
            if snippet:
                try:
                    VectorService.store_embedding(
                        db=db,
                        content=snippet,
                        content_type="text",
                        source_url=url,
                        channel_id=result.get("domain"),
                        timestamp=result.get("published_date"),
                        engagement_score=result.get("engagement_score", 0),
                        metadata={
                            "title": title,
                            "domain": result.get("domain"),
                            "perplexity_id": result.get("id")
                        }
                    )
                except Exception as e:
                    # Log error but continue
                    print(f"Error storing embedding: {str(e)}")
        
        # Step 5: Sort by score (descending)
        all_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Step 6: Find the origin (earliest verifiable source)
        origins = []
        if all_results:
            # Group by channel/domain to find earliest from each source
            sources = {}
            for result in all_results:
                channel = result.get("channel_id")
                if channel and result.get("timestamp"):
                    if channel not in sources or sources[channel]["timestamp"] > result["timestamp"]:
                        sources[channel] = result
            
            # Convert to list and sort by timestamp (ascending)
            origins = list(sources.values())
            origins.sort(key=lambda x: x["timestamp"] if x["timestamp"] else "9999-12-31")
        
        # Step 7: Calculate overall confidence
        confidence = 0.0
        if all_results:
            # Average of top 3 scores
            top_scores = [r["score"] for r in all_results[:3]] if len(all_results) >= 3 else [r["score"] for r in all_results]
            confidence = sum(top_scores) / len(top_scores)
        
        # Finalize response
        response["results"] = all_results[:10]  # Limit to top 10
        response["origins"] = origins[:3]  # Top 3 earliest sources
        response["confidence"] = confidence
        
        # Cache the result
        redis_service.set_cache(cache_key, response, ttl_days=30)
        
        return response 