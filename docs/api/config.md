# `config`

Configuration — one file to rule them all.

Reads from (in priority order):
    1. Environment variables (ALGITEX_*, PROXYM_*, etc.)
    2. ./algitex.yaml
    3. ~/.config/algitex/config.yaml
    4. Sensible defaults (everything works out of the box)


## Classes

### `ProxyConfig`

Proxym gateway settings.

**Methods:**

#### `from_env`

```python
def from_env(cls) -> ProxyConfig
```

### `TicketConfig`

Planfile ticket system settings.

**Methods:**

#### `from_env`

```python
def from_env(cls) -> TicketConfig
```

### `AnalysisConfig`

Code analysis tool settings.

**Methods:**

#### `from_env`

```python
def from_env(cls) -> AnalysisConfig
```

### `Config`

Unified config for the entire algitex stack.

**Methods:**

#### `load`

```python
def load(cls, path: Optional[str]=None) -> Config
```

Load config: YAML file → env vars → defaults.

#### `save`

```python
def save(self, path: Optional[str]=None) -> Path
```

Save current config to algitex.yaml.
