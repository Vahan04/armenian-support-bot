"""Build a persisted vector index from the sample store."""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

from eval.run_eval import load_documents
from retrieval.vector_store import VectorStore

ROOT = Path(__file__).resolve().parents[1]
INDEX_DIR = ROOT / "index"


def build_index() -> dict[str, Any]:
    documents = load_documents()
    store = VectorStore()
    store.fit(documents)
    INDEX_DIR.mkdir(exist_ok=True)
    store.save(INDEX_DIR)
    metadata = {"documents": len(documents), "backend": store.backend_name}
    (INDEX_DIR / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


if __name__ == "__main__":
    print(json.dumps(build_index(), indent=2))
