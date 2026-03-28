"""Propact Workflow Engine — execute Markdown with embedded actions.

Propact treats Markdown as a workflow format. Code blocks tagged with
`propact:rest`, `propact:shell`, `propact:mcp` are executable steps.

Usage:
    from algitex.propact import Workflow

    wf = Workflow("./refactor-v1.md")
    wf.validate()       # check syntax
    wf.execute()         # run all steps
    wf.status()          # step-by-step progress

Workflow format:
    # Fix Imports

    First, analyze the module structure.

    ```propact:shell
    code2llm ./src -f toon --json
    ```

    Then call the fix endpoint:

    ```propact:rest
    POST http://localhost:4000/v1/chat/completions
    {"model": "balanced", "messages": [{"role": "user", "content": "Fix imports"}]}
    ```

    Finally, validate:

    ```propact:shell
    vallm batch ./src --recursive
    ```
"""

from __future__ import annotations

import json
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class WorkflowStep:
    """Single executable step in a Propact workflow."""

    index: int
    type: str  # rest | shell | mcp | llm | docker
    title: str = ""
    content: str = ""
    status: str = "pending"  # pending | running | done | failed | skipped
    result: str = ""
    elapsed_ms: float = 0.0
    cost_usd: float = 0.0

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "type": self.type,
            "title": self.title,
            "status": self.status,
            "elapsed_ms": self.elapsed_ms,
        }


@dataclass
class WorkflowResult:
    """Result of workflow execution."""

    workflow_path: str
    title: str
    steps_total: int = 0
    steps_done: int = 0
    steps_failed: int = 0
    total_elapsed_ms: float = 0.0
    total_cost_usd: float = 0.0
    steps: list[WorkflowStep] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.steps_failed == 0 and self.steps_done == self.steps_total


STEP_PATTERN = re.compile(
    r"```propact:(rest|shell|mcp|llm|docker)\s*\n(.*?)```",
    re.DOTALL,
)
HEADING_PATTERN = re.compile(r"^#+\s+(.+)$", re.MULTILINE)


class Workflow:
    """Parse and execute Propact Markdown workflows."""

    def __init__(self, path: str):
        self.path = Path(path)
        self._steps: list[WorkflowStep] = []
        self._title: str = ""
        self._parsed = False

    def parse(self) -> list[WorkflowStep]:
        """Parse Markdown into executable steps."""
        if not self.path.exists():
            raise FileNotFoundError(f"Workflow not found: {self.path}")

        content = self.path.read_text()

        # Extract title
        heading = HEADING_PATTERN.search(content)
        self._title = heading.group(1) if heading else self.path.stem

        self._steps = self._extract_steps_from_content(content)
        self._parsed = True
        return self._steps

    def _extract_steps_from_content(self, content: str) -> list[WorkflowStep]:
        steps = []
        last_heading = self._title
        for i, match in enumerate(STEP_PATTERN.finditer(content)):
            step_type = match.group(1)
            step_content = match.group(2).strip()

            # Find nearest preceding heading for step title
            before = content[: match.start()]
            headings = HEADING_PATTERN.findall(before)
            if headings:
                last_heading = headings[-1]

            steps.append(
                WorkflowStep(
                    index=i,
                    type=step_type,
                    title=last_heading,
                    content=step_content,
                )
            )
        return steps

    def validate(self) -> list[str]:
        """Check workflow for errors without executing."""
        if not self._parsed:
            self.parse()

        errors = []
        for step in self._steps:
            if step.type == "rest":
                lines = step.content.strip().split("\n", 1)
                if not lines or not lines[0].strip():
                    errors.append(f"Step {step.index}: empty REST block")
                elif not any(lines[0].startswith(m) for m in ("GET", "POST", "PUT", "DELETE", "PATCH")):
                    errors.append(f"Step {step.index}: REST block must start with HTTP method")

            elif step.type == "shell":
                if not step.content.strip():
                    errors.append(f"Step {step.index}: empty shell block")

        return errors

    def _execute_step(self, step: WorkflowStep, proxy_url: str, docker_mgr) -> tuple[WorkflowStep, Any]:
        """Execute a single step and return the step and potentially updated docker_mgr."""
        if step.type == "shell":
            step = self._exec_shell(step)
        elif step.type == "rest":
            step = self._exec_rest(step, proxy_url)
        elif step.type == "mcp":
            step = self._exec_mcp(step, proxy_url)
        elif step.type == "llm":
            step = self._exec_llm(step, proxy_url)
        elif step.type == "docker":
            step = self._exec_docker(step, docker_mgr)
            if docker_mgr is None:
                # Store the manager after first docker step
                from algitex.tools.docker import DockerToolManager
                from algitex.config import Config
                docker_mgr = DockerToolManager(Config.load())
        return step, docker_mgr

    def _update_result(self, result: WorkflowResult, step: WorkflowStep, start_time: float):
        """Update result with step metrics."""
        step.elapsed_ms = (time.time() - start_time) * 1000
        result.total_elapsed_ms += step.elapsed_ms
        result.total_cost_usd += step.cost_usd

        if step.status == "done":
            result.steps_done += 1
        elif step.status == "failed":
            result.steps_failed += 1

    def _handle_step_failure(self, step: WorkflowStep, stop_on_error: bool):
        """Handle step failure and mark remaining steps as skipped if needed."""
        if stop_on_error:
            # Mark remaining as skipped
            for remaining in self._steps[step.index + 1 :]:
                remaining.status = "skipped"

    def execute(
        self,
        *,
        dry_run: bool = False,
        stop_on_error: bool = True,
        proxy_url: str = "http://localhost:4000",
    ) -> WorkflowResult:
        """Execute all steps in the workflow."""
        if not self._parsed:
            self.parse()

        result = WorkflowResult(
            workflow_path=str(self.path),
            title=self._title,
            steps_total=len(self._steps),
        )

        # Shared DockerToolManager for reuse across steps
        docker_mgr = None
        try:
            for step in self._steps:
                if dry_run:
                    step.status = "skipped"
                    result.steps.append(step)
                    continue

                step.status = "running"
                start = time.time()

                try:
                    step, docker_mgr = self._execute_step(step, proxy_url, docker_mgr)
                except Exception as e:
                    step.status = "failed"
                    step.result = str(e)

                self._update_result(result, step, start)
                
                if step.status == "failed":
                    self._handle_step_failure(step, stop_on_error)
                    if stop_on_error:
                        break

                result.steps.append(step)
        finally:
            # Cleanup Docker containers if manager was created
            if docker_mgr:
                docker_mgr.teardown_all()

        result.steps = self._steps
        return result

    def status(self) -> dict:
        """Current workflow status."""
        return {
            "title": self._title,
            "path": str(self.path),
            "steps": [s.to_dict() for s in self._steps],
            "progress": f"{sum(1 for s in self._steps if s.status == 'done')}/{len(self._steps)}",
        }

    # ── Step executors ────────────────────────────────────

    def _exec_shell(self, step: WorkflowStep) -> WorkflowStep:
        """Execute a shell command."""
        proc = subprocess.run(
            step.content,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(self.path.parent),
        )
        step.result = proc.stdout + proc.stderr
        step.status = "done" if proc.returncode == 0 else "failed"
        return step

    def _exec_rest(self, step: WorkflowStep, proxy_url: str) -> WorkflowStep:
        """Execute a REST API call."""
        import httpx

        method, url, body = self._parse_rest_block(step.content, proxy_url)

        with httpx.Client(timeout=120) as client:
            kwargs: dict[str, Any] = {}
            if body:
                try:
                    kwargs["json"] = json.loads(body)
                except json.JSONDecodeError:
                    kwargs["content"] = body

            resp = client.request(method, url, **kwargs)

        step.result = resp.text[:2000]
        step.status = "done" if resp.status_code < 400 else "failed"
        step.cost_usd = self._extract_proxy_cost(resp)

        return step

    def _parse_rest_block(self, content: str, proxy_url: str) -> tuple[str, str, str]:
        lines = content.strip().split("\n", 1)
        method_line = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""

        parts = method_line.split(None, 1)
        method = parts[0].upper()
        url = parts[1] if len(parts) > 1 else ""

        # Replace relative URLs with proxy
        if url.startswith("/"):
            url = proxy_url + url
        return method, url, body

    def _extract_proxy_cost(self, resp: Any) -> float:
        try:
            data = resp.json()
            return float(data.get("_proxy", {}).get("cost_usd", 0.0))
        except Exception:
            return 0.0

    def _exec_mcp(self, step: WorkflowStep, proxy_url: str) -> WorkflowStep:
        """Execute an MCP tool call."""
        try:
            data = json.loads(step.content)
            server = data.get("server", "")
            tool = data.get("tool", "")
            args = data.get("args", {})

            import httpx
            with httpx.Client(timeout=60) as client:
                resp = client.post(
                    f"{proxy_url}/mcp/self/tools/{tool}",
                    json=args,
                )
            step.result = resp.text[:2000]
            step.status = "done" if resp.status_code < 400 else "failed"
        except Exception as e:
            step.status = "failed"
            step.result = str(e)
        return step

    def _exec_docker(self, step: WorkflowStep, docker_mgr: Optional[DockerToolManager] = None) -> WorkflowStep:
        """Execute a step using a Docker tool from docker-tools.yaml.

        Propact syntax:
            ```propact:docker
            tool: aider-mcp
            action: aider_ai_code
            input:
              prompt: "Fix import errors in cli.py"
              relative_editable_files: ["src/algitex/cli.py"]
              model: "gemini/gemini-2.5-pro"
            ```
        """
        from algitex.tools.docker import DockerToolManager
        from algitex.config import Config
        import json
        import os

        # Parse YAML content from step
        try:
            import yaml
            params = yaml.safe_load(step.content)
        except ImportError:
            # Fallback to simple JSON parsing if yaml not available
            params = json.loads(step.content)

        tool_name = params["tool"]
        action = params["action"]
        input_data = params.get("input", {})
        env_overrides = params.get("env", {})

        # Resolve environment variables in env_overrides
        resolved_env = {}
        for k, v in env_overrides.items():
            if isinstance(v, str) and v.startswith("$"):
                env_var = v[2:-1] if v.startswith("${") else v[1:]
                resolved_env[k] = os.getenv(env_var, v)
            else:
                resolved_env[k] = v

        # Initialize DockerToolManager (reuse if provided)
        config = Config.load()
        if docker_mgr is None:
            with DockerToolManager(config) as mgr:
                return self._execute_with_manager(tool_name, action, input_data, resolved_env, step, mgr)
        else:
            return self._execute_with_manager(tool_name, action, input_data, resolved_env, step, docker_mgr)
    
    def _execute_with_manager(self, tool_name: str, action: str, input_data: dict, env: dict, step: WorkflowStep, mgr: DockerToolManager) -> WorkflowStep:
        """Execute Docker step with given manager and parameters."""
        # Spawn if not running
        if tool_name not in mgr.list_running():
            mgr.spawn(tool_name, env=env)

        # Call the tool
        result = mgr.call_tool(tool_name, action, input_data)

        step.result = json.dumps(result, indent=2)[:2000]
        step.status = "done" if result.get("rc", 0) == 0 else "error"
        
        # Extract cost if available
        if "cost_usd" in result:
            step.cost_usd = result["cost_usd"]

        return step

    def _exec_llm(self, step: WorkflowStep, proxy_url: str) -> WorkflowStep:
        """Send prompt to LLM via proxym."""
        from algitex.tools.proxy import Proxy

        try:
            with Proxy() as proxy:
                resp = proxy.ask(step.content, context=True)
            step.result = resp.content[:2000]
            step.cost_usd = resp.cost_usd
            step.status = "done"
        except Exception as e:
            step.status = "failed"
            step.result = str(e)
        return step
