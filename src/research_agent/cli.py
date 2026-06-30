"""Command-line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from research_agent.config import get_settings
from research_agent.evals import THRESHOLDS, evaluate, write_markdown
from research_agent.manager import ResearchManager
from research_agent.report import render_report

console = Console()


def _cmd_research(args) -> int:
    report = ResearchManager(get_settings()).research(args.question)
    console.print(f"[bold]Q:[/] {report.question}")
    console.print(
        f"[dim]{report.searches_used} searches · {report.steps_used} steps · {report.n_claims} claims[/]"
    )
    console.print(f"\n[bold]Summary[/]\n{report.summary}\n")
    console.print("[bold]Sources[/]")
    for c in report.citations:
        console.print(f"  [cyan]{c.source_id}[/] — {c.title}")
    if args.out:
        Path(args.out).write_text(render_report(report) + "\n")
        console.print(f"[dim]wrote report to {args.out}[/]")
    return 0


def _cmd_eval(args) -> int:
    report = evaluate(get_settings())
    table = Table(title="deep-research-agent · evaluation")
    table.add_column("metric")
    table.add_column("value", justify="right")
    table.add_column("threshold", justify="right")
    table.add_column("", justify="center")
    for metric, threshold in THRESHOLDS.items():
        value = report.aggregate.get(metric, 0.0)
        table.add_row(metric, f"{value:.3f}", f"{threshold:.2f}", "✅" if value >= threshold else "❌")
    table.add_row("avg_searches", f"{report.aggregate['avg_searches']:.2f}", "—", "")
    table.add_row("avg_claims", f"{report.aggregate['avg_claims']:.2f}", "—", "")
    console.print(table)
    if args.report:
        write_markdown(report, Path(args.report))
        console.print(f"[dim]wrote report to {args.report}[/]")
    if report.passed():
        console.print(f"[bold green]GATE PASSED[/] over {report.n} questions")
        return 0
    console.print(f"[bold red]GATE FAILED[/]: {', '.join(report.failures())}")
    return 1


def _cmd_demo(_args) -> int:
    _cmd_research(argparse.Namespace(question="How do you evaluate a large language model?", out=None))
    console.rule("evaluation")
    return _cmd_eval(argparse.Namespace(report=None))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="research-agent", description="Manager-pattern research agent.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_res = sub.add_parser("research", help="Answer a question with a cited report.")
    p_res.add_argument("question")
    p_res.add_argument("--out", default=None, help="Write the report markdown to this path.")
    p_res.set_defaults(func=_cmd_research)

    p_eval = sub.add_parser("eval", help="Run the evaluation suite + gate.")
    p_eval.add_argument("--report", default=None, help="Write a markdown report to this path.")
    p_eval.set_defaults(func=_cmd_eval)

    sub.add_parser("demo", help="Run a sample research + the eval.").set_defaults(func=_cmd_demo)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
