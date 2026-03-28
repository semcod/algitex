# `cli.todo`

Todo subcommands for algitex CLI.

## Functions

### `todo_stats`

```python
def todo_stats(file: str=typer.Argument('TODO.md', help='Path to todo file'))
```

Show tier and category stats for a TODO file.

### `todo_verify`

```python
def todo_verify(file: str=typer.Argument('TODO.md', help='Path to todo file'))
```

Verify which TODO tasks are still valid vs already fixed.

### `todo_fix_parallel`

```python
def todo_fix_parallel(file: str=typer.Argument('TODO.md', help='Path to todo file'), workers: int=typer.Option(8, '--workers', '-w', help='Number of parallel workers'), dry_run: bool=typer.Option(True, '--dry-run/--execute', help='Dry run or actually apply'), category: Optional[str]=typer.Option(None, '--category', '-c', help='Filter to specific category'))
```

Auto-fix mechanical TODO tasks in parallel.

### `todo_list`

```python
def todo_list(file: str=typer.Argument('TODO.md', help='Path to todo file'))
```

Parse and display todo tasks from a file.

### `todo_run`

```python
def todo_run(file: str=typer.Argument('TODO.md', help='Path to todo file'), tool: str=typer.Option('local', '--tool', '-t', help='Tool to use (local, filesystem-mcp, aider-mcp)'), dry_run: bool=typer.Option(False, '--dry-run', help='Preview without executing'), limit: int=typer.Option(0, '--limit', '-l', help='Limit number of tasks (0 = all)'))
```

Execute todo tasks via Docker MCP.

### `todo_fix`

```python
def todo_fix(file: str=typer.Argument('TODO.md', help='Path to todo file'), tool: str=typer.Option('ollama-mcp', '--tool', '-t', help='Tool to use (local, ollama-mcp, filesystem-mcp, aider-mcp, nap)'), task_id: Optional[str]=typer.Option(None, '--task', help='Specific task ID to fix'), limit: int=typer.Option(0, '--limit', '-l', help='Limit number of tasks (0 = all)'), dry_run: bool=typer.Option(False, '--dry-run/--execute', help='Preview without executing'), algo: bool=typer.Option(False, '--algo', help='Run only algorithmic fixes'), micro: bool=typer.Option(False, '--micro', '--small-llm', help='Run only small LLM micro-fixes'), all_phases: bool=typer.Option(False, '--all', help='Run algorithmic, small LLM, and big LLM phases'), dashboard: bool=typer.Option(False, '--dashboard', '-d', help='Show live dashboard during execution'), workers: int=typer.Option(8, '--workers', '-w', help='Workers for algorithmic and big LLM phases'), micro_workers: int=typer.Option(4, '--micro-workers', help='Workers for the small LLM phase'), model: str=typer.Option('qwen3-coder:latest', '--model', help='Ollama model for the small LLM phase'), backend: str=typer.Option('ollama', '--backend', '-b', help='Backend for the big LLM phase'), rate_limit: int=typer.Option(10, '--rate-limit', '-r', help='LLM calls per second for the big LLM phase'), proxy_url: str=typer.Option('http://localhost:4000', '--proxy-url', '-p', help='LiteLLM proxy URL'))
```

Execute fix tasks (prefact-style) via Docker MCP.
    
    5-step pipeline: parse → classify → execute → validate → report.
    CC: 8 (5 functions + 3 branches)
    Was: CC ~50 (nested phase logic)
    

### `todo_benchmark`

```python
def todo_benchmark(limit: int=typer.Argument(10, help='Number of tasks to benchmark'), file: str=typer.Option('TODO.md', '--file', '-f', help='Path to todo file'), workers: int=typer.Option(8, '--workers', '-w', help='Number of parallel workers'), compare: bool=typer.Option(False, '--compare', '-c', help='Compare parallel vs sequential'))
```

Benchmark TODO fix performance.

### `todo_hybrid`

```python
def todo_hybrid(file: str=typer.Argument('TODO.md', help='Path to todo file'), backend: str=typer.Option('litellm-proxy', '--backend', '-b', help='LLM backend: litellm-proxy, ollama, aider'), tool: str=typer.Option('aider', '--tool', '-t', help='Tool for LLM fixes: aider, ollama, direct'), workers: int=typer.Option(4, '--workers', '-w', help='Parallel workers'), rate_limit: int=typer.Option(10, '--rate-limit', '-r', help='LLM calls per second'), proxy_url: str=typer.Option('http://localhost:4000', '--proxy-url', '-p', help='LiteLLM proxy URL'), hybrid: bool=typer.Option(False, '--hybrid', '-h', help='Add mechanical fixes (default: LLM only)'), dashboard: bool=typer.Option(False, '--dashboard', '-d', help='Show live dashboard during execution'), fallback: bool=typer.Option(True, '--fallback/--no-fallback', help='Enable automatic fallback to alternative backends'), verbose: bool=typer.Option(False, '--verbose', '-v', help='Enable verbose logging for debugging'), dry_run: bool=typer.Option(True, '--dry-run/--execute', help='Preview or execute'))
```

Autofix: LLM-based code fixes (use --hybrid for mechanical + LLM).

### `todo_batch`

```python
def todo_batch(file: Path=typer.Option(Path('TODO.md'), '--file', '-f', help='TODO.md file path'), backend: str=typer.Option('ollama', '--backend', '-b', help='Backend: ollama, litellm-proxy'), model: str=typer.Option('qwen3-coder:latest', '--model', '-m', help='Ollama model name (e.g., qwen3-coder:latest, qwen3-coder:latest)'), batch_size: int=typer.Option(5, '--batch-size', '-s', help='Max files per batch'), parallel: int=typer.Option(3, '--parallel', '-p', help='Parallel groups (default: 3)'), dry_run: bool=typer.Option(True, '--dry-run/--execute', help='Dry run or execute'), verbose: bool=typer.Option(False, '--verbose', '-v', help='Verbose logging'), prune: bool=typer.Option(False, '--prune', help='Remove outdated tasks from TODO.md before batch'), limit: int=typer.Option(0, '--limit', '-l', help='Limit number of tasks (0 = all)'), no_log: bool=typer.Option(False, '--no-log', help='Disable markdown logging'), dashboard: bool=typer.Option(False, '--dashboard', '-d', help='Show live dashboard during execution'))
```

BatchFix: grupowanie i optymalizacja podobnych zadań.
    
    Zamiast wykonywać każde zadanie osobno, BatchFix grupuje podobne problemy
    (np. "f-string", "magic number") i wykonuje je za jednym razem.
    
    Przykłady:
        algitex todo batch --dry-run              # Symulacja
        algitex todo batch --execute             # Wykonaj fixy
        algitex todo batch -b ollama -s 3        # Ollama, max 3 pliki/batch
        algitex todo batch --execute --prune     # Wyczyść nieaktualne zadania
        algitex todo batch --execute --no-log   # Wyłącz logowanie markdown
    

### `todo_verify_prefact`

```python
def todo_verify_prefact(file: str=typer.Option('TODO.md', '--file', '-f', help='Path to TODO.md'), prune: bool=typer.Option(False, '--prune', '-p', help='Remove outdated tasks from TODO.md'))
```

Verify TODO.md against actual code using prefact.
    
    Uses prefact to scan for issues and compares with TODO.md.
    Shows which tasks are still valid and which are outdated.
    
    With --prune: removes outdated tasks from TODO.md
    
