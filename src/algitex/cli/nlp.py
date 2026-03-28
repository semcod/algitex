"""CLI commands for deterministic NLP refactors."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from algitex.nlp import DeadCodeDetector, DocstringShortener, find_duplicate_blocks, sort_imports_in_path


console = Console()
nlp_app = typer.Typer(help="Deterministic NLP refactor helpers.")


@nlp_app.command("docstrings")
def nlp_docstrings(
    path: str = typer.Option(".", "--path", "-p", help="File or directory to inspect."),
    fix: bool = typer.Option(False, "--fix/--dry-run", help="Write the shortened docstrings back."),
) -> None:
    """Shorten verbose docstrings using pattern-based rewriting."""
    shortener = DocstringShortener()
    changes = shortener.fix_path(path, apply=fix)
    _print_docstring_changes(changes, fix=fix)


@nlp_app.command("imports")
def nlp_imports(
    path: str = typer.Option(".", "--path", "-p", help="File or directory to inspect."),
    sort: bool = typer.Option(False, "--sort", help="Write import ordering changes back to disk."),
) -> None:
    """Sort imports with isort when available, otherwise use a deterministic fallback."""
    stats = sort_imports_in_path(path, apply=sort)
    table = Table(title="Import organization")
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    table.add_row("Files scanned", str(stats["files"]))
    table.add_row("Files changed", str(stats["changed"]))
    table.add_row("Errors", str(stats["errors"]))
    table.add_row("Mode", "write" if sort else "preview")
    console.print(table)


@nlp_app.command("dead-code")
def nlp_dead_code(
    path: str = typer.Option(".", "--path", "-p", help="Project root to scan."),
) -> None:
    """Detect top-level functions that are never referenced."""
    detector = DeadCodeDetector()
    results = detector.scan(path)
    if not results:
        console.print("[green]No obvious dead code found.[/green]")
        raise typer.Exit()
    _print_dead_code(results)


@nlp_app.command("duplicates")
def nlp_duplicates(
    path: str = typer.Option(".", "--path", "-p", help="Project root to scan."),
    min_lines: int = typer.Option(3, "--min-lines", min=2, help="Minimum duplicate block size."),
) -> None:
    """Detect repeated code blocks with a rolling hash window."""
    duplicates = find_duplicate_blocks(path, min_lines=min_lines)
    if not duplicates:
        console.print("[green]No duplicate code blocks found.[/green]")
        raise typer.Exit()
    _print_duplicates(duplicates)


def _print_docstring_changes(changes: list[dict[str, object]], *, fix: bool) -> None:
    table = Table(title="Docstring refactor")
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    table.add_row("Mode", "write" if fix else "preview")
    table.add_row("Changes", str(len(changes)))
    console.print(table)

    if not changes:
        return

    preview = Table(title="Docstring changes")
    preview.add_column("File")
    preview.add_column("Line", justify="right")
    preview.add_column("Node")
    preview.add_column("Before")
    preview.add_column("After")
    for change in changes[:10]:
        preview.add_row(
            _shorten(str(change["file"])),
            str(change["line"]),
            str(change["node_type"]),
            _shorten(str(change["before"]), 50),
            _shorten(str(change["after"]), 50),
        )
    console.print(preview)


def _print_dead_code(results: list[dict[str, object]]) -> None:
    table = Table(title="Dead code candidates")
    table.add_column("Name", style="bold")
    table.add_column("File")
    table.add_column("Line", justify="right")
    table.add_column("Reason")
    for item in results[:100]:
        table.add_row(
            str(item["name"]),
            _shorten(str(item["file"])),
            str(item["line"]),
            str(item["reason"]),
        )
    console.print(table)


def _print_duplicates(results: list[dict[str, object]]) -> None:
    table = Table(title="Duplicate blocks")
    table.add_column("Lines", justify="right")
    table.add_column("Occurrences", justify="right")
    table.add_column("Sample file")
    table.add_column("Sample line", justify="right")
    table.add_column("Preview")
    for item in results[:50]:
        occurrences = item["occurrences"]
        first = occurrences[0]
        preview = str(item["text"]).splitlines()[0] if item["text"] else ""
        table.add_row(
            str(item["lines"]),
            str(len(occurrences)),
            _shorten(str(first["file"])),
            str(first["line"]),
            _shorten(preview, 60),
        )
    console.print(table)


def _shorten(text: str, limit: int = 72) -> str:
    if len(text) <= limit:
        return text
    return f"{text[: limit - 1]}…"


__all__ = ["nlp_app", "nlp_dead_code", "nlp_docstrings", "nlp_duplicates", "nlp_imports"]
