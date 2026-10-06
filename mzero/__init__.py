"""mzero: Zero-Configuration RAG Framework and Embeddable SDK for Python."""

from mzero.main import RAG, AsyncRAG
from mzero.config import Config
from mzero.types import QueryResult, Citation, Document, Chunk, SystemStats

__version__ = "0.1.1"
__all__ = [
    "RAG",
    "AsyncRAG",
    "Config",
    "QueryResult",
    "Citation",
    "Document",
    "Chunk",
    "SystemStats",
]
