"""Ticket subcommands for algitex CLI."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def ticket_add(
    title: str = typer.Argument(...),
    priority: str = typer.Option("normal", "--priority", "-p"),
    type: str = typer.Option("task", "--type", "-t"),
):
    """Add a new ticket."""
    from algitex.tools.tickets import Tickets
    ticket = Tickets().add(title, priority=priority, type=type)
    console.print(f"\u2705 Created: [bold]{ticket.id}[/] \u2014 {ticket.title}")


def ticket_list(status: Optional[str] = typer.Option(None, "--status", "-s")) -> None:
    """List tickets."""
    from algitex.tools.tickets import Tickets
    tickets = Tickets().list(status=status)
    if not tickets:
        console.print("No tickets."); return
    table = Table(title="Tickets")
    table.add_column("ID"); table.add_column("Status")
    table.add_column("Priority"); table.add_column("Type"); table.add_column("Title")
    for t in tickets:
        table.add_row(t.id, t.status, t.priority, t.type, t.title)
    console.print(table)


def ticket_board() -> None:
    """Kanban board view."""
    from algitex.tools.tickets import Tickets
    for col, tickets in Tickets().board().items():
        if tickets:
            console.print(f"\n[bold]{col.upper()}[/] ({len(tickets)})")
            for t in tickets:
                console.print(f"  [{t.priority}] {t.id}: {t.title}")
