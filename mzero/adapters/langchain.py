"""LangChain BaseRetriever adapter for mzero."""

from typing import List, Any
from mzero.main import RAG


class MZeroLangChainRetriever:
    """LangChain-compatible retriever class wrapping mzero."""

    def __init__(self, docs_path: str = "./docs", rag_instance: RAG = None):
        self.rag = rag_instance or RAG(docs_path=docs_path)

    def get_relevant_documents(self, query: str) -> List[Any]:
        results = self.rag.search(query, top_k=5)
        documents = []
        try:
            from langchain_core.documents import Document as LCDocument
            for res in results:
                documents.append(LCDocument(
                    page_content=res.chunk.content,
                    metadata={"source": res.chunk.source_file, "score": res.score}
                ))
        except ImportError:
            # Fallback dict format if langchain is not installed
            for res in results:
                documents.append({
                    "page_content": res.chunk.content,
                    "metadata": {"source": res.chunk.source_file, "score": res.score}
                })
        return documents
