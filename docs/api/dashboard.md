# `dashboard`

Real-time TUI dashboard for algitex using Rich.

Provides live monitoring of:
- Cache performance (hit rate, entries, size)
- Tier throughput (algorithm, micro, big)
- Current operations progress
- System resource usage

Usage:
    from algitex.dashboard import LiveDashboard
    
    dashboard = LiveDashboard()
    dashboard.start()
    
    # Update metrics
    dashboard.update_cache_stats(hits=100, misses=10, entries=50)
    dashboard.update_tier_progress("micro", current=10, total=50)
    
    dashboard.stop()


## Functions

### `show_quick_dashboard`

```python
def show_quick_dashboard(duration: float=10.0)
```

Show a quick demo dashboard for a specified duration.

## Classes

### `TierState`

State tracking for a single tier.

**Methods:**

#### `percent`

```python
def percent(self) -> float
```

#### `eta_seconds`

```python
def eta_seconds(self) -> float
```

### `CacheState`

State tracking for cache metrics.

**Methods:**

#### `hit_rate`

```python
def hit_rate(self) -> float
```

#### `size_mb`

```python
def size_mb(self) -> float
```

### `LiveDashboard`

Live Rich dashboard for monitoring algitex operations.

**Methods:**

#### `__init__`

```python
def __init__(self, refresh_rate: float=1.0)
```

#### `start`

```python
def start(self)
```

Start the live dashboard.

#### `stop`

```python
def stop(self)
```

Stop the live dashboard.

#### `update_cache_stats`

```python
def update_cache_stats(self, hits: Optional[int]=None, misses: Optional[int]=None, entries: Optional[int]=None, size_bytes: Optional[int]=None)
```

Update cache statistics.

#### `update_tier_progress`

```python
def update_tier_progress(self, tier: str, current: Optional[int]=None, total: Optional[int]=None, success: Optional[int]=None, failed: Optional[int]=None, throughput: Optional[float]=None, active: Optional[bool]=None)
```

Update tier progress.

#### `set_on_update`

```python
def set_on_update(self, callback: Callable)
```

Set callback for update events.

### `SimpleProgressTracker`

Simplified progress tracking without full dashboard.

**Methods:**

#### `__init__`

```python
def __init__(self, console: Optional[Console]=None)
```

#### `start`

```python
def start(self)
```

Start progress tracking.

#### `add_task`

```python
def add_task(self, name: str, total: int) -> str
```

Add a new progress task.

#### `update`

```python
def update(self, name: str, advance: int=1, completed: Optional[int]=None)
```

Update task progress.

#### `stop`

```python
def stop(self)
```

Stop progress tracking.
