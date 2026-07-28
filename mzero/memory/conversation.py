"""Multi-turn conversation history buffer for mzero."""

from typing import List, Dict, Optional


class ConversationMemory:
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.conversations: Dict[str, List[Dict[str, str]]] = {}

    def add_turn(self, conversation_id: str, user_query: str, assistant_response: str) -> None:
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        self.conversations[conversation_id].append({
            "user": user_query,
            "assistant": assistant_response
        })
        if len(self.conversations[conversation_id]) > self.max_history:
            self.conversations[conversation_id].pop(0)

    def get_history(self, conversation_id: str) -> List[Dict[str, str]]:
        return self.conversations.get(conversation_id, [])

    def format_history_context(self, conversation_id: str) -> str:
        history = self.get_history(conversation_id)
        if not history:
            return ""
        lines = []
        for turn in history:
            lines.append(f"User: {turn['user']}")
            lines.append(f"Assistant: {turn['assistant']}")
        return "\n".join(lines)
