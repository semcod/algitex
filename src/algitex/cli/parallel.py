"""CLI command for parallel execution of algitex tasks."""
import typer
from pathlib import Path
from rich.console import Console

console = Console()


def parallel(
    path: str = typer.Argument(".", help="Path to project"),
    agents: int = typer.Option(4, "--agents", "-n", help="Number of parallel agents"),
    tool: str = typer.Option("aider-mcp", "--tool", "-t", help="Docker tool to use"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show partition plan without executing"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Execute tickets in parallel with conflict-free coordination."""
    from algitex.tools.parallel import ParallelExecutor, RegionExtractor, TaskPartitioner
    from algitex.tools.tickets import Tickets
    
    project_path = Path(path).resolve()
    
    try:
        tickets_mgr = Tickets(str(project_path))
        open_tickets = tickets_mgr.list(status="open")
    except Exception as e:
        console.print(f"[red]Error loading tickets: {e}[/red]")
        return
    
    if not open_tickets:
        console.print("[yellow]No open tickets to execute.[/yellow]")
        return
    
    console.print(f"\n[green]Found {len(open_tickets)} open tickets[/green]")
    
    try:
        extractor = RegionExtractor(str(project_path))
        regions = extractor.extract_all()
        
        if verbose:
            console.print(f"\nExtracted {len(regions)} code regions:")
            for r in regions[:10]:
                console.print(f"  - {r.key} ({r.type.value})")
            if len(regions) > 10:
                console.print(f"  ... and {len(regions) - 10} more")
        
        partitioner = TaskPartitioner(regions)
        groups = partitioner.partition(
            [t.to_dict() if hasattr(t, "to_dict") else t for t in open_tickets],
            max_agents=agents,
        )
        
        console.print(f"\nPartition plan ({len(open_tickets)} tickets → {len(groups)} agents):\n")
        for agent_idx, ticket_ids in groups.items():
            tickets_info = []
            for tid in ticket_ids:
                ticket = next(t for t in open_tickets 
                             if (t.id if hasattr(t, "id") else t.get("id")) == tid)
                title = ticket.title if hasattr(ticket, "title") else ticket.get("title", tid)
                tickets_info.append(f"{tid}: {title[:50]}...")
            console.print(f"  Agent {agent_idx} ({len(ticket_ids)} tickets):")
            for info in tickets_info:
                console.print(f"    {info}")
                
    except Exception as e:
        console.print(f"[red]Error during analysis: {e}[/red]")
        return
    
    if dry_run:
        console.print("\n[yellow]Dry run complete. Remove --dry-run to execute.[/yellow]")
        return
    
    if not typer.confirm(f"\nExecute with {len(groups)} parallel agents using {tool}?"):
        console.print("[yellow]Aborted.[/yellow]")
        return
    
    console.print(f"\nExecuting with {len(groups)} parallel agents ({tool})...\n")
    
    try:
        executor = ParallelExecutor(str(project_path), max_agents=agents)
        results = executor.execute(
            [t.to_dict() if hasattr(t, "to_dict") else t for t in open_tickets],
            tool=tool
        )
        
        console.print("\nExecution results:\n")
        for r in results:
            if isinstance(r, str):
                console.print(f"  {r}")
                continue
                
            icon = "✓" if r.status == "clean" else "✗" if r.status == "semantic_conflict" else "!"
            files = ", ".join(r.files_changed[:3]) if r.files_changed else ""
            if len(r.files_changed) > 3:
                files += f" and {len(r.files_changed) - 3} more"
            
            console.print(f"  {icon} Agent {r.agent_id}: {r.status}")
            if files:
                console.print(f"    Files: {files}")
            if r.conflicts:
                console.print(f"    Conflicts: {', '.join(r.conflicts[:3])}")
            if verbose and r.line_drift_detected:
                console.print("    Line drift detected and handled")
                
    except Exception as e:
        console.print(f"[red]Error during execution: {e}[/red]")
        return
    
    console.print("\n[green]Parallel execution complete.[/green]")
