"""Configurable multilingual vector retrieval with an offline fallback."""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class VectorStore:
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self.backend_name = "tfidf"
        self.documents: list[dict[str, Any]] = []
        self.vectorizer: TfidfVectorizer | None = None
        self.matrix = None
        self.encoder = None

    def fit(self, documents: list[dict[str, Any]]) -> None:
        self.documents = documents
        try:
            from sentence_transformers import SentenceTransformer

            self.encoder = SentenceTransformer(self.model_name)
            self.matrix = self.encoder.encode(
                [document["text"] for document in documents],
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            self.backend_name = "sentence-transformers"
        except (ImportError, OSError, RuntimeError):
            self.vectorizer = TfidfVectorizer(
                analyzer="char_wb",
                ngram_range=(2, 5),
                min_df=1,
                sublinear_tf=True,
            )
            self.matrix = self.vectorizer.fit_transform([document["text"] for document in documents])
            self.backend_name = "tfidf-fallback"

    def search(self, query: str, k: int = 3) -> list[dict[str, Any]]:
        if self.matrix is None:
            raise RuntimeError("VectorStore must be fitted or loaded before search.")
        if self.backend_name == "sentence-transformers":
            scores = np.asarray(self.encoder.encode([query], normalize_embeddings=True))[0] @ np.asarray(self.matrix).T
        else:
            query_vector = self.vectorizer.transform([query])
            scores = (self.matrix @ query_vector.T).toarray().ravel()
        indices = np.argsort(scores)[::-1][:k]
        return [
            {**self.documents[index], "score": float(scores[index])}
            for index in indices
            if scores[index] > 0
        ]

    def save(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        payload = {
            "model_name": self.model_name,
            "backend_name": self.backend_name,
            "documents": self.documents,
            "vectorizer": self.vectorizer,
            "matrix": self.matrix,
        }
        with (directory / "store.pkl").open("wb") as file:
            pickle.dump(payload, file)

    @classmethod
    def load(cls, directory: Path) -> "VectorStore":
        with (directory / "store.pkl").open("rb") as file:
            payload = pickle.load(file)
        store = cls(payload["model_name"])
        store.backend_name = payload["backend_name"]
        store.documents = payload["documents"]
        store.vectorizer = payload["vectorizer"]
        store.matrix = payload["matrix"]
        if store.backend_name == "sentence-transformers":
            from sentence_transformers import SentenceTransformer

            store.encoder = SentenceTransformer(store.model_name)
        return store
