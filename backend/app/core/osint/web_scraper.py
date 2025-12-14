"""Web scraping and reconnaissance service."""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...utils.logger import logger


class WebScraperService:
    """Service for web scraping and reconnaissance."""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Comprehensive web page scraping and analysis.

        Args:
            url: URL to scrape

        Returns:
            Dictionary with scraped data and metadata
        """
        result = {
            "url": url,
            "timestamp": datetime.utcnow().isoformat(),
            "status_code": None,
            "title": None,
            "description": None,
            "headers": {},
            "content": None,
            "links": [],
            "images": [],
            "emails": [],
            "phones": [],
            "social_media": {},
            "technologies": [],
            "metadata": {},
        }

        try:
            # Fetch the page
            response = requests.get(url, headers=self.headers, timeout=15, verify=True)
            result["status_code"] = response.status_code
            result["headers"] = dict(response.headers)

            if response.status_code != 200:
                result["error"] = f"HTTP {response.status_code}"
                return result

            # Parse HTML
            soup = BeautifulSoup(response.content, "html.parser")

            # Extract title
            if soup.title:
                result["title"] = soup.title.string.strip()

            # Extract meta description
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                result["description"] = meta_desc.get("content", "").strip()

            # Extract all text content
            result["content"] = soup.get_text(separator=" ", strip=True)

            # Extract links
            result["links"] = self._extract_links(soup, url)

            # Extract images
            result["images"] = self._extract_images(soup, url)

            # Extract emails
            result["emails"] = self._extract_emails(result["content"])

            # Extract phone numbers
            result["phones"] = self._extract_phones(result["content"])

            # Extract social media links
            result["social_media"] = self._extract_social_media(result["links"])

            # Detect technologies
            result["technologies"] = self._detect_technologies(soup, result["headers"])

            # Extract metadata
            result["metadata"] = self._extract_metadata(soup)

            # Word count
            result["word_count"] = len(result["content"].split())

            logger.info(f"Successfully scraped {url}")

        except requests.exceptions.SSLError:
            result["error"] = "SSL certificate verification failed"
            logger.warning(f"SSL error for {url}")
        except requests.exceptions.Timeout:
            result["error"] = "Request timeout"
            logger.warning(f"Timeout for {url}")
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error scraping {url}: {e}")

        return result

    def _extract_links(
        self, soup: BeautifulSoup, base_url: str
    ) -> List[Dict[str, str]]:
        """Extract all links from the page."""
        links = []
        seen = set()

        for link in soup.find_all("a", href=True):
            href = link["href"]
            absolute_url = urljoin(base_url, href)

            if absolute_url not in seen:
                seen.add(absolute_url)
                links.append(
                    {
                        "url": absolute_url,
                        "text": link.get_text(strip=True)[:100],
                        "rel": link.get("rel", []),
                    }
                )

        return links[:100]  # Limit to first 100 links

    def _extract_images(
        self, soup: BeautifulSoup, base_url: str
    ) -> List[Dict[str, str]]:
        """Extract all images from the page."""
        images = []

        for img in soup.find_all("img"):
            src = img.get("src")
            if src:
                absolute_url = urljoin(base_url, src)
                images.append(
                    {
                        "url": absolute_url,
                        "alt": img.get("alt", ""),
                        "title": img.get("title", ""),
                    }
                )

        return images[:50]  # Limit to first 50 images

    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, text)
        return list(set(emails))[:20]  # Limit to 20 unique emails

    def _extract_phones(self, text: str) -> List[str]:
        """Extract phone numbers from text."""
        # Basic phone pattern (US-centric, can be extended)
        phone_pattern = (
            r"\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b"
        )
        phones = re.findall(phone_pattern, text)
        return ["-".join(phone) for phone in phones[:20]]  # Limit to 20

    def _extract_social_media(
        self, links: List[Dict[str, str]]
    ) -> Dict[str, List[str]]:
        """Extract social media profile links."""
        social_media = {
            "twitter": [],
            "facebook": [],
            "linkedin": [],
            "instagram": [],
            "youtube": [],
            "github": [],
            "telegram": [],
        }

        for link in links:
            url = link["url"].lower()

            if "twitter.com" in url or "x.com" in url:
                social_media["twitter"].append(link["url"])
            elif "facebook.com" in url:
                social_media["facebook"].append(link["url"])
            elif "linkedin.com" in url:
                social_media["linkedin"].append(link["url"])
            elif "instagram.com" in url:
                social_media["instagram"].append(link["url"])
            elif "youtube.com" in url:
                social_media["youtube"].append(link["url"])
            elif "github.com" in url:
                social_media["github"].append(link["url"])
            elif "t.me" in url:
                social_media["telegram"].append(link["url"])

        # Remove empty lists
        return {k: v for k, v in social_media.items() if v}

    def _detect_technologies(
        self, soup: BeautifulSoup, headers: Dict[str, str]
    ) -> List[str]:
        """Detect technologies used by the website."""
        technologies = []

        # Check headers
        server = headers.get("Server", "").lower()
        if "nginx" in server:
            technologies.append("Nginx")
        elif "apache" in server:
            technologies.append("Apache")

        powered_by = headers.get("X-Powered-By", "").lower()
        if "php" in powered_by:
            technologies.append("PHP")
        elif "asp.net" in powered_by:
            technologies.append("ASP.NET")

        # Check meta tags
        for meta in soup.find_all("meta"):
            generator = meta.get("generator", "").lower()
            if "wordpress" in generator:
                technologies.append("WordPress")
            elif "drupal" in generator:
                technologies.append("Drupal")
            elif "joomla" in generator:
                technologies.append("Joomla")

        # Check scripts
        for script in soup.find_all("script", src=True):
            src = script["src"].lower()
            if "jquery" in src:
                technologies.append("jQuery")
            elif "react" in src:
                technologies.append("React")
            elif "vue" in src:
                technologies.append("Vue.js")
            elif "angular" in src:
                technologies.append("Angular")

        return list(set(technologies))

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract various metadata from the page."""
        metadata = {}

        # Open Graph tags
        og_tags = soup.find_all("meta", property=re.compile(r"^og:"))
        for tag in og_tags:
            prop = tag.get("property", "")
            content = tag.get("content", "")
            metadata[prop] = content

        # Twitter Card tags
        twitter_tags = soup.find_all("meta", attrs={"name": re.compile(r"^twitter:")})
        for tag in twitter_tags:
            name = tag.get("name", "")
            content = tag.get("content", "")
            metadata[name] = content

        # Other meta tags
        for meta in soup.find_all("meta"):
            name = meta.get("name", meta.get("property", ""))
            content = meta.get("content", "")
            if name and content and name not in metadata:
                metadata[name] = content

        return metadata

    def check_wayback_machine(self, url: str) -> Dict[str, Any]:
        """
        Check if URL is archived in Wayback Machine.

        Args:
            url: URL to check

        Returns:
            Dictionary with archive information
        """
        result = {
            "url": url,
            "archived": False,
            "snapshots": [],
            "first_snapshot": None,
            "last_snapshot": None,
        }

        try:
            # Check availability
            api_url = f"http://archive.org/wayback/available?url={url}"
            response = requests.get(api_url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                archived = data.get("archived_snapshots", {})

                if archived and "closest" in archived:
                    closest = archived["closest"]
                    result["archived"] = True
                    result["last_snapshot"] = {
                        "url": closest.get("url"),
                        "timestamp": closest.get("timestamp"),
                        "status": closest.get("status"),
                    }

            # Get calendar data for snapshot count
            calendar_url = f"http://web.archive.org/__wb/calendarcaptures/2?url={url}&selected_year=2024"
            cal_response = requests.get(calendar_url, timeout=10)

            if cal_response.status_code == 200:
                cal_data = cal_response.json()
                years = cal_data.get("years", [])
                if years:
                    result["snapshot_count"] = sum(
                        sum(month.values()) for year in years for month in year.values()
                    )

        except Exception as e:
            logger.error(f"Wayback Machine check error: {e}")
            result["error"] = str(e)

        return result

    def extract_subdomains(self, domain: str) -> List[str]:
        """
        Attempt to discover subdomains (basic enumeration).

        Args:
            domain: Domain to check

        Returns:
            List of discovered subdomains
        """
        subdomains = []
        common_subdomains = [
            "www",
            "mail",
            "ftp",
            "admin",
            "blog",
            "dev",
            "staging",
            "api",
            "app",
            "portal",
            "shop",
            "store",
            "support",
        ]

        for subdomain in common_subdomains:
            test_domain = f"{subdomain}.{domain}"
            try:
                response = requests.head(
                    f"http://{test_domain}", timeout=3, allow_redirects=True
                )
                if response.status_code < 400:
                    subdomains.append(test_domain)
            except:
                continue

        return subdomains

    def get_robots_txt(self, url: str) -> Dict[str, Any]:
        """
        Fetch and parse robots.txt file.

        Args:
            url: Base URL

        Returns:
            Dictionary with robots.txt content and parsed rules
        """
        result = {
            "url": url,
            "exists": False,
            "content": None,
            "disallowed_paths": [],
            "sitemaps": [],
        }

        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

            response = requests.get(robots_url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                result["exists"] = True
                result["content"] = response.text

                # Parse disallow rules
                for line in response.text.split("\n"):
                    line = line.strip()
                    if line.lower().startswith("disallow:"):
                        path = line.split(":", 1)[1].strip()
                        if path:
                            result["disallowed_paths"].append(path)
                    elif line.lower().startswith("sitemap:"):
                        sitemap = line.split(":", 1)[1].strip()
                        result["sitemaps"].append(sitemap)

        except Exception as e:
            logger.error(f"robots.txt fetch error: {e}")
            result["error"] = str(e)

        return result
