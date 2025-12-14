"""Artifact extraction service for extracting IOCs from text."""

import re
from typing import List, Dict, Any, Set
from ...utils.logger import logger


class ArtifactExtractor:
    """Extract various artifacts (IOCs) from text content."""

    # Regex patterns for different artifact types
    PATTERNS = {
        "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        "email": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
        "domain": r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b",
        "url": r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)",
        "md5": r"\b[a-fA-F0-9]{32}\b",
        "sha1": r"\b[a-fA-F0-9]{40}\b",
        "sha256": r"\b[a-fA-F0-9]{64}\b",
        "cve": r"CVE-\d{4}-\d{4,7}",
        "bitcoin": r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b",
        "ethereum": r"\b0x[a-fA-F0-9]{40}\b",
    }

    def extract_all(self, text: str) -> Dict[str, List[str]]:
        """
        Extract all artifact types from text.

        Args:
            text: Text content to analyze

        Returns:
            Dictionary mapping artifact types to lists of found values
        """
        artifacts = {}

        for artifact_type, pattern in self.PATTERNS.items():
            found = self.extract_by_type(text, artifact_type)
            if found:
                artifacts[artifact_type] = found

        return artifacts

    def extract_by_type(self, text: str, artifact_type: str) -> List[str]:
        """
        Extract specific artifact type from text.

        Args:
            text: Text content to analyze
            artifact_type: Type of artifact to extract

        Returns:
            List of unique artifacts found
        """
        if artifact_type not in self.PATTERNS:
            logger.warning(f"Unknown artifact type: {artifact_type}")
            return []

        pattern = self.PATTERNS[artifact_type]
        matches = re.findall(pattern, text, re.IGNORECASE)

        # Remove duplicates and filter
        unique_matches = list(set(matches))

        # Apply type-specific filtering
        if artifact_type == "ip_address":
            unique_matches = self._filter_valid_ips(unique_matches)
        elif artifact_type == "domain":
            unique_matches = self._filter_valid_domains(unique_matches)
        elif artifact_type == "email":
            unique_matches = self._filter_valid_emails(unique_matches)

        return sorted(unique_matches)

    def _filter_valid_ips(self, ips: List[str]) -> List[str]:
        """Filter out invalid or private IP addresses."""
        valid_ips = []

        for ip in ips:
            parts = ip.split(".")
            if len(parts) != 4:
                continue

            try:
                octets = [int(p) for p in parts]

                # Check valid range
                if all(0 <= octet <= 255 for octet in octets):
                    # Skip private/reserved IPs for OSINT purposes
                    if octets[0] in [10, 127]:  # Private, loopback
                        continue
                    if octets[0] == 172 and 16 <= octets[1] <= 31:  # Private
                        continue
                    if octets[0] == 192 and octets[1] == 168:  # Private
                        continue
                    if octets[0] == 0 or octets[0] >= 224:  # Reserved, multicast
                        continue

                    valid_ips.append(ip)

            except ValueError:
                continue

        return valid_ips

    def _filter_valid_domains(self, domains: List[str]) -> List[str]:
        """Filter out invalid domains."""
        valid_domains = []

        # Common file extensions to exclude
        exclude_extensions = {
            "jpg",
            "jpeg",
            "png",
            "gif",
            "pdf",
            "doc",
            "docx",
            "xls",
            "xlsx",
            "zip",
            "rar",
            "exe",
            "dll",
            "txt",
        }

        for domain in domains:
            # Skip if it's likely a file
            if "." in domain:
                ext = domain.split(".")[-1].lower()
                if ext in exclude_extensions:
                    continue

            # Must have at least one dot
            if "." not in domain:
                continue

            # Skip very short domains
            if len(domain) < 4:
                continue

            valid_domains.append(domain.lower())

        return valid_domains

    def _filter_valid_emails(self, emails: List[str]) -> List[str]:
        """Filter out invalid email addresses."""
        valid_emails = []

        for email in emails:
            # Basic validation
            if "@" not in email or "." not in email:
                continue

            # Check for common false positives
            if email.endswith(".png") or email.endswith(".jpg"):
                continue

            valid_emails.append(email.lower())

        return valid_emails

    def extract_from_document(
        self, document_text: str, document_id: int
    ) -> Dict[str, Any]:
        """
        Extract artifacts from a document and prepare for database storage.

        Args:
            document_text: Full text content of document
            document_id: ID of the source document

        Returns:
            Dictionary with extracted artifacts organized by type
        """
        result = {"document_id": document_id, "artifacts": {}, "summary": {}}

        # Extract all artifact types
        artifacts = self.extract_all(document_text)

        # Organize results
        for artifact_type, values in artifacts.items():
            result["artifacts"][artifact_type] = [
                {"value": value, "type": artifact_type, "document_id": document_id}
                for value in values
            ]

        # Create summary
        result["summary"] = {
            artifact_type: len(values) for artifact_type, values in artifacts.items()
        }

        total_artifacts = sum(result["summary"].values())
        result["summary"]["total"] = total_artifacts

        logger.info(
            f"Extracted {total_artifacts} artifacts from document {document_id}"
        )

        return result

    def extract_iocs(self, text: str) -> Dict[str, List[str]]:
        """
        Extract Indicators of Compromise (IOCs) from text.
        Focuses on security-relevant artifacts.

        Args:
            text: Text content to analyze

        Returns:
            Dictionary of IOC types and values
        """
        ioc_types = ["ip_address", "domain", "url", "md5", "sha1", "sha256", "cve"]

        iocs = {}
        for ioc_type in ioc_types:
            found = self.extract_by_type(text, ioc_type)
            if found:
                iocs[ioc_type] = found

        return iocs
