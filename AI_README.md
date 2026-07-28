# AI Assistant & Agent Context Guide: mzero Framework

> **Purpose**: This file is optimized for AI coding assistants (ChatGPT, Claude, Gemini, Cursor, Copilot, Antigravity, custom LLM tool-calling agents) to provide exact SDK references, schemas, configuration defaults, architecture patterns, and integration rules for `mzero`.

---

## 1. System Prompt Context / Core Concepts

`mzero` is a **zero-configuration Retrieval-Augmented Generation (RAG) framework** and embeddable Python SDK.

### Key AI Agent Directives:
1. **Zero Setup**: `RAG(docs_path="./docs")` handles parsing, chunking, embedding model selection, vector DB routing (FAISS / Chroma / Qdrant), hybrid search (Dense + BM25 RRF), reranking, semantic caching, and hallucination verification out of the box.
2. **Auto-Detection**: API keys (`OPENAI_API_KEY`, `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`, `GROQ_API_KEY`, `OPENROUTER_API_KEY`) are auto-detected from environment variables. If no API keys are found, it falls back to local `ollama` (`llama3`).
3. **Public Exports**: All main SDK classes are exported directly from `mzero`:
   ```python
   from mzero import RAG, AsyncRAG, Config, QueryResult, Citation, Document, Chunk, SystemStats
   ```

---

## 2. Main SDK Public API Reference

### Synchronous SDK: `RAG`

```python
from mzero import RAG

# Initialization
rag = RAG(
    docs_path="./docs",           # Knowledge base folder or document path
    llm_provider="auto",          # "openai", "gemini", "anthropic", "groq", "openrouter", "ollama"
    llm_model="auto",             # e.g., "gpt-4o-mini", "gemini-1.5-flash", "claude-3-haiku-20240307"
    embedding_model="auto",       # "auto", "bge-small-en-v1.5", "bge-m3", etc.
    vector_db_backend="auto",     # "faiss", "chroma", "qdrant", "milvus"
    enable_cache=True,            # Enable semantic vector cache
    enable_hybrid=True,           # Enable Hybrid Dense + BM25 RRF
    enable_rerank=True,           # Enable Cross-Encoder reranking
    enable_hallucination_check=True, # Verify answer grounding score
    confidence_threshold=0.35     # Min threshold for confidence
)

# 1. Ask a question (returns QueryResult)
result: QueryResult = rag.ask(question="What is the warranty period?", conversation_id="user_123")
print(result.answer)
print(result.confidence)
print(result.citations)

# 2. Stream answer tokens (yields str)
for token in rag.stream(question="Summarize section 2", conversation_id="user_123"):
    print(token, end="", flush=True)

# 3. Dynamic Ingestion & Management
rag.add("./new_doc.pdf")         # Ingest file or directory
rag.update("./existing_doc.pdf") # Re-ingest / update file
rag.remove("./deleted_doc.pdf")  # Remove doc chunks from vector store

# 4. Raw Hybrid Search
results = rag.search(query="battery specification", top_k=5)

# 5. System Metrics & Stats
stats: SystemStats = rag.stats()

# 6. Built-in FastAPI Server Launch
rag.serve(host="0.0.0.0", port=8000)
```

---

### Asynchronous SDK: `AsyncRAG`

Designed for ASGI web applications (FastAPI, Starlette) and async event loops.

```python
import asyncio
from mzero import AsyncRAG

async def main():
    rag = AsyncRAG(docs_path="./docs")

    # Async query
    result = await rag.aask("What are the setup instructions?")
    print(result.answer)

    # Async streaming
    async for token in rag.astream("Explain the configuration options"):
        print(token, end="")

    # Async document ingestion
    await rag.aadd("./new_report.pdf")

    # Async hybrid search
    search_results = await rag.asearch("installation steps", top_k=3)

asyncio.run(main())
```

---

## 3. Data Schemas & Data Types

Imported from `mzero` or `mzero.types`:

### `QueryResult`
Returned by `rag.ask()` / `await rag.aask()`:
```python
class QueryResult(BaseModel):
    query: str
    answer: str
    citations: List[Citation]             # List of source citations
    confidence: float                     # Grounding / confidence score (0.0 to 1.0)
    is_hallucination_warning: bool        # True if response confidence < threshold
    cache_hit: bool                       # True if retrieved from semantic cache
    latency_ms: float                     # Pipeline response latency in ms
    token_usage: Dict[str, int]           # e.g., {"prompt_tokens": 120, "completion_tokens": 45}
    retrieved_chunks: List[SearchResult] # Raw retrieved chunk objects
```

### `Citation`
```python
class Citation(BaseModel):
    source_file: str
    page_number: Optional[int] = None
    paragraph_number: Optional[int] = None
    snippet: str
    confidence: float = 0.0
```

### `SystemStats`
```python
class SystemStats(BaseModel):
    total_documents: int
    total_chunks: int
    total_queries: int
    cache_hit_count: int
    cache_hit_rate: float
    embedding_model: str
    vector_db_backend: str
    dataset_size_mb: float
    uptime_seconds: float
```

---

## 4. Framework Adapters (Integration Quick-Starts)

### 1. FastAPI Integration
```python
from fastapi import FastAPI
from mzero import RAG
from mzero.adapters.fastapi import create_rag_router, mount_rag_app

app = FastAPI(title="My RAG Service")
rag = RAG(docs_path="./docs")

# Option A: Mount router with /ask, /stream, /stats endpoints
router = create_rag_router(rag)
app.include_router(router, prefix="/api/v1")

# Option B: Mount complete standalone sub-app
mount_rag_app(app, rag, path="/rag")
```

### 2. Streamlit UI Integration
```python
import streamlit as st
from mzero import RAG
from mzero.adapters.streamlit import render_streamlit_chat

st.set_page_config(page_title="mzero Knowledge Assistant", layout="wide")
rag = RAG(docs_path="./docs")

# Renders full chat interface with citations & sidebar telemetry
render_streamlit_chat(rag)
```

### 3. LangChain Integration
```python
from mzero import RAG
from mzero.adapters.langchain import MZeroLangChainRetriever

rag = RAG(docs_path="./docs")
retriever = MZeroLangChainRetriever(rag=rag, top_k=5)

# Use inside standard LangChain pipelines / chains
docs = retriever.get_relevant_documents("database migration steps")
```

### 4. LlamaIndex Integration
```python
from mzero import RAG
from mzero.adapters.llamaindex import MZeroLlamaIndexRetriever

rag = RAG(docs_path="./docs")
retriever = MZeroLlamaIndexRetriever(rag=rag, top_k=5)

# Use with LlamaIndex QueryEngine
nodes = retriever.retrieve("deployment strategy")
```

---

## 5. Environment Variables & Configuration Cheat Sheet

| Variable | Description | Default Fallback |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | OpenAI API key | Auto-detected |
| `GEMINI_API_KEY` / `GOOGLE_API_KEY` | Google Gemini API key | Auto-detected |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | Auto-detected |
| `GROQ_API_KEY` | Groq API key | Auto-detected |
| `OPENROUTER_API_KEY` | OpenRouter API key | Auto-detected |

### Customizing Configuration programmatically:

```python
from mzero import Config, RAG

config = Config(
    docs_path="./kb",
    llm_provider="openai",
    llm_model="gpt-4o",
    confidence_threshold=0.5,
    enable_cache=True,
    enable_web_fallback=True
)

rag = RAG(docs_path="./kb", **config.model_dump())
```

---

## 6. AI Code Generation & Refactoring Rules

When writing code that uses or integrates `mzero`, AI models MUST follow these guidelines:

1. **Prefer `RAG` or `AsyncRAG` Top-Level Imports**:
   - DO import: `from mzero import RAG, AsyncRAG, Config`
   - AVOID importing internal pipeline modules directly (e.g. `mzero.core.pipeline.RAGPipeline`) unless doing deep core framework modifications.

2. **Handle Stream Generators Correctly**:
   - `rag.stream()` returns a standard synchronous Python `Generator[str, None, None]`.
   - `async_rag.astream()` returns an `AsyncGenerator[str, None]`.

3. **Check Citation Attributes**:
   - Citations use `citation.source_file`, `citation.snippet`, `citation.confidence`, `citation.page_number`. Do not guess names like `citation.url` or `citation.text`.

4. **FastAPI & Async Contexts**:
   - In async web frameworks (FastAPI/Sanic/Tornado), use `AsyncRAG` or `create_rag_router(rag)` from `mzero.adapters.fastapi`.

5. **Vector DB Tiering Awareness**:
   - `<50MB`: Default FAISS CPU (lightweight local memory).
   - `<1GB`: ChromaDB.
   - `>1GB`: Qdrant / Milvus.
