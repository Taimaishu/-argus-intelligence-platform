"""Knowledge graph service for building entity relationships."""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict
import re
import networkx as nx
from sqlalchemy.orm import Session

from app.core.entity_extraction_service import Entity, EntityType, EntityExtractionService
from app.models.database_models import Document, DocumentChunk
from app.utils.logger import logger


@dataclass
class Relationship:
    """Relationship between two entities."""
    source_entity: Entity
    target_entity: Entity
    relationship_type: str
    strength: float  # 0.0 to 1.0
    context: List[str]  # Textual evidence of relationship
    document_ids: Set[int]  # Documents where relationship was observed
    extra_data: Dict[str, Any]

    def __hash__(self):
        return hash((
            self.source_entity.normalized_name,
            self.target_entity.normalized_name,
            self.relationship_type
        ))


@dataclass
class KnowledgeGraph:
    """Knowledge graph containing entities and their relationships."""
    entities: List[Entity]
    relationships: List[Relationship]
    extra_data: Dict[str, Any]


class KnowledgeGraphService:
    """Service for building knowledge graphs from extracted entities."""

    def __init__(self, entity_service: EntityExtractionService):
        """Initialize knowledge graph service."""
        self.entity_service = entity_service
        self.proximity_window = 100  # Characters
        self.min_co_occurrence = 1
        self.min_relationship_strength = 0.3

        # Relationship pattern templates
        self.relationship_patterns = {
            "works_with": [
                r"{0}.*(?:worked|works|working|collaborated|cooperated).*(?:with|alongside).*{1}",
                r"{0}.*(?:and|&).*{1}.*(?:worked|collaborated)",
            ],
            "located_in": [
                r"{0}.*(?:in|at|located in|based in|stationed at).*{1}",
                r"{0}.*(?:,\s*){1}",  # Name, Location pattern
            ],
            "employed_by": [
                r"{0}.*(?:employee|worked|employed|hired).*(?:at|by|for).*{1}",
                r"{0}.*(?:,\s*)?(?:CEO|CFO|CTO|director|manager|president|VP).*(?:of|at).*{1}",
            ],
            "owns": [
                r"{0}.*(?:owns|owned|owner of|proprietor of).*{1}",
                r"{1}.*(?:owned by|belongs to).*{0}",
            ],
            "met_with": [
                r"{0}.*(?:met|meeting|spoke|talked|discussed).*(?:with)?.*{1}",
                r"{0}.*(?:and|&).*{1}.*(?:met|spoke|meeting)",
            ],
            "traveled_with": [
                r"{0}.*(?:traveled|flew|went|accompanied).*(?:with)?.*{1}",
                r"{0}.*(?:and|&).*{1}.*(?:traveled|flew|went)",
            ],
            "related_to": [
                r"{0}.*(?:related to|connected to|associated with|linked to).*{1}",
            ],
        }

        # Compile patterns
        self.compiled_patterns = {}
        for rel_type, patterns in self.relationship_patterns.items():
            self.compiled_patterns[rel_type] = patterns

    async def build_graph(
        self,
        document_ids: List[int],
        db: Session,
        include_weak_links: bool = False,
        max_entities: int = 200,
        min_confidence: float = 0.6
    ) -> KnowledgeGraph:
        """
        Build a knowledge graph from multiple documents.

        Args:
            document_ids: List of document IDs to process
            db: Database session
            include_weak_links: Whether to include low-strength relationships
            max_entities: Maximum number of entities to include (top N by importance)
            min_confidence: Minimum confidence threshold for entities

        Returns:
            KnowledgeGraph with entities and relationships
        """
        try:
            # Extract entities from all documents
            all_entities = []
            for doc_id in document_ids:
                entities = await self.entity_service.extract_entities(doc_id, db)
                all_entities.extend(entities)

            # Merge duplicate entities
            merged_entities = self.entity_service.merge_duplicate_entities(all_entities)
            logger.info(f"Merged {len(all_entities)} entities into {len(merged_entities)} unique entities")

            # Filter and limit entities for performance
            filtered_entities = self._filter_top_entities(
                merged_entities,
                max_entities=max_entities,
                min_confidence=min_confidence
            )
            logger.info(f"Filtered to top {len(filtered_entities)} entities (max: {max_entities}, min_confidence: {min_confidence})")

            # Build relationships (optimized for performance)
            relationships = await self.detect_relationships(filtered_entities, document_ids, db)

            # Filter weak relationships if requested
            if not include_weak_links:
                relationships = [
                    r for r in relationships
                    if r.strength >= self.min_relationship_strength
                ]

            # Generate metadata
            metadata = {
                "total_entities": len(filtered_entities),
                "total_relationships": len(relationships),
                "document_count": len(document_ids),
                "entity_stats": self.entity_service.get_entity_statistics(filtered_entities),
                "relationship_stats": self._get_relationship_statistics(relationships),
                "filtered_from": len(merged_entities),
            }

            graph = KnowledgeGraph(
                entities=filtered_entities,
                relationships=relationships,
                extra_data=metadata
            )

            logger.info(f"Built knowledge graph: {len(filtered_entities)} entities, {len(relationships)} relationships")
            return graph

        except Exception as e:
            logger.error(f"Failed to build knowledge graph: {e}")
            raise

    def _filter_top_entities(
        self,
        entities: List[Entity],
        max_entities: int,
        min_confidence: float
    ) -> List[Entity]:
        """
        Filter and rank entities by importance.

        Args:
            entities: List of entities to filter
            max_entities: Maximum number of entities to return
            min_confidence: Minimum confidence threshold

        Returns:
            Top N most important entities
        """
        # Filter by confidence
        filtered = [e for e in entities if e.confidence >= min_confidence]

        # Calculate importance score (confidence * mention_count)
        scored_entities = [
            (e, e.confidence * len(e.mentions))
            for e in filtered
        ]

        # Sort by importance score (descending)
        scored_entities.sort(key=lambda x: x[1], reverse=True)

        # Return top N
        top_entities = [e for e, score in scored_entities[:max_entities]]

        logger.info(f"Filtered {len(entities)} entities to {len(top_entities)} (confidence >= {min_confidence})")
        return top_entities

    async def detect_relationships(
        self,
        entities: List[Entity],
        document_ids: List[int],
        db: Session
    ) -> List[Relationship]:
        """
        Detect relationships between entities (optimized).

        Args:
            entities: List of entities to find relationships between
            document_ids: Documents to search for relationships
            db: Database session

        Returns:
            List of detected relationships
        """
        relationships: Dict[Tuple, Relationship] = {}

        # Build chunk-to-entities mapping for faster lookup
        chunk_entity_map = self._build_chunk_entity_map(entities)

        # Get all document chunks
        chunks = db.query(DocumentChunk).filter(
            DocumentChunk.document_id.in_(document_ids)
        ).all()

        logger.info(f"Analyzing {len(chunks)} chunks for relationships between {len(entities)} entities")

        # Analyze each chunk for relationships (only for entities in that chunk)
        for chunk in chunks:
            chunk_key = chunk.id
            if chunk_key not in chunk_entity_map:
                continue

            # Only check entities that appear in this chunk
            chunk_entities = chunk_entity_map[chunk_key]

            if len(chunk_entities) < 2:
                continue

            chunk_relationships = self._detect_relationships_in_text(
                text=chunk.chunk_text,
                entities=list(chunk_entities),
                document_id=chunk.document_id
            )

            # Merge relationships
            for rel in chunk_relationships:
                key = (
                    rel.source_entity.normalized_name,
                    rel.target_entity.normalized_name,
                    rel.relationship_type
                )

                if key in relationships:
                    # Merge context and strengthen relationship
                    relationships[key].context.extend(rel.context)
                    relationships[key].document_ids.update(rel.document_ids)
                    # Increase strength based on additional occurrences
                    relationships[key].strength = min(1.0, relationships[key].strength + 0.1)
                else:
                    relationships[key] = rel

        logger.info(f"Found {len(relationships)} relationships from chunk analysis")

        # Add co-occurrence relationships (limit to avoid O(n²) explosion)
        if len(entities) <= 500:  # Only run co-occurrence for reasonable entity counts
            co_occurrence_rels = self._detect_co_occurrence_relationships(entities)
            for rel in co_occurrence_rels:
                key = (
                    rel.source_entity.normalized_name,
                    rel.target_entity.normalized_name,
                    rel.relationship_type
                )
                if key not in relationships:
                    relationships[key] = rel
            logger.info(f"Added {len(co_occurrence_rels)} co-occurrence relationships")

        return list(relationships.values())

    def _build_chunk_entity_map(self, entities: List[Entity]) -> Dict[int, Set[Entity]]:
        """Build a mapping of chunk IDs to entities that appear in them."""
        chunk_map: Dict[int, Set[Entity]] = defaultdict(set)

        for entity in entities:
            for mention in entity.mentions:
                chunk_id = mention.get("chunk_id")
                if chunk_id:
                    chunk_map[chunk_id].add(entity)

        return chunk_map

    def _detect_relationships_in_text(
        self,
        text: str,
        entities: List[Entity],
        document_id: int
    ) -> List[Relationship]:
        """Detect relationships in a specific text."""
        relationships = []

        # Create entity mention positions
        entity_mentions = []
        for entity in entities:
            # Find all occurrences of entity names in text
            pattern = re.compile(re.escape(entity.name), re.IGNORECASE)
            for match in pattern.finditer(text):
                entity_mentions.append({
                    "entity": entity,
                    "start": match.start(),
                    "end": match.end(),
                    "text": match.group(0)
                })

        # Check proximity between entities
        for i, mention1 in enumerate(entity_mentions):
            for mention2 in entity_mentions[i+1:]:
                distance = abs(mention1["start"] - mention2["start"])

                if distance <= self.proximity_window:
                    # Entities are close - check for relationship patterns
                    start_pos = min(mention1["start"], mention2["start"])
                    end_pos = max(mention1["end"], mention2["end"])
                    context_text = text[max(0, start_pos - 50):min(len(text), end_pos + 50)]

                    relationship_type, strength = self._match_relationship_pattern(
                        mention1["entity"],
                        mention2["entity"],
                        context_text
                    )

                    if relationship_type:
                        relationships.append(Relationship(
                            source_entity=mention1["entity"],
                            target_entity=mention2["entity"],
                            relationship_type=relationship_type,
                            strength=strength,
                            context=[context_text],
                            document_ids={document_id},
                            extra_data={"detection_method": "pattern_proximity"}
                        ))

        return relationships

    def _match_relationship_pattern(
        self,
        entity1: Entity,
        entity2: Entity,
        context: str
    ) -> Tuple[Optional[str], float]:
        """Match relationship patterns in context."""
        # Try each relationship pattern
        for rel_type, patterns in self.compiled_patterns.items():
            for pattern_template in patterns:
                # Create pattern with entity names
                pattern_str = pattern_template.format(
                    re.escape(entity1.name),
                    re.escape(entity2.name)
                )
                pattern = re.compile(pattern_str, re.IGNORECASE | re.DOTALL)

                if pattern.search(context):
                    # Calculate strength based on pattern specificity
                    strength = 0.8  # High confidence for explicit patterns
                    return rel_type, strength

        # Check reverse direction
        for rel_type, patterns in self.compiled_patterns.items():
            for pattern_template in patterns:
                pattern_str = pattern_template.format(
                    re.escape(entity2.name),
                    re.escape(entity1.name)
                )
                pattern = re.compile(pattern_str, re.IGNORECASE | re.DOTALL)

                if pattern.search(context):
                    strength = 0.8
                    return rel_type, strength

        # Default: mentioned_together
        return "mentioned_together", 0.5

    def _detect_co_occurrence_relationships(
        self,
        entities: List[Entity]
    ) -> List[Relationship]:
        """Detect relationships based on co-occurrence in documents."""
        relationships = []

        # Build co-occurrence matrix
        doc_entities: Dict[int, Set[Entity]] = defaultdict(set)

        for entity in entities:
            for mention in entity.mentions:
                if mention["document_id"]:
                    doc_entities[mention["document_id"]].add(entity)

        # Find entity pairs that co-occur
        for doc_id, doc_entity_set in doc_entities.items():
            doc_entity_list = list(doc_entity_set)
            for i, entity1 in enumerate(doc_entity_list):
                for entity2 in doc_entity_list[i+1:]:
                    # Calculate co-occurrence strength
                    # Based on how many documents they appear together
                    co_occurrence_count = sum(
                        1 for other_doc_id, other_entities in doc_entities.items()
                        if entity1 in other_entities and entity2 in other_entities
                    )

                    if co_occurrence_count >= self.min_co_occurrence:
                        strength = min(1.0, co_occurrence_count * 0.2)
                        relationships.append(Relationship(
                            source_entity=entity1,
                            target_entity=entity2,
                            relationship_type="co_occurs_in_documents",
                            strength=strength,
                            context=[f"Co-occurred in {co_occurrence_count} document(s)"],
                            document_ids={doc_id},
                            extra_data={
                                "detection_method": "co_occurrence",
                                "co_occurrence_count": co_occurrence_count
                            }
                        ))

        return relationships

    def get_graph_data(self, graph: KnowledgeGraph) -> Dict[str, Any]:
        """
        Convert knowledge graph to React Flow format.

        Args:
            graph: Knowledge graph to convert

        Returns:
            Dictionary with nodes and edges for React Flow
        """
        nodes = []
        edges = []

        # Create nodes
        for i, entity in enumerate(graph.entities):
            node = {
                "id": f"{entity.type.value}-{i}",
                "type": entity.type.value,
                "data": {
                    "label": entity.name,
                    "entity_type": entity.type.value,
                    "normalized_name": entity.normalized_name,
                    "confidence": round(entity.confidence, 2),
                    "mention_count": len(entity.mentions),
                    "metadata": entity.extra_data
                },
                "position": {"x": 0, "y": 0}  # Will be set by layout algorithm
            }
            nodes.append(node)

        # Create entity ID mapping
        entity_to_node_id = {
            entity.normalized_name: f"{entity.type.value}-{i}"
            for i, entity in enumerate(graph.entities)
        }

        # Create edges
        for i, relationship in enumerate(graph.relationships):
            source_id = entity_to_node_id.get(relationship.source_entity.normalized_name)
            target_id = entity_to_node_id.get(relationship.target_entity.normalized_name)

            if source_id and target_id:
                edge = {
                    "id": f"edge-{i}",
                    "source": source_id,
                    "target": target_id,
                    "type": "default",
                    "data": {
                        "label": relationship.relationship_type.replace("_", " ").title(),
                        "strength": round(relationship.strength, 2),
                        "context": relationship.context[:3],  # First 3 contexts
                        "document_count": len(relationship.document_ids)
                    },
                    "animated": relationship.strength > 0.7  # Animate strong relationships
                }
                edges.append(edge)

        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": graph.extra_data
        }

    def to_networkx_graph(self, graph: KnowledgeGraph) -> nx.Graph:
        """
        Convert knowledge graph to NetworkX graph for analysis.

        Args:
            graph: Knowledge graph to convert

        Returns:
            NetworkX graph
        """
        G = nx.Graph()

        # Add nodes
        for entity in graph.entities:
            G.add_node(
                entity.normalized_name,
                type=entity.type.value,
                name=entity.name,
                confidence=entity.confidence,
                mention_count=len(entity.mentions)
            )

        # Add edges
        for relationship in graph.relationships:
            G.add_edge(
                relationship.source_entity.normalized_name,
                relationship.target_entity.normalized_name,
                relationship_type=relationship.relationship_type,
                strength=relationship.strength,
                context_count=len(relationship.context)
            )

        return G

    def _get_relationship_statistics(self, relationships: List[Relationship]) -> Dict[str, Any]:
        """Generate statistics about relationships."""
        stats = {
            "total": len(relationships),
            "by_type": defaultdict(int),
            "avg_strength": 0.0,
            "strong_relationships": 0,
            "weak_relationships": 0
        }

        for rel in relationships:
            stats["by_type"][rel.relationship_type] += 1
            if rel.strength > 0.7:
                stats["strong_relationships"] += 1
            elif rel.strength < 0.4:
                stats["weak_relationships"] += 1

        if relationships:
            stats["avg_strength"] = sum(r.strength for r in relationships) / len(relationships)

        stats["by_type"] = dict(stats["by_type"])

        return stats
