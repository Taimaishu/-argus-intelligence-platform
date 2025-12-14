"""Hash and file intelligence service using VirusTotal."""

import requests
from typing import Dict, Any, Optional
from datetime import datetime

from ...config import settings
from ...utils.logger import logger


class HashIntelligenceService:
    """Service for hash and file analysis using VirusTotal."""

    def __init__(self):
        self.vt_api_key = settings.VT_API_KEY
        self.vt_base_url = "https://www.virustotal.com/api/v3"

    def analyze_hash(self, file_hash: str) -> Dict[str, Any]:
        """
        Analyze a file hash using VirusTotal.

        Args:
            file_hash: MD5, SHA1, or SHA256 hash

        Returns:
            Dictionary with analysis results
        """
        results = {
            "hash": file_hash,
            "timestamp": datetime.utcnow().isoformat(),
            "virustotal": {},
            "threat_level": "unknown",
            "detections": {},
        }

        if not self.vt_api_key:
            results["error"] = "VirusTotal API key not configured"
            return results

        try:
            # VirusTotal file report
            vt_data = self._virustotal_lookup(file_hash)
            if vt_data:
                results["virustotal"] = vt_data
                results["detections"] = self._parse_detections(vt_data)
                results["threat_level"] = self._assess_threat(vt_data)

        except Exception as e:
            logger.error(f"Error analyzing hash {file_hash}: {e}")
            results["error"] = str(e)

        return results

    def _virustotal_lookup(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Perform VirusTotal API lookup."""
        try:
            url = f"{self.vt_base_url}/files/{file_hash}"
            headers = {"x-apikey": self.vt_api_key}

            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                data = response.json()
                attributes = data.get("data", {}).get("attributes", {})

                return {
                    "md5": attributes.get("md5"),
                    "sha1": attributes.get("sha1"),
                    "sha256": attributes.get("sha256"),
                    "file_type": attributes.get("type_description"),
                    "file_size": attributes.get("size"),
                    "names": attributes.get("names", []),
                    "first_seen": attributes.get("first_submission_date"),
                    "last_seen": attributes.get("last_analysis_date"),
                    "stats": attributes.get("last_analysis_stats", {}),
                    "results": attributes.get("last_analysis_results", {}),
                    "tags": attributes.get("tags", []),
                    "reputation": attributes.get("reputation", 0),
                }

            elif response.status_code == 404:
                return {
                    "status": "not_found",
                    "message": "Hash not found in VirusTotal database",
                }

            return None

        except Exception as e:
            logger.error(f"VirusTotal lookup error: {e}")
            return None

    def _parse_detections(self, vt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse detection statistics from VirusTotal data."""
        stats = vt_data.get("stats", {})

        return {
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "undetected": stats.get("undetected", 0),
            "harmless": stats.get("harmless", 0),
            "total_engines": sum(stats.values()) if stats else 0,
            "detection_ratio": (
                f"{stats.get('malicious', 0)}/{sum(stats.values())}" if stats else "0/0"
            ),
        }

    def _assess_threat(self, vt_data: Dict[str, Any]) -> str:
        """Assess threat level based on VirusTotal data."""
        stats = vt_data.get("stats", {})
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        total = sum(stats.values()) if stats else 0

        if total == 0:
            return "unknown"

        malicious_ratio = malicious / total if total > 0 else 0

        if malicious >= 10 or malicious_ratio > 0.3:
            return "critical"
        elif malicious >= 5 or suspicious >= 10:
            return "high"
        elif malicious >= 1 or suspicious >= 5:
            return "medium"
        elif suspicious >= 1:
            return "low"
        else:
            return "safe"

    def analyze_url(self, url: str) -> Dict[str, Any]:
        """
        Analyze a URL using VirusTotal.

        Args:
            url: URL to analyze

        Returns:
            Dictionary with analysis results
        """
        results = {
            "url": url,
            "timestamp": datetime.utcnow().isoformat(),
            "virustotal": {},
            "threat_level": "unknown",
        }

        if not self.vt_api_key:
            results["error"] = "VirusTotal API key not configured"
            return results

        try:
            # VirusTotal URL report
            vt_data = self._virustotal_url_lookup(url)
            if vt_data:
                results["virustotal"] = vt_data
                results["threat_level"] = self._assess_url_threat(vt_data)

        except Exception as e:
            logger.error(f"Error analyzing URL {url}: {e}")
            results["error"] = str(e)

        return results

    def _virustotal_url_lookup(self, url: str) -> Optional[Dict[str, Any]]:
        """Perform VirusTotal URL lookup."""
        try:
            import base64

            # URL ID is base64 encoded URL without padding
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")

            lookup_url = f"{self.vt_base_url}/urls/{url_id}"
            headers = {"x-apikey": self.vt_api_key}

            response = requests.get(lookup_url, headers=headers, timeout=15)

            if response.status_code == 200:
                data = response.json()
                attributes = data.get("data", {}).get("attributes", {})

                return {
                    "url": attributes.get("url"),
                    "title": attributes.get("title"),
                    "last_analysis_date": attributes.get("last_analysis_date"),
                    "stats": attributes.get("last_analysis_stats", {}),
                    "results": attributes.get("last_analysis_results", {}),
                    "reputation": attributes.get("reputation", 0),
                    "categories": attributes.get("categories", {}),
                }

            return None

        except Exception as e:
            logger.error(f"VirusTotal URL lookup error: {e}")
            return None

    def _assess_url_threat(self, vt_data: Dict[str, Any]) -> str:
        """Assess URL threat level."""
        stats = vt_data.get("stats", {})
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)

        if malicious >= 5:
            return "critical"
        elif malicious >= 2:
            return "high"
        elif malicious >= 1 or suspicious >= 5:
            return "medium"
        elif suspicious >= 1:
            return "low"
        else:
            return "safe"
