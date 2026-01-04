"""Entity extraction service for knowledge graph generation."""

import re
from typing import List, Dict, Any, Optional, Set, Tuple
from enum import Enum
from dataclasses import dataclass
from collections import defaultdict
import spacy
from sqlalchemy.orm import Session

from app.models.database_models import Document, DocumentChunk
from app.utils.logger import logger


# Module-level singleton for spaCy model (lazy-loaded)
_SPACY_NLP = None


def get_spacy_model():
    """
    Get or initialize the spaCy NLP model as a singleton.

    CRITICAL: Prevents multiple loads which would waste memory/startup time.

    Returns:
        Loaded spaCy model
    """
    global _SPACY_NLP
    if _SPACY_NLP is None:
        try:
            _SPACY_NLP = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy model: en_core_web_sm (singleton)")
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {e}")
            raise
    return _SPACY_NLP


class EntityType(str, Enum):
    """Types of entities that can be extracted."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    EVENT = "event"
    DOCUMENT = "document"
    VEHICLE = "vehicle"
    FINANCIAL = "financial"
    PHONE = "phone"
    EMAIL = "email"
    ADDRESS = "address"


@dataclass
class Entity:
    """Extracted entity with metadata."""
    type: EntityType
    name: str
    normalized_name: str
    confidence: float
    mentions: List[Dict[str, Any]]  # List of {document_id, chunk_id, position, context}
    extra_data: Dict[str, Any]  # Additional type-specific data

    def __hash__(self):
        return hash((self.type, self.normalized_name))

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.type == other.type and self.normalized_name == other.normalized_name


class EntityExtractionService:
    """Service for extracting entities from documents using NER and patterns."""

    def __init__(self):
        """Initialize the entity extraction service."""
        # Use singleton pattern for spaCy model (lazy-loaded on first use)
        self.nlp = get_spacy_model()

        # Pattern definitions for specialized entity extraction
        self.patterns = {
            EntityType.PHONE: [
                r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US phone
                r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # International
            ],
            EntityType.EMAIL: [
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            ],
            EntityType.FINANCIAL: [
                r'\$\s?[\d,]+(?:\.\d{2})?(?:\s?(?:million|billion|thousand|M|B|K))?',
                r'USD?\s?[\d,]+(?:\.\d{2})?',
                r'[\d,]+(?:\.\d{2})?\s?(?:dollars|USD)',
            ],
            EntityType.VEHICLE: [
                r'\b[A-Z0-9]{2,3}[-\s]?[A-Z0-9]{3,4}\b',  # License plates
                r'\b(?:19|20)\d{2}\s+[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z0-9]+)?\b',  # Year Make Model
            ],
            EntityType.ADDRESS: [
                r'\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct)',
            ],
        }

        # Compile patterns
        self.compiled_patterns = {
            entity_type: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for entity_type, patterns in self.patterns.items()
        }

    async def extract_entities(self, document_id: int, db: Session) -> List[Entity]:
        """
        Extract entities from a specific document.

        Args:
            document_id: ID of the document to extract entities from
            db: Database session

        Returns:
            List of extracted entities
        """
        try:
            # Get document
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                logger.error(f"Document {document_id} not found")
                return []

            # Get all chunks
            chunks = db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document_id
            ).all()

            if not chunks:
                logger.warning(f"No chunks found for document {document_id}")
                return []

            # Extract entities from all chunks
            all_entities: Dict[Tuple[EntityType, str], Entity] = {}

            for chunk in chunks:
                chunk_entities = self._extract_from_text(
                    text=chunk.chunk_text,
                    document_id=document_id,
                    chunk_id=chunk.id
                )

                # Merge entities
                for entity in chunk_entities:
                    key = (entity.type, entity.normalized_name)
                    if key in all_entities:
                        # Merge mentions
                        all_entities[key].mentions.extend(entity.mentions)
                        # Update confidence (average)
                        all_entities[key].confidence = (
                            all_entities[key].confidence + entity.confidence
                        ) / 2
                    else:
                        all_entities[key] = entity

            # Add document entity
            doc_entity = Entity(
                type=EntityType.DOCUMENT,
                name=document.filename,
                normalized_name=document.filename.lower(),
                confidence=1.0,
                mentions=[{
                    "document_id": document_id,
                    "chunk_id": None,
                    "position": 0,
                    "context": f"Document: {document.filename}"
                }],
                extra_data={
                    "file_type": document.file_type,
                    "upload_date": str(document.upload_date),
                    "size": document.file_size if hasattr(document, 'file_size') else None
                }
            )
            all_entities[(doc_entity.type, doc_entity.normalized_name)] = doc_entity

            logger.info(f"Extracted {len(all_entities)} entities from document {document_id}")
            return list(all_entities.values())

        except Exception as e:
            logger.error(f"Entity extraction failed for document {document_id}: {e}")
            return []

    def _extract_from_text(
        self,
        text: str,
        document_id: int,
        chunk_id: Optional[int] = None
    ) -> List[Entity]:
        """Extract entities from a text chunk."""
        entities: Dict[Tuple[EntityType, str], Entity] = {}

        # 1. spaCy NER extraction
        doc = self.nlp(text)

        for ent in doc.ents:
            entity_type = self._map_spacy_label(ent.label_)
            if not entity_type:
                continue

            normalized_name = self._normalize_name(ent.text)
            key = (entity_type, normalized_name)

            mention = {
                "document_id": document_id,
                "chunk_id": chunk_id,
                "position": ent.start_char,
                "context": self._extract_context(text, ent.start_char, ent.end_char)
            }

            if key in entities:
                entities[key].mentions.append(mention)
            else:
                entities[key] = Entity(
                    type=entity_type,
                    name=ent.text,
                    normalized_name=normalized_name,
                    confidence=0.9,  # High confidence for spaCy NER
                    mentions=[mention],
                    extra_data={"label": ent.label_}
                )

        # 2. Pattern-based extraction
        for entity_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    matched_text = match.group(0)
                    normalized_name = self._normalize_name(matched_text)
                    key = (entity_type, normalized_name)

                    mention = {
                        "document_id": document_id,
                        "chunk_id": chunk_id,
                        "position": match.start(),
                        "context": self._extract_context(text, match.start(), match.end())
                    }

                    if key in entities:
                        entities[key].mentions.append(mention)
                    else:
                        entities[key] = Entity(
                            type=entity_type,
                            name=matched_text,
                            normalized_name=normalized_name,
                            confidence=0.8,  # Good confidence for pattern matching
                            mentions=[mention],
                            extra_data={"pattern": "regex"}
                        )

        return list(entities.values())

    async def extract_from_unredaction_results(
        self,
        redaction_data: Dict[str, Any]
    ) -> List[Entity]:
        """
        Extract entities from unredaction analysis results.

        Args:
            redaction_data: Results from unredaction service

        Returns:
            List of extracted entities
        """
        entities: Dict[Tuple[EntityType, str], Entity] = {}

        predictions = redaction_data.get("predictions", [])

        for pred in predictions:
            predicted_text = pred.get("predicted", "")
            confidence = pred.get("confidence", 0) / 100  # Convert to 0-1 scale

            # Determine entity type from prediction type
            entity_type = self._map_prediction_type(predicted_text)
            if not entity_type:
                continue

            normalized_name = self._normalize_name(predicted_text)
            key = (entity_type, normalized_name)

            context = pred.get("context", "")
            mention = {
                "document_id": None,  # Will be set by caller
                "chunk_id": None,
                "position": 0,
                "context": context
            }

            if key in entities:
                entities[key].mentions.append(mention)
                entities[key].confidence = max(entities[key].confidence, confidence)
            else:
                entities[key] = Entity(
                    type=entity_type,
                    name=predicted_text,
                    normalized_name=normalized_name,
                    confidence=confidence,
                    mentions=[mention],
                    extra_data={
                        "source": "unredaction",
                        "original_context": context
                    }
                )

        return list(entities.values())

    def merge_duplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """
        Merge duplicate entities across multiple documents.

        Args:
            entities: List of entities to merge

        Returns:
            Deduplicated list of entities
        """
        merged: Dict[Tuple[EntityType, str], Entity] = {}

        for entity in entities:
            key = (entity.type, entity.normalized_name)

            if key in merged:
                # Merge mentions
                merged[key].mentions.extend(entity.mentions)
                # Update confidence (weighted average by mention count)
                old_count = len(merged[key].mentions) - len(entity.mentions)
                new_count = len(entity.mentions)
                total_count = old_count + new_count

                merged[key].confidence = (
                    (merged[key].confidence * old_count + entity.confidence * new_count)
                    / total_count
                )

                # Merge metadata
                merged[key].extra_data.update(entity.extra_data)
            else:
                merged[key] = entity

        return list(merged.values())

    def _map_spacy_label(self, label: str) -> Optional[EntityType]:
        """Map spaCy entity label to our EntityType."""
        mapping = {
            "PERSON": EntityType.PERSON,
            "ORG": EntityType.ORGANIZATION,
            "GPE": EntityType.LOCATION,  # Geopolitical entity
            "LOC": EntityType.LOCATION,
            "FAC": EntityType.LOCATION,  # Facility
            "DATE": EntityType.DATE,
            "TIME": EntityType.DATE,
            "EVENT": EntityType.EVENT,
            "MONEY": EntityType.FINANCIAL,
        }
        return mapping.get(label)

    def _map_prediction_type(self, predicted_text: str) -> Optional[EntityType]:
        """Infer entity type from prediction markers."""
        text_upper = predicted_text.upper()

        if "[PERSON_NAME]" in text_upper or "[EXECUTIVE_NAME]" in text_upper:
            return EntityType.PERSON
        elif "[LOCATION]" in text_upper or "[ADDRESS]" in text_upper:
            return EntityType.LOCATION
        elif "[ORGANIZATION]" in text_upper or "[COMPANY]" in text_upper:
            return EntityType.ORGANIZATION
        elif "[DOLLAR_AMOUNT]" in text_upper or "[FINANCIAL]" in text_upper:
            return EntityType.FINANCIAL
        elif "[LICENSE_PLATE]" in text_upper or "[VEHICLE_DESCRIPTOR]" in text_upper:
            return EntityType.VEHICLE
        elif "[PHONE]" in text_upper:
            return EntityType.PHONE
        elif "[EMAIL]" in text_upper:
            return EntityType.EMAIL
        elif "[DATE]" in text_upper:
            return EntityType.DATE
        else:
            # Try to infer from context patterns
            if re.search(r'\$\s?[\d,]+', predicted_text):
                return EntityType.FINANCIAL
            elif re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', predicted_text):
                return EntityType.PERSON

        return None

    def _normalize_name(self, text: str) -> str:
        """Normalize entity name for deduplication."""
        # Remove extra whitespace
        normalized = ' '.join(text.split())
        # Convert to lowercase
        normalized = normalized.lower()
        # Remove common prefixes/suffixes
        normalized = re.sub(r'\b(mr|mrs|ms|dr|prof|inc|llc|ltd|corp)\b\.?', '', normalized, flags=re.IGNORECASE)
        # Strip whitespace
        normalized = normalized.strip()
        return normalized

    def _extract_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Extract context around an entity mention."""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)

        context = text[context_start:context_end]

        # Add ellipsis if truncated
        if context_start > 0:
            context = "..." + context
        if context_end < len(text):
            context = context + "..."

        return context

    def get_entity_statistics(self, entities: List[Entity]) -> Dict[str, Any]:
        """Generate statistics about extracted entities."""
        stats = {
            "total_entities": len(entities),
            "by_type": defaultdict(int),
            "top_entities": [],
            "avg_confidence": 0.0,
            "unique_documents": set()
        }

        for entity in entities:
            stats["by_type"][entity.type.value] += 1
            for mention in entity.mentions:
                if mention["document_id"]:
                    stats["unique_documents"].add(mention["document_id"])

        if entities:
            stats["avg_confidence"] = sum(e.confidence for e in entities) / len(entities)

            # Top entities by mention count
            sorted_entities = sorted(entities, key=lambda e: len(e.mentions), reverse=True)
            stats["top_entities"] = [
                {
                    "type": e.type.value,
                    "name": e.name,
                    "mentions": len(e.mentions),
                    "confidence": round(e.confidence, 2)
                }
                for e in sorted_entities[:10]
            ]

        stats["by_type"] = dict(stats["by_type"])
        stats["unique_documents"] = len(stats["unique_documents"])

        return stats
