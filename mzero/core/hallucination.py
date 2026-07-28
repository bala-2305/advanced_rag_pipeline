"""Hallucination detection and Citation generator for mzero."""

import re
from typing import List, Tuple
from mzero.types import SearchResult, Citation
from mzero.utils.logger import logger


class HallucinationChecker:
    @staticmethod
    def verify_and_cite(answer: str, search_results: List[SearchResult]) -> Tuple[List[Citation], float, bool]:
        if not search_results or not answer.strip():
            return [], 0.0, True

        citations: List[Citation] = []
        answer_sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", answer) if len(s.strip()) > 10]
        
        grounded_count = 0
        total_sentences = max(len(answer_sentences), 1)

        for res in search_results:
            chunk = res.chunk
            chunk_words = set(re.findall(r"\w+", chunk.content.lower()))

            # Match sentences against chunk
            for sent in answer_sentences:
                sent_words = set(re.findall(r"\w+", sent.lower()))
                if not sent_words:
                    continue
                intersection = sent_words.intersection(chunk_words)
                overlap_ratio = len(intersection) / len(sent_words)

                if overlap_ratio >= 0.35:
                    grounded_count += 1
                    citations.append(Citation(
                        source_file=chunk.source_file,
                        page_number=chunk.page_number,
                        paragraph_number=chunk.paragraph_number,
                        snippet=chunk.content[:150] + "...",
                        confidence=round(res.score, 3)
                    ))
                    break

        confidence = round(min(grounded_count / total_sentences, 1.0), 2)
        # Low confidence (< 0.4) signals potential hallucination warning
        is_hallucination_warning = confidence < 0.4

        # Deduplicate citations
        unique_citations: List[Citation] = []
        seen_files = set()
        for cite in citations:
            key = (cite.source_file, cite.snippet)
            if key not in seen_files:
                seen_files.add(key)
                unique_citations.append(cite)

        return unique_citations, confidence, is_hallucination_warning
