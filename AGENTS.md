# AGENTS.md: AI Context & Integration Instructions for `mzero`

This file provides system instructions and architectural context for AI agents working with or generating code using the `mzero` RAG package.

## Quick Summary
- **Package Name**: `mzero`
- **Description**: Zero-Configuration RAG Framework and Embeddable SDK for Python.
- **Full AI Context & API Reference**: See [AI_README.md](file:///d:/Github%20repo/advanced_rag_pipeline/AI_README.md) and [MODULES.md](file:///d:/Github%20repo/advanced_rag_pipeline/MODULES.md).

---

## Directives for AI Agents

### 1. Primary Imports
Always import primary public interfaces from `mzero`:
```python
from mzero import RAG, AsyncRAG, Config, QueryResult, Citation, Document, Chunk, SystemStats
```

### 2. Basic Initialization & Usage Patterns
```python
from mzero import RAG

# Zero-config initialization pointing to a document folder
rag = RAG(docs_path="./docs")

# Querying
result: QueryResult = rag.ask("What is the warranty policy?")
print(result.answer)
print(result.confidence)

# Streaming
for chunk in rag.stream("Explain section 2"):
    print(chunk, end="")
```

### 3. Framework Adapters
When asked to build web apps or framework integrations:
- **FastAPI**: Use `from mzero.adapters.fastapi import create_rag_router, mount_rag_app`
- **Streamlit**: Use `from mzero.adapters.streamlit import render_streamlit_chat`
- **LangChain**: Use `from mzero.adapters.langchain import MZeroLangChainRetriever`
- **LlamaIndex**: Use `from mzero.adapters.llamaindex import MZeroLlamaIndexRetriever`
- **Flask**: Use `from mzero.adapters.flask import register_flask_rag`

### 4. Async Usage
In ASGI / FastAPI contexts, use `AsyncRAG`:
```python
from mzero import AsyncRAG

async_rag = AsyncRAG(docs_path="./docs")
result = await async_rag.aask("Your query")
```

For full type definitions, configuration keys, and detailed architecture flow, consult [AI_README.md](file:///d:/Github%20repo/advanced_rag_pipeline/AI_README.md).
