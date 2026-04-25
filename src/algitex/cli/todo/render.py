from algitex.todo import summarize_tasks
from rich.table import Table
from rich.console import Console
import re

console = Console()

def render_todo_stats(file: str, tasks) -> None:
    summary = summarize_tasks(tasks)
    tier_table = Table(title=f'TODO Stats: {file}')
    tier_table.add_column('Tier', style='bold')
    tier_table.add_column('Count', justify='right')
    tier_table.add_column('Share', justify='right')
    for tier, label in (('algorithm', 'Algorithm'), ('micro', 'Small LLM'), ('big', 'Big LLM')):
        count = summary.tier_counts.get(tier, 0)
        share = f'{summary.tier_percent(tier)}%'
        tier_table.add_row(label, str(count), share)
    console.print(tier_table)

    category_table = Table(title='Top Categories')
    category_table.add_column('Category', style='bold')
    category_table.add_column('Count', justify='right')
    for category, count in summary.top_categories(limit=12):
        category_table.add_row(category, str(count))
    console.print(category_table)

    console.print(
        rf'\[bold\]Total:\/[/] {summary.total} | '
        f'Algorithm: {summary.algorithmic} | Micro: {summary.micro} | Big: {summary.big}'
    )