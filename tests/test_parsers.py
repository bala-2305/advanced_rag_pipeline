"""Unit tests for mzero document parsers and chunkers using unittest."""

import os
import shutil
import tempfile
import unittest
from mzero.parsers.router import DocumentParserRouter
from mzero.chunkers.strategy import AdaptiveChunker
from mzero.types import DocumentType


class TestParsersAndChunkers(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_txt_and_md_parser(self):
        f_path = os.path.join(self.test_dir, "test.md")
        with open(f_path, "w", encoding="utf-8") as f:
            f.write("# Section 1\nThis is markdown text.")

        doc = DocumentParserRouter.parse(f_path)
        self.assertEqual(doc.doc_type, DocumentType.MARKDOWN)
        self.assertIn("Section 1", doc.content)

    def test_code_parser(self):
        f_path = os.path.join(self.test_dir, "app.py")
        with open(f_path, "w", encoding="utf-8") as f:
            f.write("def hello():\n    print('world')\n")

        doc = DocumentParserRouter.parse(f_path)
        self.assertEqual(doc.doc_type, DocumentType.CODE)

        chunks = AdaptiveChunker.chunk(doc)
        self.assertGreater(len(chunks), 0)
        self.assertIn("hello", chunks[0].content)

    def test_json_parser(self):
        f_path = os.path.join(self.test_dir, "data.json")
        with open(f_path, "w", encoding="utf-8") as f:
            f.write('{"name": "mzero", "type": "rag"}')

        doc = DocumentParserRouter.parse(f_path)
        self.assertEqual(doc.doc_type, DocumentType.JSON)
        self.assertIn("mzero", doc.content)


if __name__ == "__main__":
    unittest.main()
