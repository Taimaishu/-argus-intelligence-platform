"""Main OSINT orchestration service."""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from .ip_intelligence import IPIntelligenceService
from .hash_intelligence import HashIntelligenceService
from .email_intelligence import EmailIntelligenceService
from .artifact_extractor import ArtifactExtractor
from ...models.database_models import Artifact, ArtifactTag
from ...models.enums import ArtifactType, AnalysisStatus, ThreatLevel
from ...utils.logger import logger


class OSINTService:
    """Main service for coordinating OSINT operations."""

    def __init__(self):
        self.ip_intel = IPIntelligenceService()
        self.hash_intel = HashIntelligenceService()
        self.email_intel = EmailIntelligenceService()
        self.extractor = ArtifactExtractor()

    def analyze_artifact(
        self,
        db: Session,
        artifact_type: str,
        value: str,
        document_id: Optional[int] = None,
    ) -> Artifact:
        """
        Analyze an artifact and store results in database.

        Args:
            db: Database session
            artifact_type: Type of artifact (ip, domain, email, hash, url)
            value: Artifact value to analyze
            document_id: Optional source document ID

        Returns:
            Artifact database object with analysis results
        """
        # Check if artifact already exists
        existing = (
            db.query(Artifact)
            .filter(
                Artifact.artifact_type == ArtifactType[artifact_type.upper()],
                Artifact.value == value,
            )
            .first()
        )

        if existing:
            # Update existing artifact
            artifact = existing
            artifact.analysis_status = AnalysisStatus.ANALYZING
        else:
            # Create new artifact
            artifact = Artifact(
                artifact_type=ArtifactType[artifact_type.upper()],
                value=value,
                document_id=document_id,
                analysis_status=AnalysisStatus.ANALYZING,
                extracted=0 if document_id is None else 1,
            )
            db.add(artifact)
            db.commit()
            db.refresh(artifact)

        # Perform analysis based on type
        try:
            analysis_data = None

            if artifact_type == "ip_address":
                analysis_data = self.ip_intel.analyze_ip(value)
            elif artifact_type == "domain":
                analysis_data = self.ip_intel.analyze_domain(value)
            elif artifact_type == "email":
                analysis_data = self.email_intel.analyze_email(value)
            elif artifact_type in ["hash", "md5", "sha1", "sha256"]:
                analysis_data = self.hash_intel.analyze_hash(value)
            elif artifact_type == "url":
                analysis_data = self.hash_intel.analyze_url(value)

            if analysis_data:
                # Update artifact with results
                artifact.analysis_data = analysis_data
                artifact.analysis_status = AnalysisStatus.COMPLETED
                artifact.last_analyzed = datetime.utcnow()

                # Set threat level
                threat_level_str = analysis_data.get("threat_level", "unknown")
                if threat_level_str in ThreatLevel.__members__:
                    artifact.threat_level = ThreatLevel[threat_level_str.upper()]

                db.commit()
                db.refresh(artifact)

                logger.info(
                    f"Analyzed {artifact_type}: {value} - Threat: {threat_level_str}"
                )

        except Exception as e:
            logger.error(f"Error analyzing artifact {value}: {e}")
            artifact.analysis_status = AnalysisStatus.FAILED
            artifact.notes = f"Analysis error: {str(e)}"
            db.commit()
            db.refresh(artifact)

        return artifact

    def extract_and_analyze_document(
        self, db: Session, document_id: int, document_text: str
    ) -> Dict[str, Any]:
        """
        Extract artifacts from document and analyze them.

        Args:
            db: Database session
            document_id: ID of source document
            document_text: Full text content

        Returns:
            Dictionary with extraction and analysis results
        """
        result = {
            "document_id": document_id,
            "extracted_count": 0,
            "analyzed_count": 0,
            "artifacts": [],
        }

        try:
            # Extract artifacts
            extraction_result = self.extractor.extract_from_document(
                document_text, document_id
            )

            # Store and analyze each artifact
            for artifact_type, artifacts_list in extraction_result["artifacts"].items():
                for artifact_data in artifacts_list:
                    # Check if already exists
                    existing = (
                        db.query(Artifact)
                        .filter(
                            Artifact.value == artifact_data["value"],
                            Artifact.artifact_type
                            == ArtifactType[artifact_type.upper()],
                        )
                        .first()
                    )

                    if not existing:
                        # Create artifact
                        artifact = self.analyze_artifact(
                            db=db,
                            artifact_type=artifact_type,
                            value=artifact_data["value"],
                            document_id=document_id,
                        )

                        result["artifacts"].append(
                            {
                                "id": artifact.id,
                                "type": artifact_type,
                                "value": artifact.value,
                                "threat_level": artifact.threat_level.value,
                            }
                        )

                        result["extracted_count"] += 1
                        if artifact.analysis_status == AnalysisStatus.COMPLETED:
                            result["analyzed_count"] += 1

            logger.info(
                f"Document {document_id}: Extracted {result['extracted_count']} artifacts, "
                f"analyzed {result['analyzed_count']}"
            )

        except Exception as e:
            logger.error(f"Error extracting artifacts from document {document_id}: {e}")
            result["error"] = str(e)

        return result

    def get_artifacts(
        self,
        db: Session,
        artifact_type: Optional[str] = None,
        threat_level: Optional[str] = None,
        limit: int = 100,
    ) -> List[Artifact]:
        """
        Get artifacts from database with optional filtering.

        Args:
            db: Database session
            artifact_type: Filter by artifact type
            threat_level: Filter by threat level
            limit: Maximum number of results

        Returns:
            List of Artifact objects
        """
        query = db.query(Artifact)

        if artifact_type:
            query = query.filter(
                Artifact.artifact_type == ArtifactType[artifact_type.upper()]
            )

        if threat_level:
            query = query.filter(
                Artifact.threat_level == ThreatLevel[threat_level.upper()]
            )

        query = query.order_by(Artifact.first_seen.desc()).limit(limit)

        return query.all()

    def get_artifact_by_id(self, db: Session, artifact_id: int) -> Optional[Artifact]:
        """Get artifact by ID."""
        return db.query(Artifact).filter(Artifact.id == artifact_id).first()

    def delete_artifact(self, db: Session, artifact_id: int) -> bool:
        """Delete an artifact."""
        artifact = self.get_artifact_by_id(db, artifact_id)
        if artifact:
            db.delete(artifact)
            db.commit()
            return True
        return False

    def add_tag_to_artifact(self, db: Session, artifact_id: int, tag: str) -> bool:
        """Add a tag to an artifact."""
        artifact = self.get_artifact_by_id(db, artifact_id)
        if not artifact:
            return False

        # Check if tag already exists
        existing = (
            db.query(ArtifactTag)
            .filter(ArtifactTag.artifact_id == artifact_id, ArtifactTag.tag == tag)
            .first()
        )

        if not existing:
            artifact_tag = ArtifactTag(artifact_id=artifact_id, tag=tag)
            db.add(artifact_tag)
            db.commit()

        return True

    def get_statistics(self, db: Session) -> Dict[str, Any]:
        """Get OSINT statistics."""
        total_artifacts = db.query(Artifact).count()

        # Count by type
        by_type = {}
        for artifact_type in ArtifactType:
            count = (
                db.query(Artifact)
                .filter(Artifact.artifact_type == artifact_type)
                .count()
            )
            by_type[artifact_type.value] = count

        # Count by threat level
        by_threat = {}
        for threat_level in ThreatLevel:
            count = (
                db.query(Artifact).filter(Artifact.threat_level == threat_level).count()
            )
            by_threat[threat_level.value] = count

        return {
            "total_artifacts": total_artifacts,
            "by_type": by_type,
            "by_threat_level": by_threat,
        }
