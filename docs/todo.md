# algitex todo - wykonywanie zadań przez Docker MCP

## Szybki start

```bash
# Wyświetl zadania z TODO.md
algitex todo list

# Wykonaj wszystkie zadania przez nap MCP
algitex todo run

# Wykonaj tylko zadania naprawy kodu
algitex todo fix

# Podgląd bez wykonywania
algitex todo run --dry-run

# Ogranicz liczbę zadań
algitex todo run --limit 5

# Użyj innego narzędzia MCP
algitex todo run --tool aider-mcp
algitex todo run --tool filesystem-mcp
```

## Trój-tierowy System Micro-Fixów

Algitex implementuje inteligentny system klasyfikacji trój-tierowej, który kieruje zadania do najbardziej opłacalnej strategii naprawy:

```
Tier 0: Algorytmiczne (90%)  → Deterministyczne, bez LLM
Tier 1: Małe LLM (9%)        → Ollama 7B, minimalny kontekst  
Tier 2: Duże LLM (1%)        → Claude/GPT-4o, tylko złożone
```

### Klasyfikacja tierów

| Tier | Nazwa | Kategorie | Backend | Przepustowość |
|------|-------|-----------|---------|---------------|
| **0** | Algorytm | `unused_import`, `return_type`, `fstring`, `magic_known`, `module_block` | Deterministyczny | ~1500/s |
| **1** | Małe LLM | `magic`, `docstring`, `rename`, `guard_clause`, `dispatch` | Ollama 7B | ~50-100/s |
| **2** | Duże LLM | `split_function`, `dependency_cycle`, `architecture`, `other` | Claude/GPT-4o | ~5-10/s |

### CLI - Komendy trój-tierowe

```bash
# Statystyki tierów i kategorii
algitex todo stats TODO.md

# Tier 0: Tylko naprawy algorytmiczne (deterministyczne, najszybsze)
algitex todo fix --algo --dry-run
algitex todo fix --algo --execute --workers 8

# Tier 1: Małe LLM (Ollama, lokalne)
algitex todo fix --micro --dry-run
algitex todo fix --micro --execute --model qwen2.5-coder:7b --micro-workers 4

# Wszystkie tiery: Pełny workflow
algitex todo fix --all --dry-run
algitex todo fix --all --execute --workers 4 --micro-workers 2

# Z rate limiting i custom backend
algitex todo fix --all --execute \
  --backend litellm-proxy \
  --proxy-url http://localhost:4000 \
  --rate-limit 10 \
  --workers 4
```

### Inteligentne routowanie magic numbers

System inteligentnie kieruje naprawy magic numbers na podstawie znanych stałych:

- **Znane stałe** (200 → `HTTP_OK`, 404 → `HTTP_NOT_FOUND`): Tier 0, natychmiastowa zamiana
- **Nieznane stałe** (42, 7, 86400): Tier 1, małe LLM sugeruje nazwę

## BatchFix - grupowanie i optymalizacja

```bash
# Weryfikacja - sprawdź które zadania są nadal aktualne
algitex todo verify-prefact

# Wyczyść nieaktualne zadania z TODO.md
algitex todo verify-prefact --prune

# BatchFix - symulacja (dry-run)
algitex todo batch --dry-run

# BatchFix - wykonaj z limitem i równoległością
algitex todo batch --execute --limit 10 --parallel 2

# BatchFix z czyszczeniem nieaktualnych zadań
algitex todo batch --execute --prune

# Wyłączenie logowania markdown
algitex todo batch --execute --no-log
```

## Komendy CLI

| Komenda | Opis | Przykład |
|---------|------|----------|
| `list` | Wyświetl zadania z TODO.md | `algitex todo list` |
| `run` | Wykonaj zadania przez MCP | `algitex todo run --limit 5` |
| `fix` | Wykonaj tylko zadania naprawy | `algitex todo fix --dry-run` |
| `stats` | Statystyki tierów i kategorii | `algitex todo stats TODO.md` |
| `batch` | BatchFix - grupowanie zadań | `algitex todo batch --execute` |
| `verify-prefact` | Weryfikacja z prefact | `algitex todo verify-prefact --prune` |

### Opcje trój-tierowe (fix)

| Flaga | Opis | Domyślnie |
|-------|------|-----------|
| `--algo` | Tylko Tier 0 (algorytmiczne) | False |
| `--micro` | Tylko Tier 1 (małe LLM) | False |
| `--all` | Wszystkie tiery w sekwencji | False |
| `--model` | Model Ollama (dla Tier 1) | qwen2.5-coder:7b |
| `--micro-workers` | Workerów dla Tier 1 | 4 |
| `--workers` | Workerów dla Tier 0 i 2 | 8 |
| `--rate-limit` | Limit zapytań LLM/sek | 10 |
| `--dry-run/--execute` | Symulacja lub wykonanie | dry-run |

## Opcje BatchFix

| Flaga | Opis | Domyślnie |
|-------|------|-----------|
| `--dry-run/--execute` | Symulacja lub wykonanie | dry-run |
| `-b, --backend` | Backend: ollama, litellm-proxy | ollama |
| `-s, --batch-size` | Max plików w batchu | 5 |
| `-p, --parallel` | Równoległe grupy | 3 |
| `--prune` | Usuń nieaktualne zadania | False |
| `-l, --limit` | Limit liczby zadań | 0 (wszystkie) |
| `--no-log` | Wyłącz logi markdown | False |

## Logi Markdown

BatchFix automatycznie generuje logi w formacie markdown w katalogu `.algitex/logs/`:

```bash
# Log zapisywany automatycznie
algitex todo batch --execute
# Log zapisany: .algitex/logs/batch_YYYYMMDD_HHMMSS.md

# Wyłączenie logowania
algitex todo batch --execute --no-log
```

### Struktura logu

```markdown
# BatchFix Session Log

**Started:** 2026-03-28 14:46:36
**Ended:** 2026-03-28 14:46:36

## Configuration
| Parameter | Value |
|-----------|-------|
| Backend | ollama |
| Batch Size | 2 |
| Parallel Groups | 3 |

## Summary
| Metric | Count |
|--------|-------|
| Total Entries | 3 |
| Successful | 2 |
| Failed | 0 |
| Dry Run | 1 |
| Total Duration | 45.2s |

## Details
### [1/3] unused_import
**Status:** ✅ `success`
**Duration:** 15.3s
**Files:**
- `src/main.py`
- `src/utils.py`
```

### 1. GitHub-style (checkbox)
```markdown
- [ ] Fix import in src/main.py
- [x] Update documentation
- [ ] Add tests for new feature
```

### 2. Prefact-style (z lokalizacją)
```markdown
- [ ] src/main.py:15 - Function 'main' missing return type
- [ ] src/utils.py:30 - Unused import: 'json'
- [ ] src/app.py:45 - Magic number: 200 - use named constant
```

### 3. Generic list
```markdown
* [P0] Critical security fix
* [P1] Add input validation
* Review error handling
```

## Narzędzia MCP

| Narzędzie | Przeznaczenie |
|-----------|---------------|
| `nap` | Automatyczna naprawa kodu (domyślne) |
| `aider-mcp` | AI code editing |
| `filesystem-mcp` | Operacje na plikach |
| `github-mcp` | Operacje GitHub |

## Konfiguracja w docker-tools.yaml

Narzędzie `nap` jest już skonfigurowane:

```yaml
tools:
  nap:
    image: wronai/nap:latest
    transport: mcp-stdio
    volumes:
      - "${PROJECT_DIR}:/workspace"
    capabilities:
      - fix_issue
      - fix_imports
      - fix_types
      - fix_style
      - apply_patch
      - validate_fix
```

## Przykład workflow

```bash
# 1. Generowanie TODO przez prefact
prefact -a > TODO.md

# 2. Podgląd zadań
algitex todo list TODO.md

# 3. Wykonanie napraw
algitex todo fix TODO.md

# 4. Sprawdzenie statusu
algitex todo list TODO.md
```

## API Python

### Trój-tierowy system micro-fixów

```python
from algitex.todo import (
    parse_todo,
    classify_task,
    partition_tasks,
    MicroFixer,
    HybridAutofix,
    parallel_fix_and_update,
    BIG_CATEGORIES,
)

# Parsowanie i klasyfikacja zadań
tasks = parse_todo("TODO.md")
for task in tasks:
    triage = classify_task(task)
    print(f"{task.description}: Tier {triage.tier} - {triage.category}")

# Podział na tiery
buckets = partition_tasks(tasks)
print(f"Algorytmiczne: {len(buckets['algorithm'])}")
print(f"Małe LLM: {len(buckets['micro'])}")
print(f"Duże LLM: {len(buckets['big'])}")

# Tier 0: Naprawy algorytmiczne (deterministyczne)
result = parallel_fix_and_update(
    "TODO.md",
    workers=8,
    dry_run=False,
    tasks=buckets["algorithm"]
)
print(f"Fixed: {result['fixed']}, Skipped: {result['skipped']}")

# Tier 1: Małe LLM (Ollama)
micro_fixer = MicroFixer(
    ollama_url="http://localhost:11434",
    model="qwen2.5-coder:7b",
    workers=4,
    dry_run=False,
)
result = micro_fixer.fix_tasks(buckets["micro"])
print(f"Fixed: {result['fixed']}, Skipped: {result['skipped']}")

# Tier 2: Duże LLM (Claude/GPT-4o)
hybrid = HybridAutofix(
    backend="litellm-proxy",
    workers=4,
    rate_limit=10,
    dry_run=False,
)
result = hybrid.fix_complex(
    "TODO.md",
    include_categories=BIG_CATEGORIES,
    tasks=buckets["big"]
)
print(f"Fixed: {result.get('fixed', 0)}")
```

### Tradycyjne API (TodoRunner)

```python
from algitex.tools.todo_runner import TodoRunner

with TodoRunner(".") as runner:
    results = runner.run_from_file("TODO.md", tool="nap")
    for r in results:
        print(f"{r.task.id}: {'✓' if r.success else '✗'} {r.task.description}")
```
