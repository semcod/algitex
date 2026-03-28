"""CLI commands for deterministic NLP refactors."""

from __future__ import annotations

from pathlib import Path

import clickmd
from clickmd import command, option, argument
from rich.console import Console
from rich.table import Table

from algitex.nlp import DeadCodeDetector, DocstringShortener, find_duplicate_blocks, sort_imports_in_path


console = Console()


@command()
@option("--path", "-p", default=".", help="File or directory to inspect.")
@option("--fix/--dry-run", default=False, help="Write the shortened docstrings back.")
def nlp_docstrings(path: str, fix: bool) -> None:
    """Shorten verbose docstrings using pattern-based rewriting."""
    shortener = DocstringShortener()
    changes = shortener.fix_path(path, apply=fix)
    _print_docstring_changes(changes, fix=fix)


@command()
@option("--path", "-p", default=".", help="File or directory to inspect.")
@option("--sort", is_flag=True, help="Write import ordering changes back to disk.")
def nlp_imports(path: str, sort: bool) -> None:
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


@command()
@argument("path", default=".")
@option("--min-lines", default=3, type=int, help="Minimum duplicate block size.")
def nlp_duplicates(path: str, min_lines: int) -> None:
    """Detect repeated code blocks with a rolling hash window."""
    duplicates = find_duplicate_blocks(path, min_lines=min_lines)
    if not duplicates:
        console.print("[green]No duplicate code blocks found.[/green]")
        return
    _print_duplicates(duplicates)


@command()
@argument("path", default=".")
def nlp_dead_code(path: str) -> None:
    """Detect top-level functions that are never referenced."""
    detector = DeadCodeDetector()
    results = detector.scan(path)
    if not results:
        console.print("[green]No obvious dead code found.[/green]")
        return
    _print_dead_code(results)


def _print_docstring_changes(changes: list[dict[str, object]], *, fix: bool) -> None:
    table = Table(title="Docstring refactor")
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    table.add_row("Mode", "write" if fix else "preview")
    table.add_row("Files scanned", str(len(changes)))
    console.print(table)


def _print_dead_code(results: list[dict]) -> None:
    table = Table(title="Dead code candidates")
    table.add_column("Function", style="bold")
    table.add_column("File")
    table.add_column("Line")
    for r in results[:10]:
        table.add_row(r["name"], str(r["file"]), str(r["line"]))
    console.print(table)


def _print_duplicates(duplicates: list[dict]) -> None:
    table = Table(title="Duplicate blocks")
    table.add_column("Hash", style="dim")
    table.add_column("Lines")
    table.add_column("Locations")
    for d in duplicates[:10]:
        locs = " | ".join(f"{p['file']}:{p['line']}" for p in d["positions"][:3])
        table.add_row(d["hash"][:8], str(d["line_count"]), locs)
    console.print(table)
    if len(duplicates) > 10:
        console.print(f"[dim]... and {len(duplicates) - 10} more[/dim]")
