"""Render a single research report as markdown."""

from __future__ import annotations

from research_agent.schemas import ResearchReport


def render_report(report: ResearchReport) -> str:
    lines = [
        f"# Research: {report.question}",
        "",
        "## Summary",
        report.summary,
        "",
        "## Findings (each traced to a source)",
    ]
    lines += [f"- {claim.text} `[{claim.source_id}]`" for claim in report.claims]
    lines += ["", "## Sources"]
    lines += [f"- `{c.source_id}` — {c.title}" for c in report.citations]
    lines += [
        "",
        f"_searched {report.searches_used} time(s) across {len(report.sub_queries)} queries; "
        f"{report.steps_used} sub-agent steps._",
    ]
    return "\n".join(lines)
