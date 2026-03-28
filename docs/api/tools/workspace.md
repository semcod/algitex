# `tools.workspace`

Multi-repo workspace orchestration for algitex.

Manage multiple repositories as a single workspace with dependency ordering.


## Functions

### `create_workspace_template`

```python
def create_workspace_template(name: str, repos: List[Dict]) -> str
```

Create a workspace configuration template.

### `init_workspace`

```python
def init_workspace(name: str, config_path: str='workspace.yaml') -> None
```

Initialize a new workspace with template.

## Classes

### `RepoConfig`

Configuration for a single repository in the workspace.

### `Workspace`

Manage multiple repos as a single workspace.

**Methods:**

#### `__init__`

```python
def __init__(self, config_path: str='workspace.yaml')
```

#### `clone_all`

```python
def clone_all(self, base_dir: str='.') -> None
```

Clone all repositories if they don't exist.

#### `pull_all`

```python
def pull_all(self) -> None
```

Pull latest changes for all repositories.

#### `analyze_all`

```python
def analyze_all(self, full: bool=True) -> Dict[str, dict]
```

Run algitex analyze on each repo in dependency order.

#### `plan_all`

```python
def plan_all(self, sprints: int=2) -> Dict[str, List]
```

Generate cross-repo plan respecting dependencies.

#### `execute_all`

```python
def execute_all(self, tool: str='aider-mcp', max_tickets: int=5) -> Dict[str, dict]
```

Execute tickets across repos in correct order.

#### `validate_all`

```python
def validate_all(self) -> Dict[str, dict]
```

Run validation across all repositories.

#### `status`

```python
def status(self) -> dict
```

Get status of all repositories.

#### `get_dependency_graph`

```python
def get_dependency_graph(self) -> Dict[str, List[str]]
```

Get the dependency graph for visualization.

#### `find_repos_by_tag`

```python
def find_repos_by_tag(self, tag: str) -> List[RepoConfig]
```

Find all repositories with a specific tag.

#### `get_execution_plan`

```python
def get_execution_plan(self) -> List[str]
```

Get the execution order for repositories.
