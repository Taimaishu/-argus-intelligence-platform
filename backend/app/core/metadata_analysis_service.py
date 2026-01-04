"""Metadata analysis service for extracting insights from entity and document metadata."""

import re
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.database_models import (
    EntityKnowledge,
    CanvasNode,
    CanvasEdge,
    Document,
    DocumentChunk,
)
from app.utils.logger import logger


class MetadataAnalysisService:
    """Service for analyzing metadata across all entities and drawing connections."""

    def __init__(self):
        """Initialize metadata analysis service."""
        self.date_patterns = [
            r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b',  # MM/DD/YYYY or DD/MM/YYYY
            r'\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b',  # YYYY/MM/DD
            r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b',  # Month DD, YYYY
            r'\b(\d{4})\b',  # Just year
        ]

        self.location_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2})\b',  # City, ST
            r'\b([A-Z][a-z]+\s+(?:Island|Beach|City|Street|Avenue|Road|Drive))\b',  # Location names
        ]

        self.title_patterns = [
            r'\b(Prince|Princess|King|Queen|Duke|Duchess|Lord|Lady|Sir|Dame)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\b(President|Vice President|Senator|Representative|Governor|Mayor)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\b(Dr\.|Doctor|Professor|Judge)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\b(CEO|CFO|CTO|Director|Manager)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]

        self.organization_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Inc\.|LLC|Corp\.|Corporation|Company|Foundation|Trust)\b',
            r'\b(FBI|CIA|DOJ|IRS|SEC)\b',
        ]

    def extract_metadata_from_text(self, text: str) -> Dict[str, Any]:
        """Extract structured metadata from text."""
        metadata = {
            "dates": [],
            "locations": [],
            "titles": [],
            "organizations": [],
            "phone_numbers": [],
            "emails": [],
            "financial_amounts": [],
        }

        # Extract dates
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            metadata["dates"].extend(matches)

        # Extract locations
        for pattern in self.location_patterns:
            matches = re.findall(pattern, text)
            metadata["locations"].extend(matches)

        # Extract titles
        for pattern in self.title_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    metadata["titles"].append(f"{match[0]} {match[1]}")

        # Extract organizations
        for pattern in self.organization_patterns:
            matches = re.findall(pattern, text)
            metadata["organizations"].extend(matches)

        # Extract phone numbers
        phone_pattern = r'\b(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})\b'
        metadata["phone_numbers"] = re.findall(phone_pattern, text)

        # Extract emails
        email_pattern = r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
        metadata["emails"] = re.findall(email_pattern, text)

        # Extract financial amounts
        money_pattern = r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'
        metadata["financial_amounts"] = re.findall(money_pattern, text)

        # Remove duplicates
        for key in metadata:
            if isinstance(metadata[key], list):
                metadata[key] = list(set(metadata[key]))

        return metadata

    def analyze_entity_metadata(self, entity_name: str, db: Session) -> Dict[str, Any]:
        """Analyze all metadata related to an entity."""
        try:
            # Get all document chunks mentioning the entity
            chunks = db.query(DocumentChunk).filter(
                DocumentChunk.chunk_text.ilike(f'%{entity_name}%')
            ).all()

            # Aggregate metadata from all mentions
            aggregated_metadata = {
                "dates": set(),
                "locations": set(),
                "titles": set(),
                "organizations": set(),
                "phone_numbers": set(),
                "emails": set(),
                "financial_amounts": set(),
                "co_occurring_entities": defaultdict(int),
                "documents": set(),
                "total_mentions": len(chunks),
            }

            # Get all canvas nodes to check for co-occurrences
            all_nodes = db.query(CanvasNode).all()
            entity_names = [node.data.get('label', '') for node in all_nodes if node.data.get('label')]

            for chunk in chunks:
                # Extract metadata from chunk
                chunk_metadata = self.extract_metadata_from_text(chunk.chunk_text)

                # Aggregate
                for key in ["dates", "locations", "titles", "organizations", "phone_numbers", "emails", "financial_amounts"]:
                    if key in chunk_metadata:
                        aggregated_metadata[key].update(chunk_metadata[key])

                # Track co-occurring entities
                chunk_lower = chunk.chunk_text.lower()
                for other_entity in entity_names:
                    if other_entity.lower() != entity_name.lower() and other_entity.lower() in chunk_lower:
                        aggregated_metadata["co_occurring_entities"][other_entity] += 1

                # Track documents
                doc = db.query(Document).filter(Document.id == chunk.document_id).first()
                if doc:
                    aggregated_metadata["documents"].add(doc.filename)

            # Convert sets to sorted lists
            for key in ["dates", "locations", "titles", "organizations", "phone_numbers", "emails", "financial_amounts", "documents"]:
                aggregated_metadata[key] = sorted(list(aggregated_metadata[key]))

            # Convert co-occurring entities to sorted list
            aggregated_metadata["co_occurring_entities"] = sorted(
                [{"entity": entity, "mentions": count}
                 for entity, count in aggregated_metadata["co_occurring_entities"].items()],
                key=lambda x: x["mentions"],
                reverse=True
            )

            return aggregated_metadata

        except Exception as e:
            logger.error(f"Error analyzing metadata for {entity_name}: {e}")
            return {}

    def find_metadata_connections(self, db: Session) -> Dict[str, Any]:
        """Find all connections between entities based on shared metadata."""
        try:
            nodes = db.query(CanvasNode).all()
            connections = {
                "shared_dates": [],
                "shared_locations": [],
                "shared_organizations": [],
                "shared_documents": [],
                "temporal_proximity": [],
                "geographic_proximity": [],
            }

            # Get metadata for all entities
            entity_metadata = {}
            for node in nodes:
                entity_name = node.data.get('label', '')
                if entity_name:
                    entity_metadata[entity_name] = self.analyze_entity_metadata(entity_name, db)

            # Find shared metadata
            entity_names = list(entity_metadata.keys())
            for i, entity1 in enumerate(entity_names):
                for entity2 in entity_names[i+1:]:
                    meta1 = entity_metadata[entity1]
                    meta2 = entity_metadata[entity2]

                    # Shared dates
                    shared_dates = set(meta1.get("dates", [])) & set(meta2.get("dates", []))
                    if shared_dates:
                        connections["shared_dates"].append({
                            "entities": [entity1, entity2],
                            "dates": list(shared_dates),
                            "significance": "Both mentioned on same dates"
                        })

                    # Shared locations
                    shared_locs = set(meta1.get("locations", [])) & set(meta2.get("locations", []))
                    if shared_locs:
                        connections["shared_locations"].append({
                            "entities": [entity1, entity2],
                            "locations": list(shared_locs),
                            "significance": "Both associated with same locations"
                        })

                    # Shared organizations
                    shared_orgs = set(meta1.get("organizations", [])) & set(meta2.get("organizations", []))
                    if shared_orgs:
                        connections["shared_organizations"].append({
                            "entities": [entity1, entity2],
                            "organizations": list(shared_orgs),
                            "significance": "Both connected to same organizations"
                        })

                    # Shared documents
                    shared_docs = set(meta1.get("documents", [])) & set(meta2.get("documents", []))
                    if shared_docs:
                        connections["shared_documents"].append({
                            "entities": [entity1, entity2],
                            "documents": list(shared_docs),
                            "significance": "Both mentioned in same documents"
                        })

            return connections

        except Exception as e:
            logger.error(f"Error finding metadata connections: {e}")
            return {}

    async def generate_metadata_theories(
        self,
        entity_name: str,
        metadata: Dict[str, Any],
        connections: Dict[str, Any],
        db: Session,
        ai_provider: str = "openai",
        ai_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate theories and conclusions based on metadata analysis."""
        try:
            from app.core.chat_service import ChatService
            chat = ChatService()

            # Build prompt with metadata
            prompt = f"""Analyze this entity's metadata and draw investigative conclusions:

ENTITY: {entity_name}

METADATA ANALYSIS:
- Total Mentions: {metadata.get('total_mentions', 0)}
- Documents: {', '.join(metadata.get('documents', [])[:5])}
- Dates Mentioned: {', '.join(metadata.get('dates', [])[:10])}
- Locations: {', '.join(metadata.get('locations', [])[:10])}
- Associated Organizations: {', '.join(metadata.get('organizations', [])[:10])}
- Financial Amounts: {', '.join(metadata.get('financial_amounts', [])[:5])}

CO-OCCURRING ENTITIES:
{chr(10).join([f"- {item['entity']} ({item['mentions']} mentions together)"
               for item in metadata.get('co_occurring_entities', [])[:10]])}

METADATA CONNECTIONS:
Shared Dates: {len(connections.get('shared_dates', []))} connections
Shared Locations: {len(connections.get('shared_locations', []))} connections
Shared Organizations: {len(connections.get('shared_organizations', []))} connections
Shared Documents: {len(connections.get('shared_documents', []))} connections

Based on this metadata, provide:

1. TEMPORAL ANALYSIS:
[When was this entity most active? What time periods are significant?]

2. GEOGRAPHIC ANALYSIS:
[What locations are most associated? Why are they significant?]

3. NETWORK ANALYSIS:
[Who are the key connections? What do the co-occurrences suggest?]

4. FINANCIAL ANALYSIS:
[What financial patterns emerge from the metadata?]

5. THEORIES & CONCLUSIONS:
[What conclusions can be drawn from all this metadata? What theories emerge?]

6. INVESTIGATIVE LEADS:
[What should be investigated further based on this metadata?]"""

            analysis = await chat.generate_response(prompt, None, db, ai_provider, ai_model)

            # Parse response into structured format
            sections = {
                "temporal_analysis": "",
                "geographic_analysis": "",
                "network_analysis": "",
                "financial_analysis": "",
                "theories": "",
                "leads": ""
            }

            current = None
            for line in analysis.split('\n'):
                upper = line.strip().upper()
                if 'TEMPORAL ANALYSIS' in upper:
                    current = 'temporal_analysis'
                elif 'GEOGRAPHIC ANALYSIS' in upper:
                    current = 'geographic_analysis'
                elif 'NETWORK ANALYSIS' in upper:
                    current = 'network_analysis'
                elif 'FINANCIAL ANALYSIS' in upper:
                    current = 'financial_analysis'
                elif 'THEORIES' in upper or 'CONCLUSIONS' in upper:
                    current = 'theories'
                elif 'LEADS' in upper or 'INVESTIGATIVE' in upper:
                    current = 'leads'
                elif current and line.strip():
                    sections[current] += line.strip() + " "

            return {
                "raw_analysis": analysis,
                **sections,
                "metadata_summary": metadata,
                "connections_found": len(connections.get('shared_dates', [])) +
                                   len(connections.get('shared_locations', [])) +
                                   len(connections.get('shared_organizations', []))
            }

        except Exception as e:
            logger.error(f"Error generating metadata theories: {e}")
            return {"error": str(e)}
