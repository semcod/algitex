# `tools.cicd`

CI/CD generation for algitex pipelines.

Generate GitHub Actions / GitLab CI workflows with quality gates.


## Functions

### `init_ci_cd`

```python
def init_ci_cd(project_path: str='.', platform: str='github') -> None
```

Initialize CI/CD for a project.

### `create_quality_gate_config`

```python
def create_quality_gate_config(max_cc: float=3.5, require_tests: bool=True, security_scan: bool=True) -> Dict
```

Create a quality gate configuration.

## Classes

### `CICDGenerator`

Generate CI/CD pipelines for algitex projects.

**Methods:**

#### `__init__`

```python
def __init__(self, project_path: str='.')
```

#### `generate_github_actions`

```python
def generate_github_actions(self, output_path: Optional[str]=None) -> str
```

Generate GitHub Actions workflow with quality gates.

#### `generate_gitlab_ci`

```python
def generate_gitlab_ci(self, output_path: Optional[str]=None) -> str
```

Generate GitLab CI configuration.

#### `generate_dockerfile`

```python
def generate_dockerfile(self, output_path: Optional[str]=None) -> str
```

Generate Dockerfile for algitex project.

#### `generate_precommit_config`

```python
def generate_precommit_config(self, output_path: Optional[str]=None) -> str
```

Generate pre-commit configuration.

#### `generate_all`

```python
def generate_all(self, github: bool=True, gitlab: bool=False, dockerfile: bool=True, precommit: bool=True) -> Dict[str, str]
```

Generate all CI/CD configurations.

#### `update_config`

```python
def update_config(self, config: Dict) -> None
```

Update CI/CD configuration.
