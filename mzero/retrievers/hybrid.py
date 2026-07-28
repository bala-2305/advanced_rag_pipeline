"""Hybrid Retriever combining Dense Vector and Sparse BM25 via Reciprocal Rank Fusion (RRF)."""

from typing import List, Dict
from mzero.types import Chunk, SearchResult
from mzero.vectordb.base import BaseVectorStore
from mzero.retrievers.bm25 import BM25Retriever
from mzero.utils.logger import logger


class HybridRetriever:
    def __init__(self, vector_store: BaseVectorStore):
        self.vector_store = vector_store
        self.bm25_retriever = BM25Retriever()

    def update_bm25_index(self, chunks: List[Chunk]):
        self.bm25_retriever.index_chunks(chunks)

    def search(self, query: str, query_embedding: List[float], top_k: int = 5, k_rrf: int = 60) -> List[SearchResult]:
        # 1. Dense search
        dense_results = self.vector_store.search(query_embedding, top_k=top_k * 2)

        # 2. BM25 search
        bm25_results = self.bm25_retriever.search(query, top_k=top_k * 2)

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Chunk] = {}

        # Process dense ranks
        for rank, res in enumerate(dense_results, start=1):
            cid = res.chunk.id
            chunk_map[cid] = res.chunk
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k_rrf + rank))

        # Process BM25 ranks
        for rank, res in enumerate(bm25_results, start=1):
            cid = res.chunk.id
            chunk_map[cid] = res.chunk
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k_rrf + rank))

        # Sort combined results
        sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)[:top_k]

        fused_results: List[SearchResult] = []
        for cid in sorted_ids:
            fused_results.append(SearchResult(
                chunk=chunk_map[cid],
                score=rrf_scores[cid],
                retrieval_method="hybrid"
            ))

        return fused_results
