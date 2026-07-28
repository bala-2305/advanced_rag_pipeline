"""Automatic Vector Database Tier Router for mzero."""

import os
from pathlib import Path
from typing import List
from mzero.vectordb.base import BaseVectorStore
from mzero.vectordb.faiss_store import FaissVectorStore
from mzero.vectordb.chroma_store import ChromaVectorStore
from mzero.utils.logger import logger


class VectorDBRouter:
    @classmethod
    def select_backend(cls, docs_path: str, override_backend: str = "auto") -> BaseVectorStore:
        if override_backend != "auto":
            logger.info(f"Using explicitly configured vector DB backend: {override_backend}")
            if override_backend.lower() == "chroma":
                return ChromaVectorStore()
            return FaissVectorStore()

        # Calculate total dataset size in MB
        total_size_bytes = 0
        if os.path.exists(docs_path):
            p = Path(docs_path)
            if p.is_file():
                total_size_bytes = p.stat().st_size
            else:
                for f in p.rglob("*"):
                    if f.is_file():
                        total_size_bytes += f.stat().st_size

        total_size_mb = total_size_bytes / (1024 * 1024)
        logger.info(f"Detected dataset size: {total_size_mb:.2f} MB")

        if total_size_mb < 50.0:
            logger.info("Dataset < 50MB. Auto-selecting high-speed FAISS vector store.")
            return FaissVectorStore()
        else:
            logger.info("Dataset >= 50MB. Auto-selecting ChromaDB vector store.")
            return ChromaVectorStore()
