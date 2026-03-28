# `tools.parallel.partitioner`

Task partitioning — partition tickets into non-conflicting groups.

## Classes

### `TaskPartitioner`

Partition tickets into non-conflicting groups for parallel execution.

**Methods:**

#### `__init__`

```python
def __init__(self, regions: List[CodeRegion])
```

#### `partition`

```python
def partition(self, tickets: List[Dict], max_agents: int=4) -> Dict[int, List[str]]
```

Assign tickets to agents ensuring no region overlap.
