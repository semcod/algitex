"""Shared test fixtures."""

import os
import pytest
from pathlib import Path


@pytest.fixture(autouse=True)
def clean_cwd(tmp_path, monkeypatch):
    """Ensure tests don't pollute the real working directory.
    Each test gets its own tmp_path and clean environment."""
    monkeypatch.delenv("PROXYM_URL", raising=False)
    monkeypatch.delenv("PROXYM_API_KEY", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)


@pytest.fixture
def sample_workflow(tmp_path):
    """Create a sample Propact workflow file."""
    wf = tmp_path / "sample.md"
    wf.write_text("""# Sample Workflow

## Check environment

```propact:shell
echo "running in $(pwd)"
```

## List files

```propact:shell
ls -la
```
""")
    return wf


@pytest.fixture
def sample_project(tmp_path):
    """Create a minimal Python project structure."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "__init__.py").write_text('"""Sample project."""\n__version__ = "0.1.0"\n')
    (src / "main.py").write_text("""
def hello(name: str) -> str:
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    print(hello("world"))
""")
    (src / "utils.py").write_text("""
import os

def get_env(key: str, default: str = "") -> str:
    return os.getenv(key, default)

def file_exists(path: str) -> bool:
    return os.path.isfile(path)
""")
    (tmp_path / "pyproject.toml").write_text("""
[project]
name = "sample"
version = "0.1.0"
""")
    return tmp_path
