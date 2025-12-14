"""IP and Domain intelligence service using Shodan and other APIs."""

import requests
import socket
import dns.resolver
from typing import Dict, Any, Optional
from datetime import datetime

from ...config import settings
from ...utils.logger import logger


class IPIntelligenceService:
    """Service for IP address and domain intelligence."""

    def __init__(self):
        self.shodan_api_key = settings.SHODAN_API_KEY
        self.shodan_base_url = "https://api.shodan.io"

    def analyze_ip(self, ip_address: str) -> Dict[str, Any]:
        """
        Comprehensive IP address analysis.

        Args:
            ip_address: IP address to analyze

        Returns:
            Dictionary with analysis results
        """
        results = {
            "ip": ip_address,
            "timestamp": datetime.utcnow().isoformat(),
            "geolocation": {},
            "shodan_data": {},
            "reverse_dns": None,
            "threat_intel": {},
        }

        try:
            # Reverse DNS lookup
            try:
                results["reverse_dns"] = socket.gethostbyaddr(ip_address)[0]
            except:
                pass

            # Shodan lookup
            if self.shodan_api_key:
                shodan_data = self._shodan_lookup(ip_address)
                if shodan_data:
                    results["shodan_data"] = shodan_data
                    results["geolocation"] = {
                        "country": shodan_data.get("country_name"),
                        "city": shodan_data.get("city"),
                        "latitude": shodan_data.get("latitude"),
                        "longitude": shodan_data.get("longitude"),
                        "org": shodan_data.get("org"),
                        "isp": shodan_data.get("isp"),
                    }

            # Basic threat assessment
            results["threat_intel"] = self._assess_threat(results)

        except Exception as e:
            logger.error(f"Error analyzing IP {ip_address}: {e}")
            results["error"] = str(e)

        return results

    def analyze_domain(self, domain: str) -> Dict[str, Any]:
        """
        Comprehensive domain analysis.

        Args:
            domain: Domain name to analyze

        Returns:
            Dictionary with analysis results
        """
        results = {
            "domain": domain,
            "timestamp": datetime.utcnow().isoformat(),
            "dns_records": {},
            "whois": {},
            "ips": [],
            "subdomains": [],
        }

        try:
            # DNS resolution
            results["dns_records"] = self._get_dns_records(domain)

            # Extract IP addresses
            if "A" in results["dns_records"]:
                results["ips"] = results["dns_records"]["A"]

            # WHOIS lookup (basic)
            results["whois"] = self._whois_lookup(domain)

        except Exception as e:
            logger.error(f"Error analyzing domain {domain}: {e}")
            results["error"] = str(e)

        return results

    def _shodan_lookup(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Perform Shodan API lookup."""
        if not self.shodan_api_key:
            return None

        try:
            url = f"{self.shodan_base_url}/shodan/host/{ip_address}"
            params = {"key": self.shodan_api_key}

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    "ip": data.get("ip_str"),
                    "country_name": data.get("country_name"),
                    "city": data.get("city"),
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude"),
                    "org": data.get("org"),
                    "isp": data.get("isp"),
                    "asn": data.get("asn"),
                    "ports": data.get("ports", []),
                    "hostnames": data.get("hostnames", []),
                    "domains": data.get("domains", []),
                    "vulns": data.get("vulns", []),
                    "tags": data.get("tags", []),
                }

            return None

        except Exception as e:
            logger.error(f"Shodan lookup error: {e}")
            return None

    def _get_dns_records(self, domain: str) -> Dict[str, list]:
        """Get DNS records for a domain."""
        records = {}
        record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]

        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(domain, record_type)
                records[record_type] = [str(rdata) for rdata in answers]
            except:
                pass

        return records

    def _whois_lookup(self, domain: str) -> Dict[str, Any]:
        """Basic WHOIS lookup using API."""
        try:
            # Using a free WHOIS API
            url = f"https://www.whoisxmlapi.com/whoisserver/WhoisService"
            params = {"domainName": domain, "outputFormat": "JSON"}

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()

            return {}
        except Exception as e:
            logger.error(f"WHOIS lookup error: {e}")
            return {}

    def _assess_threat(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess threat level based on analysis data."""
        threat_indicators = []
        threat_level = "unknown"

        shodan = analysis_data.get("shodan_data", {})

        # Check for vulnerabilities
        if shodan.get("vulns"):
            threat_indicators.append("Known vulnerabilities detected")
            threat_level = "high"

        # Check for suspicious tags
        suspicious_tags = ["malware", "botnet", "tor", "proxy", "scanner"]
        tags = shodan.get("tags", [])
        if any(tag in tags for tag in suspicious_tags):
            threat_indicators.append(
                f"Suspicious tags: {', '.join(set(tags) & set(suspicious_tags))}"
            )
            threat_level = "medium" if threat_level == "unknown" else threat_level

        # Check open ports
        ports = shodan.get("ports", [])
        suspicious_ports = [
            23,
            445,
            1433,
            3306,
            3389,
            5900,
        ]  # Telnet, SMB, MSSQL, MySQL, RDP, VNC
        open_suspicious = [p for p in ports if p in suspicious_ports]
        if open_suspicious:
            threat_indicators.append(
                f"Suspicious open ports: {', '.join(map(str, open_suspicious))}"
            )
            if threat_level == "unknown":
                threat_level = "low"

        if not threat_indicators and shodan:
            threat_level = "safe"
            threat_indicators.append("No obvious threats detected")

        return {"level": threat_level, "indicators": threat_indicators}
