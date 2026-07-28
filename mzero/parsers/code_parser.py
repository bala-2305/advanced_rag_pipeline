"""Source code and GitHub repository parser for mzero."""

import os
from pathlib import Path
from mzero.types import Document, DocumentType
from mzero.utils.logger import logger

CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".cs",
    ".go", ".rs", ".php", ".rb", ".swift", ".kt", ".scala", ".sh", ".sql",
    ".html", ".css", ".scss", ".yaml", ".yml", ".toml"
}


class CodeParser:
    @staticmethod
    def parse_code(file_path: str) -> Document:
        ext = Path(file_path).suffix.lower()
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        return Document(
            id=file_path,
            source_path=file_path,
            content=content,
            doc_type=DocumentType.CODE,
            metadata={"language": ext.lstrip(".")}
        )

    @staticmethod
    def parse_github_repo(repo_url: str) -> Document:
        content = f"[GitHub Repository Link: {repo_url}]"
        return Document(
            id=repo_url,
            source_path=repo_url,
            content=content,
            doc_type=DocumentType.CODE,
            metadata={"source": "github", "url": repo_url}
        )
