# `tools.parallel.extractor`

Region extraction — AST-based extraction of lockable code regions.

## Classes

### `RegionExtractor`

Extract lockable AST regions from Python files using map.toon.

**Methods:**

#### `__init__`

```python
def __init__(self, project_path: str)
```

#### `extract_all`

```python
def extract_all(self) -> List[CodeRegion]
```

Parse map.toon to get all function/class regions with line ranges.
