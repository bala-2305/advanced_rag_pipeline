"""Semantic and paragraph-aware text chunking for mzero."""

import re
from typing import List
from mzero.types import Document, Chunk


class SemanticChunker:
    @staticmethod
    def chunk(doc: Document, max_chunk_size: int = 500, overlap: int = 50) -> List[Chunk]:
        content = doc.content.strip()
        if not content:
            return []

        # Split into paragraphs
        paragraphs = re.split(r"\n\s*\n", content)
        chunks: List[Chunk] = []
        current_chunk_text = ""
        current_paragraph_index = 1
        chunk_index = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk_text) + len(para) <= max_chunk_size:
                current_chunk_text += ("\n\n" if current_chunk_text else "") + para
            else:
                if current_chunk_text:
                    chunks.append(Chunk(
                        id=f"{doc.id}_chunk_{chunk_index}",
                        doc_id=doc.id,
                        content=current_chunk_text,
                        chunk_index=chunk_index,
                        source_file=doc.source_path,
                        paragraph_number=current_paragraph_index
                    ))
                    chunk_index += 1

                # If individual paragraph is longer than max_chunk_size, split by sentences
                if len(para) > max_chunk_size:
                    sentences = re.split(r"(?<=[.!?])\s+", para)
                    sub_text = ""
                    for sent in sentences:
                        if len(sub_text) + len(sent) <= max_chunk_size:
                            sub_text += (" " if sub_text else "") + sent
                        else:
                            if sub_text:
                                chunks.append(Chunk(
                                    id=f"{doc.id}_chunk_{chunk_index}",
                                    doc_id=doc.id,
                                    content=sub_text,
                                    chunk_index=chunk_index,
                                    source_file=doc.source_path,
                                    paragraph_number=current_paragraph_index
                                ))
                                chunk_index += 1
                            sub_text = sent
                    if sub_text:
                        current_chunk_text = sub_text
                    else:
                        current_chunk_text = ""
                else:
                    current_chunk_text = para
            current_paragraph_index += 1

        if current_chunk_text:
            chunks.append(Chunk(
                id=f"{doc.id}_chunk_{chunk_index}",
                doc_id=doc.id,
                content=current_chunk_text,
                chunk_index=chunk_index,
                source_file=doc.source_path,
                paragraph_number=current_paragraph_index
            ))

        return chunks
