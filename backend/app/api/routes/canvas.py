"""Canvas API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.database_models import CanvasNode, CanvasEdge
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
def create_node(node: NodeCreate, db: Session = Depends(get_db)):
    """Create a new canvas node."""
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
