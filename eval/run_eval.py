"""Run the deterministic Milestone 1 retrieval and answer benchmark."""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "sample_store"
EVAL_PATH = ROOT / "eval" / "questions.jsonl"
RESULTS_DIR = ROOT / "results"
INDEX_DIR = ROOT / "index"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def load_documents() -> list[dict[str, Any]]:
    products = load_json(DATA_DIR / "products.json")
    faqs = load_json(DATA_DIR / "faqs.json")
    documents = []
    for product in products:
        documents.append({
            "id": f"product:{product['id']}",
            "kind": "product",
            "title": product["title"],
            "text": " ".join(str(value) for value in product.values()),
            "facts": [
                product["title"],
                product["author"],
                f"{product['price_amd']} AMD",
                "in stock" if product["in_stock"] else "out of stock",
            ],
        })
    for faq in faqs:
        documents.append({
            "id": f"faq:{faq['id']}",
            "kind": "faq",
            "title": faq["topic"],
            "text": " ".join(str(value) for value in faq.values()),
            "facts": faq["facts"],
        })
    return documents


def tokenize(text: str) -> set[str]:
    return {
        token.lower()
        for token in re.findall(r"[0-9A-Za-zԱ-Ֆա-ֆЁёА-Яа-я']+", text)
        if len(token) > 1
    }


def detect_form(text: str) -> str:
    has_armenian = bool(re.search(r"[Ա-Ֆա-ֆ]", text))
    has_cyrillic = bool(re.search(r"[А-Яа-яЁё]", text))
    has_latin = bool(re.search(r"[A-Za-z]", text))
    if has_armenian and not has_latin and not has_cyrillic:
        return "hy"
    if has_cyrillic and not has_latin and not has_armenian:
        return "ru"
    if has_latin and (has_armenian or has_cyrillic):
        return "mixed"
    if has_latin:
        return "translit"
    return "unknown"


def retrieve(question: str, documents: list[dict[str, Any]], k: int = 3) -> list[dict[str, Any]]:
    question_tokens = tokenize(question)
    scored = []
    for document in documents:
        document_tokens = tokenize(document["text"])
        overlap = len(question_tokens & document_tokens)
        title_overlap = len(question_tokens & tokenize(document["title"]))
        scored.append((overlap + 2 * title_overlap, document))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [document for score, document in scored[:k] if score > 0]


def expected_document_ids(row: dict[str, Any]) -> set[str]:
    return set(row.get("expected_document_ids", []))


def facts_present(row: dict[str, Any], retrieved: list[dict[str, Any]]) -> bool:
    if not row["answerable"]:
        return True
    combined = " ".join(document["text"] for document in retrieved).lower()
    return all(str(fact).lower() in combined for fact in row["expected_answer_facts"])


def correct_refusal(row: dict[str, Any], retrieved: list[dict[str, Any]]) -> bool:
    if row["answerable"]:
        return True
    return not bool(set(row.get("expected_document_ids", [])) & {doc["id"] for doc in retrieved})


def evaluate_row(row: dict[str, Any], documents: list[dict[str, Any]]) -> dict[str, Any]:
    retrieved = retrieve(row["text"], documents)
    retrieved_ids = {document["id"] for document in retrieved}
    target_ids = expected_document_ids(row)
    return {
        "id": row["id"],
        "base_id": row["base_id"],
        "form": row["form"],
        "detected_form": detect_form(row["text"]),
        "answerable": row["answerable"],
        "needs_native_check": row.get("needs_native_check", False),
        "retrieved_ids": "|".join(document["id"] for document in retrieved),
        "retrieval_hit_at_3": bool(target_ids & retrieved_ids) if row["answerable"] else correct_refusal(row, retrieved),
        "answer_correct": facts_present(row, retrieved),
        "correct_refusal": correct_refusal(row, retrieved),
        "overall_correct": (facts_present(row, retrieved) if row["answerable"] else correct_refusal(row, retrieved)),
    }


def write_results(results: list[dict[str, Any]]) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    fields = list(results[0])
    with (RESULTS_DIR / "evaluation_by_question.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for result in results:
        grouped[result["form"]].append(result)
    summary = []
    for form in ("hy", "ru", "translit", "mixed"):
        rows = grouped[form]
        summary.append({
            "form": form,
            "questions": len(rows),
            "retrieval_hit_at_3": sum(row["retrieval_hit_at_3"] for row in rows) / len(rows),
            "answer_correct": sum(row["answer_correct"] for row in rows) / len(rows),
            "correct_refusal": sum(row["correct_refusal"] for row in rows) / len(rows),
            "overall_accuracy": sum(row["overall_correct"] for row in rows) / len(rows),
        })
    with (RESULTS_DIR / "summary_by_form.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)

    figure, axis = plt.subplots(figsize=(8, 4.5))
    axis.bar([row["form"] for row in summary], [row["overall_accuracy"] for row in summary], color="#587c63")
    axis.set_ylim(0, 1)
    axis.set_ylabel("Accuracy")
    axis.set_title("Baseline RAG accuracy by question form")
    for index, row in enumerate(summary):
        axis.text(index, row["overall_accuracy"] + 0.03, f"{row['overall_accuracy']:.0%}", ha="center")
    figure.tight_layout()
    figure.savefig(RESULTS_DIR / "accuracy_by_form.png", dpi=160)
    plt.close(figure)


def run_vector_eval() -> list[dict[str, Any]]:
    from bot.pipeline import StrictRAG
    from ingest.build_index import build_index
    from retrieval.vector_store import VectorStore

    build_index()
    rag = StrictRAG(VectorStore.load(INDEX_DIR))
    with EVAL_PATH.open(encoding="utf-8") as file:
        rows = [json.loads(line) for line in file if line.strip()]
    results = []
    for row in rows:
        retrieved = rag.retrieve(row["text"])
        retrieved_ids = {document["id"] for document in retrieved}
        target_ids = expected_document_ids(row)
        answer = rag.answer(row["text"])
        answer_text = answer["text"].lower()
        facts_ok = (not row["answerable"]) or all(
            str(fact).lower() in answer_text for fact in row["expected_answer_facts"]
        )
        refusal_ok = row["answerable"] or answer["handoff"]
        results.append({
            "id": row["id"],
            "base_id": row["base_id"],
            "form": row["form"],
            "detected_form": detect_form(row["text"]),
            "answerable": row["answerable"],
            "needs_native_check": row.get("needs_native_check", False),
            "retrieved_ids": "|".join(document["id"] for document in retrieved),
            "retrieval_hit_at_3": bool(target_ids & retrieved_ids) if row["answerable"] else refusal_ok,
            "answer_correct": facts_ok,
            "correct_refusal": refusal_ok,
            "overall_correct": facts_ok and refusal_ok,
        })
    return results


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "lexical"
    documents = load_documents()
    with EVAL_PATH.open(encoding="utf-8") as file:
        rows = [json.loads(line) for line in file if line.strip()]
    results = run_vector_eval() if mode == "vector" else [evaluate_row(row, documents) for row in rows]
    write_results(results)
    print(f"Evaluated {len(results)} questions.")
    for form in ("hy", "ru", "translit", "mixed"):
        form_results = [row for row in results if row["form"] == form]
        accuracy = sum(row["overall_correct"] for row in form_results) / len(form_results)
        print(f"{form:8} accuracy={accuracy:.1%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
