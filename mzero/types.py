"""Core data types and Pydantic models for mzero RAG framework."""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class DocumentType(str, Enum):
    TXT = "txt"
    MARKDOWN = "markdown"
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    HTML = "html"
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    CODE = "code"
    IMAGE = "image"
    YOUTUBE = "youtube"
    WEB = "web"
    UNKNOWN = "unknown"


class ChunkStrategy(str, Enum):
    SEMANTIC = "semantic"
    CODE_AST = "code_ast"
    FAQ = "faq"
    SECTION = "section"
    PARAGRAPH = "paragraph"
    SLIDING = "sliding"


class Document(BaseModel):
    id: str
    source_path: str
    content: str
    doc_type: DocumentType = DocumentType.UNKNOWN
    metadata: Dict[str, Any] = Field(default_factory=dict)
    hash: str = ""
    updated_at: float = Field(default_factory=lambda: datetime.now().timestamp())


class Chunk(BaseModel):
    id: str
    doc_id: str
    content: str
    chunk_index: int
    source_file: str
    page_number: Optional[int] = None
    paragraph_number: Optional[int] = None
    section_title: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None


class Citation(BaseModel):
    source_file: str
    page_number: Optional[int] = None
    paragraph_number: Optional[int] = None
    snippet: str
    confidence: float = 0.0


class SearchResult(BaseModel):
    chunk: Chunk
    score: float
    retrieval_method: str = "hybrid"  # dense, bm25, or hybrid


class QueryResult(BaseModel):
    query: str
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    confidence: float = 0.0
    is_hallucination_warning: bool = False
    cache_hit: bool = False
    latency_ms: float = 0.0
    token_usage: Dict[str, int] = Field(default_factory=dict)
    retrieved_chunks: List[SearchResult] = Field(default_factory=list)


class SystemStats(BaseModel):
    total_documents: int = 0
    total_chunks: int = 0
    total_queries: int = 0
    cache_hit_count: int = 0
    cache_hit_rate: float = 0.0
    embedding_model: str = "auto"
    vector_db_backend: str = "auto"
    dataset_size_mb: float = 0.0
    uptime_seconds: float = 0.0
