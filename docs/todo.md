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

## Formaty obsługiwanych plików todo

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
