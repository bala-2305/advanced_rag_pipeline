"""ChromaDB adapter for medium-scale datasets in mzero."""

import os
from typing import List
from mzero.types import Chunk, SearchResult
from mzero.vectordb.base import BaseVectorStore
from mzero.utils.logger import logger


class ChromaVectorStore(BaseVectorStore):
    def __init__(self, persist_dir: str = ".mzero/chroma"):
        self.persist_dir = persist_dir
        self.client = None
        self.collection = None
        self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=self.persist_dir)
            self.collection = self.client.get_or_create_collection(name="mzero_chunks")
        except Exception as e:
            logger.warning(f"Failed to initialize ChromaDB: {e}. Defaulting to FAISS.")

    def add_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        if not self.collection or not chunks:
            return

        ids = [c.id for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = [{"doc_id": c.doc_id, "source_file": c.source_file} for c in chunks]

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def delete_chunks(self, doc_ids: List[str]) -> None:
        if not self.collection or not doc_ids:
            return
        for doc_id in doc_ids:
            self.collection.delete(where={"doc_id": doc_id})

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        if not self.collection:
            return []

        res = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        results: List[SearchResult] = []
        if res and res.get("documents") and res["documents"][0]:
            ids = res["ids"][0]
            docs = res["documents"][0]
            metas = res["metadatas"][0]
            distances = res["distances"][0] if "distances" in res else [1.0] * len(ids)

            for i in range(len(ids)):
                chunk = Chunk(
                    id=ids[i],
                    doc_id=metas[i].get("doc_id", ""),
                    content=docs[i],
                    chunk_index=i,
                    source_file=metas[i].get("source_file", "")
                )
                score = 1.0 - distances[i] if distances else 0.5
                results.append(SearchResult(chunk=chunk, score=score, retrieval_method="dense"))

        return results

    def count(self) -> int:
        return self.collection.count() if self.collection else 0
