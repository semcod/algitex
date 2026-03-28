# `algo`

Progressive Algorithmization Loop.

The 5-stage pipeline: LLM → patterns → rules → hybrid → deterministic.

Usage:
    from algitex.algo.loop import Loop

    loop = Loop("./my-app")
    loop.discover()        # Stage 1: LLM handles all, collect traces
    loop.extract()         # Stage 2: identify hot paths
    loop.generate_rules()  # Stage 3: AI writes deterministic replacements
    loop.route()           # Stage 4: confidence-based routing
    loop.optimize()        # Stage 5: monitor, minimize LLM usage
    loop.report()          # show progress: % deterministic vs LLM


## Classes

### `TraceEntry`

Single LLM interaction trace.

**Methods:**

#### `to_dict`

```python
def to_dict(self) -> dict
```

### `Pattern`

Extracted repeating pattern from traces.

### `Rule`

Deterministic replacement for an LLM pattern.

### `LoopState`

Current state of the progressive algorithmization loop.

**Methods:**

#### `deterministic_ratio`

```python
def deterministic_ratio(self) -> float
```

#### `stage_name`

```python
def stage_name(self) -> str
```

### `Loop`

The progressive algorithmization engine.

**Methods:**

#### `__init__`

```python
def __init__(self, project_path: str='.')
```

#### `discover`

```python
def discover(self, proxy_url: str='http://localhost:4000') -> LoopState
```

Stage 1: Enable trace collection from proxym.

        Registers a webhook with proxym to capture all LLM interactions.
        Traces are stored locally for pattern analysis.
        

#### `add_trace`

```python
def add_trace(self, prompt: str, response: str, **meta) -> TraceEntry
```

Manually add a trace entry (or called by proxym hook).

#### `extract`

```python
def extract(self, min_frequency: int=3) -> list[Pattern]
```

Stage 2: Identify repeating patterns from traces.

        Groups traces by prompt similarity, ranks by frequency and cost.
        

#### `generate_rules`

```python
def generate_rules(self, use_llm: bool=True) -> list[Rule]
```

Stage 3: Generate deterministic rules for top patterns.

        Uses LLM (via proxym) to create its own replacement:
        decision trees, lookup tables, regex matchers.
        

#### `route`

```python
def route(self, prompt: str) -> dict
```

Stage 4: Route request to rule or LLM based on confidence.

        Returns:
            {"handler": "rule"|"llm", "rule_id": ..., "confidence": ...}
        

#### `optimize`

```python
def optimize(self) -> dict
```

Stage 5: Report optimization status and detect regressions.

#### `report`

```python
def report(self) -> dict
```

Full progress report on algorithmization.
