from algitex.todo.fixer import mark_tasks_completed
from algitex.tools.todo_parser import TodoParser

from algitex.tools.autofix.base import FixResult, Task


def update_todo_mark_completed(tasks: list[Task], results: list[FixResult], elapsed: float) -> None:
    """Oznacz naprawione zadania jako zrobione w TODO.md."""
    completed_task_ids = set()
    for r in results:
        if r.success:
            completed_task_ids.add(r.task_id)
    if not completed_task_ids:
        print('\n⚠️  Żadne zadania nie zostały naprawione - TODO.md nie zostanie zaktualizowane')
        return
    parser = TodoParser('TODO.md')
    todo_tasks = parser.parse()
    completed_todo_tasks = []
    print(f'     🔍 Szukam {len(completed_task_ids)} zadań w {len(todo_tasks)} taskach z TODO.md')
    for task in todo_tasks:
        if task.id in completed_task_ids:
            completed_todo_tasks.append(task)
            print(f'       ✓ Znaleziono do oznaczenia: {task.id} - {task.description[:50]}...')
    if not completed_todo_tasks:
        print(f'       ⚠️  Przykłady completed_task_ids: {list(completed_task_ids)[:5]}')
        print(f'       ⚠️  Przykłady task.id z TODO: {[t.id for t in todo_tasks[:5]]}')
    if completed_todo_tasks:
        marked = mark_tasks_completed('TODO.md', completed_todo_tasks)
        print(f'\n📝 Zaktualizowano TODO.md: {marked}/{len(completed_task_ids)} zadań oznaczonych jako ukończone')
    else:
        print('\n⚠️  Nie znaleziono zadań w TODO.md do oznaczenia (może format jest inny)')
