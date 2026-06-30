"""Sub-agents, exposed to the manager as callable tools.

Each function is one specialist the manager can invoke: a planner that proposes
follow-up searches, a synthesizer that turns sources into cited claims, a fact-checker
that verifies every claim traces back to its source, and a writer that assembles the
report. Deterministic by default (set ``RESEARCH_PROVIDER=openai`` to synthesize with a
model); the fact-check stays deterministic either way.
"""

from __future__ import annotations

from research_agent.corpus import overlap, sentences, tokens
from research_agent.schemas import Citation, Claim, Source


def relevance(question: str, sentence: str) -> float:
    """Fraction of the question's content tokens covered by the sentence."""
    return overlap(question, sentence)


def plan_followups(titles: list[str], asked: set[str], limit: int) -> list[str]:
    """Propose follow-up queries from what the first search surfaced (iterative deepening)."""
    out: list[str] = []
    for title in titles:
        q = title.strip()
        if q and q.lower() not in {a.lower() for a in asked} and q not in out:
            out.append(q)
        if len(out) >= limit:
            break
    return out


def synthesize(question: str, sources: list[Source], min_relevance: float) -> list[Claim]:
    """Extract, from each source, the single sentence most relevant to the question."""
    claims: list[Claim] = []
    for source in sources:
        best_sentence, best_score = "", 0.0
        for sentence in sentences(source.text):
            score = relevance(question, sentence)
            if score > best_score:
                best_sentence, best_score = sentence, score
        if best_sentence and best_score >= min_relevance:
            claims.append(Claim(text=best_sentence, source_id=source.id))
    claims.sort(key=lambda c: relevance(question, c.text), reverse=True)
    return claims


def fact_check(claims: list[Claim], by_id: dict[str, Source], min_support: float = 0.6) -> list[Claim]:
    """Keep only claims whose text is actually supported by the cited source."""
    verified: list[Claim] = []
    for claim in claims:
        source = by_id.get(claim.source_id)
        if source and overlap(claim.text, source.text) >= min_support:
            verified.append(claim)
    return verified


def write(question: str, claims: list[Claim], by_id: dict[str, Source]) -> tuple[str, list[Citation]]:
    """Assemble a short grounded summary + the citation list."""
    if not claims:
        return ("No sufficiently grounded findings were retrieved within budget.", [])
    summary = " ".join(claim.text for claim in claims[:5])
    seen: dict[str, Citation] = {}
    for claim in claims:
        source = by_id.get(claim.source_id)
        if source and source.id not in seen:
            seen[source.id] = Citation(source_id=source.id, title=source.title)
    return summary, list(seen.values())


def keyword_queries(question: str, limit: int) -> list[str]:
    """Salient single-keyword fallback queries derived from the question."""
    seen: list[str] = []
    for t in tokens(question):
        if len(t) >= 5 and t not in seen:
            seen.append(t)
        if len(seen) >= limit:
            break
    return seen
