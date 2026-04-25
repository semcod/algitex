from pathlib import Path

def read_todo_file(file: str) -> list:
    todo_path = Path(file)
    if not todo_path.exists():
        raise FileNotFoundError(f'{file} not found')
    return todo_path.read_text().splitlines()

def write_todo_file(file: str, content: str) -> None:
    with open(file, 'w') as f:
        f.write(content)