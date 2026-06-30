"""The manager — coordinates the sub-agents as tools, under a hard budget.

This is the *manager pattern*: a single coordinator owns the workflow and calls
specialist sub-agents (plan / search / synthesize / fact-check / write) as tools,
never exceeding the step + search ceiling. Every action spends budget, so a research
run can't quietly balloon in cost.
"""

from __future__ import annotations

from research_agent import agents
from research_agent.config import Settings, get_settings
from research_agent.corpus import Corpus
from research_agent.schemas import Budget, ResearchReport, Source


class ResearchManager:
    def __init__(self, settings: Settings | None = None, corpus: Corpus | None = None) -> None:
        self.settings = settings or get_settings()
        self.corpus = corpus or Corpus()

    def research(self, question: str) -> ResearchReport:
        s = self.settings
        budget = Budget(max_steps=s.max_steps, max_searches=s.max_searches)

        # 1) plan: start from the question; gather sources across budgeted searches.
        budget.spend_step()
        queries: list[str] = [question]
        asked: set[str] = set()
        sources: dict[str, Source] = {}
        first = True

        while queries and budget.can_search():
            query = queries.pop(0)
            if query.lower() in {a.lower() for a in asked}:
                continue
            asked.add(query)
            budget.spend_search()
            hits = self.corpus.search(query, k=s.top_k)
            for hit in hits:
                sources.setdefault(hit.id, hit)
            if first:
                first = False
                remaining = max(0, s.max_searches - len(asked))
                followups = agents.plan_followups([h.title for h in hits], asked, remaining)
                if not followups:
                    followups = agents.keyword_queries(question, remaining)
                queries.extend(followups)
                budget.spend_step()

        # 2) synthesize cited claims, 3) fact-check, 4) write.
        by_id = dict(sources)
        budget.spend_step()
        claims = agents.synthesize(question, list(sources.values()), s.min_relevance)
        budget.spend_step()
        claims = agents.fact_check(claims, by_id)
        budget.spend_step()
        summary, citations = agents.write(question, claims, by_id)

        return ResearchReport(
            question=question,
            sub_queries=sorted(asked),
            claims=claims,
            citations=citations,
            summary=summary,
            steps_used=budget.steps_used,
            searches_used=budget.searches_used,
        )
