"""Content extraction from URLs (YouTube, web pages, etc.)."""

import re
from typing import Optional, Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi
from bs4 import BeautifulSoup
import requests

from app.utils.logger import logger


class ContentExtractor:
    """Extract content from various URL types for LLM context."""

    def __init__(self):
        self.youtube_pattern = re.compile(
            r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})"
        )
        self.url_pattern = re.compile(
            r"https?://[^\s<>\"]+|www\.[^\s<>\"]+", re.IGNORECASE
        )

    def extract_urls(self, text: str) -> list[str]:
        """Extract all URLs from text."""
        return self.url_pattern.findall(text)

    def extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL."""
        match = self.youtube_pattern.search(url)
        return match.group(1) if match else None

    def get_youtube_transcript(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get transcript from a YouTube video.

        Returns:
            Dict with 'title', 'transcript', and 'url'
        """
        try:
            # Get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

            # Combine all transcript segments
            full_transcript = " ".join([entry["text"] for entry in transcript_list])

            # Try to get video title from YouTube
            url = f"https://www.youtube.com/watch?v={video_id}"
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")
                title_tag = soup.find("meta", property="og:title")
                title = (
                    title_tag["content"] if title_tag else f"YouTube Video {video_id}"
                )
            except:
                title = f"YouTube Video {video_id}"

            return {
                "type": "youtube",
                "title": title,
                "transcript": full_transcript,
                "url": url,
                "video_id": video_id,
            }

        except Exception as e:
            logger.error(f"Error getting YouTube transcript for {video_id}: {e}")
            return None

    def get_webpage_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract main content from a webpage.

        Returns:
            Dict with 'title', 'content', and 'url'
        """
        try:
            response = requests.get(
                url,
                timeout=15,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Try to get title
            title = soup.title.string if soup.title else url

            # Get main content
            # Try to find main content area
            main_content = (
                soup.find("main")
                or soup.find("article")
                or soup.find("div", class_=re.compile("content|main|article"))
                or soup.find("body")
            )

            if main_content:
                text = main_content.get_text(separator=" ", strip=True)
                # Clean up extra whitespace
                text = re.sub(r"\s+", " ", text).strip()
                # Limit length
                text = text[:15000]  # ~15k chars max
            else:
                text = "Could not extract content from page"

            return {"type": "webpage", "title": title, "content": text, "url": url}

        except Exception as e:
            logger.error(f"Error extracting webpage content from {url}: {e}")
            return None

    def extract_all_content(self, message: str) -> list[Dict[str, Any]]:
        """
        Extract content from all URLs found in a message.

        Returns:
            List of extracted content dictionaries
        """
        urls = self.extract_urls(message)
        extracted_content = []

        for url in urls:
            # Check if YouTube
            video_id = self.extract_youtube_id(url)
            if video_id:
                content = self.get_youtube_transcript(video_id)
                if content:
                    extracted_content.append(content)
            else:
                # Try as regular webpage
                content = self.get_webpage_content(url)
                if content:
                    extracted_content.append(content)

        return extracted_content

    def format_content_for_context(
        self, extracted_content: list[Dict[str, Any]]
    ) -> str:
        """Format extracted content as context for LLM."""
        if not extracted_content:
            return ""

        context_parts = ["\n\n--- REFERENCE CONTENT ---"]

        for content in extracted_content:
            if content["type"] == "youtube":
                context_parts.append(
                    f"\nYouTube Video: {content['title']}\nURL: {content['url']}\n"
                    f"Transcript:\n{content['transcript']}\n"
                )
            elif content["type"] == "webpage":
                context_parts.append(
                    f"\nWebpage: {content['title']}\nURL: {content['url']}\n"
                    f"Content:\n{content['content']}\n"
                )

        context_parts.append("--- END REFERENCE CONTENT ---\n")

        return "\n".join(context_parts)
