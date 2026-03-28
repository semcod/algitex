"""BatchFix backend — grupowanie i optymalizacja podobnych zadań.

Zamiast wykonywać każde zadanie osobno (N API calls),
BatchFix grupuje podobne problemy i wykonuje je za jednym razem (1 API call).

Przykład:
    # 10 zadań "String concatenation" w różnych plikach
    # Normalnie: 10 × 30s = 300s
    # BatchFix: 1 × 60s = 60s (5× szybciej!)
"""

from __future__ import annotations

import sys
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from algitex.tools.autofix.base import FixResult, Task
from algitex.todo.fixer import mark_tasks_completed
from algitex.tools.ollama import OllamaService, OllamaClient
from algitex.tools.autofix.batch_logger import BatchLogger


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
    
    DEFAULT_TIMEOUT = 300.0  # 5 minut - większe pliki potrzebują więcej czasu
    MAX_FILES_PER_BATCH = 5
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: Optional[str] = None,
        dry_run: bool = True,
        timeout: float = DEFAULT_TIMEOUT,
        enable_logging: bool = True
    ):
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
        """Wykonaj wszystkie zadania w batch z równoległym przetwarzaniem.
        
        Args:
            tasks: Lista zadań do wykonania
            max_parallel: Liczba równoległych grup (default: 3)
            
        Returns:
            Lista wyników dla każdego zadania
        """
        start_time = time.time()
        
        # Auto-backup przed rozpoczęciem (jeśli nie dry_run)
        if not self.dry_run:
            backup_dir = self._create_backup()
            print(f"💾 Backup utworzony: {backup_dir}")
        
        # Pre-flight: sprawdź składnię wszystkich plików Python
        if not self.dry_run:
            self._preflight_syntax_check(tasks)
        
        # Grupuj zadania według kategorii
        groups = self._group_tasks(tasks)
        total_groups = len(groups)
        print(f"📦 BatchFix: {len(tasks)} zadań → {total_groups} grup")
        print(f"⚡ Równoległość: {max_parallel} grup na raz\n")
        
        # Inicjalizacja loggera markdown (po grupowaniu, gdy znamy total_groups)
        if self.enable_logging:
            self._logger = BatchLogger(backend="ollama", batch_size=self.MAX_FILES_PER_BATCH, parallel=max_parallel)
            self._logger.set_totals(len(tasks), total_groups)
        else:
            self._logger = None
        
        # Weryfikacja: sprawdź które zadania są nadal aktualne
        print("🔍 Weryfikacja TODO: Sprawdzam które problemy nadal istnieją...")
        tasks = self._verify_tasks_exist(tasks)
        if not tasks:
            print("   ✓ Wszystkie problemy zostały już naprawione!")
            return []
        print(f"   📋 Pozostało {len(tasks)} aktualnych zadań\n")
        
        results = []
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
                print(f"\n📊 Postęp: {completed}/{total_groups} grup | ETA: {eta/60:.1f}min")
            return group_results
        
        # Równoległe przetwarzanie grup
        with ThreadPoolExecutor(max_workers=max_parallel) as executor:
            futures = {
                executor.submit(process_group_with_progress, i+1, group): group 
                for i, group in enumerate(groups)
            }
            
            for future in as_completed(futures):
                try:
                    group_results = future.result()
                    results.extend(group_results)
                except Exception as e:
                    group = futures[future]
                    print(f"\n   ✗ Grupa {group.category} failed: {e}")
        
        elapsed = time.time() - start_time
        print(f"\n✓ BatchFix zakończony: {len(results)} wyników w {elapsed:.1f}s")
        
        # Aktualizacja TODO.md - oznacz naprawione zadania jako zrobione
        if not self.dry_run:
            self._update_todo_mark_completed(tasks, results, elapsed)
        
        # Zapisz log markdown
        if hasattr(self, '_logger') and self._logger:
            log_path = self._logger.finalize()
            print(f"\nLog zapisany: {log_path}")
        
        return results
    
    def _update_todo_mark_completed(self, tasks: list[Task], results: list[FixResult], elapsed: float) -> None:
        """Oznacz naprawione zadania jako zrobione w TODO.md."""
        from algitex.todo.fixer import TodoTask, parse_todo
        
        # Znajdź zadania które zostały naprawione (success=True)
        completed_task_ids = set()
        for r in results:
            if r.success:
                # Dodaj ID zadania do listy ukończonych
                completed_task_ids.add(r.task_id)
        
        if not completed_task_ids:
            print("\n⚠️  Żadne zadania nie zostały naprawione - TODO.md nie zostanie zaktualizowane")
            return
        
        # Konwertuj Task (z autofix) na TodoTask (z fixer)
        todo_tasks = parse_todo("TODO.md")
        completed_todo_tasks = []
        
        print(f"     🔍 Szukam {len(completed_task_ids)} zadań w {len(todo_tasks)} taskach z TODO.md")
        
        for task in todo_tasks:
            if task.id in completed_task_ids:
                completed_todo_tasks.append(task)
                print(f"       ✓ Znaleziono do oznaczenia: {task.id} - {task.description[:50]}...")
        
        if not completed_todo_tasks:
            # Debug: pokaż przykłady ID które nie pasują
            print(f"       ⚠️  Przykłady completed_task_ids: {list(completed_task_ids)[:5]}")
            print(f"       ⚠️  Przykłady task.id z TODO: {[t.id for t in todo_tasks[:5]]}")
        
        if completed_todo_tasks:
            marked = mark_tasks_completed("TODO.md", completed_todo_tasks)
            print(f"\n📝 Zaktualizowano TODO.md: {marked}/{len(completed_task_ids)} zadań oznaczonych jako ukończone")
        else:
            print(f"\n⚠️  Nie znaleziono zadań w TODO.md do oznaczenia (może format jest inny)")
    
    def _create_backup(self) -> str:
        """Utwórz backup wszystkich plików Python przed batch."""
        from datetime import datetime
        import shutil
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(f".algitex/backups/batch_{timestamp}")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Znajdź wszystkie pliki .py w projekcie
        py_files = list(Path(".").rglob("*.py"))
        py_files = [f for f in py_files if not str(f).startswith(".")]
        
        for py_file in py_files:
            try:
                dest = backup_dir / py_file
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(py_file, dest)
            except Exception:
                pass  # Pomijamy pliki których nie można skopiować
        
        return str(backup_dir)
    
    def _preflight_syntax_check(self, tasks: list[Task]) -> None:
        """Sprawdź składnię wszystkich plików Python przed batch."""
        print("🔍 Pre-flight: Sprawdzanie składni plików...")
        
        # Znajdź unikalne pliki Python
        py_files = set()
        for task in tasks:
            if task.file_path.endswith('.py'):
                py_files.add(task.file_path)
        
        if not py_files:
            print("   ℹ️  Brak plików Python do sprawdzenia")
            return
        
        errors = []
        for filepath in sorted(py_files):
            try:
                path = Path(filepath)
                if not path.exists():
                    continue
                    
                # Sprawdź składnię przez py_compile
                import py_compile
                import tempfile
                import os
                
                # Kopiuj do temp i sprawdź
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
                    tmp.write(path.read_text())
                    tmp_path = tmp.name
                
                try:
                    py_compile.compile(tmp_path, doraise=True)
                finally:
                    os.unlink(tmp_path)
                    
            except py_compile.PyCompileError as e:
                errors.append(f"   ✗ {filepath}: {e}")
            except Exception as e:
                errors.append(f"   WARN {filepath}: {e}")
        
        if errors:
            print("\n".join(errors[:5]))  # Pokaż max 5 błędów
            if len(errors) > 5:
                print(f"   ... i {len(errors) - 5} wiecej bledow")
            print("\n⚠️  Znaleziono błędy składniowe! Napraw je przed batch fix.")
            # Nie przerywamy
        else:
            print(f"   ✓ Sprawdzono {len(py_files)} plików - brak błędów składniowych")
    
    def _verify_tasks_exist(self, tasks: list[Task]) -> list[Task]:
        """Sprawdź które zadania nadal istnieją w kodzie (nie są już naprawione)."""
        import py_compile
        import tempfile
        import os
        
        verified = []
        for task in tasks:
            filepath = task.file_path
            try:
                path = Path(filepath)
                if not path.exists():
                    continue  # Plik nie istnieje - zadanie nieaktualne
                
                # Sprawdź czy problem nadal występuje
                content = path.read_text()
                
                # Dla unused_import - sprawdź czy import wciąż jest unused
                if "unused" in task.description.lower() or "unused_import" in str(task.id):
                    # Prosta heurystyka: sprawdź czy linia wciąż zawiera "import"
                    lines = content.split('\n')
                    line_no = task.line_number - 1 if task.line_number else 0
                    if 0 <= line_no < len(lines):
                        line = lines[line_no]
                        if "import" in line and not line.strip().startswith("#"):
                            verified.append(task)
                        else:
                            print(f"   ✓ Już naprawione: {filepath}:{task.line_number}")
                    else:
                        # Linia nie istnieje - prawdopodobnie naprawione
                        print(f"   ✓ Już naprawione: {filepath}:{task.line_number}")
                else:
                    # Dla innych typów - zakładamy że problem istnieje
                    verified.append(task)
                    
            except Exception as e:
                # Błąd odczytu - pomijamy zadanie
                print(f"   ⚠️  Błąd weryfikacji {filepath}: {e}")
                continue
        
        return verified
    
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
    
    def _process_group(self, group: TaskGroup, group_idx: int = 0, total_groups: int = 0) -> list[FixResult]:
        """Przetwórz grupę zadań."""
        start = time.time()
        
        if total_groups > 0:
            print(f"  [{group_idx}/{total_groups}] 🔧 {group.category}: {len(group.tasks)} plików")
        else:
            print(f"  🔧 {group.category}: {len(group.tasks)} plików")
        
        for f in group.files[:3]:
            # Pokaż pełną ścieżkę dla łatwiejszego debugowania
            rel_path = Path(f).relative_to(Path.cwd()) if str(f).startswith(str(Path.cwd())) else f
            print(f"     • {rel_path}")
        if len(group.files) > 3:
            print(f"     ... i {len(group.files) - 3} więcej")
        
        if self.dry_run:
            # Log dry run
            if hasattr(self, '_logger') and self._logger:
                files = [t.file_path for t in group.tasks]
                self._logger.start_group(group_idx, total_groups, group.category, files)
                self._logger.end_group("dry-run")
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
            
            # Log success
            if hasattr(self, '_logger') and self._logger:
                files = [t.file_path for t in group.tasks]
                self._logger.start_group(0, 1, group.category, files)
                self._logger.end_group("success")
            
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
            # Log failure
            if hasattr(self, '_logger') and self._logger:
                files = [t.file_path for t in group.tasks]
                self._logger.start_group(0, 1, group.category, files)
                self._logger.end_group("failed", str(e))
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
            # Pokaż pełną ścieżkę dla łatwiejszego debugowania
            rel_path = Path(task.file_path).relative_to(Path.cwd()) if str(task.file_path).startswith(str(Path.cwd())) else task.file_path
            print(f"     • Individual fix: {rel_path}")
            print(f"       Opis: {task.description}")
            print(f"       Linia: {task.line_number}")
            result = self._fix_single(task)
            print(f"       Wynik: {'✓ Sukces' if result.success else '✗ Porażka'} ({result.method})")
            if result.error:
                print(f"       Błąd: {result.error}")
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
            except Exception as e:
                print(f"     ⚠️  Błąd odczytu {task.file_path}: {e}")
                continue
        
        if not files_content:
            print(f"     ✗ Brak plików do przetworzenia w grupie {group.category}")
            return ""
        
        prompt = f"""You are a code refactoring tool. Fix the following {group.pattern} issues in multiple files.

{''.join(files_content)}

INSTRUCTIONS:
1. Apply fixes to ALL files above
2. Return the COMPLETE fixed content for each file
3. Use EXACTLY this format for each file:

=== FIXED: /full/path/to/file.py ===
<complete fixed file content here>

=== FIXED: /full/path/to/another_file.py ===
<complete fixed file content here>

IMPORTANT:
- Do NOT explain what you did
- Do NOT provide instructions or examples
- ONLY return the === FIXED: sections with complete code
- Fix ALL files mentioned above"""
        # Logowanie promptu (pierwsze 500 znaków)
        print(f"     📝 Prompt length: {len(prompt)} chars")
        print(f"     📝 Prompt preview:\n{prompt[:500]}...\n")
        
        return prompt
    
    def _call_llm(self, prompt: str, model: str, max_retries: int = 2) -> str:
        """Wywołaj LLM z spinnerem i retry dla timeoutów."""
        
        for attempt in range(max_retries + 1):
            response_container = [None]
            error_container = [None]
            
            def call_llm():
                try:
                    response_container[0] = self.service.client.generate(
                        prompt=prompt,
                        model=model,
                        temperature=0.3
                    )
                except Exception as e:
                    error_container[0] = e
            
            # Start LLM call in thread
            thread = threading.Thread(target=call_llm)
            thread.start()
            
            # Spinner pokazujący postęp
            spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            i = 0
            start = time.time()
            
            if attempt == 0:
                sys.stdout.write(f"      🤖 LLM: {model} ")
            else:
                sys.stdout.write(f"      🔄 Retry {attempt}/{max_retries}: {model} ")
            sys.stdout.flush()
            
            while thread.is_alive():
                elapsed = time.time() - start
                sys.stdout.write(f"\r      🤖 LLM: {model} {spinner[i % len(spinner)]} {elapsed:.0f}s/{self.timeout:.0f}s")
                sys.stdout.flush()
                time.sleep(0.1)
                i += 1
                
                if elapsed > self.timeout:
                    sys.stdout.write(f"\r      ✗ LLM timeout po {elapsed:.0f}s\n")
                    sys.stdout.flush()
                    break
            
            thread.join(timeout=1.0)  # Daj czas na zakończenie
            
            # Jeśli timeout i mamy retry, spróbuj ponownie z większym timeout
            if not response_container[0] and attempt < max_retries:
                print(f"\n      ⏱️  Timeout - retry {attempt + 1}/{max_retries} z timeout={self.timeout * 1.5:.0f}s")
                self.timeout *= 1.5  # Zwiększ timeout dla retry
                continue
            
            if error_container[0]:
                if attempt < max_retries:
                    print(f"\n      ⚠️  Błąd: {error_container[0]} - retry {attempt + 1}/{max_retries}")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise error_container[0]
            
            elapsed = time.time() - start
            sys.stdout.write(f"\r      ✓ LLM: {elapsed:.1f}s{' ' * 20}\n")
            sys.stdout.flush()
            
            # Logowanie odpowiedzi (pierwsze 1000 znaków)
            response_content = response_container[0].content
            print(f"     📝 LLM response length: {len(response_content)} chars")
            print(f"     📝 LLM response preview:\n{response_content[:1000]}...\n")
            
            return response_content
        
        raise TimeoutError(f"LLM call exceeded timeout after {max_retries} retries")
    
    def _parse_batch_response(self, response: str, group: TaskGroup) -> dict[str, bool]:
        """Parsuj odpowiedź batch i zastosuj fixy."""
        results = {}
        backups = {}  # filepath -> original content
        
        print(f"     🔍 Parsowanie odpowiedzi dla {len(group.tasks)} zadań...")
        print(f"     🔍 Oczekiwane pliki: {[t.file_path for t in group.tasks]}")
        
        # Parsuj sekcje === FIXED: path ===
        import re
        pattern = r'=== FIXED: (.+?) ===\n(.*?)(?==== FIXED:|$)'
        matches = re.findall(pattern, response, re.DOTALL)
        
        print(f"     🔍 Znaleziono {len(matches)} sekcji FIXED w odpowiedzi")
        
        for idx, (filepath, fixed_content) in enumerate(matches):
            filepath = filepath.strip()
            fixed_content = fixed_content.strip()
            print(f"     [{idx+1}] Parsowanie: {filepath}")
            print(f"         Content length: {len(fixed_content)} chars")
            print(f"         Content preview: {fixed_content[:200]}...")
            
            try:
                path = Path(filepath)
                # Backup przed zapisem
                if path.exists():
                    backups[filepath] = path.read_text()
                    print(f"         📦 Backup created ({len(backups[filepath])} chars)")
                else:
                    backups[filepath] = None  # Nowy plik
                    print(f"         📦 Nowy plik (brak backup)")
                
                # Sprawdź czy content jest różny
                original_content = backups.get(filepath, "")
                if original_content == fixed_content:
                    print(f"         ⚠️  Content nie zmieniony - pomijam zapis")
                    results[filepath] = False
                    continue
                
                path.write_text(fixed_content)
                results[filepath] = True
                print(f"         ✓ Zapisano: {filepath}")
            except Exception as e:
                print(f"         ✗ Błąd zapisu {filepath}: {e}")
                results[filepath] = False
        
        # Oznacz pliki bez odpowiedzi jako failed
        missing_count = 0
        for task in group.tasks:
            if task.file_path not in results:
                print(f"     ⚠️  Brak odpowiedzi dla: {task.file_path}")
                results[task.file_path] = False
                missing_count += 1
        
        if missing_count > 0:
            print(f"     ✗ {missing_count} plików bez odpowiedzi z LLM")
        
        # Podsumowanie
        success_count = sum(1 for v in results.values() if v)
        print(f"     📊 Podsumowanie: {success_count}/{len(results)} plików zapisanych")
        
        # Walidacja i rollback jeśli potrzeba
        if results and any(results.values()):
            print(f"     🔍 Rozpoczynam walidację...")
            self._validate_and_rollback(results, backups)
        return results
    
    def _validate_and_rollback(self, results: dict, backups: dict) -> None:
        """Waliduj pliki przez vallm i rollbackuj jeśli błędy."""
        try:
            import importlib
            vallm = importlib.import_module("vallm")
        except ImportError:
            print("     ⚠️  vallm nie jest zainstalowany - pominięto walidację")
            return
        
        for filepath, success in list(results.items()):
            if not success:
                continue
            
            try:
                # Waliduj plik
                validation = vallm.validate_file(filepath)
                
                if not validation.is_valid:
                    print(f"     ⚠️  Walidacja nie przeszła dla {filepath}:")
                    for error in validation.errors[:3]:  # Pokaż max 3 błędy
                        print(f"        - {error}")
                    
                    # Rollback - przywróć oryginalną zawartość
                    original = backups.get(filepath)
                    if original is not None:
                        Path(filepath).write_text(original)
                        print(f"     ↩️  Rollback: {filepath}")
                    else:
                        # Nowy plik - usuń
                        Path(filepath).unlink(missing_ok=True)
                        print(f"     🗑️  Usunięto nowy plik: {filepath}")
                    
                    results[filepath] = False
                else:
                    print(f"     ✓ Walidacja OK: {filepath}")
                    
            except Exception as e:
                print(f"     ⚠️  Błąd walidacji {filepath}: {e}")
                # W przypadku błędu walidacji robimy rollback dla bezpieczeństwa
                original = backups.get(filepath)
                if original is not None:
                    try:
                        Path(filepath).write_text(original)
                        print(f"     ↩️  Rollback (bezpieczeństwo): {filepath}")
                        results[filepath] = False
                    except Exception:
                        pass
    
    def _ensure_model(self) -> Optional[str]:
        """Wybierz model."""
        if self.model:
            return self.model
        
        models = self.service.get_recommended_models()
        if models:
            self.model = models[0]
            return self.model
        return None
