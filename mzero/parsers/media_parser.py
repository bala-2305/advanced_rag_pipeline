"""YouTube transcript and web page parser for mzero."""

import re
import httpx
from bs4 import BeautifulSoup
from mzero.types import Document, DocumentType
from mzero.utils.logger import logger


class MediaParser:
    @staticmethod
    def parse_youtube(url_or_id: str) -> Document:
        content = ""
        metadata = {"url": url_or_id}
        
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url_or_id)
        video_id = video_id_match.group(1) if video_id_match else url_or_id
        
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            texts = [item.get("text", "") for item in transcript]
            content = "\n".join(texts)
        except Exception as e:
            logger.warning(f"Could not fetch YouTube transcript for {url_or_id}: {e}")
            content = f"[YouTube Video Transcript for ID {video_id} - Unavailable]"

        return Document(
            id=url_or_id,
            source_path=url_or_id,
            content=content,
            doc_type=DocumentType.YOUTUBE,
            metadata=metadata
        )

    @staticmethod
    def parse_web_page(url: str) -> Document:
        content = ""
        try:
            resp = httpx.get(url, timeout=10.0, follow_redirects=True)
            soup = BeautifulSoup(resp.text, "html.parser")
            for script in soup(["script", "style", "nav", "footer"]):
                script.extract()
            text = soup.get_text(separator="\n")
            lines = (line.strip() for line in text.splitlines())
            content = "\n".join(chunk for chunk in lines if chunk)
        except Exception as e:
            logger.error(f"Error fetching web page {url}: {e}")
            content = f"[Web page content for {url} - Failed to fetch]"

        return Document(
            id=url,
            source_path=url,
            content=content,
            doc_type=DocumentType.WEB,
            metadata={"url": url}
        )
