"""End-to-end manager behavior + the eval gate."""

from __future__ import annotations

import pytest

from research_agent.corpus import Corpus, overlap
from research_agent.evals import evaluate
from research_agent.manager import ResearchManager


def test_every_claim_is_cited_and_faithful():
    corpus = Corpus()
    by_id = {s.id: s for s in corpus.sources}
    report = ResearchManager(corpus=corpus).research("How do you evaluate a large language model?")
    assert report.n_claims > 0
    for claim in report.claims:
        assert claim.source_id in by_id
        assert overlap(claim.text, by_id[claim.source_id].text) >= 0.6


@pytest.fixture(scope="module")
def eval_report():
    return evaluate()


def test_gate_passes(eval_report):
    assert eval_report.passed(), f"gate failed on: {eval_report.failures()}"


def test_faithfulness_is_perfect(eval_report):
    assert eval_report.aggregate["faithfulness"] == 1.0
    assert eval_report.aggregate["citation_rate"] == 1.0


def test_coverage_is_reasonable(eval_report):
    assert eval_report.aggregate["coverage"] >= 0.60


def test_budget_always_respected(eval_report):
    assert eval_report.aggregate["budget_respected"] == 1.0
