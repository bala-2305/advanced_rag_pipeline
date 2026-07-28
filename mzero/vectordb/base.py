"""Base abstract class for Vector DB adapters in mzero."""

from typing import List, Tuple
from mzero.types import Chunk, SearchResult


class BaseVectorStore:
    def add_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        raise NotImplementedError

    def delete_chunks(self, doc_ids: List[str]) -> None:
        raise NotImplementedError

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        raise NotImplementedError

    def count(self) -> int:
        raise NotImplementedError

    def persist(self) -> None:
        pass
