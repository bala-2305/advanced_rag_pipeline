"""Automatic document router for mzero."""

import os
from pathlib import Path
from mzero.types import Document, DocumentType
from mzero.parsers.text_parser import TextParser
from mzero.parsers.doc_parser import DocParser
from mzero.parsers.code_parser import CodeParser, CODE_EXTENSIONS
from mzero.parsers.media_parser import MediaParser
from mzero.parsers.ocr_parser import OCRParser
from mzero.utils.logger import logger


class DocumentParserRouter:
    @classmethod
    def parse(cls, source_path_or_url: str) -> Document:
        s = source_path_or_url.strip()
        
        # 1. Check if URL
        if s.startswith("http://") or s.startswith("https://"):
            if "youtube.com" in s or "youtu.be" in s:
                return MediaParser.parse_youtube(s)
            elif "github.com" in s and not s.endswith(".txt"):
                return CodeParser.parse_github_repo(s)
            else:
                return MediaParser.parse_web_page(s)

        # 2. Check local file extension
        ext = Path(s).suffix.lower()
        
        if ext in [".txt", ".md", ".markdown"]:
            return TextParser.parse_txt_or_md(s)
        elif ext == ".html":
            return TextParser.parse_html(s)
        elif ext == ".csv":
            return TextParser.parse_csv(s)
        elif ext == ".json":
            return TextParser.parse_json(s)
        elif ext == ".pdf":
            return DocParser.parse_pdf(s)
        elif ext == ".docx":
            return DocParser.parse_docx(s)
        elif ext == ".pptx":
            return DocParser.parse_pptx(s)
        elif ext in CODE_EXTENSIONS:
            return CodeParser.parse_code(s)
        elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"]:
            return OCRParser.parse_image(s)
        else:
            # Fallback text parser
            try:
                return TextParser.parse_txt_or_md(s)
            except Exception as e:
                logger.error(f"Failed to parse document {s}: {e}")
                return Document(
                    id=s,
                    source_path=s,
                    content="",
                    doc_type=DocumentType.UNKNOWN
                )
