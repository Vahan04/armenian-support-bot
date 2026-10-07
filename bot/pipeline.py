"""Baseline retrieve-then-answer pipeline with refusal behavior."""

from __future__ import annotations

from typing import Any

from eval.run_eval import detect_form


class StrictRAG:
    def __init__(self, store, k: int = 3):
        self.store = store
        self.k = k

    def retrieve(self, question: str) -> list[dict[str, Any]]:
        return self.store.search(question, self.k)

    def answer(self, question: str) -> dict[str, Any]:
        form = detect_form(question)
        documents = self.retrieve(question)
        if not documents or documents[0]["score"] < 0.15:
            return {
                "text": self._refusal(form),
                "confidence": 0.0,
                "sources": [],
                "handoff": True,
            }
        source = documents[0]
        return {
            "text": f"According to {source['title']}: {source['text']}",
            "confidence": source["score"],
            "sources": [document["id"] for document in documents],
            "handoff": False,
        }

    @staticmethod
    def _refusal(form: str) -> str:
        if form == "ru":
            return "У меня нет этой информации в данных магазина. Я передам вопрос сотруднику."
        if form in {"hy", "mixed"}:
            return "Այս տեղեկությունը խանութի տվյալներում չկա։ Հարցը կփոխանցեմ աշխատակցին։"
        return "Ays texekutyuny khanut i tvyalnerum chka. Harcy kփոխանցեմ ashkhatakcin."
