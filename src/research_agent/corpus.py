"""Tokenization + a BM25 corpus search tool.

The corpus is a small committed knowledge base; ``search`` is the agent's only
window into it. Keeping retrieval deterministic (BM25) is what makes the whole
research run reproducible offline.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi

from research_agent.schemas import Source

_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "to",
    "in",
    "on",
    "for",
    "is",
    "are",
    "be",
    "with",
    "that",
    "this",
    "by",
    "as",
    "it",
    "you",
    "can",
    "how",
    "what",
    "why",
    "do",
    "does",
    "make",
    "more",
    "your",
}


def tokens(text: str) -> list[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOP and len(t) > 1]


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def overlap(a: str, b: str) -> float:
    """Jaccard-ish token overlap of `a` against `b` (fraction of a's tokens in b)."""
    ta, tb = set(tokens(a)), set(tokens(b))
    if not ta:
        return 0.0
    return len(ta & tb) / len(ta)


def _corpus_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "corpus.jsonl"


class Corpus:
    def __init__(self, sources: list[Source] | None = None) -> None:
        self.sources = sources if sources is not None else self._load()
        self._index = BM25Okapi([tokens(s.title + " " + s.text) for s in self.sources])

    @staticmethod
    def _load() -> list[Source]:
        with _corpus_path().open() as fh:
            return [Source(**json.loads(line)) for line in fh if line.strip()]

    def search(self, query: str, k: int = 3) -> list[Source]:
        scores = self._index.get_scores(tokens(query))
        ranked = sorted(zip(scores, self.sources, strict=True), key=lambda x: x[0], reverse=True)
        return [s for score, s in ranked[:k] if score > 0]
