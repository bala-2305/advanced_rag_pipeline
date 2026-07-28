"""FastAPI REST server & Web Dashboard endpoint for mzero."""

import os
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from mzero.main import RAG
from mzero.dashboard.app import get_dashboard_html
from mzero.utils.logger import logger


class AskPayload(BaseModel):
    question: str
    conversation_id: Optional[str] = None


class AddPayload(BaseModel):
    path_or_url: str


def create_app(rag_instance: RAG) -> FastAPI:
    app = FastAPI(title="mzero API Server", version="0.1.0")

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "mzero"}

    @app.get("/status")
    def status():
        stats = rag_instance.stats()
        return stats.model_dump()

    @app.post("/ask")
    def ask(payload: AskPayload):
        res = rag_instance.ask(payload.question, conversation_id=payload.conversation_id)
        return res.model_dump()

    @app.post("/upload")
    async def upload(file: UploadFile = File(...)):
        temp_dir = os.path.join(rag_instance.config.mzero_dir, "uploads")
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        rag_instance.add(file_path)
        return {"message": f"File '{file.filename}' uploaded and indexed successfully.", "path": file_path}

    @app.get("/sources")
    def sources():
        docs = rag_instance.pipeline.all_documents
        return [{"id": d.id, "source_path": d.source_path, "type": d.doc_type} for d in docs]

    @app.get("/dashboard", response_class=HTMLResponse)
    def dashboard():
        return HTMLResponse(content=get_dashboard_html())

    @app.get("/")
    def index():
        return HTMLResponse(content=get_dashboard_html())

    return app


def start_server(rag_instance: RAG, host: str = "0.0.0.0", port: int = 8000):
    app = create_app(rag_instance)
    logger.info(f"Starting mzero server & Web Dashboard at http://{host}:{port}/dashboard")
    uvicorn.run(app, host=host, port=port)
