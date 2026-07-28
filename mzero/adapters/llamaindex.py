"""LlamaIndex compatible retriever adapter for mzero."""

from typing import Any, List
from mzero.main import RAG


class MZeroLlamaIndexRetriever:
    """LlamaIndex-compatible retriever class wrapping mzero."""

    def __init__(self, docs_path: str = "./docs", rag_instance: RAG = None):
        self.rag = rag_instance or RAG(docs_path=docs_path)

    def retrieve(self, str_or_query_bundle: str) -> List[Any]:
        query = str(str_or_query_bundle)
        results = self.rag.search(query, top_k=5)
        nodes = []
        try:
            from llama_index.core.schema import NodeWithScore, TextNode
            for res in results:
                node = TextNode(text=res.chunk.content, metadata={"source": res.chunk.source_file})
                nodes.append(NodeWithScore(node=node, score=res.score))
        except ImportError:
            for res in results:
                nodes.append({"text": res.chunk.content, "score": res.score, "source": res.chunk.source_file})
        return nodes
