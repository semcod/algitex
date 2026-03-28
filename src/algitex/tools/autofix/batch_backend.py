"""BatchFix backend — grupowanie i optymalizacja podobnych zadań.

Zamiast wykonywać każde zadanie osobno (N API calls),
BatchFix grupuje podobne problemy i wykonuje je za jednym razem (1 API call).

Przykład:
    # 10 zadań "String concatenation" w różnych plikach
    # Normalnie: 10 × 30s = 300s
    # BatchFix: 1 × 60s = 60s (5× szybciej!)
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from algitex.tools.autofix.base import FixResult, Task
from algitex.tools.ollama import OllamaService, OllamaClient


@dataclass
class TaskGroup:
    """Grupa podobnych zadań do batch fix."""
    category: str
    pattern: str
    tasks: list[Task]
    files: list[str]


class BatchFixBackend:
    """Backend do optymalizacji fixów przez grupowanie.
    
    Args:
        base_url: URL do Ollama (domyślnie localhost:11434)
        model: Nazwa modelu (domyślnie auto-detect)
        dry_run: Jeśli True, tylko symulacja
        timeout: Timeout w sekundach
    """
    
    DEFAULT_TIMEOUT = 120.0
    MAX_FILES_PER_BATCH = 5
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: Optional[str] = None,
        dry_run: bool = True,
        timeout: float = DEFAULT_TIMEOUT
    ):
        self.base_url = base_url
        self.model = model
        self.dry_run = dry_run
        self.timeout = timeout
        
        if not dry_run:
            client = OllamaClient(host=base_url, timeout=timeout)
            self.service = OllamaService(client=client)
    
    def fix_batch(self, tasks: list[Task]) -> list[FixResult]:
        """Wykonaj wszystkie zadania w batch.
        
        Args:
            tasks: Lista zadań do wykonania
            
        Returns:
            Lista wyników dla każdego zadania
        """
        start_time = time.time()
        
        # Grupuj zadania według kategorii
        groups = self._group_tasks(tasks)
        print(f"📦 BatchFix: {len(tasks)} zadań → {len(groups)} grup")
        
        results = []
        for group in groups:
            group_results = self._process_group(group)
            results.extend(group_results)
        
        elapsed = time.time() - start_time
        print(f"✓ BatchFix zakończony: {len(results)} wyników w {elapsed:.1f}s")
        return results
    
    def _group_tasks(self, tasks: list[Task]) -> list[TaskGroup]:
        """Grupuj zadania według podobieństwa."""
        # Kategorie które można batchować
        BATCH_CATEGORIES = {
            "string_concat": [
                "string concatenation",
                "can be converted to f-string",
                "f-string"
            ],
            "magic_number": [
                "magic number",
                "use named constant"
            ],
            "unused_import": [
                "unused import",
                "unused"
            ],
            "missing_return": [
                "missing return type",
                "return type"
            ],
            "docstring": [
                "llm-style docstring",
                "docstring"
            ],
            "module_block": [
                "module execution block",
                "if __name__"
            ]
        }
        
        groups = defaultdict(list)
        
        for task in tasks:
            desc_lower = task.description.lower()
            assigned = False
            
            for category, patterns in BATCH_CATEGORIES.items():
                if any(p in desc_lower for p in patterns):
                    groups[category].append(task)
                    assigned = True
                    break
            
            if not assigned:
                # Zadania których nie można batchować — każde osobno
                groups[f"single_{task.id}"].append(task)
        
        # Podziel duże grupy na mniejsze batch-e
        result = []
        for category, task_list in groups.items():
            if category.startswith("single_"):
                result.append(TaskGroup(
                    category="single",
                    pattern="individual",
                    tasks=task_list,
                    files=[t.file_path for t in task_list]
                ))
            else:
                # Podziel na grupy max 5 plików
                for i in range(0, len(task_list), self.MAX_FILES_PER_BATCH):
                    batch = task_list[i:i + self.MAX_FILES_PER_BATCH]
                    result.append(TaskGroup(
                        category=category,
                        pattern=BATCH_CATEGORIES[category][0],
                        tasks=batch,
                        files=[t.file_path for t in batch]
                    ))
        
        return result
    
    def _process_group(self, group: TaskGroup) -> list[FixResult]:
        """Przetwórz grupę zadań."""
        start = time.time()
        
        print(f"\n  🔧 {group.category}: {len(group.tasks)} plików")
        for f in group.files[:3]:
            print(f"     • {Path(f).name}")
        if len(group.files) > 3:
            print(f"     ... i {len(group.files) - 3} więcej")
        
        if self.dry_run:
            return [
                FixResult(
                    task_id=t.id,
                    task_description=t.description,
                    success=True,
                    method=f"batch-{group.category}-dry-run",
                    time_ms=0,
                    file_path=t.file_path
                )
                for t in group.tasks
            ]
        
        # Wykonaj batch fix
        if group.category == "single":
            return self._fix_individual(group)
        else:
            return self._fix_batch_group(group)
    
    def _fix_batch_group(self, group: TaskGroup) -> list[FixResult]:
        """Fix całej grupy za jednym razem."""
        start = time.time()
        
        try:
            # Przygotuj prompt batch
            prompt = self._build_batch_prompt(group)
            
            # Wywołaj LLM raz dla całej grupy
            model = self._ensure_model()
            response = self._call_llm(prompt, model)
            
            # Parsuj odpowiedź i zastosuj fixy
            fixes = self._parse_batch_response(response, group)
            
            elapsed = time.time() - start
            print(f"     ✓ Batch fix: {len(fixes)} plików w {elapsed:.1f}s")
            
            return [
                FixResult(
                    task_id=t.id,
                    task_description=t.description,
                    success=fixes.get(t.file_path, False),
                    method=f"batch-{group.category}",
                    time_ms=elapsed * 1000 / len(group.tasks),
                    file_path=t.file_path
                )
                for t in group.tasks
            ]
            
        except Exception as e:
            print(f"     ✗ Batch fix failed: {e}")
            return [
                FixResult(
                    task_id=t.id,
                    task_description=t.description,
                    success=False,
                    method=f"batch-{group.category}",
                    time_ms=(time.time() - start) * 1000,
                    error=str(e),
                    file_path=t.file_path
                )
                for t in group.tasks
            ]
    
    def _fix_individual(self, group: TaskGroup) -> list[FixResult]:
        """Fix pojedynczych zadań których nie można batchować."""
        results = []
        for task in group.tasks:
            # Fallback do standardowego fix
            print(f"     • Individual fix: {Path(task.file_path).name}")
            result = self._fix_single(task)
            results.append(result)
        return results
    
    def _fix_single(self, task: Task) -> FixResult:
        """Fix pojedynczego zadania."""
        start = time.time()
        
        try:
            model = self._ensure_model()
            success = self.service.auto_fix_file(
                task.file_path,
                task.description,
                task.line_number,
                model
            )
            
            return FixResult(
                task_id=task.id,
                task_description=task.description,
                success=success,
                method="individual",
                time_ms=(time.time() - start) * 1000,
                file_path=task.file_path
            )
        except Exception as e:
            return FixResult(
                task_id=task.id,
                task_description=t.description,
                success=False,
                method="individual",
                time_ms=(time.time() - start) * 1000,
                error=str(e),
                file_path=task.file_path
            )
    
    def _build_batch_prompt(self, group: TaskGroup) -> str:
        """Zbuduj prompt dla batch fix."""
        files_content = []
        for task in group.tasks:
            try:
                content = Path(task.file_path).read_text()
                files_content.append(f"""
=== FILE: {task.file_path} ===
Line {task.line_number}: {task.description}

{content}
""")
            except Exception:
                continue
        
        return f"""Fix the following {group.pattern} issues in multiple files.

{''.join(files_content)}

Apply fixes to ALL files. Return the complete fixed content for each file.
Format:
=== FIXED: <filepath> ===
<fixed content>
"""
    
    def _call_llm(self, prompt: str, model: str) -> str:
        """Wywołaj LLM."""
        response = self.service.client.generate(
            prompt=prompt,
            model=model,
            temperature=0.3
        )
        return response.content
    
    def _parse_batch_response(self, response: str, group: TaskGroup) -> dict[str, bool]:
        """Parsuj odpowiedź batch i zastosuj fixy."""
        results = {}
        
        # Parsuj sekcje === FIXED: path ===
        import re
        pattern = r'=== FIXED: (.+?) ===\n(.*?)(?==== FIXED:|$)'
        matches = re.findall(pattern, response, re.DOTALL)
        
        for filepath, fixed_content in matches:
            filepath = filepath.strip()
            try:
                Path(filepath).write_text(fixed_content.strip())
                results[filepath] = True
            except Exception:
                results[filepath] = False
        
        # Oznacz pliki bez odpowiedzi jako failed
        for task in group.tasks:
            if task.file_path not in results:
                results[task.file_path] = False
        
        return results
    
    def _ensure_model(self) -> Optional[str]:
        """Wybierz model."""
        if self.model:
            return self.model
        
        models = self.service.get_recommended_models()
        if models:
            self.model = models[0]
            return self.model
        return None
