# AGENTS.md: Comprehensive AI Context & Multi-Provider RAG Integration Guide for `mzero` / `mzero-rag`

This document serves as the authoritative operational guide for AI agents (and developers) initializing, configuring, and integrating `mzero` with **any chosen LLM provider** and **custom document directory**.

---

## 1. Primary Package Imports

Always import primary entry points and data types directly from `mzero`:

```python
from mzero import RAG, AsyncRAG, Config, QueryResult, Citation, Document, Chunk, SystemStats
```

---

## 2. Choosing and Configuring LLM Providers

`mzero` supports zero-configuration provider selection via **environment variables** or **explicit initialization parameters**.

### Option A: Zero-Config Auto Detection (Recommended)
Set the environment variable corresponding to your chosen provider, then pass your document folder:

```bash
# Set your preferred provider key in shell or .env
export OPENAI_API_KEY="sk-..."
# or export GEMINI_API_KEY="AIzaSy..."
# or export NVIDIA_API_KEY="nvapi-..."
# or export ANTHROPIC_API_KEY="sk-ant-..."
# or export GROQ_API_KEY="gsk_..."
# or export OPENROUTER_API_KEY="sk-or-..."
```

```python
from mzero import RAG

# Automatically detects the active API key and selects the matching provider
rag = RAG(docs_path="./my_documents")
```

---

### Option B: Provider-Specific Initialization Matrix

Below are explicit setup patterns for each supported LLM provider:

#### 1. NVIDIA NIM Provider
```python
import os
from mzero import RAG

# Environmental Variable: NVIDIA_API_KEY or NVAPI_KEY
os.environ["NVIDIA_API_KEY"] = "nvapi-..."

rag = RAG(
    docs_path="./my_documents",
    llm_provider="nvidia",
    llm_model="meta/llama-3.1-70b-instruct" # Optional custom model
)
```

#### 2. OpenAI Provider
```python
from mzero import RAG

rag = RAG(
    docs_path="./my_documents",
    llm_provider="openai",
    llm_model="gpt-4o-mini",
    api_key="sk-..." # Or set OPENAI_API_KEY in environment
)
```

#### 3. Google Gemini Provider
```python
from mzero import RAG

rag = RAG(
    docs_path="./my_documents",
    llm_provider="gemini",
    llm_model="gemini-1.5-flash",
    api_key="AIzaSy..." # Or set GEMINI_API_KEY / GOOGLE_API_KEY in environment
)
```

#### 4. Anthropic Claude Provider
```python
from mzero import RAG

rag = RAG(
    docs_path="./my_documents",
    llm_provider="anthropic",
    llm_model="claude-3-haiku-20240307",
    api_key="sk-ant-..." # Or set ANTHROPIC_API_KEY in environment
)
```

#### 5. Groq Provider
```python
from mzero import RAG

rag = RAG(
    docs_path="./my_documents",
    llm_provider="groq",
    llm_model="llama3-8b-8192",
    api_key="gsk_..." # Or set GROQ_API_KEY in environment
)
```

#### 6. OpenRouter Provider
```python
from mzero import RAG

rag = RAG(
    docs_path="./my_documents",
    llm_provider="openrouter",
    api_key="sk-or-..." # Or set OPENROUTER_API_KEY in environment
)
```

#### 7. Local Ollama Provider (Offline)
```python
from mzero import RAG

# No API key required; targets local Ollama server at http://localhost:11434
rag = RAG(
    docs_path="./my_documents",
    llm_provider="ollama",
    llm_model="llama3"
)
```

---

## 3. Core RAG Operations & Querying

```python
from mzero import RAG

rag = RAG(docs_path="./knowledge_base", llm_provider="nvidia")

# 1. Single Question & Structured Answer Response
result: QueryResult = rag.ask("What is the refund window?")
print("Answer:", result.answer)
print("Confidence Score:", result.confidence)
print("Citations:", result.citations)
print("Latency:", result.latency_ms, "ms")

# 2. Token Streaming
for token in rag.stream("Explain section 2 in detail"):
    print(token, end="", flush=True)

# 3. Dynamic Knowledge Management
rag.add("./new_contract.pdf")       # Ingest additional file or folder
rag.update("./modified_policy.txt") # Re-index updated file
rag.remove("./deprecated_doc.pdf")  # Delete document vectors
```

---

## 4. Async RAG SDK (`AsyncRAG`)

Use `AsyncRAG` in asynchronous ASGI applications, FastAPI routes, and asyncio loops:

```python
import asyncio
from mzero import AsyncRAG

async def main():
    async_rag = AsyncRAG(
        docs_path="./docs",
        llm_provider="openai",
        api_key="sk-..."
    )

    # Async query execution
    result = await async_rag.aask("What are the system requirements?")
    print(result.answer)

    # Async streaming
    async for chunk in async_rag.astream("Summarize the main guide"):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

---

## 5. Framework Integration Adapters

- **FastAPI**:
  ```python
  from fastapi import FastAPI
  from mzero.adapters.fastapi import mount_mzero

  app = FastAPI()
  mount_mzero(app, docs_path="./docs", llm_provider="nvidia")
  ```

- **Streamlit**:
  ```python
  import streamlit as st
  from mzero.adapters.streamlit import render_mzero_chat

  render_mzero_chat(docs_path="./docs", llm_provider="gemini")
  ```

- **LangChain**:
  ```python
  from mzero.adapters.langchain import MZeroLangChainRetriever

  retriever = MZeroLangChainRetriever(docs_path="./docs")
  ```

- **LlamaIndex**:
  ```python
  from mzero.adapters.llamaindex import MZeroLlamaIndexRetriever

  retriever = MZeroLlamaIndexRetriever(docs_path="./docs")
  ```

---

## 6. Architecture & Full Specs

For exhaustive schema documentation, internal vector DB routing logic, and retriever details, see:
- [AI_README.md](file:///d:/Github%20repo/advanced_rag_pipeline/AI_README.md)
- [MODULES.md](file:///d:/Github%20repo/advanced_rag_pipeline/MODULES.md)
