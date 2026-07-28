"""Language and domain detection to auto-select embedding model in mzero."""

import re
from typing import List
from mzero.embeddings.provider import BaseEmbeddingProvider, SentenceTransformerProvider
from mzero.utils.logger import logger


class EmbeddingSelector:
    @classmethod
    def select_model(cls, sample_texts: List[str], override_model: str = "auto") -> BaseEmbeddingProvider:
        if override_model != "auto":
            logger.info(f"Using explicitly configured embedding model: {override_model}")
            return SentenceTransformerProvider(override_model)

        combined_sample = " ".join(sample_texts[:5])

        # 1. Code detection
        if re.search(r"\b(def|class|import|function|const|let|var|public|private|return)\b", combined_sample):
            logger.info("Detected Code domain. Auto-selecting code embedding model: BAAI/bge-small-en-v1.5")
            return SentenceTransformerProvider("BAAI/bge-small-en-v1.5")

        # 2. Medical / Bio detection
        if re.search(r"\b(patient|clinical|diagnosis|symptom|dosage|pharma|bio)\b", combined_sample, re.IGNORECASE):
            logger.info("Detected Medical/Biomedical domain. Auto-selecting domain model: BAAI/bge-small-en-v1.5")
            return SentenceTransformerProvider("BAAI/bge-small-en-v1.5")

        # 3. Non-ASCII / Multilingual detection
        non_ascii_count = len(re.findall(r"[^\x00-\x7F]", combined_sample))
        if non_ascii_count > 20:
            logger.info("Detected Multilingual content. Auto-selecting BGE-M3: BAAI/bge-m3")
            return SentenceTransformerProvider("BAAI/bge-m3")

        # 4. Standard English default
        logger.info("Auto-selected English embedding model: BAAI/bge-small-en-v1.5")
        return SentenceTransformerProvider("BAAI/bge-small-en-v1.5")
