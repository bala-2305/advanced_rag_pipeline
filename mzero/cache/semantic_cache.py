"""Exact match and semantic query cache for mzero."""

import time
import numpy as np
from typing import Optional, List, Tuple
from mzero.types import QueryResult
from mzero.utils.logger import logger


class SemanticCache:
    def __init__(self, similarity_threshold: float = 0.92, max_entries: int = 1000):
        self.similarity_threshold = similarity_threshold
        self.max_entries = max_entries
        self.cache: List[Tuple[str, List[float], QueryResult]] = []

    def get(self, query: str, query_embedding: List[float]) -> Optional[QueryResult]:
        # 1. Exact match lookup
        for cached_q, _, res in self.cache:
            if cached_q.strip().lower() == query.strip().lower():
                logger.info("Exact cache hit!")
                res_copy = res.model_copy()
                res_copy.cache_hit = True
                return res_copy

        # 2. Semantic vector match lookup
        if not self.cache:
            return None

        q_vec = np.array(query_embedding, dtype=np.float32)
        norm_q = np.linalg.norm(q_vec)
        if norm_q == 0:
            return None

        for cached_q, cached_emb, res in self.cache:
            c_vec = np.array(cached_emb, dtype=np.float32)
            norm_c = np.linalg.norm(c_vec)
            if norm_c == 0:
                continue
            sim = float(np.dot(q_vec, c_vec) / (norm_q * norm_c))
            if sim >= self.similarity_threshold:
                logger.info(f"Semantic cache hit (similarity: {sim:.3f})!")
                res_copy = res.model_copy()
                res_copy.cache_hit = True
                return res_copy

        return None

    def put(self, query: str, query_embedding: List[float], result: QueryResult) -> None:
        if len(self.cache) >= self.max_entries:
            self.cache.pop(0)
        self.cache.append((query, query_embedding, result))

    def clear(self) -> None:
        self.cache.clear()

    def stats(self) -> dict:
        return {"total_cached_queries": len(self.cache)}
