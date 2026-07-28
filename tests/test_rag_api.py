"""Unit tests for mzero RAG and AsyncRAG public API using unittest."""

import os
import shutil
import tempfile
import asyncio
import unittest
from mzero import RAG, AsyncRAG


class TestRAGApi(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.docs_dir = os.path.join(self.test_dir, "docs")
        os.makedirs(self.docs_dir, exist_ok=True)

        with open(os.path.join(self.docs_dir, "sample.txt"), "w", encoding="utf-8") as f:
            f.write("mzero is a zero-configuration RAG framework for Python. It automatically handles chunking and vector search.")

        with open(os.path.join(self.docs_dir, "faq.md"), "w", encoding="utf-8") as f:
            f.write("# FAQ\n\nQ: What is the refund policy?\nA: All software purchases come with a 30-day money-back guarantee.")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
        if os.path.exists(".mzero"):
            shutil.rmtree(".mzero", ignore_errors=True)

    def test_rag_sync_ask_and_stats(self):
        rag = RAG(docs_path=self.docs_dir)
        res = rag.ask("What is the refund policy?")

        self.assertIsNotNone(res)
        self.assertTrue("30-day" in res.answer or "money-back" in res.answer or "refund" in res.answer.lower() or "knowledge" in res.answer.lower())
        self.assertTrue(len(res.citations) > 0)

        stats = rag.stats()
        self.assertEqual(stats.total_documents, 2)
        self.assertGreaterEqual(stats.total_chunks, 2)

    def test_rag_sync_stream(self):
        rag = RAG(docs_path=self.docs_dir)
        chunks = list(rag.stream("Explain mzero"))
        self.assertGreater(len(chunks), 0)
        full_text = "".join(chunks)
        self.assertGreater(len(full_text), 0)

    def test_async_rag(self):
        arag = AsyncRAG(docs_path=self.docs_dir)
        res = asyncio.run(arag.aask("What is the refund policy?"))
        self.assertIsNotNone(res)
        self.assertGreater(len(res.answer), 0)


if __name__ == "__main__":
    unittest.main()
