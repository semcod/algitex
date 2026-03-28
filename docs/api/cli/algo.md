# `cli.algo`

Algorithmization subcommands for algitex CLI.

## Functions

### `algo_discover`

```python
def algo_discover(path: str=typer.Option('.', '--path', '-p')) -> None
```

Stage 1: Start trace collection from proxym.

### `algo_extract`

```python
def algo_extract(path: str=typer.Option('.', '--path', '-p'), min_freq: int=typer.Option(3, '--min-freq'))
```

Stage 2: Extract repeating patterns from traces.

### `algo_rules`

```python
def algo_rules(path: str=typer.Option('.', '--path', '-p'), no_llm: bool=typer.Option(False, '--no-llm'))
```

Stage 3: Generate deterministic rules for top patterns.

### `algo_report`

```python
def algo_report(path: str=typer.Option('.', '--path', '-p'))
```

Show algorithmization progress.
