"""Zero-Configuration Engine and Auto-Detector for mzero."""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Config(BaseModel):
    docs_path: str = "./docs"
    mzero_dir: str = ".mzero"
    
    # Auto-detected LLM settings
    llm_provider: str = "auto"       # openai, gemini, anthropic, groq, ollama, lmstudio, mock
    llm_model: str = "auto"
    llm_api_key: Optional[str] = None
    
    # Auto-detected Embedding settings
    embedding_model: str = "auto"    # BGE, BGE-M3, Code, Bio, or Cloud API
    embedding_device: str = "cpu"    # cpu, cuda, mps
    
    # Auto-detected Vector DB settings
    vector_db_backend: str = "auto"  # faiss, chroma, qdrant, milvus
    
    # Feature Toggles
    enable_cache: bool = True
    enable_hybrid: bool = True
    enable_rerank: bool = True
    enable_hallucination_check: bool = True
    enable_web_fallback: bool = False
    
    # Thresholds
    confidence_threshold: float = 0.35
    similarity_top_k: int = 5
    rerank_top_k: int = 3
    
    @classmethod
    def create_auto(cls, docs_path: str = "./docs", **overrides) -> "Config":
        cfg = cls(docs_path=docs_path)
        
        # Map 'api_key' alias to 'llm_api_key' if provided
        if "api_key" in overrides:
            overrides["llm_api_key"] = overrides.pop("api_key")

        # Override values if user explicitly passed them
        for k, v in overrides.items():
            if v is not None and hasattr(cfg, k):
                setattr(cfg, k, v)
                
        # If provider specified but key not passed explicitly, attempt env var lookup for that provider
        if cfg.llm_provider != "auto" and not cfg.llm_api_key:
            env_map = {
                "openai": ["OPENAI_API_KEY"],
                "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
                "anthropic": ["ANTHROPIC_API_KEY"],
                "groq": ["GROQ_API_KEY"],
                "nvidia": ["NVIDIA_API_KEY", "NVAPI_KEY"],
                "openrouter": ["OPENROUTER_API_KEY"]
            }
            if cfg.llm_provider in env_map:
                for env_var in env_map[cfg.llm_provider]:
                    if os.getenv(env_var):
                        cfg.llm_api_key = os.getenv(env_var)
                        break

        # Auto-detect LLM Provider if set to auto
        if cfg.llm_provider == "auto":
            if os.getenv("OPENAI_API_KEY"):
                cfg.llm_provider = "openai"
                cfg.llm_model = cfg.llm_model if cfg.llm_model != "auto" else "gpt-4o-mini"
                cfg.llm_api_key = os.getenv("OPENAI_API_KEY")
            elif os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
                cfg.llm_provider = "gemini"
                cfg.llm_model = cfg.llm_model if cfg.llm_model != "auto" else "gemini-1.5-flash"
                cfg.llm_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            elif os.getenv("ANTHROPIC_API_KEY"):
                cfg.llm_provider = "anthropic"
                cfg.llm_model = cfg.llm_model if cfg.llm_model != "auto" else "claude-3-haiku-20240307"
                cfg.llm_api_key = os.getenv("ANTHROPIC_API_KEY")
            elif os.getenv("GROQ_API_KEY"):
                cfg.llm_provider = "groq"
                cfg.llm_model = cfg.llm_model if cfg.llm_model != "auto" else "llama3-8b-8192"
                cfg.llm_api_key = os.getenv("GROQ_API_KEY")
            elif os.getenv("NVIDIA_API_KEY") or os.getenv("NVAPI_KEY"):
                cfg.llm_provider = "nvidia"
                cfg.llm_model = cfg.llm_model if cfg.llm_model != "auto" else "meta/llama-3.1-70b-instruct"
                cfg.llm_api_key = os.getenv("NVIDIA_API_KEY") or os.getenv("NVAPI_KEY")
            elif os.getenv("OPENROUTER_API_KEY"):
                cfg.llm_provider = "openrouter"
                cfg.llm_model = cfg.llm_model if cfg.llm_model != "auto" else "auto"
                cfg.llm_api_key = os.getenv("OPENROUTER_API_KEY")
            else:
                # Local fallback
                cfg.llm_provider = "ollama"
                cfg.llm_model = cfg.llm_model if cfg.llm_model != "auto" else "llama3"
                
        # Ensure persistence directory exists
        os.makedirs(cfg.mzero_dir, exist_ok=True)
        return cfg
