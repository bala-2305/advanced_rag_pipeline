"""Central RAG Orchestrator Pipeline for mzero."""

import os
import time
import httpx
from typing import List, Generator, AsyncGenerator, Optional
from mzero.config import Config
from mzero.types import Document, Chunk, QueryResult, SearchResult, SystemStats
from mzero.parsers.router import DocumentParserRouter
from mzero.chunkers.strategy import AdaptiveChunker
from mzero.embeddings.selector import EmbeddingSelector
from mzero.vectordb.router import VectorDBRouter
from mzero.retrievers.hybrid import HybridRetriever
from mzero.reranker.engine import CrossEncoderReranker
from mzero.memory.conversation import ConversationMemory
from mzero.cache.semantic_cache import SemanticCache
from mzero.core.query_engine import QueryEngine
from mzero.core.hallucination import HallucinationChecker
from mzero.utils.incremental import IncrementalTracker
from mzero.utils.logger import logger


class RAGPipeline:
    def __init__(self, config: Config):
        self.config = config
        self.incremental_tracker = IncrementalTracker(os.path.join(config.mzero_dir, "state.json"))
        
        self.all_documents: List[Document] = []
        self.all_chunks: List[Chunk] = []
        
        # Load embedding & vector store
        self.embedding_provider = EmbeddingSelector.select_model([], override_model=config.embedding_model)
        self.vector_store = VectorDBRouter.select_backend(config.docs_path, override_backend=config.vector_db_backend)
        self.hybrid_retriever = HybridRetriever(self.vector_store)
        self.reranker = CrossEncoderReranker()
        
        self.memory = ConversationMemory()
        self.query_engine = QueryEngine(self.memory)
        self.cache = SemanticCache()
        
        self.start_time = time.time()
        self.total_queries = 0
        self.cache_hits = 0

        # Auto-ingest docs if path exists
        if os.path.exists(config.docs_path):
            self.ingest_directory(config.docs_path)

    def ingest_directory(self, dir_path: str) -> None:
        added, modified, deleted = self.incremental_tracker.scan_directory(dir_path)
        logger.info(f"Ingestion scan for '{dir_path}': {len(added)} added, {len(modified)} modified, {len(deleted)} deleted.")

        # Process deleted
        if deleted:
            self.vector_store.delete_chunks(deleted)
            self.all_documents = [d for d in self.all_documents if d.source_path not in deleted]
            self.all_chunks = [c for c in self.all_chunks if c.source_file not in deleted]

        # Process added and modified
        files_to_process = added + modified
        new_chunks: List[Chunk] = []

        for f_path in files_to_process:
            try:
                doc = DocumentParserRouter.parse(f_path)
                chunks = AdaptiveChunker.chunk(doc)
                self.all_documents.append(doc)
                self.all_chunks.extend(chunks)
                new_chunks.extend(chunks)
            except Exception as e:
                logger.error(f"Error parsing file {f_path}: {e}")

        if new_chunks:
            logger.info(f"Embedding and indexing {len(new_chunks)} chunks...")
            texts = [c.content for c in new_chunks]
            embeddings = self.embedding_provider.embed_documents(texts)
            self.vector_store.add_chunks(new_chunks, embeddings)
            self.hybrid_retriever.update_bm25_index(self.all_chunks)

    def ask(self, question: str, conversation_id: str = None) -> QueryResult:
        start_t = time.time()
        self.total_queries += 1
        
        # 1. Rewrite query & multi-turn memory lookup
        rewritten_q = self.query_engine.rewrite_query(question, conversation_id)
        
        # 2. Embed query
        query_emb = self.embedding_provider.embed_queries([rewritten_q])[0]
        
        # 3. Cache check
        if self.config.enable_cache:
            cached_res = self.cache.get(rewritten_q, query_emb)
            if cached_res:
                self.cache_hits += 1
                return cached_res

        # 4. Hybrid retrieval & Reranking
        retrieved = self.hybrid_retriever.search(
            query=rewritten_q,
            query_embedding=query_emb,
            top_k=self.config.similarity_top_k
        )
        
        if self.config.enable_rerank and retrieved:
            retrieved = self.reranker.rerank(rewritten_q, retrieved, top_k=self.config.rerank_top_k)

        # 5. Compress context & Generate LLM Answer
        context_str = self.query_engine.compress_context(retrieved)
        answer = self._generate_llm_answer(rewritten_q, context_str)

        # 6. Hallucination check & Citations
        citations, confidence, is_warning = HallucinationChecker.verify_and_cite(answer, retrieved)

        latency_ms = round((time.time() - start_t) * 1000, 2)
        res = QueryResult(
            query=question,
            answer=answer,
            citations=citations,
            confidence=confidence,
            is_hallucination_warning=is_warning,
            cache_hit=False,
            latency_ms=latency_ms,
            retrieved_chunks=retrieved
        )

        # Update memory & cache
        if conversation_id:
            self.memory.add_turn(conversation_id, question, answer)
        if self.config.enable_cache:
            self.cache.put(rewritten_q, query_emb, res)

        return res

    def stream(self, question: str, conversation_id: str = None) -> Generator[str, None, None]:
        res = self.ask(question, conversation_id)
        words = res.answer.split(" ")
        for word in words:
            yield word + " "
            time.sleep(0.02)

    def _generate_llm_answer(self, query: str, context: str) -> str:
        if not context.strip():
            return "I could not find relevant documentation in the knowledge base to answer your question."

        provider = self.config.llm_provider
        api_key = self.config.llm_api_key

        prompt = (
            f"You are a helpful AI assistant. Answer the question accurately using ONLY the provided context.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n\nAnswer:"
        )

        # 1. OpenAI Provider
        if provider == "openai" and api_key:
            try:
                resp = httpx.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": self.config.llm_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2
                    },
                    timeout=30.0
                )
                return resp.json()["choices"][0]["message"]["content"].strip()
            except Exception as e:
                logger.error(f"OpenAI API call failed: {e}")

        # 2. Gemini Provider
        elif provider == "gemini" and api_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.config.llm_model}:generateContent?key={api_key}"
                resp = httpx.post(
                    url,
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                    timeout=30.0
                )
                return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            except Exception as e:
                logger.error(f"Gemini API call failed: {e}")

        # 3. Groq Provider
        elif provider == "groq" and api_key:
            try:
                resp = httpx.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": self.config.llm_model,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=30.0
                )
                return resp.json()["choices"][0]["message"]["content"].strip()
            except Exception as e:
                logger.error(f"Groq API call failed: {e}")

        # 4. NVIDIA NIM Provider
        elif provider == "nvidia" and api_key:
            try:
                resp = httpx.post(
                    "https://integrate.api.nvidia.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": self.config.llm_model if self.config.llm_model != "auto" else "meta/llama-3.1-70b-instruct",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2
                    },
                    timeout=30.0
                )
                return resp.json()["choices"][0]["message"]["content"].strip()
            except Exception as e:
                logger.error(f"NVIDIA API call failed: {e}")

        # 4. Ollama Local Provider
        elif provider == "ollama":
            try:
                resp = httpx.post(
                    "http://localhost:11434/api/generate",
                    json={"model": self.config.llm_model, "prompt": prompt, "stream": False},
                    timeout=30.0
                )
                return resp.json()["response"].strip()
            except Exception:
                pass

        # 5. Smart Extractive Deterministic Fallback
        lines = [line.strip() for line in context.split("\n") if line.strip() and not line.startswith("[Source:")]
        extracted = " ".join(lines[:4])
        return f"Based on the knowledge base: {extracted}"

    def get_stats(self) -> SystemStats:
        uptime = round(time.time() - self.start_time, 2)
        hit_rate = round(self.cache_hits / max(self.total_queries, 1), 2)
        return SystemStats(
            total_documents=len(self.all_documents),
            total_chunks=len(self.all_chunks),
            total_queries=self.total_queries,
            cache_hit_count=self.cache_hits,
            cache_hit_rate=hit_rate,
            embedding_model=self.config.embedding_model,
            vector_db_backend=self.vector_store.__class__.__name__,
            uptime_seconds=uptime
        )
