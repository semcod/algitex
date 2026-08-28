"""Shared capability and filesystem guards for Algitex MCP containers."""

from __future__ import annotations

import os
from pathlib import Path


_TRUE_VALUES = {"1", "true", "yes", "on"}


def env_flag(name: str) -> bool:
    """Return whether an explicit boolean environment capability is enabled."""
    return os.getenv(name, "").strip().lower() in _TRUE_VALUES


def require_capability(name: str, action: str) -> None:
    """Fail closed unless a capability was explicitly enabled."""
    if not env_flag(name):
        raise PermissionError(
            f"{action} is disabled; set {name}=1 only for trusted MCP clients"
        )


def project_root(*, env_name: str = "ALGITEX_MCP_PROJECT_ROOT") -> Path:
    """Return the configured, existing workspace root."""
    root = Path(os.getenv(env_name, ".")).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise NotADirectoryError(f"Configured project root is not a directory: {root}")
    return root


def resolve_workspace_path(
    path: str | None,
    *,
    env_name: str = "ALGITEX_MCP_PROJECT_ROOT",
    must_exist: bool = True,
) -> Path:
    """Resolve a path without allowing it to escape the configured workspace."""
    root = project_root(env_name=env_name)

    raw = (path or ".").strip() or "."
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.resolve()

    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise PermissionError(
            f"Project path must stay within {env_name}: {root}"
        ) from exc

    if must_exist and not candidate.exists():
        raise FileNotFoundError(f"Project path does not exist: {candidate}")
    return candidate


def resolve_project_path(
    path: str | None, *, env_name: str = "ALGITEX_MCP_PROJECT_ROOT"
) -> Path:
    """Resolve an existing project directory within the configured workspace root."""
    candidate = resolve_workspace_path(path, env_name=env_name)
    if not candidate.is_dir():
        raise NotADirectoryError(f"Project path is not a directory: {candidate}")
    return candidate
