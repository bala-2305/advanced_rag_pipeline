"""Text, Markdown, HTML, CSV, JSON, XML parsers for mzero."""

import os
import json
import csv
from pathlib import Path
from bs4 import BeautifulSoup
from mzero.types import Document, DocumentType
from mzero.utils.logger import logger


class TextParser:
    @staticmethod
    def parse_txt_or_md(file_path: str) -> Document:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        ext = Path(file_path).suffix.lower()
        doc_type = DocumentType.MARKDOWN if ext in [".md", ".markdown"] else DocumentType.TXT
        return Document(
            id=file_path,
            source_path=file_path,
            content=content,
            doc_type=doc_type
        )

    @staticmethod
    def parse_html(file_path: str) -> Document:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            # Strip script and style tags
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text(separator="\n")
            lines = (line.strip() for line in text.splitlines())
            cleaned_content = "\n".join(chunk for chunk in lines if chunk)

        return Document(
            id=file_path,
            source_path=file_path,
            content=cleaned_content,
            doc_type=DocumentType.HTML
        )

    @staticmethod
    def parse_csv(file_path: str) -> Document:
        rows = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(" | ".join(row))
        content = "\n".join(rows)
        return Document(
            id=file_path,
            source_path=file_path,
            content=content,
            doc_type=DocumentType.CSV
        )

    @staticmethod
    def parse_json(file_path: str) -> Document:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
        content = json.dumps(data, indent=2)
        return Document(
            id=file_path,
            source_path=file_path,
            content=content,
            doc_type=DocumentType.JSON
        )
