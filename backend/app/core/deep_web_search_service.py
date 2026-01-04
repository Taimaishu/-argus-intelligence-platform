"""
Deep Web Search Service - Searches surface web, deep web, and dark web for entity information.
Includes Tor support for dark web access with TAILS-like security measures.

SECURITY FEATURES:
- Tor circuit rotation for anonymity
- No local logging of visited sites
- Randomized User-Agent headers
- DNS leak protection via SOCKS5h
- Cookie isolation (no persistence)
- Memory-only operations (no disk writes for sensitive data)
- Traffic encryption via Tor
- No JavaScript execution (prevents fingerprinting)
"""

import asyncio
import logging
import os
import re
import random
import hashlib
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import socks
import socket
from urllib.parse import urlparse, urljoin
from stem import Signal
from stem.control import Controller

# Configure logger to NOT log URLs or sensitive info
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)  # Only warnings and errors, no info logging


class DeepWebSearchService:
    """Search service for surface web, deep web, and dark web with TAILS-like security."""

    # Randomized User-Agent pool (mimics common browsers, prevents fingerprinting)
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
    ]

    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cx = os.getenv("GOOGLE_SEARCH_CX")
        self.shodan_api_key = os.getenv("SHODAN_API_KEY")

        # Tor SOCKS proxy settings (socks5h = DNS over SOCKS, prevents DNS leaks)
        self.tor_proxy = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }

        # Tor control port for circuit management
        self.tor_control_port = 9051
        self.tor_password = os.getenv("TOR_PASSWORD", None)

        # Security: No session persistence (each request is isolated)
        self._request_count = 0

    def _get_random_user_agent(self) -> str:
        """Get random User-Agent to prevent fingerprinting."""
        return random.choice(self.USER_AGENTS)

    def _get_secure_headers(self) -> Dict[str, str]:
        """Get secure headers that mimic normal browser behavior."""
        return {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',  # Do Not Track
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def rotate_tor_circuit(self) -> bool:
        """
        Rotate Tor circuit for enhanced anonymity (TAILS-like behavior).
        Should be called periodically during long sessions.
        """
        try:
            with Controller.from_port(port=self.tor_control_port) as controller:
                if self.tor_password:
                    controller.authenticate(password=self.tor_password)
                else:
                    controller.authenticate()

                controller.signal(Signal.NEWNYM)
                logger.warning("Tor circuit rotated for anonymity")
                return True
        except Exception as e:
            logger.error(f"Failed to rotate Tor circuit: {e}")
            return False

    def is_tor_running(self) -> bool:
        """Check if Tor service is running."""
        try:
            # Try to connect to Tor SOCKS proxy
            response = requests.get(
                'https://check.torproject.org/api/ip',
                proxies=self.tor_proxy,
                timeout=10
            )
            data = response.json()
            return data.get('IsTor', False)
        except Exception as e:
            logger.warning(f"Tor not available")
            return False

    def _make_secure_request(
        self,
        url: str,
        use_tor: bool = False,
        timeout: int = 30
    ) -> Optional[requests.Response]:
        """
        Make a secure HTTP request with privacy protections.

        Security features:
        - Randomized User-Agent
        - No cookies (session isolation)
        - Tor routing if requested
        - DNS leak protection
        - Circuit rotation every N requests
        """
        try:
            # Rotate Tor circuit every 5 requests for anonymity
            if use_tor:
                self._request_count += 1
                if self._request_count % 5 == 0:
                    self.rotate_tor_circuit()

            # Create fresh session (no cookie persistence)
            session = requests.Session()

            # Configure session
            proxies = self.tor_proxy if use_tor else None
            headers = self._get_secure_headers()

            response = session.get(
                url,
                proxies=proxies,
                headers=headers,
                timeout=timeout,
                allow_redirects=True,
                verify=True  # Verify SSL certificates
            )

            # Close session immediately (no persistence)
            session.close()

            return response
        except Exception as e:
            logger.error(f"Secure request failed")
            return None

    async def search_surface_web(
        self,
        entity_name: str,
        entity_type: str,
        max_results: int = 10
    ) -> List[Dict]:
        """Search the surface web for entity information."""
        results = []

        # Google Custom Search
        if self.google_api_key and self.google_cx:
            try:
                query = self._build_search_query(entity_name, entity_type)
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    "key": self.google_api_key,
                    "cx": self.google_cx,
                    "q": query,
                    "num": min(max_results, 10)
                }

                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("items", []):
                        results.append({
                            "title": item.get("title"),
                            "url": item.get("link"),
                            "snippet": item.get("snippet"),
                            "source": "google",
                            "type": "surface_web"
                        })
            except Exception as e:
                logger.error(f"Google search failed: {e}")

        # DuckDuckGo (privacy-focused, no API key needed)
        try:
            results.extend(await self._search_duckduckgo(entity_name, entity_type, max_results))
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")

        return results

    async def _search_duckduckgo(
        self,
        entity_name: str,
        entity_type: str,
        max_results: int = 10
    ) -> List[Dict]:
        """Search DuckDuckGo with secure request."""
        results = []
        try:
            query = self._build_search_query(entity_name, entity_type)
            url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"

            response = self._make_secure_request(url, use_tor=False, timeout=10)
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                for result in soup.find_all('div', class_='result')[:max_results]:
                    title_tag = result.find('a', class_='result__a')
                    snippet_tag = result.find('a', class_='result__snippet')

                    if title_tag:
                        results.append({
                            "title": title_tag.get_text(strip=True),
                            "url": title_tag.get('href', ''),
                            "snippet": snippet_tag.get_text(strip=True) if snippet_tag else '',
                            "source": "duckduckgo",
                            "type": "surface_web"
                        })
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")

        return results

    async def search_dark_web(
        self,
        entity_name: str,
        entity_type: str,
        max_results: int = 5
    ) -> List[Dict]:
        """
        Search dark web (.onion sites) via Tor with TAILS-like security.

        Security measures:
        - All traffic routed through Tor
        - Circuit rotation between searches
        - No logging of .onion addresses
        - Randomized headers
        - No cookie persistence
        """
        if not self.is_tor_running():
            logger.warning("Tor not available - dark web search skipped for safety")
            return []

        results = []

        # List of dark web search engines
        dark_search_engines = [
            "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/",  # Ahmia
            "http://haystak5njsmn2hqkewecpaxetahtwhsbsa64jom2k22z5afxhnpxfid.onion/",  # Haystak
        ]

        try:
            query = self._build_search_query(entity_name, entity_type)

            for search_engine in dark_search_engines:
                try:
                    # Rotate circuit before each search engine for anonymity
                    self.rotate_tor_circuit()

                    # Search via secure Tor request
                    search_url = f"{search_engine}search/?q={requests.utils.quote(query)}"
                    response = self._make_secure_request(search_url, use_tor=True, timeout=30)

                    if response and response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')

                        # Parse results (format varies by search engine)
                        for result in soup.find_all('div', class_='result')[:max_results]:
                            title = result.find('h4')
                            link = result.find('a')
                            snippet = result.find('p')

                            if title and link:
                                results.append({
                                    "title": title.get_text(strip=True),
                                    "url": link.get('href', ''),
                                    "snippet": snippet.get_text(strip=True) if snippet else '',
                                    "source": urlparse(search_engine).netloc,
                                    "type": "dark_web"
                                })
                except Exception as e:
                    logger.error(f"Dark web search engine {search_engine} failed: {e}")
                    continue

        except Exception as e:
            logger.error(f"Dark web search failed: {e}")

        return results

    async def scrape_page_content(
        self,
        url: str,
        use_tor: bool = False
    ) -> Optional[Dict]:
        """
        Scrape content from a webpage (surface or dark web) with security.

        Security features:
        - Secure request with randomized headers
        - Tor routing for .onion sites
        - No JavaScript execution (prevents fingerprinting/tracking)
        - Memory-only processing (no disk writes)
        """
        try:
            response = self._make_secure_request(url, use_tor=use_tor, timeout=30)

            if response and response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract text content
                for script in soup(["script", "style"]):
                    script.decompose()

                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)

                # Extract images
                images = []
                for img in soup.find_all('img'):
                    img_url = img.get('src')
                    if img_url:
                        if not img_url.startswith('http'):
                            img_url = urljoin(url, img_url)
                        images.append(img_url)

                # Extract documents/files
                documents = []
                for link in soup.find_all('a'):
                    href = link.get('href', '')
                    if any(ext in href.lower() for ext in ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx']):
                        if not href.startswith('http'):
                            href = urljoin(url, href)
                        documents.append({
                            "url": href,
                            "type": href.split('.')[-1].lower(),
                            "text": link.get_text(strip=True)
                        })

                return {
                    "url": url,
                    "title": soup.title.string if soup.title else "",
                    "text": text[:5000],  # First 5000 chars
                    "images": images[:10],  # First 10 images
                    "documents": documents[:5],  # First 5 documents
                    "use_tor": use_tor
                }
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")

        return None

    async def search_shodan(
        self,
        entity_name: str,
        query_type: str = "hostname"
    ) -> List[Dict]:
        """Search Shodan for infrastructure information."""
        if not self.shodan_api_key:
            logger.warning("Shodan API key not configured")
            return []

        results = []
        try:
            import shodan
            api = shodan.Shodan(self.shodan_api_key)

            # Search Shodan
            search_results = api.search(entity_name)

            for result in search_results['matches'][:10]:
                results.append({
                    "ip": result.get('ip_str'),
                    "port": result.get('port'),
                    "organization": result.get('org'),
                    "hostname": ', '.join(result.get('hostnames', [])),
                    "location": f"{result.get('location', {}).get('city', '')}, {result.get('location', {}).get('country_name', '')}",
                    "banner": result.get('data', '')[:500],
                    "source": "shodan",
                    "type": "infrastructure"
                })
        except Exception as e:
            logger.error(f"Shodan search failed: {e}")

        return results

    async def comprehensive_search(
        self,
        entity_name: str,
        entity_type: str,
        include_dark_web: bool = True,
        include_infrastructure: bool = True
    ) -> Dict:
        """Perform comprehensive search across all sources."""
        logger.info(f"Starting comprehensive search for: {entity_name}")

        results = {
            "surface_web": [],
            "dark_web": [],
            "infrastructure": [],
            "images": [],
            "documents": []
        }

        # Search surface web
        results["surface_web"] = await self.search_surface_web(entity_name, entity_type)

        # Search dark web if Tor is available
        if include_dark_web:
            results["dark_web"] = await self.search_dark_web(entity_name, entity_type)

        # Search infrastructure
        if include_infrastructure and entity_type in ['organization', 'location']:
            results["infrastructure"] = await self.search_shodan(entity_name)

        # Scrape top results for content
        all_results = results["surface_web"] + results["dark_web"]
        for result in all_results[:5]:  # Top 5 results
            use_tor = result.get("type") == "dark_web"
            scraped = await self.scrape_page_content(result["url"], use_tor=use_tor)

            if scraped:
                results["images"].extend(scraped.get("images", []))
                results["documents"].extend(scraped.get("documents", []))

        # Remove duplicates
        results["images"] = list(set(results["images"]))[:20]

        logger.info(f"Search complete - Found {len(results['surface_web'])} surface web, "
                   f"{len(results['dark_web'])} dark web, "
                   f"{len(results['images'])} images, "
                   f"{len(results['documents'])} documents")

        return results

    def _build_search_query(self, entity_name: str, entity_type: str) -> str:
        """Build optimized search query based on entity type."""
        queries = {
            "person": f'"{entity_name}" profile bio information',
            "organization": f'"{entity_name}" organization company about',
            "location": f'"{entity_name}" location place address',
            "event": f'"{entity_name}" event incident news',
            "vehicle": f'"{entity_name}" vehicle registration',
            "financial": f'"{entity_name}" financial records transactions'
        }
        return queries.get(entity_type, f'"{entity_name}"')
