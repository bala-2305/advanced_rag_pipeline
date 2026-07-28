# mzero Framework Guide & Feature Matrix

## Introduction
`mzero` (or `mzero-rag`) is a zero-configuration Retrieval-Augmented Generation (RAG) framework and embeddable Python SDK. It abstracts document ingestion, domain-aware chunking, dynamic vector store routing, hybrid dense/sparse search, cross-encoder reranking, conversation state management, and hallucination verification behind a minimal single-line interface.

## Key Features & Capabilities

### 1. Zero-Configuration Engine
Automatic runtime initialization of storage, indexes, and model pipelines based on inspecting the document directory.

### 2. Multi-Format Parsing
Built-in support for parsing:
- Text documents (PDF, DOCX, TXT, MD, HTML, CSV, JSON, XML, PPTX)
- Source code ASTs (Python, JavaScript, TypeScript, Go, Rust, C++)
- Web pages & URL content extraction
- OCR Images & YouTube transcripts

### 3. Provider & LLM Agnostic Integration
Seamlessly switch or auto-detect LLM providers via environment variables or explicit parameters:
- **NVIDIA NIM**: `llm_provider="nvidia"`, default model `meta/llama-3.1-70b-instruct`
- **OpenAI**: `llm_provider="openai"`, default model `gpt-4o-mini`
- **Google Gemini**: `llm_provider="gemini"`, default model `gemini-1.5-flash`
- **Anthropic Claude**: `llm_provider="anthropic"`, default model `claude-3-haiku-20240307`
- **Groq**: `llm_provider="groq"`, default model `llama3-8b-8192`
- **OpenRouter**: `llm_provider="openrouter"`
- **Local Ollama**: `llm_provider="ollama"`, default model `llama3`

### 4. Dynamic Vector Database Routing
Automatic backend selection:
- **FAISS CPU**: Lightweight local datasets under 50MB
- **ChromaDB**: Medium local stores under 1GB
- **Qdrant / Milvus**: Enterprise scale deployments over 1GB

### 5. Hybrid Retrieval & Reranking
Combines dense vector similarity with sparse BM25 keyword matching via Reciprocal Rank Fusion (RRF), followed by Cross-Encoder reranking.
