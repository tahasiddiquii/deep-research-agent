"""Corpus search + text utilities."""

from __future__ import annotations

from research_agent.corpus import Corpus, overlap, sentences, tokens


def test_search_finds_topical_doc():
    ids = [s.id for s in Corpus().search("reduce inference cost of language models", 3)]
    assert {"quantization", "mixture-of-experts", "kv-caching"} & set(ids)


def test_tokens_drop_stopwords():
    assert "the" not in tokens("the model is fast")
    assert "model" in tokens("the model is fast")


def test_sentences_split():
    assert len(sentences("A first idea. A second one. A third.")) == 3


def test_overlap_fraction():
    assert overlap("inference cost", "reduce inference cost now") == 1.0
    assert overlap("bananas", "reduce inference cost") == 0.0
