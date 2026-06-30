# deep-research-agent — evaluation report

Runs the manager over **5** research questions. The gate enforces the two things a research agent must never get wrong: **faithfulness** (every claim traces to a cited source) and **budget adherence** (the run never exceeds its step/search ceiling).

| metric | value | threshold |
| --- | --- | --- |
| faithfulness | 1.000 | ≥ 0.99 |
| citation_rate | 1.000 | ≥ 0.99 |
| coverage | 0.800 | ≥ 0.60 |
| budget_respected | 1.000 | ≥ 1.00 |
| avg_searches | 4.00 | (budget 1×ceiling) |
| avg_claims | 3.20 | — |

**Gate: PASSED**

Faithfulness is 1.0 **by construction** — claims are extracted from the cited source and a fact-check pass drops anything unsupported — and the gate keeps it that way as the synthesizer evolves (e.g. swapping in an LLM). Coverage is the honest quality signal: it measures how much of each question the budgeted search actually surfaced.
