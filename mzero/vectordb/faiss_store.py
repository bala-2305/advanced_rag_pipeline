"""FAISS CPU implementation for fast lightweight vector search in mzero."""

import os
import pickle
import numpy as np
from typing import List, Optional
from mzero.types import Chunk, SearchResult
from mzero.vectordb.base import BaseVectorStore
from mzero.utils.logger import logger


class FaissVectorStore(BaseVectorStore):
    def __init__(self, persist_dir: str = ".mzero/faiss"):
        self.persist_dir = persist_dir
        self.chunks: List[Chunk] = []
        self.embeddings_matrix: Optional[np.ndarray] = None
        self.index = None
        self._load()

    def _load(self):
        os.makedirs(self.persist_dir, exist_ok=True)
        chunks_path = os.path.join(self.persist_dir, "chunks.pkl")
        embeddings_path = os.path.join(self.persist_dir, "embeddings.npy")

        if os.path.exists(chunks_path) and os.path.exists(embeddings_path):
            try:
                with open(chunks_path, "rb") as f:
                    self.chunks = pickle.load(f)
                self.embeddings_matrix = np.load(embeddings_path)
                self._rebuild_index()
            except Exception as e:
                logger.warning(f"Failed to load FAISS index: {e}")
                self.chunks = []
                self.embeddings_matrix = None

    def _rebuild_index(self):
        if self.embeddings_matrix is not None and len(self.embeddings_matrix) > 0:
            dim = self.embeddings_matrix.shape[1]
            try:
                import faiss
                self.index = faiss.IndexFlatIP(dim)
                self.index.add(self.embeddings_matrix.astype(np.float32))
            except Exception:
                # Cosine similarity matrix fallback
                self.index = "numpy"

    def add_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        if not chunks or not embeddings:
            return
        
        arr = np.array(embeddings, dtype=np.float32)
        if self.embeddings_matrix is None:
            self.embeddings_matrix = arr
        else:
            self.embeddings_matrix = np.vstack([self.embeddings_matrix, arr])
            
        self.chunks.extend(chunks)
        self._rebuild_index()
        self.persist()

    def delete_chunks(self, doc_ids: List[str]) -> None:
        doc_set = set(doc_ids)
        keep_indices = [i for i, c in enumerate(self.chunks) if c.doc_id not in doc_set]
        
        if len(keep_indices) == len(self.chunks):
            return

        self.chunks = [self.chunks[i] for i in keep_indices]
        if self.embeddings_matrix is not None and len(keep_indices) > 0:
            self.embeddings_matrix = self.embeddings_matrix[keep_indices]
        else:
            self.embeddings_matrix = None
            
        self._rebuild_index()
        self.persist()

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        if not self.chunks or self.embeddings_matrix is None:
            return []

        q_vec = np.array([query_embedding], dtype=np.float32)
        top_k = min(top_k, len(self.chunks))

        if self.index != "numpy" and self.index is not None:
            scores, indices = self.index.search(q_vec, top_k)
            scores = scores[0]
            indices = indices[0]
        else:
            # Cosine similarity numpy fallback
            norms = np.linalg.norm(self.embeddings_matrix, axis=1) * np.linalg.norm(q_vec)
            norms[norms == 0] = 1e-10
            sims = np.dot(self.embeddings_matrix, q_vec.T).squeeze() / norms
            indices = np.argsort(sims)[::-1][:top_k]
            scores = sims[indices]

        results: List[SearchResult] = []
        for score, idx in zip(scores, indices):
            if 0 <= idx < len(self.chunks):
                results.append(SearchResult(
                    chunk=self.chunks[idx],
                    score=float(score),
                    retrieval_method="dense"
                ))
        return results

    def count(self) -> int:
        return len(self.chunks)

    def persist(self) -> None:
        chunks_path = os.path.join(self.persist_dir, "chunks.pkl")
        embeddings_path = os.path.join(self.persist_dir, "embeddings.npy")
        with open(chunks_path, "wb") as f:
            pickle.dump(self.chunks, f)
        if self.embeddings_matrix is not None:
            np.save(embeddings_path, self.embeddings_matrix)
