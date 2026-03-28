"""Workflow subcommands for algitex CLI."""

from __future__ import annotations

import typer
from rich.console import Console

console = Console()


def workflow_run(
    path: str = typer.Argument(..., help="Path to .md workflow"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Execute a Propact Markdown workflow."""
    from algitex.project import Project
    p = Project(".")
    with console.status(f"Running workflow {path}..."):
        result = p.run_workflow(path, dry_run=dry_run)
    if result["success"]:
        console.print(f"\u2705 Workflow complete: {result['steps_done']} steps, ${result['total_cost_usd']:.4f}")
    else:
        console.print(f"\u274c Workflow failed: {result.get('steps_failed', 0)} steps failed")
        for err in result.get("errors", []):
            console.print(f"  {err}")


def workflow_validate(path: str = typer.Argument(...)):
    """Check a Propact workflow for errors."""
    from algitex.propact import Workflow
    wf = Workflow(path)
    errors = wf.validate()
    if errors:
        console.print(f"\u274c {len(errors)} errors:")
        for e in errors:
            console.print(f"  {e}")
    else:
        steps = wf.parse()
        console.print(f"\u2705 Valid workflow: {len(steps)} steps")
