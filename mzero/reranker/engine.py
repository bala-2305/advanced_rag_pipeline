"""Cross-Encoder Document Reranker for mzero."""

from typing import List
from mzero.types import SearchResult
from mzero.utils.logger import logger


class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self._reranker = None

    def _get_reranker(self):
        if self._reranker is None:
            try:
                from sentence_transformers import CrossEncoder
                self._reranker = CrossEncoder(self.model_name)
            except Exception as e:
                logger.warning(f"Could not load CrossEncoder model {self.model_name}: {e}. Skipping reranking.")
                self._reranker = "fallback"
        return self._reranker

    def rerank(self, query: str, search_results: List[SearchResult], top_k: int = 3) -> List[SearchResult]:
        if not search_results:
            return []

        reranker = self._get_reranker()
        if reranker == "fallback":
            return search_results[:top_k]

        pairs = [[query, res.chunk.content] for res in search_results]
        try:
            scores = reranker.predict(pairs)
            for idx, res in enumerate(search_results):
                res.score = float(scores[idx])

            reranked = sorted(search_results, key=lambda x: x.score, reverse=True)[:top_k]
            return reranked
        except Exception as e:
            logger.error(f"Error during cross-encoder reranking: {e}")
            return search_results[:top_k]
