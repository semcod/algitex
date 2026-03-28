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
| `batch` | BatchFix - grupowanie zadań | `algitex todo batch --execute` |
| `verify-prefact` | Weryfikacja z prefact | `algitex todo verify-prefact --prune` |

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

```python
from algitex.tools.todo_runner import TodoRunner

with TodoRunner(".") as runner:
    results = runner.run_from_file("TODO.md", tool="nap")
    for r in results:
        print(f"{r.task.id}: {'✓' if r.success else '✗'} {r.task.description}")
```
