"""BM25 Keyword Retriever for mzero with pure-Python fallback."""

import math
import re
from typing import List, Dict, Any, Optional
from mzero.types import Chunk, SearchResult
from mzero.utils.logger import logger


class SimpleBM25:
    """Pure Python implementation of BM25Okapi algorithm."""

    def __init__(self, corpus: List[List[str]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = len(corpus)
        self.avgdl = sum(len(doc) for doc in corpus) / max(self.corpus_size, 1)
        self.doc_freqs: List[Dict[str, int]] = []
        self.idf: Dict[str, float] = {}
        self.doc_len: List[int] = []

        # Calculate document frequencies
        df: Dict[str, int] = {}
        for doc in corpus:
            self.doc_len.append(len(doc))
            frequencies: Dict[str, int] = {}
            for word in doc:
                frequencies[word] = frequencies.get(word, 0) + 1
            self.doc_freqs.append(frequencies)
            for word in frequencies:
                df[word] = df.get(word, 0) + 1

        # Calculate IDF scores
        for word, freq in df.items():
            self.idf[word] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1.0)

    def get_scores(self, query: List[str]) -> List[float]:
        scores = [0.0] * self.corpus_size
        for q in query:
            if q not in self.idf:
                continue
            q_idf = self.idf[q]
            for idx, doc_freq in enumerate(self.doc_freqs):
                freq = doc_freq.get(q, 0)
                if freq == 0:
                    continue
                numerator = freq * (self.k1 + 1)
                denominator = freq + self.k1 * (1 - self.b + self.b * (self.doc_len[idx] / self.avgdl))
                scores[idx] += q_idf * (numerator / denominator)
        return scores


class BM25Retriever:
    def __init__(self):
        self.chunks: List[Chunk] = []
        self.bm25: Optional[Any] = None

    def index_chunks(self, chunks: List[Chunk]) -> None:
        self.chunks = chunks
        if not chunks:
            self.bm25 = None
            return

        corpus = [self._tokenize(c.content) for c in chunks]
        try:
            from rank_bm25 import BM25Okapi  # type: ignore # noqa: F401
            self.bm25 = BM25Okapi(corpus)
        except Exception:
            # Pure Python fallback
            self.bm25 = SimpleBM25(corpus)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.findall(r"\w+", text.lower())

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        if not self.bm25 or not self.chunks:
            return []

        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        top_k = min(top_k, len(self.chunks))
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        results: List[SearchResult] = []
        for idx in top_indices:
            if scores[idx] > 0.0:
                results.append(SearchResult(
                    chunk=self.chunks[idx],
                    score=float(scores[idx]),
                    retrieval_method="bm25"
                ))
        return results
