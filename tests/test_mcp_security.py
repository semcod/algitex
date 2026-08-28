"""Safety regression tests for the standalone MCP containers."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCKER_ROOT = REPO_ROOT / "docker"
sys.path.insert(0, str(DOCKER_ROOT))

from mcp_security import require_capability, resolve_project_path  # noqa: E402


def _load_server(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / relative_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_capabilities_fail_closed(monkeypatch):
    monkeypatch.delenv("ALGITEX_MCP_ALLOW_MUTATION", raising=False)
    with pytest.raises(PermissionError, match="ALGITEX_MCP_ALLOW_MUTATION"):
        require_capability("ALGITEX_MCP_ALLOW_MUTATION", "test mutation")

    monkeypatch.setenv("ALGITEX_MCP_ALLOW_MUTATION", "yes")
    require_capability("ALGITEX_MCP_ALLOW_MUTATION", "test mutation")


def test_project_paths_are_confined(monkeypatch, tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    project = workspace / "project"
    project.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.setenv("ALGITEX_MCP_PROJECT_ROOT", str(workspace))

    assert resolve_project_path("project") == project
    with pytest.raises(PermissionError, match="must stay within"):
        resolve_project_path(str(outside))


def test_mutating_servers_require_opt_in(monkeypatch, tmp_path):
    pytest.importorskip("mcp.server.fastmcp")
    monkeypatch.setenv("ALGITEX_MCP_PROJECT_ROOT", str(tmp_path))
    monkeypatch.delenv("ALGITEX_MCP_ALLOW_MUTATION", raising=False)
    aider = _load_server("algitex_test_aider", "docker/aider-mcp/aider_mcp_server.py")
    planfile = _load_server(
        "algitex_test_planfile", "docker/planfile-mcp/planfile_mcp_server.py"
    )

    with pytest.raises(PermissionError, match="ALLOW_MUTATION"):
        aider.aider_ai_code("change code", ["example.py"])
    with pytest.raises(PermissionError, match="ALLOW_MUTATION"):
        planfile.planfile_create_ticket("unsafe write")
    assert not (tmp_path / "planfile.yaml").exists()


def test_aider_rejects_paths_outside_workspace(monkeypatch, tmp_path):
    pytest.importorskip("mcp.server.fastmcp")
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.setenv("ALGITEX_MCP_PROJECT_ROOT", str(workspace))
    monkeypatch.setenv("ALGITEX_MCP_ALLOW_MUTATION", "true")
    aider = _load_server(
        "algitex_test_aider_paths", "docker/aider-mcp/aider_mcp_server.py"
    )

    assert aider.aider_ai_code("change code", ["new.py"])["status"] == "success"
    with pytest.raises(PermissionError, match="must stay within"):
        aider.aider_ai_code("escape", ["../outside.py"])


def test_validation_and_network_require_opt_in(monkeypatch):
    pytest.importorskip("mcp.server.fastmcp")
    pytest.importorskip("tiktoken")
    monkeypatch.delenv("ALGITEX_MCP_ALLOW_EXECUTE", raising=False)
    monkeypatch.delenv("ALGITEX_MCP_ALLOW_NETWORK", raising=False)
    vallm = _load_server("algitex_test_vallm", "docker/vallm/vallm_mcp_server.py")
    proxym = _load_server("algitex_test_proxym", "docker/proxym/proxym_mcp_server.py")

    with pytest.raises(PermissionError, match="ALLOW_EXECUTE"):
        vallm.validate_runtime(".")
    with pytest.raises(PermissionError, match="ALLOW_NETWORK"):
        proxym.simple_prompt("hello")


def test_proxy_enforces_request_limits(monkeypatch):
    pytest.importorskip("mcp.server.fastmcp")
    pytest.importorskip("tiktoken")
    monkeypatch.setenv("ALGITEX_MCP_ALLOW_NETWORK", "true")
    monkeypatch.setenv("ALGITEX_MCP_MAX_PROMPT_BYTES", "4")
    monkeypatch.setenv("ALGITEX_MCP_MAX_OUTPUT_TOKENS", "8")
    proxym = _load_server(
        "algitex_test_proxym_limits", "docker/proxym/proxym_mcp_server.py"
    )

    with pytest.raises(ValueError, match="MAX_PROMPT_BYTES"):
        proxym.simple_prompt("12345")
    with pytest.raises(ValueError, match="max_tokens"):
        proxym.chat_completion([{"role": "user", "content": "ok"}], max_tokens=9)


def test_orchestrator_uses_extracted_lifecycle_and_defaults():
    from algitex.tools.mcp import MCPOrchestrator
    from algitex.tools.mcp_lifecycle import MCPLifecycleManager

    orchestrator = MCPOrchestrator()
    assert isinstance(orchestrator, MCPLifecycleManager)
    assert set(orchestrator.services) == {
        "aider",
        "code2llm",
        "filesystem",
        "github",
        "docker",
    }
