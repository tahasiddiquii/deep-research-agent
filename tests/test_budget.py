"""Budget mechanics + the manager respecting it."""

from __future__ import annotations

from research_agent.config import get_settings
from research_agent.manager import ResearchManager
from research_agent.schemas import Budget


def test_budget_search_ceiling():
    b = Budget(max_steps=10, max_searches=2)
    assert b.can_search()
    b.spend_search()
    b.spend_search()
    assert not b.can_search()


def test_budget_step_ceiling():
    b = Budget(max_steps=1, max_searches=5)
    b.spend_step()
    assert b.exhausted
    assert not b.can_search()


def test_manager_never_exceeds_budget():
    settings = get_settings()
    report = ResearchManager().research("How can you reduce the inference cost of language models?")
    assert report.searches_used <= settings.max_searches
    assert report.steps_used <= settings.max_steps
