from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

from algitex.tools.autofix.base import FixResult, Task
from algitex.tools.autofix.batch_logger import BatchLogger
from algitex.tools.ollama import OllamaClient, OllamaService

from .fs_utils import create_backup, preflight_syntax_check
from .models import TaskGroup
from .todo_utils import update_todo_mark_completed


class BatchFixBackend:
    """Backend do optymalizacji fixów przez grupowanie.

    Args:
        base_url: URL do Ollama (domyślnie localhost:11434)
        model: Nazwa modelu (domyślnie auto-detect)
        dry_run: Jeśli True, tylko symulacja
        timeout: Timeout w sekundach
    """

    DEFAULT_TIMEOUT = 300.0
    MAX_FILES_PER_BATCH = 5

    def __init__(self, base_url: str = 'http://localhost:11434', model: Optional[str] = None, dry_run: bool = True, timeout: float = DEFAULT_TIMEOUT, enable_logging: bool = True):
        self.base_url = base_url
        self.model = model
        self.dry_run = dry_run
        self.timeout = timeout
        self.enable_logging = enable_logging
        self._logger = None
        if not dry_run:
            client = OllamaClient(host=base_url, timeout=timeout)
            self.service = OllamaService(client=client)

    def fix_batch(self, tasks: list[Task], max_parallel: int = 3) -> list[FixResult]:
        start_time = time.time()
        if not self.dry_run:
            backup_dir = create_backup()
            print(f'💾 Backup utworzony: {backup_dir}')
            preflight_syntax_check(tasks)
        groups = self._group_tasks(tasks)
        total_groups = len(groups)
        print(f'📦 BatchFix: {len(tasks)} zadań → {total_groups} grup')
        print(f'⚡ Równoległość: {max_parallel} grup na raz\n')
        if self.enable_logging:
            self._logger = BatchLogger(backend='ollama', batch_size=self.MAX_FILES_PER_BATCH, parallel=max_parallel)
            self._logger.set_totals(len(tasks), total_groups)
        else:
            self._logger = None
        print('🔍 Weryfikacja TODO: Sprawdzam które problemy nadal istnieją...')
        tasks = self._verify_tasks_exist(tasks)
        if not tasks:
            print('   ✓ Wszystkie problemy zostały już naprawione!')
            return []
        print(f'   📋 Pozostało {len(tasks)} aktualnych zadań\n')
        results: list[FixResult] = []
        completed = 0
        lock = threading.Lock()

        def process_group_with_progress(group_idx: int, group: TaskGroup) -> list[FixResult]:
            nonlocal completed
            group_results = self._process_group(group, group_idx, total_groups)
            with lock:
                completed += 1
                remaining = total_groups - completed
                elapsed = time.time() - start_time
                avg_time = elapsed / completed if completed > 0 else 0
                eta = avg_time * remaining
                print(f'\n📊 Postęp: {completed}/{total_groups} grup | ETA: {eta / 60:.1f}min')
            return group_results

        with ThreadPoolExecutor(max_workers=max_parallel) as executor:
            futures = {executor.submit(process_group_with_progress, i + 1, group): group for i, group in enumerate(groups)}
            for future in as_completed(futures):
                try:
                    group_results = future.result()
                    results.extend(group_results)
                except Exception as e:
                    group = futures[future]
                    print(f'\n   ✗ Grupa {group.category} failed: {e}')
        elapsed = time.time() - start_time
        print(f'\n✓ BatchFix zakończony: {len(results)} wyników w {elapsed:.1f}s')
        if not self.dry_run:
            update_todo_mark_completed(tasks, results, elapsed)
        if hasattr(self, '_logger') and self._logger:
            log_path = self._logger.finalize()
            print(f'\nLog zapisany: {log_path}')
        return results

    def _group_tasks(self, tasks: list[Task]) -> list[TaskGroup]:
        return []

    def _verify_tasks_exist(self, tasks: list[Task]) -> list[Task]:
        return tasks

    def _process_group(self, group: TaskGroup, group_idx: int, total_groups: int) -> list[FixResult]:
        return []
