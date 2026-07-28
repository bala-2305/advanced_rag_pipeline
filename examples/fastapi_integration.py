"""FastAPI integration example for mzero."""

from fastapi import FastAPI
from mzero import RAG
from mzero.adapters.fastapi import mount_mzero

app = FastAPI(title="My Enterprise API with mzero RAG")

# 1. Initialize RAG
rag = RAG("./sample_docs")

# 2. Mount mzero routes on existing FastAPI app
mount_mzero(app, rag, prefix="/rag")

@app.get("/")
def home():
    return {"message": "Welcome to Enterprise API. RAG endpoints active at /rag/ask and /rag/stats"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
