"""Unit tests for multi-API key detection, provider priority, and environment variable overrides in mzero."""

import os
import unittest
from mzero import Config


class TestMultiAPIKeys(unittest.TestCase):
    def setUp(self):
        self.original_env = os.environ.copy()
        # Clean up relevant env vars for isolated test execution
        keys_to_clean = [
            "OPENAI_API_KEY",
            "GEMINI_API_KEY",
            "GOOGLE_API_KEY",
            "ANTHROPIC_API_KEY",
            "GROQ_API_KEY",
            "NVIDIA_API_KEY",
            "NVAPI_KEY",
            "OPENROUTER_API_KEY",
            "LLM_PROVIDER_PRIORITY",
            "LLM_PROVIDER",
            "MZERO_LLM_PROVIDER",
        ]
        for key in keys_to_clean:
            os.environ.pop(key, None)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_default_priority_with_multiple_keys(self):
        # Set both OPENAI_API_KEY and NVIDIA_API_KEY
        os.environ["OPENAI_API_KEY"] = "sk-test-openai"
        os.environ["NVIDIA_API_KEY"] = "nvapi-test-nvidia"

        cfg = Config.create_auto(docs_path="./docs")
        # Default priority: openai before nvidia
        self.assertEqual(cfg.llm_provider, "openai")
        self.assertEqual(cfg.llm_api_key, "sk-test-openai")
        self.assertEqual(cfg.llm_model, "gpt-4o-mini")

    def test_custom_provider_priority_override(self):
        os.environ["OPENAI_API_KEY"] = "sk-test-openai"
        os.environ["NVIDIA_API_KEY"] = "nvapi-test-nvidia"

        # Explicitly pass priority putting nvidia before openai
        cfg = Config.create_auto(docs_path="./docs", provider_priority=["nvidia", "openai"])
        self.assertEqual(cfg.llm_provider, "nvidia")
        self.assertEqual(cfg.llm_api_key, "nvapi-test-nvidia")
        self.assertEqual(cfg.llm_model, "meta/llama-3.1-70b-instruct")

    def test_env_provider_priority_override(self):
        os.environ["OPENAI_API_KEY"] = "sk-test-openai"
        os.environ["GEMINI_API_KEY"] = "AIzaSy-test-gemini"
        os.environ["LLM_PROVIDER_PRIORITY"] = "gemini,openai"

        cfg = Config.create_auto(docs_path="./docs")
        self.assertEqual(cfg.llm_provider, "gemini")
        self.assertEqual(cfg.llm_api_key, "AIzaSy-test-gemini")
        self.assertEqual(cfg.llm_model, "gemini-1.5-flash")

    def test_env_llm_provider_override(self):
        os.environ["OPENAI_API_KEY"] = "sk-test-openai"
        os.environ["NVIDIA_API_KEY"] = "nvapi-test-nvidia"
        os.environ["MZERO_LLM_PROVIDER"] = "nvidia"

        cfg = Config.create_auto(docs_path="./docs")
        self.assertEqual(cfg.llm_provider, "nvidia")
        self.assertEqual(cfg.llm_api_key, "nvapi-test-nvidia")

    def test_no_keys_fallback_to_ollama(self):
        cfg = Config.create_auto(docs_path="./docs")
        self.assertEqual(cfg.llm_provider, "ollama")
        self.assertEqual(cfg.llm_model, "llama3")


if __name__ == "__main__":
    unittest.main()
