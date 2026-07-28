"""Query rewriting, reference resolution, and context compression engine for mzero."""

import re
from typing import List
from mzero.types import SearchResult
from mzero.memory.conversation import ConversationMemory
from mzero.utils.logger import logger


class QueryEngine:
    def __init__(self, memory: ConversationMemory):
        self.memory = memory

    def rewrite_query(self, query: str, conversation_id: str = None) -> str:
        """Converts vague or multi-turn follow-up questions into optimized standalone search queries."""
        if not conversation_id:
            return query

        history = self.memory.get_history(conversation_id)
        if not history:
            return query

        last_turn = history[-1]
        user_prev = last_turn["user"]

        # Pronoun & follow-up reference detection (he, she, it, they, his, her, that, this, where was he born)
        if re.search(r"\b(he|she|it|they|his|her|this|that|him|there)\b", query, re.IGNORECASE):
            rewritten = f"{user_prev} - {query}"
            logger.info(f"Rewrote multi-turn query: '{query}' -> '{rewritten}'")
            return rewritten

        return query

    @staticmethod
    def compress_context(search_results: List[SearchResult], max_chars: int = 4000) -> str:
        """Compresses retrieved context snippets to fit within token budgets while preserving key facts."""
        compressed_snippets = []
        current_len = 0

        for res in search_results:
            snippet = res.chunk.content.strip()
            if current_len + len(snippet) > max_chars:
                allowed = max_chars - current_len
                if allowed > 100:
                    compressed_snippets.append(snippet[:allowed] + "...")
                break
            compressed_snippets.append(f"[Source: {res.chunk.source_file}]\n{snippet}")
            current_len += len(snippet)

        return "\n\n".join(compressed_snippets)
