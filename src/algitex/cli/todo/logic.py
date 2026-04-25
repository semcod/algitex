from typing import List
import re

Task = dict[str, str]

def parse_todo_tasks(todo_lines: List[str]) -> List[Task]:
    tasks = []
    for line in todo_lines:
        match = re.match(r'- \[([ x])\] (.+):(\d+) - (.+)', line)
        if match:
            status, filepath, lineno, message = match.groups()
            tasks.append({
                'status': status,
                'file': filepath,
                'line': int(lineno),
                'message': message,
                'original_line': line
            })
    return tasks

def validate_task(task: Task) -> bool:
    filepath = task['file']
    try:
        path = Path(filepath)
        if not path.exists():
            return False
        lines = path.read_text().splitlines()
        line_no = task['line'] - 1
        if line_no >= len(lines):
            return False
        line_content = lines[line_no]
        msg_lower = task['message'].lower()
        is_valid = True
        if 'unused' in msg_lower and 'import' in msg_lower:
            if 'import' not in line_content:
                is_valid = False
        elif 'f-string' in msg_lower or 'string concatenation' in msg_lower:
            if '"' not in line_content and "'" not in line_content:
                is_valid = False
        elif 'magic number' in msg_lower:
            if not re.search(r'\b\d+\b', line_content):
                is_valid = False
        return is_valid
    except Exception as e:
        print(f'[yellow]⚠️  Error checking {filepath}: {e}[/]')
        return True