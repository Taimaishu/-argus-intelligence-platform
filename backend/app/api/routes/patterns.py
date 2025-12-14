"""Pattern detection API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.core.pattern_detector import PatternDetector
from app.core.vector_store import VectorStore

router = APIRouter(tags=["patterns"])


# Schemas
class SimilarityRequest(BaseModel):
    """Request for finding similar documents."""
    document_id: int
    top_k: int = 5


class ConnectionsRequest(BaseModel):
    """Request for suggesting connections."""
    document_id: int
    threshold: Optional[float] = None


class ClusterRequest(BaseModel):
    """Request for document clustering."""
    n_clusters: Optional[int] = None


# Routes
@router.post("/patterns/similar")
def find_similar_documents(request: SimilarityRequest, db: Session = Depends(get_db)):
    """
    Find documents similar to the specified document.

    Uses semantic similarity based on document embeddings.
    """
    vector_store = VectorStore()
    pattern_detector = PatternDetector(vector_store)

    similar_docs = pattern_detector.detect_similar_documents(
        document_id=request.document_id,
        db=db,
        top_k=request.top_k
    )

    return {
        "document_id": request.document_id,
        "similar_documents": similar_docs,
        "count": len(similar_docs)
    }


@router.post("/patterns/connections")
def suggest_connections(request: ConnectionsRequest, db: Session = Depends(get_db)):
    """
    Suggest potential connections for the canvas.

    Returns high-confidence connections that can be visualized.
    """
    vector_store = VectorStore()
    pattern_detector = PatternDetector(vector_store)

    connections = pattern_detector.suggest_connections(
        document_id=request.document_id,
        db=db,
        threshold=request.threshold
    )

    return {
        "document_id": request.document_id,
        "connections": connections,
        "count": len(connections)
    }


@router.post("/patterns/cluster")
def cluster_documents(request: ClusterRequest, db: Session = Depends(get_db)):
    """
    Cluster documents into themes based on content similarity.

    Uses K-means clustering on document embeddings.
    """
    vector_store = VectorStore()
    pattern_detector = PatternDetector(vector_store)

    result = pattern_detector.cluster_documents(
        db=db,
        n_clusters=request.n_clusters
    )

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.get("/patterns/network")
def analyze_network(db: Session = Depends(get_db)):
    """
    Analyze the overall document network structure.

    Returns central documents, isolated documents, and network metrics.
    """
    vector_store = VectorStore()
    pattern_detector = PatternDetector(vector_store)

    analysis = pattern_detector.analyze_document_network(db=db)

    if "error" in analysis:
        raise HTTPException(status_code=500, detail=analysis["error"])

    return analysis


@router.get("/patterns/insights/{document_id}")
def get_document_insights(document_id: int, db: Session = Depends(get_db)):
    """
    Get comprehensive insights for a document.

    Combines similar documents, suggested connections, and cluster membership.
    """
    vector_store = VectorStore()
    pattern_detector = PatternDetector(vector_store)

    # Get similar documents
    similar_docs = pattern_detector.detect_similar_documents(
        document_id=document_id,
        db=db,
        top_k=5
    )

    # Get connection suggestions
    connections = pattern_detector.suggest_connections(
        document_id=document_id,
        db=db
    )

    # Get clustering info
    clusters = pattern_detector.cluster_documents(db=db)

    # Find which cluster this document belongs to
    document_cluster = None
    for cluster in clusters.get("clusters", []):
        if any(doc["id"] == document_id for doc in cluster["documents"]):
            document_cluster = {
                "cluster_id": cluster["cluster_id"],
                "theme": next(
                    (t["theme_name"] for t in clusters.get("themes", [])
                     if t["cluster_id"] == cluster["cluster_id"]),
                    f"Cluster {cluster['cluster_id']}"
                ),
                "size": cluster["size"]
            }
            break

    return {
        "document_id": document_id,
        "similar_documents": similar_docs,
        "suggested_connections": connections,
        "cluster_membership": document_cluster,
        "total_similar": len(similar_docs),
        "total_connections": len(connections)
    }
