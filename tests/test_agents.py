"""Sub-agents: synthesize, fact-check, write."""

from __future__ import annotations

from research_agent.agents import fact_check, synthesize, write
from research_agent.schemas import Claim, Source


def _sources():
    return [Source(id="s1", title="Quantization", text="Quantization reduces inference cost. It uses int8.")]


def test_synthesize_extracts_grounded_claim():
    claims = synthesize("how to reduce inference cost", _sources(), 0.1)
    assert claims
    assert claims[0].source_id == "s1"


def test_fact_check_drops_unsupported_claim():
    by_id = {"s1": _sources()[0]}
    good = Claim(text="Quantization reduces inference cost.", source_id="s1")
    bad = Claim(text="Bananas are a tropical yellow fruit.", source_id="s1")
    kept = fact_check([good, bad], by_id)
    assert good in kept
    assert bad not in kept


def test_write_builds_citations():
    by_id = {"s1": _sources()[0]}
    claims = [Claim(text="Quantization reduces inference cost.", source_id="s1")]
    summary, citations = write("q", claims, by_id)
    assert summary
    assert citations and citations[0].source_id == "s1"
