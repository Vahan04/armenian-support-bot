import unittest
from pathlib import Path

from bot.pipeline import StrictRAG
from ingest.build_index import build_index
from retrieval.vector_store import VectorStore


ROOT = Path(__file__).resolve().parents[1]


class VectorRAGTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build_index()
        cls.rag = StrictRAG(VectorStore.load(ROOT / "index"))

    def test_index_has_all_documents(self):
        self.assertEqual(len(self.rag.store.documents), 45)

    def test_known_product_returns_a_source(self):
        result = self.rag.answer("How much does 1984 cost?")
        self.assertIn("product:p002", result["sources"])
        self.assertFalse(result["handoff"])

    def test_unknown_question_handoffs(self):
        result = self.rag.answer("What will the weather be tomorrow?")
        self.assertTrue(result["handoff"])


if __name__ == "__main__":
    unittest.main()
