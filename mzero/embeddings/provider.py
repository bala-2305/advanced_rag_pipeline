"""Embedding model providers for mzero."""

import numpy as np
from typing import List
from mzero.utils.logger import logger


class BaseEmbeddingProvider:
    def embed_queries(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError


class SentenceTransformerProvider(BaseEmbeddingProvider):
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer model {self.model_name}: {e}. Falling back to Hash embedding.")
                self._model = "fallback"
        return self._model

    def embed_queries(self, texts: List[str]) -> List[List[float]]:
        model = self._get_model()
        if model == "fallback":
            return [self._hash_embed(t) for t in texts]
        embeddings = model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        model = self._get_model()
        if model == "fallback":
            return [self._hash_embed(t) for t in texts]
        embeddings = model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    @staticmethod
    def _hash_embed(text: str, dim: int = 384) -> List[float]:
        """Lightweight deterministic fallback vector generator when HuggingFace downloads are offline."""
        np.random.seed(abs(hash(text)) % (2**32))
        vec = np.random.randn(dim)
        norm = np.linalg.norm(vec)
        return (vec / norm).tolist()
