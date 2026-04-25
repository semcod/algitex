from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil

from algitex.tools.autofix.base import Task


def create_backup() -> str:
    """Utwórz backup wszystkich plików Python przed batch."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path('.algitex/backups/batch_' + timestamp)
    backup_dir.mkdir(parents=True, exist_ok=True)
    py_files = list(Path('.').rglob('*.py'))
    py_files = [f for f in py_files if not str(f).startswith('.')]
    for py_file in py_files:
        try:
            dest = backup_dir / py_file
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(py_file, dest)
        except Exception:
            pass
    return str(backup_dir)


def preflight_syntax_check(tasks: list[Task]) -> None:
    """Sprawdź składnię wszystkich plików Python przed batch."""
    print('🔍 Pre-flight: Sprawdzanie składni plików...')
    py_files = {task.file_path for task in tasks if task.file_path.endswith('.py')}
    if not py_files:
        print('   ℹ️  Brak plików Python do sprawdzenia')
        return

    errors: list[str] = []
    for filepath in sorted(py_files):
        try:
            path = Path(filepath)
            if not path.exists():
                continue
            import py_compile
            import tempfile

            with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as tmp:
                tmp_path = Path(tmp.name)
            try:
                py_compile.compile(str(path), doraise=True)
            finally:
                if tmp_path.exists():
                    tmp_path.unlink(missing_ok=True)
        except Exception as e:
            errors.append(f'{filepath}: {e}')

    if errors:
        print('   ⚠️  Wykryto błędy składni:')
        for err in errors:
            print(f'      - {err}')
