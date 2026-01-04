"""Canvas API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.database_models import CanvasNode, CanvasEdge, EntityKnowledge
from app.models.enums import NodeType

router = APIRouter(tags=["canvas"])


# Schemas
class NodeData(BaseModel):
    """Node data schema."""

    label: str
    content: Optional[str] = None
    color: Optional[str] = None
    document_id: Optional[int] = None


class NodeCreate(BaseModel):
    """Create node request."""

    id: str
    type: str
    position: dict
    data: NodeData


class NodeUpdate(BaseModel):
    """Update node request."""

    position: Optional[dict] = None
    data: Optional[NodeData] = None


class EdgeCreate(BaseModel):
    """Create edge request."""

    id: str
    source: str
    target: str
    type: Optional[str] = "default"
    data: Optional[dict] = None


class CanvasState(BaseModel):
    """Complete canvas state."""

    nodes: List[dict]
    edges: List[dict]


# Routes
@router.get("/canvas/nodes")
def get_nodes(db: Session = Depends(get_db)):
    """Get all canvas nodes."""
    nodes = db.query(CanvasNode).all()
    return [
        {
            "id": node.id,
            "type": node.type.value,
            "position": {"x": node.position_x, "y": node.position_y},
            "data": node.data,
        }
        for node in nodes
    ]


@router.get("/canvas/edges")
def get_edges(db: Session = Depends(get_db)):
    """Get all canvas edges."""
    edges = db.query(CanvasEdge).all()
    return [
        {
            "id": edge.id,
            "source": edge.source_node_id,
            "target": edge.target_node_id,
            "type": edge.connection_type,
            "data": edge.data or {},
        }
        for edge in edges
    ]


@router.get("/canvas/state")
def get_canvas_state(db: Session = Depends(get_db)):
    """Get complete canvas state."""
    nodes = db.query(CanvasNode).all()
    edges = db.query(CanvasEdge).all()

    return {
        "nodes": [
            {
                "id": node.id,
                "type": node.type.value,
                "position": {"x": node.position_x, "y": node.position_y},
                "data": node.data,
            }
            for node in nodes
        ],
        "edges": [
            {
                "id": edge.id,
                "source": edge.source_node_id,
                "target": edge.target_node_id,
                "type": edge.connection_type,
                "data": edge.data or {},
            }
            for edge in edges
        ],
    }


@router.post("/canvas/nodes")
async def create_node(node: NodeCreate, db: Session = Depends(get_db)):
    """Create a new canvas node with automatic enrichment."""
    # Check if node already exists
    existing = db.query(CanvasNode).filter(CanvasNode.id == node.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Node already exists")

    # Map string type to enum
    try:
        node_type = NodeType(node.type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid node type: {node.type}")

    # Create node
    db_node = CanvasNode(
        id=node.id,
        type=node_type,
        position_x=node.position["x"],
        position_y=node.position["y"],
        data=node.data.dict(),
        document_id=node.data.document_id,
    )

    db.add(db_node)
    db.commit()
    db.refresh(db_node)

    # AUTO-ENRICH: Automatically add photo and metadata for new entity
    # Only for person/organization types to save costs
    if node_type.value in ['person', 'organization'] and node.data.label:
        try:
            from app.core.entity_enrichment_service import EntityEnrichmentService
            enrichment_service = EntityEnrichmentService()

            # Run basic enrichment (photo + metadata, no expensive AI yet)
            entity_name = node.data.label
            enhanced_name = enrichment_service._get_enhanced_name(entity_name, db)

            # Add photo
            images = enrichment_service.image_service.search_images(enhanced_name, node_type.value, 1)
            if images and images[0].get('source') != 'placeholder':
                data = db_node.data if isinstance(db_node.data, dict) else {}
                data['image_url'] = images[0]['url']
                db_node.data = data

            # Extract basic metadata (cheap, no AI)
            metadata = enrichment_service.metadata_service.analyze_entity_metadata(entity_name, db)

            # Create knowledge entry (no AI theories yet - those are expensive)
            knowledge = EntityKnowledge(
                entity_name=entity_name,
                full_name=enhanced_name,
                entity_type=node_type.value,
                entity_metadata=metadata,
                mention_count=metadata.get('total_mentions', 0),
                photo_url=images[0]['url'] if images and images[0].get('source') != 'placeholder' else None,
                photo_source='wikipedia' if images and images[0].get('source') != 'placeholder' else None,
            )
            db.add(knowledge)
            db.commit()

            logger.info(f"✓ Auto-enriched {entity_name} with photo and metadata")
        except Exception as e:
            logger.warning(f"Could not auto-enrich {node.data.label}: {e}")
            # Don't fail the node creation if enrichment fails
            pass

    db.refresh(db_node)

    return {
        "id": db_node.id,
        "type": db_node.type.value,
        "position": {"x": db_node.position_x, "y": db_node.position_y},
        "data": db_node.data,
    }


@router.patch("/canvas/nodes/{node_id}")
def update_node(node_id: str, update: NodeUpdate, db: Session = Depends(get_db)):
    """Update a canvas node."""
    node = db.query(CanvasNode).filter(CanvasNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    if update.position:
        node.position_x = update.position["x"]
        node.position_y = update.position["y"]

    if update.data:
        node.data = update.data.dict()
        if update.data.document_id:
            node.document_id = update.data.document_id

    db.commit()
    db.refresh(node)

    return {
        "id": node.id,
        "type": node.type.value,
        "position": {"x": node.position_x, "y": node.position_y},
        "data": node.data,
    }


@router.delete("/canvas/nodes/{node_id}")
def delete_node(node_id: str, db: Session = Depends(get_db)):
    """Delete a canvas node."""
    node = db.query(CanvasNode).filter(CanvasNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    db.delete(node)
    db.commit()

    return {"message": "Node deleted"}


@router.post("/canvas/edges")
def create_edge(edge: EdgeCreate, db: Session = Depends(get_db)):
    """Create a new canvas edge."""
    # Check if edge already exists
    existing = db.query(CanvasEdge).filter(CanvasEdge.id == edge.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Edge already exists")

    # Verify source and target nodes exist
    source = db.query(CanvasNode).filter(CanvasNode.id == edge.source).first()
    target = db.query(CanvasNode).filter(CanvasNode.id == edge.target).first()

    if not source or not target:
        raise HTTPException(status_code=404, detail="Source or target node not found")

    # Create edge
    db_edge = CanvasEdge(
        id=edge.id,
        source_node_id=edge.source,
        target_node_id=edge.target,
        connection_type=edge.type or "default",
        data=edge.data,
    )

    db.add(db_edge)
    db.commit()
    db.refresh(db_edge)

    return {
        "id": db_edge.id,
        "source": db_edge.source_node_id,
        "target": db_edge.target_node_id,
        "type": db_edge.connection_type,
        "data": db_edge.data,
    }


@router.delete("/canvas/edges/{edge_id}")
def delete_edge(edge_id: str, db: Session = Depends(get_db)):
    """Delete a canvas edge."""
    edge = db.query(CanvasEdge).filter(CanvasEdge.id == edge_id).first()
    if not edge:
        raise HTTPException(status_code=404, detail="Edge not found")

    db.delete(edge)
    db.commit()

    return {"message": "Edge deleted"}


@router.post("/canvas/state")
def save_canvas_state(state: CanvasState, db: Session = Depends(get_db)):
    """Save complete canvas state (bulk update)."""
    # This is a full state replacement - clear existing and create new
    db.query(CanvasEdge).delete()
    db.query(CanvasNode).delete()

    # Create nodes
    for node_data in state.nodes:
        try:
            node_type = NodeType(node_data["type"])
        except ValueError:
            continue

        node = CanvasNode(
            id=node_data["id"],
            type=node_type,
            position_x=node_data["position"]["x"],
            position_y=node_data["position"]["y"],
            data=node_data["data"],
            document_id=node_data["data"].get("document_id"),
        )
        db.add(node)

    db.flush()  # Ensure nodes exist before creating edges

    # Create edges
    for edge_data in state.edges:
        edge = CanvasEdge(
            id=edge_data["id"],
            source_node_id=edge_data["source"],
            target_node_id=edge_data["target"],
            connection_type=edge_data.get("type", "default"),
            data=edge_data.get("data"),
        )
        db.add(edge)

    db.commit()

    return {
        "message": "Canvas state saved",
        "nodes": len(state.nodes),
        "edges": len(state.edges),
    }


@router.delete("/canvas/clear")
def clear_canvas(db: Session = Depends(get_db)):
    """Clear entire canvas."""
    db.query(CanvasEdge).delete()
    db.query(CanvasNode).delete()
    db.commit()

    return {"message": "Canvas cleared"}


# Additional imports for advanced features
import logging
from app.core.image_search_service import ImageSearchService
from app.core.knowledge_graph_service import KnowledgeGraphService
from app.core.entity_extraction_service import EntityExtractionService
from app.models.database_models import Document, DocumentChunk

logger = logging.getLogger(__name__)
image_service = ImageSearchService()
entity_service = EntityExtractionService()
kg_service = KnowledgeGraphService(entity_service)


@router.post("/canvas/search-all-images")
async def search_all_entity_images(db: Session = Depends(get_db)):
    """Auto-find photos for ALL entities on canvas from Wikipedia."""
    try:
        nodes = db.query(CanvasNode).all()
        results = {
            "total": len(nodes),
            "found": 0,
            "skipped": 0,
            "updated": []
        }

        for node in nodes:
            data = node.data if isinstance(node.data, dict) else {}
            if data.get('image_url'):
                results["skipped"] += 1
                continue

            name = data.get('label', '')
            if not name:
                continue

            # Skip date entities - they shouldn't have photos
            node_type = str(node.type.value if hasattr(node.type, 'value') else node.type)
            if node_type in ['date', 'event']:
                results["skipped"] += 1
                continue

            # Skip generic/ambiguous names
            if len(name) <= 3 or name.lower() in ['ted', 'the', 'today', '24']:
                results["skipped"] += 1
                continue

            # Check for known entities first (name mappings)
            name_mappings = {
                "epstein": "Jeffrey Epstein",
                "clinton": "Bill Clinton",
                "andrew": "Prince Andrew",
                "trump": "Donald Trump",
                "maxwell": "Ghislaine Maxwell",
            }

            enhanced_name = name
            name_lower = name.lower()

            # Use name mapping if available
            if name_lower in name_mappings:
                enhanced_name = name_mappings[name_lower]
                logger.info(f"Using name mapping: '{name}' -> '{enhanced_name}'")
            else:
                # Get context from document chunks to build a better search query
                try:
                    chunks = db.query(DocumentChunk).filter(
                        DocumentChunk.chunk_text.ilike(f'%{name}%')
                    ).limit(5).all()

                    # Look for enhanced names like "Prince Andrew", "President Clinton", etc.
                    import re
                    for chunk in chunks:
                        text = chunk.chunk_text
                        # Try to find the name with titles/context
                        patterns = [
                            rf'((?:Prince|President|King|Queen|Duke|Duchess|Lord|Lady|Sir|Dr\.|Professor)\s+{re.escape(name)}(?:\s+\w+)?)',
                            rf'({re.escape(name)}\s+(?:Duke|Prince|President|of\s+\w+))',
                            rf'({re.escape(name)}\s+\w+(?:\s+\w+)?)',  # Full name variants
                        ]

                        for pattern in patterns:
                            match = re.search(pattern, text, re.IGNORECASE)
                            if match:
                                potential_name = match.group(1).strip()
                                # Use the enhanced name if it's longer and more specific
                                if len(potential_name) > len(enhanced_name):
                                    enhanced_name = potential_name
                                    logger.info(f"Enhanced '{name}' to '{enhanced_name}' from context")
                                    break
                        if enhanced_name != name:
                            break
                except Exception as context_error:
                    logger.warning(f"Could not get context for {name}: {context_error}")

            try:
                images = image_service.search_images(enhanced_name, str(node.type.value if hasattr(node.type, 'value') else node.type), 1)
                if images and images[0].get('source') != 'placeholder':
                    data['image_url'] = images[0]['url']
                    node.data = data
                    results["found"] += 1
                    results["updated"].append({"name": name, "enhanced": enhanced_name, "url": images[0]['url']})
            except:
                continue

        db.commit()
        return results
    except Exception as e:
        logger.error(f"Batch image search failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/canvas/search-image")
async def search_entity_image(request: dict, db: Session = Depends(get_db)):
    """Search for image of a single entity with context enhancement."""
    try:
        name = request.get("entity_name")
        etype = request.get("entity_type", "person")
        if not name:
            raise HTTPException(400, "entity_name required")

        # Check for known entities first (name mappings)
        name_mappings = {
            "epstein": "Jeffrey Epstein",
            "clinton": "Bill Clinton",
            "andrew": "Prince Andrew",
            "trump": "Donald Trump",
            "maxwell": "Ghislaine Maxwell",
        }

        enhanced_name = name
        name_lower = name.lower()

        # Use name mapping if available
        if name_lower in name_mappings:
            enhanced_name = name_mappings[name_lower]
            logger.info(f"Using name mapping: '{name}' -> '{enhanced_name}'")
        else:
            # Get context from document chunks to build a better search query
            try:
                chunks = db.query(DocumentChunk).filter(
                    DocumentChunk.chunk_text.ilike(f'%{name}%')
                ).limit(5).all()

                # Look for enhanced names like "Prince Andrew", "President Clinton", etc.
                import re
                for chunk in chunks:
                    text = chunk.chunk_text
                    # Try to find the name with titles/context
                    patterns = [
                        rf'((?:Prince|President|King|Queen|Duke|Duchess|Lord|Lady|Sir|Dr\.|Professor)\s+{re.escape(name)}(?:\s+\w+)?)',
                        rf'({re.escape(name)}\s+(?:Duke|Prince|President|of\s+\w+))',
                        rf'({re.escape(name)}\s+\w+(?:\s+\w+)?)',  # Full name variants
                    ]

                    for pattern in patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            potential_name = match.group(1).strip()
                            # Use the enhanced name if it's longer and more specific
                            if len(potential_name) > len(enhanced_name):
                                enhanced_name = potential_name
                                logger.info(f"Enhanced '{name}' to '{enhanced_name}' from context")
                                break
                    if enhanced_name != name:
                        break
            except Exception as context_error:
                logger.warning(f"Could not get context for {name}: {context_error}")

        images = image_service.search_images(enhanced_name, etype, 5)
        return {"entity_name": name, "enhanced_name": enhanced_name, "images": images, "count": len(images)}
    except Exception as e:
        logger.error(f"Image search failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/canvas/entity-info")
async def get_entity_info(request: dict, db: Session = Depends(get_db)):
    """Get comprehensive entity information with AI analysis."""
    try:
        name = request.get("entity_name")
        etype = request.get("entity_type", "person")
        provider = request.get("provider", "openai")
        model = request.get("model")

        if not name:
            raise HTTPException(400, "entity_name required")

        # Get document chunks
        chunks = db.query(DocumentChunk).filter(DocumentChunk.chunk_text.ilike(f"%{name}%")).limit(10).all()
        context = "\n\n".join([f"Excerpt {i+1}: {c.chunk_text[:500]}" for i, c in enumerate(chunks[:5])])

        # AI analysis
        from app.core.chat_service import ChatService
        chat = ChatService()
        prompt = f"""Analyze this entity from investigation documents:

ENTITY: {name}
TYPE: {etype}

DOCUMENT EXCERPTS:
{context or "No excerpts available"}

Provide:

WHO THEY ARE:
[1-2 sentences on identity/role]

BACKGROUND & PAST:
[3-5 key facts about their history]

CONNECTION TO INVESTIGATION:
[2-3 sentences on their relevance]

KEY ASSOCIATIONS:
[List 3-5 connected people/orgs]

THEORY & CONCLUSION:
[2-3 sentences analysis and conclusion based on evidence]"""

        analysis = await chat.generate_response(prompt, None, db, provider, model)

        # Parse response
        sections = {"who_they_are": "", "background": "", "connection": "", "associations": [], "theory": ""}
        current = None
        for line in analysis.split('\n'):
            upper = line.strip().upper()
            if 'WHO THEY ARE' in upper:
                current = 'who_they_are'
            elif 'BACKGROUND' in upper:
                current = 'background'
            elif 'CONNECTION' in upper:
                current = 'connection'
            elif 'ASSOCIATIONS' in upper:
                current = 'associations'
            elif 'THEORY' in upper or 'CONCLUSION' in upper:
                current = 'theory'
            elif current and line.strip():
                if current == 'associations':
                    cleaned = line.strip().lstrip('-•*0123456789. ')
                    if cleaned and len(cleaned) > 5:
                        sections['associations'].append(cleaned)
                else:
                    sections[current] += line.strip() + " "

        # Get connections
        nodes = db.query(CanvasNode).all()
        edges = db.query(CanvasEdge).all()
        node_id = next((n.id for n in nodes if name.lower() in n.data.get('label', '').lower()), None)

        connected = []
        if node_id:
            for e in edges:
                if e.source_node_id == node_id:
                    target = next((n for n in nodes if n.id == e.target_node_id), None)
                    if target:
                        connected.append({"label": target.data.get('label'), "type": target.type.value, "relationship": e.connection_type})
                elif e.target_node_id == node_id:
                    source = next((n for n in nodes if n.id == e.source_node_id), None)
                    if source:
                        connected.append({"label": source.data.get('label'), "type": source.type.value, "relationship": e.connection_type})

        # Get evidence
        evidence = []
        for chunk in chunks[:5]:
            doc = db.query(Document).filter(Document.id == chunk.document_id).first()
            if doc:
                evidence.append({
                    "excerpt": chunk.chunk_text[:300] + "..." if len(chunk.chunk_text) > 300 else chunk.chunk_text,
                    "document_name": doc.filename,
                    "document_id": doc.id
                })

        return {
            "entity_name": name,
            "who_they_are": sections['who_they_are'].strip(),
            "background": sections['background'].strip(),
            "connection": sections['connection'].strip(),
            "associations": sections['associations'],
            "theory": sections['theory'].strip(),
            "connected_entities": connected,
            "evidence": evidence
        }
    except Exception as e:
        logger.error(f"Entity info failed: {e}", exc_info=True)
        raise HTTPException(500, str(e))


@router.post("/canvas/auto-generate")
async def auto_generate_canvas(request: dict, db: Session = Depends(get_db)):
    """Auto-generate knowledge graph from documents."""
    try:
        from app.models.database_models import Document
        docs = db.query(Document).all()
        if not docs:
            raise HTTPException(400, "No documents found")

        result = await kg_service.generate_knowledge_graph_from_documents([d.id for d in docs], db)
        return result
    except Exception as e:
        logger.error(f"Auto-generate failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/canvas/build-knowledge-database")
async def build_knowledge_database(request: dict, db: Session = Depends(get_db)):
    """Build comprehensive knowledge database for all entities on canvas."""
    try:
        provider = request.get("provider", "openai")
        model = request.get("model")

        nodes = db.query(CanvasNode).all()
        results = {
            "total": 0,
            "created": 0,
            "updated": 0,
            "failed": 0,
            "entities": []
        }

        # Only process entity nodes (not document/insight/note)
        entity_types = ['person', 'organization', 'location', 'event', 'vehicle', 'financial', 'phone', 'email', 'address']

        for node in nodes:
            if str(node.type.value) not in entity_types:
                continue

            results["total"] += 1
            name = node.data.get('label', '')
            if not name:
                continue

            try:
                # Check if knowledge entry already exists
                knowledge = db.query(EntityKnowledge).filter(
                    EntityKnowledge.entity_name == name
                ).first()

                is_new = knowledge is None
                if is_new:
                    knowledge = EntityKnowledge(
                        entity_name=name,
                        entity_type=str(node.type.value)
                    )
                    db.add(knowledge)

                # Get context from document chunks
                import re
                from datetime import datetime
                chunks = db.query(DocumentChunk).filter(
                    DocumentChunk.chunk_text.ilike(f'%{name}%')
                ).limit(10).all()

                # Extract enhanced name
                enhanced_name = name
                for chunk in chunks:
                    text = chunk.chunk_text
                    patterns = [
                        rf'((?:Prince|President|King|Queen|Duke|Duchess|Lord|Lady|Sir|Dr\.|Professor)\s+{re.escape(name)}(?:\s+\w+)?)',
                        rf'({re.escape(name)}\s+(?:Duke|Prince|President|of\s+\w+))',
                        rf'({re.escape(name)}\s+\w+(?:\s+\w+)?)',
                    ]
                    for pattern in patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            potential = match.group(1).strip()
                            if len(potential) > len(enhanced_name):
                                enhanced_name = potential
                                break
                    if enhanced_name != name:
                        break

                knowledge.full_name = enhanced_name
                knowledge.mention_count = len(chunks)

                # Get AI analysis
                from app.core.chat_service import ChatService
                chat = ChatService()
                context = "\n\n".join([f"Excerpt {i+1}: {c.chunk_text[:500]}" for i, c in enumerate(chunks[:5])])

                prompt = f"""Analyze this entity from investigation documents:

ENTITY: {enhanced_name}
TYPE: {str(node.type.value)}

DOCUMENT EXCERPTS:
{context or "No excerpts available"}

Provide:

WHO THEY ARE:
[1-2 sentences on identity/role]

BACKGROUND & PAST:
[3-5 key facts about their history]

CONNECTION TO INVESTIGATION:
[2-3 sentences on their relevance]

KEY ASSOCIATIONS:
[List 3-5 connected people/orgs]

THEORY & CONCLUSION:
[2-3 sentences analysis based on evidence]"""

                analysis = await chat.generate_response(prompt, None, db, provider, model)

                # Parse AI response
                sections = {"who": "", "background": "", "connection": "", "associations": [], "theory": ""}
                current = None
                for line in analysis.split('\n'):
                    upper = line.strip().upper()
                    if 'WHO THEY ARE' in upper:
                        current = 'who'
                    elif 'BACKGROUND' in upper:
                        current = 'background'
                    elif 'CONNECTION' in upper:
                        current = 'connection'
                    elif 'ASSOCIATIONS' in upper:
                        current = 'associations'
                    elif 'THEORY' in upper or 'CONCLUSION' in upper:
                        current = 'theory'
                    elif current and line.strip():
                        if current == 'associations':
                            cleaned = line.strip().lstrip('-•*0123456789. ')
                            if cleaned and len(cleaned) > 5:
                                sections['associations'].append(cleaned)
                        else:
                            sections[current] += line.strip() + " "

                # Update knowledge fields
                knowledge.description = sections['who'].strip()
                knowledge.background = sections['background'].strip()
                knowledge.connection_to_investigation = sections['connection'].strip()
                knowledge.theories = sections['theory'].strip()
                knowledge.key_associations = sections['associations']

                # Extract role/title from enhanced name
                title_match = re.match(r'^(Prince|President|King|Queen|Duke|Duchess|Lord|Lady|Sir|Dr\.|Professor)', enhanced_name, re.IGNORECASE)
                if title_match:
                    knowledge.role_title = title_match.group(1)

                # Get photo
                images = image_service.search_images(enhanced_name, str(node.type.value), 1)
                if images and images[0].get('source') != 'placeholder':
                    knowledge.photo_url = images[0]['url']
                    knowledge.photo_source = images[0]['source']
                    knowledge.photo_attribution = images[0].get('attribution', '')

                # Evidence excerpts
                evidence = []
                for chunk in chunks[:5]:
                    doc = db.query(Document).filter(Document.id == chunk.document_id).first()
                    if doc:
                        evidence.append({
                            "text": chunk.chunk_text[:300],
                            "document_id": doc.id,
                            "document_name": doc.filename
                        })
                knowledge.evidence_excerpts = evidence
                knowledge.document_ids = [chunk.document_id for chunk in chunks]

                knowledge.last_analyzed = datetime.utcnow()
                knowledge.confidence_score = min(1.0, len(chunks) / 10)  # More mentions = higher confidence

                db.commit()

                if is_new:
                    results["created"] += 1
                else:
                    results["updated"] += 1

                results["entities"].append({
                    "name": name,
                    "full_name": enhanced_name,
                    "type": str(node.type.value),
                    "mentions": len(chunks)
                })

            except Exception as e:
                logger.error(f"Failed to process entity {name}: {e}")
                results["failed"] += 1
                db.rollback()
                continue

        return results
    except Exception as e:
        logger.error(f"Build knowledge database failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/canvas/analyze-metadata")
async def analyze_entity_metadata(request: dict, db: Session = Depends(get_db)):
    """Analyze metadata for a specific entity."""
    try:
        from app.core.metadata_analysis_service import MetadataAnalysisService

        entity_name = request.get("entity_name")
        if not entity_name:
            raise HTTPException(400, "entity_name required")

        service = MetadataAnalysisService()
        metadata = service.analyze_entity_metadata(entity_name, db)

        return {
            "entity_name": entity_name,
            "metadata": metadata,
            "analyzed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Metadata analysis failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/canvas/find-connections")
async def find_metadata_connections(db: Session = Depends(get_db)):
    """Find all connections between entities based on shared metadata."""
    try:
        from app.core.metadata_analysis_service import MetadataAnalysisService

        service = MetadataAnalysisService()
        connections = service.find_metadata_connections(db)

        return {
            "connections": connections,
            "total_connections": sum(len(v) for v in connections.values()),
            "analyzed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Connection analysis failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/canvas/generate-metadata-report")
async def generate_metadata_report(request: dict, db: Session = Depends(get_db)):
    """Generate comprehensive metadata analysis report with AI theories.

    NOTE: This endpoint uses AI and costs money. Only called on-demand when user
    clicks on an entity, not automatically for every entity.
    """
    try:
        from app.core.metadata_analysis_service import MetadataAnalysisService

        entity_name = request.get("entity_name")
        provider = request.get("provider", "openai")
        model = request.get("model")

        if not entity_name:
            raise HTTPException(400, "entity_name required")

        # Check if we already have recent AI analysis (cache for 24 hours)
        knowledge = db.query(EntityKnowledge).filter(
            EntityKnowledge.entity_name == entity_name
        ).first()

        if knowledge and knowledge.last_analyzed:
            time_since_analysis = (datetime.utcnow() - knowledge.last_analyzed).total_seconds()
            if time_since_analysis < 86400:  # 24 hours
                logger.info(f"Using cached AI analysis for {entity_name} (analyzed {time_since_analysis/3600:.1f} hours ago)")
                return {
                    "entity_name": entity_name,
                    "metadata": knowledge.entity_metadata or {},
                    "theories": {
                        "temporal_analysis": knowledge.description or "",
                        "geographic_analysis": knowledge.background or "",
                        "network_analysis": knowledge.connection_to_investigation or "",
                        "theories": knowledge.theories or "",
                        "cached": True,
                        "analyzed_at": knowledge.last_analyzed.isoformat()
                    },
                    "cached": True
                }

        service = MetadataAnalysisService()

        # Get metadata
        metadata = service.analyze_entity_metadata(entity_name, db)

        # Get connections
        all_connections = service.find_metadata_connections(db)

        # Filter connections for this entity
        entity_connections = {
            "shared_dates": [c for c in all_connections.get("shared_dates", [])
                           if entity_name in c["entities"]],
            "shared_locations": [c for c in all_connections.get("shared_locations", [])
                               if entity_name in c["entities"]],
            "shared_organizations": [c for c in all_connections.get("shared_organizations", [])
                                   if entity_name in c["entities"]],
            "shared_documents": [c for c in all_connections.get("shared_documents", [])
                               if entity_name in c["entities"]],
        }

        # Generate AI analysis and theories
        theories = await service.generate_metadata_theories(
            entity_name, metadata, entity_connections, db, provider, model
        )

        # Update knowledge database with metadata
        knowledge = db.query(EntityKnowledge).filter(
            EntityKnowledge.entity_name == entity_name
        ).first()

        if knowledge:
            knowledge.entity_metadata = metadata
            knowledge.last_analyzed = datetime.utcnow()
            db.commit()

        return {
            "entity_name": entity_name,
            "metadata": metadata,
            "connections": entity_connections,
            "theories": theories,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Metadata report generation failed: {e}", exc_info=True)
        raise HTTPException(500, str(e))


@router.post("/canvas/enrich-existing-entities")
async def enrich_existing_entities(db: Session = Depends(get_db)):
    """
    One-time enrichment of all existing entities with photos and metadata.

    Does NOT use AI (to save costs) - only adds:
    - Accurate photos from Wikipedia (FREE)
    - Metadata extraction (FREE)
    - Knowledge database entries (FREE)

    AI theories can be generated on-demand later when user clicks an entity.
    """
    try:
        from app.core.entity_enrichment_service import EntityEnrichmentService

        enrichment_service = EntityEnrichmentService()
        nodes = db.query(CanvasNode).all()

        results = {
            "total": len(nodes),
            "enriched": 0,
            "skipped": 0,
            "failed": 0,
            "entities": []
        }

        for node in nodes:
            entity_name = node.data.get('label', '')
            if not entity_name:
                results["skipped"] += 1
                continue

            entity_type = str(node.type.value if hasattr(node.type, 'value') else node.type)

            # Skip non-person/organization types
            if entity_type not in ['person', 'organization']:
                results["skipped"] += 1
                continue

            # Skip if already has photo and knowledge entry
            has_photo = bool(node.data.get('image_url'))
            has_knowledge = db.query(EntityKnowledge).filter(
                EntityKnowledge.entity_name == entity_name
            ).first() is not None

            if has_photo and has_knowledge:
                results["skipped"] += 1
                continue

            try:
                # Get enhanced name
                enhanced_name = enrichment_service._get_enhanced_name(entity_name, db)

                # Add photo if missing
                if not has_photo:
                    images = enrichment_service.image_service.search_images(enhanced_name, entity_type, 1)
                    if images and images[0].get('source') != 'placeholder':
                        data = node.data if isinstance(node.data, dict) else {}
                        data['image_url'] = images[0]['url']
                        node.data = data
                        logger.info(f"✓ Added photo for {entity_name}")

                # Extract metadata
                metadata = enrichment_service.metadata_service.analyze_entity_metadata(entity_name, db)

                # Create/update knowledge entry
                knowledge = db.query(EntityKnowledge).filter(
                    EntityKnowledge.entity_name == entity_name
                ).first()

                if not knowledge:
                    knowledge = EntityKnowledge(
                        entity_name=entity_name,
                        full_name=enhanced_name,
                        entity_type=entity_type,
                        entity_metadata=metadata,
                        mention_count=metadata.get('total_mentions', 0),
                        photo_url=node.data.get('image_url'),
                        photo_source='wikipedia' if node.data.get('image_url') else None,
                    )
                    db.add(knowledge)
                else:
                    knowledge.entity_metadata = metadata
                    knowledge.mention_count = metadata.get('total_mentions', 0)

                db.commit()
                results["enriched"] += 1
                results["entities"].append({
                    "name": entity_name,
                    "enhanced": enhanced_name,
                    "mentions": metadata.get('total_mentions', 0)
                })

            except Exception as e:
                logger.error(f"Failed to enrich {entity_name}: {e}")
                results["failed"] += 1
                db.rollback()

        return results

    except Exception as e:
        logger.error(f"Bulk enrichment failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/canvas/extract-more-entities")
async def extract_more_entities(request: dict, db: Session = Depends(get_db)):
    """
    Extract more entities from documents using regex patterns and add to canvas.
    Simple extraction that doesn't require AI.
    """
    try:
        import re
        import uuid
        from collections import Counter

        # Get all document chunks
        chunks = db.query(DocumentChunk).all()
        if not chunks:
            return {"error": "No document chunks found", "added": 0}

        logger.info(f"Processing {len(chunks)} document chunks for entity extraction")

        # Combine all text
        all_text = "\n\n".join([chunk.chunk_text for chunk in chunks])

        # Entity patterns
        # Names: Capitalized words (2-3 words)
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'

        # Locations: Known locations
        location_pattern = r'\b(New York|Los Angeles|Miami|Palm Beach|London|Paris|Washington|Bradford|Manhattan|Florida|California|Virginia|Boston|Chicago|Dallas|Houston|Seattle|Portland|Denver|Phoenix|Las Vegas|San Francisco|San Diego|Philadelphia|Baltimore|Atlanta|Charlotte|Raleigh|Nashville|Memphis|Detroit|Minneapolis|Cleveland|Pittsburgh|Cincinnati|Indianapolis|Columbus|Milwaukee|Kansas City|St\. Louis)\b'

        # Organizations
        org_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Corp|Corporation|Inc|LLC|Ltd|LLP|Organization|Agency|Bureau|Foundation|Institute|University|College|School|Hospital|Bank|Group|Company|Partners|Associates)))\b|'
        org_pattern += r'\b(FBI|CIA|DOJ|NSA|NYPD|LAPD|SEC|IRS|DEA|ATF|ICE|TSA|DHS|NASA|EPA)\b'

        # Dates
        date_pattern = r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b|\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b|\b((19|20)\d{2})\b'

        # Phone numbers
        phone_pattern = r'\b(\d{3}[-.]?\d{3}[-.]?\d{4})\b'

        # Email addresses
        email_pattern = r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'

        # Financial amounts
        financial_pattern = r'\$\s*([0-9,]+(?:\.[0-9]{2})?)'

        # Extract all matches
        names = re.findall(name_pattern, all_text)
        locations = re.findall(location_pattern, all_text)
        orgs = re.findall(org_pattern, all_text)
        orgs = [o for sublist in orgs for o in sublist if o]  # Flatten
        dates = re.findall(date_pattern, all_text)
        dates = [d[0] if isinstance(d, tuple) else d for d in dates if (d[0] if isinstance(d, tuple) else d)]  # Flatten
        phones = re.findall(phone_pattern, all_text)
        emails = re.findall(email_pattern, all_text)
        financials = re.findall(financial_pattern, all_text)

        logger.info(f"Found {len(names)} names, {len(locations)} locations, {len(orgs)} organizations")

        # Count occurrences
        name_counts = Counter(names)
        location_counts = Counter(locations)
        org_counts = Counter(orgs)
        date_counts = Counter(dates)
        phone_counts = Counter(phones)
        email_counts = Counter(emails)
        financial_counts = Counter(financials)

        # Get existing canvas nodes
        existing_nodes = db.query(CanvasNode).all()
        existing_labels = {node.data.get('label', '').lower() for node in existing_nodes}

        # Common words to skip
        common_words = {'The', 'This', 'That', 'These', 'Those', 'What', 'When', 'Where', 'Why', 'How',
                       'Could', 'Would', 'Should', 'Must', 'Can', 'Will', 'May', 'Might',
                       'United States', 'New Year', 'Palm Beach County', 'New York City', 'Los Angeles County'}

        added = 0
        row_size = 10
        x_spacing = 300
        y_spacing = 200
        start_x = 100
        start_y = 500
        idx = len(existing_nodes)

        entities_to_add = []

        # Process names (persons) - top 30
        for name, count in name_counts.most_common(30):
            if count >= 2 and name not in common_words and name.lower() not in existing_labels:
                entities_to_add.append(('PERSON', name, count))

        # Process locations - top 20
        for location, count in location_counts.most_common(20):
            if count >= 2 and location.lower() not in existing_labels:
                entities_to_add.append(('LOCATION', location, count))

        # Process organizations - top 15
        for org, count in org_counts.most_common(15):
            if count >= 2 and org.lower() not in existing_labels:
                entities_to_add.append(('ORGANIZATION', org, count))

        # Process dates - top 10
        for date, count in date_counts.most_common(10):
            if count >= 3 and date.lower() not in existing_labels:
                entities_to_add.append(('DATE', date, count))

        # Process phones - top 5
        for phone, count in phone_counts.most_common(5):
            if count >= 2 and phone.lower() not in existing_labels:
                entities_to_add.append(('PHONE', phone, count))

        # Process emails - top 5
        for email, count in email_counts.most_common(5):
            if count >= 2 and email.lower() not in existing_labels:
                entities_to_add.append(('EMAIL', email, count))

        # Process financial - top 10
        for amount, count in financial_counts.most_common(10):
            if count >= 2 and amount.lower() not in existing_labels:
                entities_to_add.append(('FINANCIAL', f'${amount}', count))

        # Add to canvas
        for entity_type, name, count in entities_to_add:
            row = idx // row_size
            col = idx % row_size
            x = start_x + (col * x_spacing)
            y = start_y + (row * y_spacing)

            node_id = f"{entity_type.lower()}-{uuid.uuid4().hex[:8]}"
            node = CanvasNode(
                id=node_id,
                type=entity_type,
                position_x=x,
                position_y=y,
                data={
                    'label': name,
                    'mentions': count
                }
            )

            db.add(node)
            added += 1
            idx += 1

        db.commit()

        logger.info(f"Added {added} new entities to canvas")

        return {
            "added": added,
            "total_nodes": len(existing_nodes) + added,
            "previous_nodes": len(existing_nodes)
        }

    except Exception as e:
        logger.error(f"Entity extraction failed: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(500, str(e))
