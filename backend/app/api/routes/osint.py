"""OSINT API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from ...database import get_db
from ...core.osint.osint_service import OSINTService
from ...core.osint.web_scraper import WebScraperService
from ...models.schemas import ErrorResponse
from pydantic import BaseModel, Field

router = APIRouter(tags=["osint"])
osint_service = OSINTService()
web_scraper = WebScraperService()


# Request/Response Schemas
class ArtifactSubmitRequest(BaseModel):
    """Schema for submitting an artifact for analysis."""

    artifact_type: str = Field(
        ..., description="Type: ip_address, domain, email, hash, url, etc."
    )
    value: str = Field(..., description="Artifact value to analyze")


class ArtifactResponse(BaseModel):
    """Schema for artifact response."""

    id: int
    artifact_type: str
    value: str
    analysis_status: str
    threat_level: str
    analysis_data: dict = None
    first_seen: str
    last_analyzed: str = None
    document_id: int = None
    extracted: bool
    notes: str = None

    class Config:
        from_attributes = True


class ArtifactListResponse(BaseModel):
    """Schema for list of artifacts."""

    artifacts: List[ArtifactResponse]
    total: int


class OSINTStatsResponse(BaseModel):
    """Schema for OSINT statistics."""

    total_artifacts: int
    by_type: dict
    by_threat_level: dict


class ExtractRequest(BaseModel):
    """Schema for extracting artifacts from text."""

    text: str = Field(..., description="Text to extract artifacts from")
    document_id: Optional[int] = None


class ExtractResponse(BaseModel):
    """Schema for extraction results."""

    artifacts: dict
    summary: dict


@router.post(
    "/osint/analyze",
    response_model=ArtifactResponse,
    status_code=status.HTTP_201_CREATED,
)
def analyze_artifact(
    request: ArtifactSubmitRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Submit an artifact for OSINT analysis.

    Supports: IP addresses, domains, emails, hashes (MD5/SHA1/SHA256), URLs.
    """
    try:
        artifact = osint_service.analyze_artifact(
            db=db, artifact_type=request.artifact_type, value=request.value
        )

        return ArtifactResponse(
            id=artifact.id,
            artifact_type=artifact.artifact_type.value,
            value=artifact.value,
            analysis_status=artifact.analysis_status.value,
            threat_level=artifact.threat_level.value,
            analysis_data=artifact.analysis_data,
            first_seen=artifact.first_seen.isoformat(),
            last_analyzed=(
                artifact.last_analyzed.isoformat() if artifact.last_analyzed else None
            ),
            document_id=artifact.document_id,
            extracted=bool(artifact.extracted),
            notes=artifact.notes,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Analysis failed: {str(e)}"
        )


@router.get("/osint/artifacts", response_model=ArtifactListResponse)
def list_artifacts(
    artifact_type: Optional[str] = None,
    threat_level: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    List artifacts with optional filtering.

    Query parameters:
    - artifact_type: Filter by type (ip_address, domain, email, hash, url)
    - threat_level: Filter by threat level (safe, low, medium, high, critical)
    - limit: Maximum number of results (default: 100)
    """
    artifacts = osint_service.get_artifacts(
        db=db, artifact_type=artifact_type, threat_level=threat_level, limit=limit
    )

    artifact_responses = [
        ArtifactResponse(
            id=a.id,
            artifact_type=a.artifact_type.value,
            value=a.value,
            analysis_status=a.analysis_status.value,
            threat_level=a.threat_level.value,
            analysis_data=a.analysis_data,
            first_seen=a.first_seen.isoformat(),
            last_analyzed=a.last_analyzed.isoformat() if a.last_analyzed else None,
            document_id=a.document_id,
            extracted=bool(a.extracted),
            notes=a.notes,
        )
        for a in artifacts
    ]

    return ArtifactListResponse(
        artifacts=artifact_responses, total=len(artifact_responses)
    )


@router.get("/osint/artifacts/{artifact_id}", response_model=ArtifactResponse)
def get_artifact(artifact_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific artifact."""
    artifact = osint_service.get_artifact_by_id(db, artifact_id)

    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artifact {artifact_id} not found",
        )

    return ArtifactResponse(
        id=artifact.id,
        artifact_type=artifact.artifact_type.value,
        value=artifact.value,
        analysis_status=artifact.analysis_status.value,
        threat_level=artifact.threat_level.value,
        analysis_data=artifact.analysis_data,
        first_seen=artifact.first_seen.isoformat(),
        last_analyzed=(
            artifact.last_analyzed.isoformat() if artifact.last_analyzed else None
        ),
        document_id=artifact.document_id,
        extracted=bool(artifact.extracted),
        notes=artifact.notes,
    )


@router.delete("/osint/artifacts/{artifact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_artifact(artifact_id: int, db: Session = Depends(get_db)):
    """Delete an artifact."""
    success = osint_service.delete_artifact(db, artifact_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artifact {artifact_id} not found",
        )

    return None


@router.post("/osint/extract", response_model=ExtractResponse)
def extract_artifacts(request: ExtractRequest, db: Session = Depends(get_db)):
    """
    Extract artifacts from text.

    Automatically identifies and extracts:
    - IP addresses
    - Domains
    - Email addresses
    - URLs
    - File hashes (MD5, SHA1, SHA256)
    - CVE identifiers
    - Cryptocurrency addresses
    """
    try:
        result = osint_service.extractor.extract_all(request.text)

        summary = {k: len(v) for k, v in result.items()}
        summary["total"] = sum(summary.values())

        return ExtractResponse(artifacts=result, summary=summary)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extraction failed: {str(e)}",
        )


@router.post("/osint/documents/{document_id}/extract")
def extract_from_document(
    document_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """
    Extract and analyze artifacts from a document.

    This will:
    1. Extract all IOCs from the document
    2. Store them in the database
    3. Analyze each artifact for threats
    """
    from ...models.database_models import Document

    # Get document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found",
        )

    # Get document text (from chunks)
    document_text = " ".join([chunk.chunk_text for chunk in document.chunks])

    if not document_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has no text content",
        )

    # Extract and analyze (in background)
    def process_extraction():
        osint_service.extract_and_analyze_document(
            db=db, document_id=document_id, document_text=document_text
        )

    background_tasks.add_task(process_extraction)

    return {
        "message": f"Extraction started for document {document_id}",
        "document_id": document_id,
    }


@router.get("/osint/stats", response_model=OSINTStatsResponse)
def get_osint_stats(db: Session = Depends(get_db)):
    """Get OSINT statistics and overview."""
    stats = osint_service.get_statistics(db)

    return OSINTStatsResponse(
        total_artifacts=stats["total_artifacts"],
        by_type=stats["by_type"],
        by_threat_level=stats["by_threat_level"],
    )


@router.post("/osint/artifacts/{artifact_id}/tag")
def add_tag(artifact_id: int, tag: str, db: Session = Depends(get_db)):
    """Add a tag to an artifact."""
    success = osint_service.add_tag_to_artifact(db, artifact_id, tag)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artifact {artifact_id} not found",
        )

    return {"message": f"Tag '{tag}' added to artifact {artifact_id}"}


# Web Scraping Endpoints
class ScrapeRequest(BaseModel):
    """Schema for web scraping request."""

    url: str = Field(..., description="URL to scrape")


@router.post("/osint/scrape")
def scrape_website(request: ScrapeRequest):
    """
    Scrape a website and extract all useful information.

    Extracts:
    - Page title, description, content
    - All links, images
    - Email addresses, phone numbers
    - Social media profiles
    - Technologies used
    - Metadata (Open Graph, Twitter Cards)
    """
    try:
        result = web_scraper.scrape_url(request.url)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Scraping failed: {str(e)}"
        )


@router.get("/osint/wayback/{url:path}")
def check_wayback(url: str):
    """
    Check if URL is archived in Wayback Machine.

    Returns information about available snapshots.
    """
    try:
        result = web_scraper.check_wayback_machine(url)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wayback check failed: {str(e)}",
        )


@router.get("/osint/robots/{url:path}")
def get_robots(url: str):
    """
    Fetch and parse robots.txt file.

    Returns disallowed paths and sitemaps.
    """
    try:
        result = web_scraper.get_robots_txt(url)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"robots.txt fetch failed: {str(e)}",
        )


@router.get("/osint/subdomains/{domain}")
def discover_subdomains(domain: str):
    """
    Attempt to discover subdomains for a given domain.

    Uses basic enumeration with common subdomain names.
    """
    try:
        subdomains = web_scraper.extract_subdomains(domain)
        return {"domain": domain, "subdomains": subdomains, "count": len(subdomains)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Subdomain discovery failed: {str(e)}",
        )
