"""FastAPI integration adapter for mzero."""

from typing import Any
from mzero.main import RAG


def mount_mzero(app: Any, rag_instance: RAG, prefix: str = "/rag") -> None:
    """Mounts mzero RAG routes onto an existing FastAPI application."""
    from fastapi import APIRouter
    from pydantic import BaseModel

    router = APIRouter(prefix=prefix, tags=["mzero"])

    class AskRequest(BaseModel):
        question: str
        conversation_id: str = None

    @router.post("/ask")
    def ask_endpoint(req: AskRequest):
        res = rag_instance.ask(req.question, conversation_id=req.conversation_id)
        return res.model_dump()

    @router.get("/stats")
    def stats_endpoint():
        return rag_instance.stats().model_dump()

    app.include_router(router)
