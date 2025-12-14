"""Email intelligence service with breach checking."""

import requests
import re
from typing import Dict, Any, Optional
from datetime import datetime

from ...utils.logger import logger


class EmailIntelligenceService:
    """Service for email analysis and breach checking."""

    def __init__(self):
        self.hibp_base_url = "https://haveibeenpwned.com/api/v3"

    def analyze_email(self, email: str) -> Dict[str, Any]:
        """
        Comprehensive email analysis.

        Args:
            email: Email address to analyze

        Returns:
            Dictionary with analysis results
        """
        results = {
            "email": email,
            "timestamp": datetime.utcnow().isoformat(),
            "valid": False,
            "domain": None,
            "breaches": [],
            "breach_count": 0,
            "pastes": [],
            "threat_level": "unknown",
        }

        try:
            # Validate email format
            results["valid"] = self._validate_email(email)

            if results["valid"]:
                # Extract domain
                results["domain"] = email.split("@")[1]

                # Check for breaches (using HIBP API)
                breach_data = self._check_breaches(email)
                if breach_data:
                    results["breaches"] = breach_data
                    results["breach_count"] = len(breach_data)

                # Assess threat level
                results["threat_level"] = self._assess_threat(results)

        except Exception as e:
            logger.error(f"Error analyzing email {email}: {e}")
            results["error"] = str(e)

        return results

    def _validate_email(self, email: str) -> bool:
        """Validate email format using regex."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def _check_breaches(self, email: str) -> Optional[list]:
        """
        Check if email appears in known data breaches using Have I Been Pwned API.

        Note: HIBP API requires an API key for breach checking, but we'll use
        a basic implementation that works without authentication.
        """
        try:
            # Using the public breach API (limited functionality without API key)
            url = f"{self.hibp_base_url}/breachedaccount/{email}"
            headers = {"User-Agent": "ResearchTool-OSINT"}

            # Note: This will return 401 without API key, but we'll handle gracefully
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                breaches = response.json()
                return [
                    {
                        "name": breach.get("Name"),
                        "title": breach.get("Title"),
                        "domain": breach.get("Domain"),
                        "breach_date": breach.get("BreachDate"),
                        "added_date": breach.get("AddedDate"),
                        "pwn_count": breach.get("PwnCount"),
                        "description": breach.get("Description", "")[:200],  # Truncate
                        "data_classes": breach.get("DataClasses", []),
                        "is_verified": breach.get("IsVerified"),
                        "is_sensitive": breach.get("IsSensitive"),
                    }
                    for breach in breaches
                ]

            elif response.status_code == 404:
                # No breaches found (good!)
                return []

            elif response.status_code == 401:
                # API key required for full functionality
                return [
                    {
                        "note": "HIBP API key required for breach checking. Add to .env file."
                    }
                ]

            return None

        except Exception as e:
            logger.error(f"Breach check error: {e}")
            return [{"error": f"Breach check failed: {str(e)}"}]

    def parse_email_header(self, header: str) -> Dict[str, Any]:
        """
        Parse email headers for investigation.

        Args:
            header: Raw email header text

        Returns:
            Dictionary with parsed header information
        """
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "from": None,
            "to": None,
            "subject": None,
            "date": None,
            "message_id": None,
            "ip_addresses": [],
            "domains": [],
            "received_hops": [],
        }

        try:
            lines = header.split("\n")

            for line in lines:
                # Extract key headers
                if line.startswith("From:"):
                    results["from"] = line.split(":", 1)[1].strip()
                elif line.startswith("To:"):
                    results["to"] = line.split(":", 1)[1].strip()
                elif line.startswith("Subject:"):
                    results["subject"] = line.split(":", 1)[1].strip()
                elif line.startswith("Date:"):
                    results["date"] = line.split(":", 1)[1].strip()
                elif line.startswith("Message-ID:"):
                    results["message_id"] = line.split(":", 1)[1].strip()
                elif line.startswith("Received:"):
                    results["received_hops"].append(line.split(":", 1)[1].strip())

            # Extract IP addresses from header
            ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
            results["ip_addresses"] = list(set(re.findall(ip_pattern, header)))

            # Extract domains
            domain_pattern = r"@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
            results["domains"] = list(set(re.findall(domain_pattern, header)))

        except Exception as e:
            logger.error(f"Email header parsing error: {e}")
            results["error"] = str(e)

        return results

    def _assess_threat(self, analysis_data: Dict[str, Any]) -> str:
        """Assess threat level based on breach data."""
        breach_count = analysis_data.get("breach_count", 0)

        if breach_count >= 10:
            return "critical"
        elif breach_count >= 5:
            return "high"
        elif breach_count >= 1:
            return "medium"
        else:
            return "safe"
