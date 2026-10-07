import json
import unittest
from pathlib import Path

from eval.run_eval import detect_form, load_documents


ROOT = Path(__file__).resolve().parents[1]


class EvaluationDataTests(unittest.TestCase):
    def test_has_160_rows_and_four_forms(self):
        path = ROOT / "eval" / "questions.jsonl"
        with path.open(encoding="utf-8") as file:
            rows = [json.loads(line) for line in file if line.strip()]
        self.assertEqual(len(rows), 160)
        self.assertEqual({row["form"] for row in rows}, {"hy", "ru", "translit", "mixed"})

    def test_native_check_flags_are_present(self):
        with (ROOT / "eval" / "questions.jsonl").open(encoding="utf-8") as file:
            rows = [json.loads(line) for line in file if line.strip()]
        for row in rows:
            if row["form"] in {"hy", "translit", "mixed"}:
                self.assertTrue(row["needs_native_check"])

    def test_sample_store_counts(self):
        self.assertEqual(len(load_documents()), 45)

    def test_form_detection_examples(self):
        self.assertEqual(detect_form("Բարև, այս գիրքը ունե՞ք։"), "hy")
        self.assertEqual(detect_form("Здравствуйте, эта книга есть?"), "ru")
        self.assertEqual(detect_form("Barev, ays girqy uneq?"), "translit")
        self.assertEqual(detect_form("Barev, eta kniga есть?"), "mixed")
