"""deep-research-agent — a manager-pattern research workflow.

A coordinator orchestrates planner / searcher / synthesizer / fact-checker / writer
sub-agents (agents-as-tools) under a hard step + search budget, producing a cited
report behind a faithfulness gate. Runs fully offline over a committed corpus.
"""

from __future__ import annotations

from research_agent.config import Settings, get_settings
from research_agent.corpus import Corpus
from research_agent.evals import THRESHOLDS, EvalReport, evaluate
from research_agent.manager import ResearchManager
from research_agent.schemas import Budget, Claim, ResearchReport, Source

__version__ = "0.1.0"

__all__ = [
    "THRESHOLDS",
    "Budget",
    "Claim",
    "Corpus",
    "EvalReport",
    "ResearchManager",
    "ResearchReport",
    "Settings",
    "Source",
    "evaluate",
    "get_settings",
    "__version__",
]
