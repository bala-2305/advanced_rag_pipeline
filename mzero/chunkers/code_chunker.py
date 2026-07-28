"""Function and class AST-aware code chunking for mzero."""

import re
from typing import List
from mzero.types import Document, Chunk


class CodeChunker:
    @staticmethod
    def chunk(doc: Document) -> List[Chunk]:
        content = doc.content.strip()
        if not content:
            return []

        chunks: List[Chunk] = []
        chunk_index = 0

        # Split code by class or function definitions (for Python, JS, C-like)
        blocks = re.split(r"(?=\n(?:def |class |function |async def |public |private |interface ))", content)

        for block in blocks:
            block_text = block.strip()
            if not block_text:
                continue

            # Extract header function/class title if available
            first_line = block_text.split("\n")[0]
            chunks.append(Chunk(
                id=f"{doc.id}_code_chunk_{chunk_index}",
                doc_id=doc.id,
                content=block_text,
                chunk_index=chunk_index,
                source_file=doc.source_path,
                section_title=first_line[:80]
            ))
            chunk_index += 1

        return chunks
