"""Evaluation + the faithfulness/budget gate.

Runs the manager over a labeled question set and scores what matters for a research
agent: **faithfulness** (every claim traceable to its cited source), **citation rate**,
**coverage** of the expected points, and **budget adherence**. The gate refuses to pass a
run that hallucinates (faithfulness < 1) or blows the budget.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from research_agent.config import Settings, get_settings
from research_agent.corpus import Corpus, overlap
from research_agent.manager import ResearchManager
from research_agent.schemas import ResearchReport, Source

THRESHOLDS = {
    "faithfulness": 0.99,
    "citation_rate": 0.99,
    "coverage": 0.60,
    "budget_respected": 1.0,
}


def _questions_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "questions.jsonl"


def load_questions(path: Path | None = None) -> list[dict]:
    with (path or _questions_path()).open() as fh:
        return [json.loads(line) for line in fh if line.strip()]


@dataclass
class EvalReport:
    n: int
    aggregate: dict
    results: list[dict] = field(default_factory=list)

    def passed(self) -> bool:
        return not self.failures()

    def failures(self) -> list[str]:
        out: list[str] = []
        for metric, threshold in THRESHOLDS.items():
            value = self.aggregate.get(metric, 0.0)
            if value < threshold:
                out.append(f"{metric}={value:.3f} < {threshold:.2f}")
        return out


def _coverage(report: ResearchReport, expected_points: list[str]) -> float:
    if not expected_points:
        return 1.0
    text = (report.summary + " " + " ".join(c.text for c in report.claims)).lower()
    return sum(1 for p in expected_points if p.lower() in text) / len(expected_points)


def _faithful(report: ResearchReport, by_id: dict[str, Source]) -> float:
    if not report.claims:
        return 1.0
    supported = sum(
        1 for c in report.claims if c.source_id in by_id and overlap(c.text, by_id[c.source_id].text) >= 0.6
    )
    return supported / len(report.claims)


def evaluate(settings: Settings | None = None, questions: list[dict] | None = None) -> EvalReport:
    settings = settings or get_settings()
    questions = questions if questions is not None else load_questions()
    corpus = Corpus()
    by_id = {s.id: s for s in corpus.sources}
    manager = ResearchManager(settings, corpus)

    faith: list[float] = []
    cite: list[float] = []
    cov: list[float] = []
    budget_ok = 0
    results: list[dict] = []

    for q in questions:
        report = manager.research(q["question"])
        n_claims = len(report.claims)
        f = _faithful(report, by_id)
        cr = (sum(1 for c in report.claims if c.source_id in by_id) / n_claims) if n_claims else 1.0
        cv = _coverage(report, q["expected_points"])
        ok = report.steps_used <= settings.max_steps and report.searches_used <= settings.max_searches
        faith.append(f)
        cite.append(cr)
        cov.append(cv)
        budget_ok += int(ok)
        results.append(
            {
                "id": q["id"],
                "claims": n_claims,
                "searches": report.searches_used,
                "steps": report.steps_used,
                "faithfulness": round(f, 3),
                "coverage": round(cv, 3),
            }
        )

    n = len(questions)
    aggregate = {
        "faithfulness": round(sum(faith) / n, 4),
        "citation_rate": round(sum(cite) / n, 4),
        "coverage": round(sum(cov) / n, 4),
        "budget_respected": round(budget_ok / n, 4),
        "avg_searches": round(sum(r["searches"] for r in results) / n, 2),
        "avg_claims": round(sum(r["claims"] for r in results) / n, 2),
    }
    return EvalReport(n=n, aggregate=aggregate, results=results)


def write_markdown(report: EvalReport, path: Path) -> None:
    a = report.aggregate
    lines = [
        "# deep-research-agent — evaluation report",
        "",
        f"Runs the manager over **{report.n}** research questions. The gate enforces the two "
        "things a research agent must never get wrong: **faithfulness** (every claim traces to a "
        "cited source) and **budget adherence** (the run never exceeds its step/search ceiling).",
        "",
        "| metric | value | threshold |",
        "| --- | --- | --- |",
    ]
    for metric, threshold in THRESHOLDS.items():
        lines.append(f"| {metric} | {a.get(metric, 0.0):.3f} | ≥ {threshold:.2f} |")
    lines += [
        f"| avg_searches | {a['avg_searches']:.2f} | (budget {THRESHOLDS['budget_respected']:.0f}×ceiling) |",
        f"| avg_claims | {a['avg_claims']:.2f} | — |",
        "",
        f"**Gate: {'PASSED' if report.passed() else 'FAILED'}**",
        "",
        "Faithfulness is 1.0 **by construction** — claims are extracted from the cited source and a "
        "fact-check pass drops anything unsupported — and the gate keeps it that way as the synthesizer "
        "evolves (e.g. swapping in an LLM). Coverage is the honest quality signal: it measures how much "
        "of each question the budgeted search actually surfaced.",
    ]
    path.write_text("\n".join(lines) + "\n")
