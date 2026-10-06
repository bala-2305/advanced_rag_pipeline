"""Zero-Configuration Engine and Auto-Detector for mzero."""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from mzero.utils.logger import logger


class Config(BaseModel):
    docs_path: str = "./docs"
    mzero_dir: str = ".mzero"
    
    # Auto-detected LLM settings
    llm_provider: str = "auto"       # openai, gemini, anthropic, groq, nvidia, openrouter, ollama, lmstudio, mock
    llm_model: str = "auto"
    llm_api_key: Optional[str] = None
    provider_priority: List[str] = Field(
        default_factory=lambda: ["openai", "gemini", "anthropic", "groq", "nvidia", "openrouter"]
    )
    
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

        # Check LLM_PROVIDER_PRIORITY env var if provider_priority not explicitly passed in overrides
        if "provider_priority" not in overrides and os.getenv("LLM_PROVIDER_PRIORITY"):
            env_priority = [p.strip().lower() for p in os.getenv("LLM_PROVIDER_PRIORITY").split(",") if p.strip()]
            if env_priority:
                cfg.provider_priority = env_priority

        # Check environment variable for explicit provider override if llm_provider not explicitly passed in overrides
        if "llm_provider" not in overrides and (os.getenv("MZERO_LLM_PROVIDER") or os.getenv("LLM_PROVIDER")):
            cfg.llm_provider = os.getenv("MZERO_LLM_PROVIDER") or os.getenv("LLM_PROVIDER")

        # Override values if user explicitly passed them
        for k, v in overrides.items():
            if v is not None and hasattr(cfg, k):
                setattr(cfg, k, v)
                
        env_map = {
            "openai": ["OPENAI_API_KEY"],
            "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
            "anthropic": ["ANTHROPIC_API_KEY"],
            "groq": ["GROQ_API_KEY"],
            "nvidia": ["NVIDIA_API_KEY", "NVAPI_KEY"],
            "openrouter": ["OPENROUTER_API_KEY"]
        }
        default_models = {
            "openai": "gpt-4o-mini",
            "gemini": "gemini-1.5-flash",
            "anthropic": "claude-3-haiku-20240307",
            "groq": "llama3-8b-8192",
            "nvidia": "meta/llama-3.1-70b-instruct",
            "openrouter": "auto"
        }

        # If provider specified but key not passed explicitly, attempt env var lookup for that provider
        if cfg.llm_provider != "auto" and not cfg.llm_api_key:
            if cfg.llm_provider in env_map:
                for env_var in env_map[cfg.llm_provider]:
                    if os.getenv(env_var):
                        cfg.llm_api_key = os.getenv(env_var)
                        break

        # Auto-detect LLM Provider if set to auto
        if cfg.llm_provider == "auto":
            detected_providers = []
            for provider, env_vars in env_map.items():
                for env_var in env_vars:
                    val = os.getenv(env_var)
                    if val and val.strip():
                        detected_providers.append((provider, env_var, val.strip()))
                        break

            if len(detected_providers) > 1:
                env_names = [d[1] for d in detected_providers]
                logger.info(
                    f"Multiple LLM API keys detected in environment: {env_names}. "
                    f"Evaluating choices against provider priority: {cfg.provider_priority}"
                )

            selected_provider = None
            selected_key = None
            for p in cfg.provider_priority:
                match = next((d for d in detected_providers if d[0] == p.lower()), None)
                if match:
                    selected_provider, _, selected_key = match
                    break

            if selected_provider:
                cfg.llm_provider = selected_provider
                cfg.llm_api_key = selected_key
                cfg.llm_model = cfg.llm_model if cfg.llm_model != "auto" else default_models.get(selected_provider, "auto")
                if len(detected_providers) > 1:
                    logger.info(f"Auto-selected provider '{cfg.llm_provider}' (Model: {cfg.llm_model}).")
            else:
                # Local fallback
                cfg.llm_provider = "ollama"
                cfg.llm_model = cfg.llm_model if cfg.llm_model != "auto" else "llama3"
                
        # Ensure persistence directory exists
        os.makedirs(cfg.mzero_dir, exist_ok=True)
        return cfg

