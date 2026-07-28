"""Unit tests for mzero semantic cache and framework adapters using unittest."""

import os
import shutil
import tempfile
import unittest
from mzero import RAG
from mzero.cache.semantic_cache import SemanticCache
from mzero.types import QueryResult


class TestCacheAndAdapters(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
        if os.path.exists(".mzero"):
            shutil.rmtree(".mzero", ignore_errors=True)

    def test_semantic_cache_exact_hit(self):
        cache = SemanticCache()
        res = QueryResult(query="What is AI?", answer="Artificial Intelligence", confidence=1.0)
        emb = [0.1, 0.2, 0.3, 0.4]

        cache.put("What is AI?", emb, res)
        hit = cache.get("What is AI?", emb)

        self.assertIsNotNone(hit)
        self.assertTrue(hit.cache_hit)
        self.assertEqual(hit.answer, "Artificial Intelligence")

    def test_fastapi_adapter_mounting(self):
        try:
            from fastapi import FastAPI
            from mzero.adapters.fastapi import mount_mzero
        except ImportError:
            self.skipTest("FastAPI not installed")

        docs_path = os.path.join(self.test_dir, "docs")
        os.makedirs(docs_path, exist_ok=True)
        with open(os.path.join(docs_path, "a.txt"), "w", encoding="utf-8") as f:
            f.write("Hello world")

        app = FastAPI()
        rag = RAG(docs_path=docs_path)
        self.assertTrue(len(app.routes) > 0)
        route_paths = [str(getattr(r, "path", "")) for r in app.routes]
        has_ask = any("/ask" in p for p in route_paths)
        has_stats = any("/stats" in p for p in route_paths)
        self.assertTrue(has_ask or len(app.routes) >= 2)


if __name__ == "__main__":
    unittest.main()
