"""Search API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.search_engine import SearchEngine
from app.core.embeddings.factory import EmbeddingFactory
from app.models.schemas import SearchRequest, SearchResponse, SearchResultItem
from app.utils.logger import logger

router = APIRouter(prefix="/search", tags=["search"])
search_engine = SearchEngine()


@router.post("", response_model=SearchResponse)
def search_documents(search_request: SearchRequest, db: Session = Depends(get_db)):
    """
    Perform semantic search across all documents.

    Args:
        search_request: Search request with query and parameters
        db: Database session

    Returns:
        Search results ranked by relevance

    Raises:
        HTTPException: If search fails
    """
    try:
        logger.info(f"Search request: '{search_request.query}'")

        # Perform search
        results = search_engine.search(
            query=search_request.query,
            db=db,
            top_k=search_request.top_k,
            document_ids=search_request.document_ids,
        )

        # Convert to response schema
        result_items = [
            SearchResultItem(
                document_id=r.document_id,
                document_title=r.document_title,
                document_filename=r.document_filename,
                chunk_text=r.chunk_text,
                snippet=r.snippet,
                relevance_score=r.relevance_score,
                chunk_index=r.chunk_index,
            )
            for r in results
        ]

        # Get embedding model name
        embedding_service = EmbeddingFactory.get_singleton()
        model_name = embedding_service.get_model_name()

        return SearchResponse(
            query=search_request.query,
            results=result_items,
            total_results=len(result_items),
            embedding_model=model_name,
        )

    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/similar/{document_id}/{chunk_index}")
def get_similar_chunks(
    document_id: int, chunk_index: int, top_k: int = 5, db: Session = Depends(get_db)
):
    """
    Find similar chunks to a given chunk (for "related documents" feature).

    Args:
        document_id: ID of the document
        chunk_index: Index of the chunk
        top_k: Number of similar chunks to return
        db: Database session

    Returns:
        List of similar chunks

    Raises:
        HTTPException: If operation fails
    """
    try:
        results = search_engine.get_similar_chunks(
            document_id=document_id, chunk_index=chunk_index, db=db, top_k=top_k
        )

        result_items = [
            SearchResultItem(
                document_id=r.document_id,
                document_title=r.document_title,
                document_filename=r.document_filename,
                chunk_text=r.chunk_text,
                snippet=r.snippet,
                relevance_score=r.relevance_score,
                chunk_index=r.chunk_index,
            )
            for r in results
            if r.document_id != document_id  # Filter out same document
        ][:top_k]

        return {
            "document_id": document_id,
            "chunk_index": chunk_index,
            "similar_chunks": result_items,
        }

    except Exception as e:
        logger.error(f"Failed to get similar chunks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document/{document_id}/summary")
def get_document_search_summary(document_id: int, db: Session = Depends(get_db)):
    """
    Get summary of document's searchability.

    Args:
        document_id: ID of the document
        db: Database session

    Returns:
        Summary statistics

    Raises:
        HTTPException: If document not found
    """
    try:
        summary = search_engine.get_document_summary(document_id, db)

        if not summary:
            raise HTTPException(status_code=404, detail="Document not found")

        return summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
