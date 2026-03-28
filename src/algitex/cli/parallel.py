"""CLI command for parallel execution of algitex tasks."""
import click
from pathlib import Path

@click.command("parallel")
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("--agents", "-n", default=4, help="Number of parallel agents")
@click.option("--tool", "-t", default="aider-mcp", 
              type=click.Choice(["aider-mcp", "claude-code", "ollama"]),
              help="Docker tool to use")
@click.option("--dry-run", is_flag=True, help="Show partition plan without executing")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def parallel(path, agents, tool, dry_run, verbose):
    """Execute tickets in parallel with conflict-free coordination.
    
    This command analyzes the codebase to extract AST regions, partitions
    tickets into non-conflicting groups, and executes them in parallel
    using git worktrees for isolation.
    
    Examples:
        algitex parallel ./my-project --agents 4 --tool aider-mcp
        algitex parallel --dry-run --agents 2
    """
    from algitex.tools.parallel import ParallelExecutor, RegionExtractor, TaskPartitioner
    from algitex.tools.tickets import Tickets
    
    # Convert to absolute path
    project_path = Path(path).resolve()
    
    # Load tickets
    try:
        tickets_mgr = Tickets(str(project_path))
        open_tickets = tickets_mgr.list(status="open")
    except Exception as e:
        click.echo(f"Error loading tickets: {e}", err=True)
        return
    
    if not open_tickets:
        click.echo("No open tickets to execute.")
        return
    
    click.echo(f"\nFound {len(open_tickets)} open tickets")
    
    # Show partition plan
    try:
        extractor = RegionExtractor(str(project_path))
        regions = extractor.extract_all()
        
        if verbose:
            click.echo(f"\nExtracted {len(regions)} code regions:")
            for r in regions[:10]:  # Show first 10
                click.echo(f"  - {r.key} ({r.type.value})")
            if len(regions) > 10:
                click.echo(f"  ... and {len(regions) - 10} more")
        
        partitioner = TaskPartitioner(regions)
        groups = partitioner.partition(
            [t.to_dict() if hasattr(t, 'to_dict') else t for t in open_tickets],
            max_agents=agents,
        )
        
        click.echo(f"\nPartition plan ({len(open_tickets)} tickets → {len(groups)} agents):\n")
        for agent_idx, ticket_ids in groups.items():
            tickets_info = []
            for tid in ticket_ids:
                ticket = next(t for t in open_tickets 
                             if (t.id if hasattr(t, 'id') else t.get('id')) == tid)
                title = ticket.title if hasattr(ticket, 'title') else ticket.get('title', tid)
                tickets_info.append(f"{tid}: {title[:50]}...")
            click.echo(f"  Agent {agent_idx} ({len(ticket_ids)} tickets):")
            for info in tickets_info:
                click.echo(f"    {info}")
                
    except Exception as e:
        click.echo(f"Error during analysis: {e}", err=True)
        return
    
    if dry_run:
        click.echo("\nDry run complete. Use --no-dry-run to execute.")
        return
    
    # Confirm execution
    if not click.confirm(f"\nExecute with {len(groups)} parallel agents using {tool}?"):
        click.echo("Aborted.")
        return
    
    click.echo(f"\nExecuting with {len(groups)} parallel agents ({tool})...\n")
    
    # Execute
    try:
        executor = ParallelExecutor(str(project_path), max_agents=agents)
        results = executor.execute(
            [t.to_dict() if hasattr(t, 'to_dict') else t for t in open_tickets],
            tool=tool
        )
        
        # Report results
        click.echo("\nExecution results:\n")
        for r in results:
            if isinstance(r, str):
                click.echo(f"  {r}")
                continue
                
            icon = "✓" if r.status == "clean" else "✗" if r.status == "semantic_conflict" else "!"
            files = ", ".join(r.files_changed[:3]) if r.files_changed else ""
            if len(r.files_changed) > 3:
                files += f" and {len(r.files_changed) - 3} more"
            
            click.echo(f"  {icon} Agent {r.agent_id}: {r.status}")
            if files:
                click.echo(f"    Files: {files}")
            if r.conflicts:
                click.echo(f"    Conflicts: {', '.join(r.conflicts[:3])}")
            if verbose and r.line_drift_detected:
                click.echo(f"    Line drift detected and handled")
                
    except Exception as e:
        click.echo(f"Error during execution: {e}", err=True)
        return
    
    click.echo("\nParallel execution complete.")
