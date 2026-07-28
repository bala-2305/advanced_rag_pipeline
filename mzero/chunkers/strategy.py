"""Adaptive Chunking Strategy Router for mzero."""

import re
from typing import List
from mzero.types import Document, Chunk, DocumentType, ChunkStrategy
from mzero.chunkers.semantic import SemanticChunker
from mzero.chunkers.code_chunker import CodeChunker
from mzero.utils.logger import logger


class AdaptiveChunker:
    @classmethod
    def chunk(cls, doc: Document) -> List[Chunk]:
        content = doc.content.strip()
        if not content:
            return []

        # 1. Source code AST chunking
        if doc.doc_type == DocumentType.CODE:
            return CodeChunker.chunk(doc)

        # 2. FAQ detection (high frequency of Q&A patterns or question marks)
        q_count = len(re.findall(r"\b(?:Q:|Question:|FAQ|What|How|Why)\b", content, re.IGNORECASE))
        if q_count > 5:
            logger.debug(f"Detected FAQ structure in {doc.source_path}. Applying FAQ small chunking.")
            return SemanticChunker.chunk(doc, max_chunk_size=250, overlap=30)

        # 3. Legal document detection (presence of clauses, articles, section numbers)
        if re.search(r"\b(?:Section \d+|Article \d+|Clause \d+|\u00a7)\b", content, re.IGNORECASE):
            logger.debug(f"Detected Legal structure in {doc.source_path}. Applying Clause-aware chunking.")
            return SemanticChunker.chunk(doc, max_chunk_size=400, overlap=50)

        # 4. Books / Large narrative text (>10k chars)
        if len(content) > 10000:
            logger.debug(f"Detected Book/Narrative structure in {doc.source_path}. Applying large semantic chunking.")
            return SemanticChunker.chunk(doc, max_chunk_size=800, overlap=100)

        # 5. Default semantic chunking
        return SemanticChunker.chunk(doc, max_chunk_size=500, overlap=50)
