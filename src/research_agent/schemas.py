"""Typed domain model + the research budget."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, Field


@dataclass
class Budget:
    """A hard ceiling on work. The manager checks this before every action."""

    max_steps: int
    max_searches: int
    steps_used: int = 0
    searches_used: int = 0

    def can_step(self) -> bool:
        return self.steps_used < self.max_steps

    def can_search(self) -> bool:
        return self.searches_used < self.max_searches and self.can_step()

    def spend_step(self) -> None:
        self.steps_used += 1

    def spend_search(self) -> None:
        self.searches_used += 1
        self.steps_used += 1

    @property
    def exhausted(self) -> bool:
        return not self.can_step()


class Source(BaseModel):
    id: str
    title: str
    text: str


class Claim(BaseModel):
    text: str
    source_id: str


class Citation(BaseModel):
    source_id: str
    title: str


class ResearchReport(BaseModel):
    question: str
    sub_queries: list[str] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    summary: str = ""
    steps_used: int = 0
    searches_used: int = 0

    @property
    def n_claims(self) -> int:
        return len(self.claims)

    def cited_ids(self) -> set[str]:
        return {c.source_id for c in self.claims}
