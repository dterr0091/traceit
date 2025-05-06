import os
import logging
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import asyncio
import httpx
from uuid import uuid4

from ..services.redis_service import RedisService

logger = logging.getLogger(__name__)

class LineageService:
    """
    Service for managing origin lineage information.
    Handles storage, retrieval, and tracking of origin data,
    with special handling for composite media.
    """
    
    def __init__(self):
        """Initialize the LineageService with required dependencies."""
        self.redis_service = RedisService()
        self.neo4j_enabled = bool(os.getenv("NEO4J_URI"))
        
        # Will be initialized if Neo4j is enabled
        self.neo4j_driver = None
        
        if self.neo4j_enabled:
            # Import here to avoid dependency on Neo4j when not needed
            from neo4j import AsyncGraphDatabase
            self.neo4j_driver = AsyncGraphDatabase.driver(
                os.getenv("NEO4J_URI"),
                auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
            )
            logger.info("Neo4j lineage graph enabled")
        else:
            logger.info("Neo4j lineage graph disabled - will use Redis for storage")
    
    async def store_origin(self, 
                          artifact_id: str, 
                          artifact_type: str, 
                          origin_data: Dict[str, Any],
                          is_composite: bool = False,
                          audio_origin: Optional[Dict[str, Any]] = None, 
                          visual_origin: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Store origin information for an artifact.
        
        Args:
            artifact_id: Unique identifier for the artifact (e.g., hash)
            artifact_type: Type of artifact (text, image, audio, video)
            origin_data: Origin information
            is_composite: Whether this is a composite media (e.g., audio+visual)
            audio_origin: Origin data for audio component (if composite)
            visual_origin: Origin data for visual component (if composite)
            
        Returns:
            Dict containing storage results
        """
        # Create lineage record
        lineage_record = {
            "artifact_id": artifact_id,
            "artifact_type": artifact_type,
            "origin_data": origin_data,
            "is_composite": is_composite,
            "audio_origin": audio_origin,
            "visual_origin": visual_origin,
            "timestamp": datetime.utcnow().isoformat(),
            "record_id": str(uuid4())
        }
        
        # Store in Redis (fast retrieval cache)
        redis_key = f"lineage:{artifact_id}"
        await self.redis_service.set(redis_key, lineage_record, expire_seconds=60*60*24*90)  # 90 days
        
        # Store in Neo4j if enabled
        if self.neo4j_enabled:
            try:
                await self._store_in_graph(lineage_record)
            except Exception as e:
                logger.error(f"Error storing lineage in Neo4j: {str(e)}")
                return {
                    "success": True,
                    "redis_stored": True,
                    "graph_stored": False,
                    "error": str(e)
                }
        
        return {
            "success": True,
            "redis_stored": True,
            "graph_stored": self.neo4j_enabled,
            "record_id": lineage_record["record_id"]
        }
    
    async def get_origin(self, artifact_id: str) -> Dict[str, Any]:
        """
        Retrieve origin information for an artifact.
        
        Args:
            artifact_id: Unique identifier for the artifact
            
        Returns:
            Dict containing origin information
        """
        # Try Redis first (fast cache)
        redis_key = f"lineage:{artifact_id}"
        cached_data = await self.redis_service.get(redis_key)
        
        if cached_data:
            return cached_data
        
        # If not in Redis and Neo4j is enabled, try there
        if self.neo4j_enabled:
            try:
                graph_data = await self._get_from_graph(artifact_id)
                if graph_data:
                    # Cache in Redis for future queries
                    await self.redis_service.set(redis_key, graph_data, expire_seconds=60*60*24)  # 1 day
                    return graph_data
            except Exception as e:
                logger.error(f"Error retrieving lineage from Neo4j: {str(e)}")
        
        return None
    
    async def _store_in_graph(self, lineage_record: Dict[str, Any]) -> None:
        """
        Store lineage information in Neo4j graph database.
        Special handling for composite media.
        
        Args:
            lineage_record: Lineage data to store
        """
        if not self.neo4j_driver:
            return
        
        async with self.neo4j_driver.session() as session:
            # Create artifact node
            artifact_query = """
            MERGE (a:Artifact {id: $artifact_id})
            SET a.type = $artifact_type,
                a.created_at = $timestamp,
                a.is_composite = $is_composite
            RETURN a
            """
            
            await session.run(
                artifact_query,
                artifact_id=lineage_record["artifact_id"],
                artifact_type=lineage_record["artifact_type"],
                timestamp=lineage_record["timestamp"],
                is_composite=lineage_record["is_composite"]
            )
            
            # Handle composite media differently
            if lineage_record["is_composite"]:
                await self._store_composite_origins(
                    session,
                    lineage_record["artifact_id"],
                    lineage_record["audio_origin"],
                    lineage_record["visual_origin"]
                )
            else:
                # For non-composite media, create a single origin relationship
                origin_query = """
                MATCH (a:Artifact {id: $artifact_id})
                MERGE (o:Origin {id: $origin_id})
                SET o.url = $url,
                    o.title = $title,
                    o.channel_id = $channel_id,
                    o.timestamp = $origin_timestamp,
                    o.confidence = $confidence
                MERGE (a)-[r:ORIGINATED_FROM]->(o)
                SET r.confidence = $confidence
                RETURN o
                """
                
                origin_data = lineage_record["origin_data"]
                if origin_data and origin_data.get("found", False):
                    hit = origin_data.get("hit", {})
                    await session.run(
                        origin_query,
                        artifact_id=lineage_record["artifact_id"],
                        origin_id=hit.get("id", str(uuid4())),
                        url=hit.get("url", ""),
                        title=hit.get("title", ""),
                        channel_id=hit.get("channel_id", ""),
                        origin_timestamp=hit.get("timestamp", ""),
                        confidence=origin_data.get("confidence", 0)
                    )
    
    async def _store_composite_origins(self, 
                                      session,
                                      artifact_id: str,
                                      audio_origin: Dict[str, Any],
                                      visual_origin: Dict[str, Any]) -> None:
        """
        Store composite media origins in Neo4j.
        Creates separate AUDIO_FROM and VISUAL_FROM relationships.
        
        Args:
            session: Neo4j session
            artifact_id: Artifact ID
            audio_origin: Audio origin data
            visual_origin: Visual origin data
        """
        # Store audio origin
        if audio_origin and audio_origin.get("found", False):
            audio_query = """
            MATCH (a:Artifact {id: $artifact_id})
            MERGE (o:Origin {id: $origin_id})
            SET o.url = $url,
                o.title = $title,
                o.channel_id = $channel_id,
                o.timestamp = $origin_timestamp,
                o.confidence = $confidence,
                o.type = 'audio'
            MERGE (a)-[r:AUDIO_FROM]->(o)
            SET r.confidence = $confidence
            RETURN o
            """
            
            hit = audio_origin.get("hit", {})
            await session.run(
                audio_query,
                artifact_id=artifact_id,
                origin_id=hit.get("id", str(uuid4())),
                url=hit.get("url", ""),
                title=hit.get("title", ""),
                channel_id=hit.get("channel_id", ""),
                origin_timestamp=hit.get("timestamp", ""),
                confidence=audio_origin.get("confidence", 0)
            )
        
        # Store visual origin
        if visual_origin and visual_origin.get("found", False):
            visual_query = """
            MATCH (a:Artifact {id: $artifact_id})
            MERGE (o:Origin {id: $origin_id})
            SET o.url = $url,
                o.title = $title,
                o.channel_id = $channel_id,
                o.timestamp = $origin_timestamp,
                o.confidence = $confidence,
                o.type = 'visual',
                o.matching_frames = $matching_frames
            MERGE (a)-[r:VISUAL_FROM]->(o)
            SET r.confidence = $confidence,
                r.matching_frames = $matching_frames
            RETURN o
            """
            
            hit = visual_origin.get("hit", {})
            await session.run(
                visual_query,
                artifact_id=artifact_id,
                origin_id=hit.get("id", str(uuid4())),
                url=hit.get("url", ""),
                title=hit.get("title", ""),
                channel_id=hit.get("channel_id", ""),
                origin_timestamp=hit.get("timestamp", ""),
                confidence=visual_origin.get("confidence", 0),
                matching_frames=visual_origin.get("matching_frames", 0)
            )
    
    async def _get_from_graph(self, artifact_id: str) -> Dict[str, Any]:
        """
        Retrieve lineage information from Neo4j graph.
        
        Args:
            artifact_id: Artifact ID to retrieve
            
        Returns:
            Lineage record or None
        """
        if not self.neo4j_driver:
            return None
        
        async with self.neo4j_driver.session() as session:
            # Check if this is a composite media
            artifact_query = """
            MATCH (a:Artifact {id: $artifact_id})
            RETURN a.is_composite AS is_composite
            """
            
            result = await session.run(artifact_query, artifact_id=artifact_id)
            record = await result.single()
            
            if not record:
                return None
                
            is_composite = record["is_composite"]
            
            if is_composite:
                # Get composite origins (audio and visual)
                composite_query = """
                MATCH (a:Artifact {id: $artifact_id})
                OPTIONAL MATCH (a)-[audio:AUDIO_FROM]->(ao:Origin)
                OPTIONAL MATCH (a)-[visual:VISUAL_FROM]->(vo:Origin)
                RETURN a, audio, ao, visual, vo
                """
                
                result = await session.run(composite_query, artifact_id=artifact_id)
                record = await result.single()
                
                if not record:
                    return None
                
                # Build response object
                lineage_record = {
                    "artifact_id": artifact_id,
                    "is_composite": True,
                    "audio_origin": self._build_origin_from_record(record.get("ao"), record.get("audio")),
                    "visual_origin": self._build_origin_from_record(record.get("vo"), record.get("visual")),
                    "timestamp": record.get("a").get("created_at")
                }
                
                return lineage_record
            else:
                # Get single origin
                origin_query = """
                MATCH (a:Artifact {id: $artifact_id})-[r:ORIGINATED_FROM]->(o:Origin)
                RETURN a, r, o
                """
                
                result = await session.run(origin_query, artifact_id=artifact_id)
                record = await result.single()
                
                if not record:
                    return None
                
                # Build response object
                lineage_record = {
                    "artifact_id": artifact_id,
                    "is_composite": False,
                    "origin_data": self._build_origin_from_record(record.get("o"), record.get("r")),
                    "timestamp": record.get("a").get("created_at")
                }
                
                return lineage_record
    
    def _build_origin_from_record(self, origin_node, relationship) -> Dict[str, Any]:
        """
        Build origin data dictionary from Neo4j nodes and relationships.
        
        Args:
            origin_node: Neo4j Origin node
            relationship: Neo4j relationship
            
        Returns:
            Origin data dictionary
        """
        if not origin_node or not relationship:
            return None
        
        return {
            "found": True,
            "confidence": relationship.get("confidence", 0),
            "matching_frames": relationship.get("matching_frames", 0) if "matching_frames" in relationship else None,
            "hit": {
                "id": origin_node.get("id", ""),
                "url": origin_node.get("url", ""),
                "title": origin_node.get("title", ""),
                "channel_id": origin_node.get("channel_id", ""),
                "timestamp": origin_node.get("timestamp", "")
            }
        }
    
    async def build_multi_hop_graph(self) -> Dict[str, Any]:
        """
        Build multi-hop lineage graph by creating SPREAD_TO relationships 
        between content that shares the same origin.
        
        This is a nightly batch job that:
        1. Identifies artifacts that share the same origin
        2. Creates SPREAD_TO relationships between them
        3. Computes spread metrics (hop count, path, etc.)
        
        Returns:
            Dict containing update statistics
        """
        if not self.neo4j_driver:
            return {"status": "error", "reason": "Neo4j not enabled"}
        
        stats = {
            "start_time": datetime.utcnow().isoformat(),
            "relationships_created": 0,
            "artifacts_processed": 0,
            "errors": []
        }
        
        async with self.neo4j_driver.session() as session:
            try:
                # First, create SPREAD_TO relationships between artifacts that share the same origin
                spread_query = """
                MATCH (a1:Artifact)-[:ORIGINATED_FROM]->(o:Origin)<-[:ORIGINATED_FROM]-(a2:Artifact)
                WHERE a1 <> a2 AND NOT EXISTS((a1)-[:SPREAD_TO]-(a2))
                WITH a1, a2, o
                CREATE (a1)-[r:SPREAD_TO {
                    created_at: datetime(),
                    origin_id: o.id,
                    hop_count: 1
                }]->(a2)
                RETURN count(r) as rel_count
                """
                
                result = await session.run(spread_query)
                record = await result.single()
                stats["relationships_created"] += record["rel_count"] if record else 0
                
                # Create relationships for composite media (audio)
                audio_spread_query = """
                MATCH (a1:Artifact)-[:AUDIO_FROM]->(o:Origin)<-[:AUDIO_FROM]-(a2:Artifact)
                WHERE a1 <> a2 AND NOT EXISTS((a1)-[:AUDIO_SPREAD_TO]-(a2))
                WITH a1, a2, o
                CREATE (a1)-[r:AUDIO_SPREAD_TO {
                    created_at: datetime(),
                    origin_id: o.id,
                    hop_count: 1
                }]->(a2)
                RETURN count(r) as rel_count
                """
                
                result = await session.run(audio_spread_query)
                record = await result.single()
                stats["relationships_created"] += record["rel_count"] if record else 0
                
                # Create relationships for composite media (visual)
                visual_spread_query = """
                MATCH (a1:Artifact)-[:VISUAL_FROM]->(o:Origin)<-[:VISUAL_FROM]-(a2:Artifact)
                WHERE a1 <> a2 AND NOT EXISTS((a1)-[:VISUAL_SPREAD_TO]-(a2))
                WITH a1, a2, o
                CREATE (a1)-[r:VISUAL_SPREAD_TO {
                    created_at: datetime(),
                    origin_id: o.id,
                    hop_count: 1
                }]->(a2)
                RETURN count(r) as rel_count
                """
                
                result = await session.run(visual_spread_query)
                record = await result.single()
                stats["relationships_created"] += record["rel_count"] if record else 0
                
                # Get count of artifacts processed
                count_query = """
                MATCH (a:Artifact)
                RETURN count(a) as artifact_count
                """
                
                result = await session.run(count_query)
                record = await result.single()
                stats["artifacts_processed"] = record["artifact_count"] if record else 0
                
                # Update metrics for multi-hop chains (transitive closure)
                transitive_query = """
                MATCH (a1:Artifact)-[r1:SPREAD_TO]->(a2:Artifact)-[r2:SPREAD_TO]->(a3:Artifact)
                WHERE a1 <> a3 AND NOT EXISTS((a1)-[:SPREAD_TO]->(a3))
                WITH a1, a3, min(r1.hop_count + r2.hop_count) as total_hops
                CREATE (a1)-[r:SPREAD_TO {
                    created_at: datetime(),
                    hop_count: total_hops
                }]->(a3)
                RETURN count(r) as rel_count
                """
                
                result = await session.run(transitive_query)
                record = await result.single()
                stats["multi_hop_relationships"] = record["rel_count"] if record else 0
                stats["relationships_created"] += stats["multi_hop_relationships"]
                
                # Update engagement metrics based on spread count
                engagement_query = """
                MATCH (o:Origin)<-[:ORIGINATED_FROM]-(a:Artifact)
                WITH o, count(a) as spread_count
                SET o.spread_count = spread_count,
                    o.engagement_score = CASE
                      WHEN spread_count > 100 THEN 5
                      WHEN spread_count > 50 THEN 4
                      WHEN spread_count > 20 THEN 3
                      WHEN spread_count > 5 THEN 2
                      ELSE 1
                    END
                RETURN count(o) as origins_updated
                """
                
                result = await session.run(engagement_query)
                record = await result.single()
                stats["origins_updated"] = record["origins_updated"] if record else 0
                
                stats["status"] = "success"
                stats["end_time"] = datetime.utcnow().isoformat()
                
                return stats
                
            except Exception as e:
                logger.error(f"Error building multi-hop graph: {str(e)}")
                stats["status"] = "error"
                stats["error"] = str(e)
                stats["end_time"] = datetime.utcnow().isoformat()
                return stats
    
    async def get_spread_view(self, artifact_id: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        Get the spread view for an artifact showing how content has spread.
        
        Args:
            artifact_id: ID of the artifact to get spread view for
            max_depth: Maximum depth of the spread graph to return
            
        Returns:
            Dict containing spread view data
        """
        if not self.neo4j_driver:
            return {"status": "error", "reason": "Neo4j not enabled"}
        
        async with self.neo4j_driver.session() as session:
            try:
                # Query to get the spread graph for standard media
                spread_query = f"""
                MATCH path = (a:Artifact {{id: $artifact_id}})-[r:SPREAD_TO*1..{max_depth}]->(related:Artifact)
                WITH related, min(length(path)) as min_path_length
                MATCH (related)-[:ORIGINATED_FROM]->(ro:Origin)
                RETURN related.id as artifact_id, 
                       related.type as artifact_type,
                       min_path_length as hop_count,
                       ro.url as url,
                       ro.title as title,
                       ro.channel_id as channel_id,
                       ro.timestamp as timestamp,
                       ro.spread_count as spread_count,
                       ro.engagement_score as engagement_score
                ORDER BY min_path_length, ro.timestamp
                """
                
                result = await session.run(spread_query, artifact_id=artifact_id)
                records = await result.fetch(100)  # Limit to 100 results for performance
                
                # Check if this is a composite media
                composite_check = """
                MATCH (a:Artifact {id: $artifact_id})
                RETURN a.is_composite as is_composite
                """
                
                composite_result = await session.run(composite_check, artifact_id=artifact_id)
                composite_record = await composite_result.single()
                is_composite = composite_record["is_composite"] if composite_record else False
                
                spread_items = []
                
                # Process standard spread items
                for record in records:
                    spread_items.append({
                        "artifact_id": record["artifact_id"],
                        "artifact_type": record["artifact_type"],
                        "hop_count": record["hop_count"],
                        "url": record["url"],
                        "title": record["title"],
                        "channel_id": record["channel_id"],
                        "timestamp": record["timestamp"],
                        "spread_count": record["spread_count"],
                        "engagement_score": record["engagement_score"]
                    })
                
                # If composite, add audio and visual spread items
                if is_composite:
                    # Audio spread query
                    audio_query = f"""
                    MATCH path = (a:Artifact {{id: $artifact_id}})-[r:AUDIO_SPREAD_TO*1..{max_depth}]->(related:Artifact)
                    WITH related, min(length(path)) as min_path_length
                    MATCH (related)-[:AUDIO_FROM]->(ro:Origin)
                    RETURN related.id as artifact_id, 
                           related.type as artifact_type,
                           min_path_length as hop_count,
                           ro.url as url,
                           ro.title as title,
                           ro.channel_id as channel_id,
                           ro.timestamp as timestamp,
                           ro.spread_count as spread_count,
                           ro.engagement_score as engagement_score,
                           'audio' as component
                    ORDER BY min_path_length, ro.timestamp
                    """
                    
                    audio_result = await session.run(audio_query, artifact_id=artifact_id)
                    audio_records = await audio_result.fetch(50)
                    
                    for record in audio_records:
                        spread_items.append({
                            "artifact_id": record["artifact_id"],
                            "artifact_type": record["artifact_type"],
                            "hop_count": record["hop_count"],
                            "url": record["url"],
                            "title": record["title"],
                            "channel_id": record["channel_id"],
                            "timestamp": record["timestamp"],
                            "spread_count": record["spread_count"],
                            "engagement_score": record["engagement_score"],
                            "component": "audio"
                        })
                    
                    # Visual spread query
                    visual_query = f"""
                    MATCH path = (a:Artifact {{id: $artifact_id}})-[r:VISUAL_SPREAD_TO*1..{max_depth}]->(related:Artifact)
                    WITH related, min(length(path)) as min_path_length
                    MATCH (related)-[:VISUAL_FROM]->(ro:Origin)
                    RETURN related.id as artifact_id, 
                           related.type as artifact_type,
                           min_path_length as hop_count,
                           ro.url as url,
                           ro.title as title,
                           ro.channel_id as channel_id,
                           ro.timestamp as timestamp,
                           ro.spread_count as spread_count,
                           ro.engagement_score as engagement_score,
                           'visual' as component
                    ORDER BY min_path_length, ro.timestamp
                    """
                    
                    visual_result = await session.run(visual_query, artifact_id=artifact_id)
                    visual_records = await visual_result.fetch(50)
                    
                    for record in visual_records:
                        spread_items.append({
                            "artifact_id": record["artifact_id"],
                            "artifact_type": record["artifact_type"],
                            "hop_count": record["hop_count"],
                            "url": record["url"],
                            "title": record["title"],
                            "channel_id": record["channel_id"],
                            "timestamp": record["timestamp"],
                            "spread_count": record["spread_count"],
                            "engagement_score": record["engagement_score"],
                            "component": "visual"
                        })
                
                # Get origin metadata as well
                origin_query = """
                MATCH (a:Artifact {id: $artifact_id})
                OPTIONAL MATCH (a)-[:ORIGINATED_FROM]->(o:Origin)
                OPTIONAL MATCH (a)-[:AUDIO_FROM]->(ao:Origin)
                OPTIONAL MATCH (a)-[:VISUAL_FROM]->(vo:Origin)
                RETURN a.is_composite as is_composite,
                       o as origin,
                       ao as audio_origin,
                       vo as visual_origin
                """
                
                origin_result = await session.run(origin_query, artifact_id=artifact_id)
                origin_record = await origin_result.single()
                
                origin_data = None
                audio_origin_data = None
                visual_origin_data = None
                
                if origin_record:
                    if origin_record["origin"]:
                        origin_data = {
                            "url": origin_record["origin"].get("url", ""),
                            "title": origin_record["origin"].get("title", ""),
                            "channel_id": origin_record["origin"].get("channel_id", ""),
                            "timestamp": origin_record["origin"].get("timestamp", ""),
                            "spread_count": origin_record["origin"].get("spread_count", 0),
                            "engagement_score": origin_record["origin"].get("engagement_score", 0)
                        }
                    
                    if origin_record["audio_origin"]:
                        audio_origin_data = {
                            "url": origin_record["audio_origin"].get("url", ""),
                            "title": origin_record["audio_origin"].get("title", ""),
                            "channel_id": origin_record["audio_origin"].get("channel_id", ""),
                            "timestamp": origin_record["audio_origin"].get("timestamp", ""),
                            "spread_count": origin_record["audio_origin"].get("spread_count", 0),
                            "engagement_score": origin_record["audio_origin"].get("engagement_score", 0),
                            "component": "audio"
                        }
                    
                    if origin_record["visual_origin"]:
                        visual_origin_data = {
                            "url": origin_record["visual_origin"].get("url", ""),
                            "title": origin_record["visual_origin"].get("title", ""),
                            "channel_id": origin_record["visual_origin"].get("channel_id", ""),
                            "timestamp": origin_record["visual_origin"].get("timestamp", ""),
                            "spread_count": origin_record["visual_origin"].get("spread_count", 0),
                            "engagement_score": origin_record["visual_origin"].get("engagement_score", 0),
                            "component": "visual"
                        }
                
                # Construct final response
                return {
                    "status": "success",
                    "artifact_id": artifact_id,
                    "is_composite": is_composite,
                    "origin": origin_data,
                    "audio_origin": audio_origin_data,
                    "visual_origin": visual_origin_data,
                    "spread_items": spread_items,
                    "total_items": len(spread_items)
                }
                
            except Exception as e:
                logger.error(f"Error getting spread view: {str(e)}")
                return {
                    "status": "error", 
                    "error": str(e), 
                    "artifact_id": artifact_id
                }
    
    async def close(self):
        """Close Neo4j connection when service is shutting down."""
        if self.neo4j_driver:
            await self.neo4j_driver.close() 