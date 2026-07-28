"""Main public entry points RAG and AsyncRAG for mzero."""

import asyncio
from typing import List, Generator, AsyncGenerator, Dict, Any, Optional
from mzero.config import Config
from mzero.core.pipeline import RAGPipeline
from mzero.types import QueryResult, SearchResult, SystemStats


class RAG:
    """Zero-Configuration RAG Framework for Python."""

    def __init__(self, docs_path: str = "./docs", **kwargs):
        self.config = Config.create_auto(docs_path=docs_path, **kwargs)
        self.pipeline = RAGPipeline(self.config)

    def ask(self, question: str, conversation_id: Optional[str] = None) -> QueryResult:
        return self.pipeline.ask(question, conversation_id=conversation_id)

    def stream(self, question: str, conversation_id: Optional[str] = None) -> Generator[str, None, None]:
        yield from self.pipeline.stream(question, conversation_id=conversation_id)

    def add(self, path_or_url: str) -> None:
        self.pipeline.ingest_directory(path_or_url)

    def remove(self, path_or_identifier: str) -> None:
        self.pipeline.vector_store.delete_chunks([path_or_identifier])

    def update(self, path: str) -> None:
        self.pipeline.ingest_directory(path)

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        q_emb = self.pipeline.embedding_provider.embed_queries([query])[0]
        return self.pipeline.hybrid_retriever.search(query, q_emb, top_k=top_k)

    def stats(self) -> SystemStats:
        return self.pipeline.get_stats()

    def serve(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        from mzero.api.server import start_server
        start_server(self, host=host, port=port)


class AsyncRAG:
    """Asynchronous Zero-Configuration RAG SDK for ASGI and asyncio applications."""

    def __init__(self, docs_path: str = "./docs", **kwargs):
        self._sync_rag = RAG(docs_path=docs_path, **kwargs)

    async def aask(self, question: str, conversation_id: Optional[str] = None) -> QueryResult:
        return await asyncio.to_thread(self._sync_rag.ask, question, conversation_id)

    async def astream(self, question: str, conversation_id: Optional[str] = None) -> AsyncGenerator[str, None]:
        res = await self.aask(question, conversation_id)
        words = res.answer.split(" ")
        for word in words:
            yield word + " "
            await asyncio.sleep(0.02)

    async def aadd(self, path_or_url: str) -> None:
        await asyncio.to_thread(self._sync_rag.add, path_or_url)

    async def asearch(self, query: str, top_k: int = 5) -> List[SearchResult]:
        return await asyncio.to_thread(self._sync_rag.search, query, top_k)
