# Agent / contributor guide

Orientation for an AI agent or new contributor working in this repo.

## What this is

A **manager-pattern** research agent: a coordinator calls specialist sub-agents
(plan / search / synthesize / fact-check / write) as tools, under a hard step + search
budget, producing a cited report. **Fully offline** — retrieval is BM25 over a committed
corpus and synthesis is extractive by default, so every run is reproducible.

## Layout

```
src/research_agent/
  corpus.py     BM25 search tool + tokenization (the agent's window into the corpus)
  agents.py     sub-agents as pure functions: plan_followups / synthesize / fact_check / write
  manager.py    ResearchManager — orchestrates the sub-agents under a Budget
  schemas.py    Budget, Source, Claim, ResearchReport
  evals.py      faithfulness / citation / coverage / budget gate (THRESHOLDS)
  report.py     render a research report to markdown
  cli.py        research / eval / demo
data/           corpus.jsonl · questions.jsonl
tests/          one file per module
reports/        research_report_example.md (committed proof)
```

## Conventions

- Python 3.11+ (CI pins 3.12). `from __future__ import annotations` everywhere. Ruff for
  lint/format (`make fmt`, `make lint`); line length 110.
- **Budget is sacred.** Every action goes through `Budget`; the manager checks `can_search`
  / `can_step` before acting. A change that can exceed the ceiling is a bug.
- **Faithfulness by construction.** Claims are extracted from a cited source and the
  fact-check pass drops anything unsupported. If you swap in an LLM synthesizer, keep the
  deterministic fact-check — it's what guarantees claims trace to sources.
- **Never hand-write metrics.** Every number in the README/report is produced by
  `evaluate()`. Change behavior, regenerate (`make report`), update the README.

## Definition of done

```bash
make lint   # ruff clean
make test   # all tests pass
make eval   # gate exits 0 (faithfulness == 1, budget respected, coverage >= 0.60)
```

The same checks run in CI ([.github/workflows/ci.yml](.github/workflows/ci.yml)).

## Extending

- Real synthesis: set `RESEARCH_PROVIDER=openai`; keep `fact_check` deterministic.
- Bigger corpus: add docs to `data/corpus.jsonl`; retrieval is generic.
- New metric: compute it in `evaluate` and gate it in `THRESHOLDS`.
