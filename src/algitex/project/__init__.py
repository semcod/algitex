"""Project — the single object you need to know.

Refactored: split into functional mixins to reduce complexity.

Expanded from wronai with:
- Progressive algorithmization (Loop)
- Propact workflow execution
- Planfile-aware proxy headers (X-Planfile-Ref, X-Workflow-Ref)
- Per-ticket cost ledger
- DSL rule extraction

Usage:
    from algitex import Project

    p = Project("./my-app")
    p.analyze()                     # code2llm + vallm + redup
    p.plan(sprints=2)               # generate strategy → tickets
    p.execute()                     # llx picks model, proxym routes
    p.run_workflow("refactor.md")   # execute Propact workflow
    p.algo.discover()               # start progressive algorithmization
    p.status()                      # health + tickets + budget + algo progress
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from algitex.config import Config
from algitex.tools.analysis import Analyzer, HealthReport
from algitex.tools.tickets import Tickets, Ticket
from algitex.algo import Loop
from algitex.tools.ollama import OllamaService

from algitex.project.services import ServiceMixin
from algitex.project.autofix import AutoFixMixin
from algitex.project.ollama import OllamaMixin
from algitex.project.batch import BatchMixin
from algitex.project.benchmark import BenchmarkMixin
from algitex.project.ide import IDEMixin
from algitex.project.config import ConfigMixin
from algitex.project.mcp import MCPMixin


class Project(ServiceMixin, AutoFixMixin, OllamaMixin, BatchMixin, BenchmarkMixin,
              IDEMixin, ConfigMixin, MCPMixin):
    """One project, all tools, zero boilerplate."""

    def __init__(self, path: str = ".", config: Optional[Config] = None):
        self.path = Path(path).resolve()
        self.config = config or Config.load()
        self.config.project_path = str(self.path)

        # Lazy initialization cache
        self._components = {}
        self._last_report: Optional[HealthReport] = None

        # Initialize only essential components
        self.algo = Loop(str(self.path))
        
        # Initialize mixins that don't require heavy setup
        ServiceMixin.__init__(self)
        AutoFixMixin.__init__(self, str(self.path / "TODO.md"))
        
        # Defer heavy initialization to properties
        IDEMixin.__init__(self)
        ConfigMixin.__init__(self)
        MCPMixin.__init__(self)

    # ── Lazy properties ─────────────────────────────────────

    @property
    def _analyzer(self) -> Analyzer:
        """Lazy initialize Analyzer."""
        if "analyzer" not in self._components:
            self._components["analyzer"] = Analyzer(str(self.path))
        return self._components["analyzer"]
    
    @property
    def _tickets(self) -> Tickets:
        """Lazy initialize Tickets."""
        if "tickets" not in self._components:
            self._components["tickets"] = Tickets(str(self.path), self.config.tickets)
        return self._components["tickets"]
    
    @property
    def _ollama_service(self) -> OllamaService:
        """Lazy initialize OllamaService."""
        if "ollama_service" not in self._components:
            self._components["ollama_service"] = OllamaService()
            # Initialize dependent mixins when service is created
            OllamaMixin.__init__(self)
            BatchMixin.__init__(self, str(self.path), self._components["ollama_service"].client)
            BenchmarkMixin.__init__(self, self._components["ollama_service"].client)
        return self._components["ollama_service"]

    # ── Core workflow ─────────────────────────────────────

    def analyze(self, full: bool = True) -> HealthReport:
        """Analyze project health."""
        if full:
            self._last_report = self._analyzer.full()
        else:
            self._last_report = self._analyzer.health()
        return self._last_report

    def plan(
        self,
        sprints: int = 2,
        focus: str = "complexity",
        auto_tickets: bool = True,
    ) -> dict:
        """Generate a sprint plan from analysis results."""
        if not self._last_report:
            self._last_report = self.analyze()

        tickets_created = []
        if auto_tickets:
            tickets_created = self._tickets.from_analysis(self._last_report)

        plan = {
            "project": str(self.path),
            "grade": self._last_report.grade,
            "sprints_planned": sprints,
            "focus": focus,
            "tickets_created": len(tickets_created),
            "summary": self._last_report.summary(),
            "tickets": [t.to_dict() for t in tickets_created],
        }

        plan["strategy"] = self._generate_strategy(sprints, focus)
        return plan

    def execute(self, ticket_id: Optional[str] = None) -> dict:
        """Execute work with planfile-aware headers and cost tracking."""
        from algitex.tools.proxy import Proxy

        results = []
        proxy = Proxy(self.config.proxy)

        tickets_to_run = (
            [t for t in self._tickets.list() if t.id == ticket_id]
            if ticket_id
            else self._tickets.list(status="open")
        )

        for ticket in tickets_to_run[:10]:
            self._tickets.update(ticket.id, status="in_progress")

            prompt = self._build_prompt(ticket)
            tier = self._select_tier(ticket)

            # Planfile-aware headers
            response = proxy.ask(
                prompt,
                tier=tier,
                context=True,
                planfile_ref=f"{self.path.name}/current/{ticket.id}",
            )

            # Track cost per ticket
            if "[proxy error" not in response.content:
                cost_meta = {
                    "model": response.model,
                    "cost_usd": response.cost_usd,
                    "elapsed_ms": response.elapsed_ms,
                    "tier": response.tier,
                }
                self._tickets.update(ticket.id, status="review", meta=cost_meta)

                # Feed trace to algo loop
                self.algo.add_trace(
                    prompt=prompt,
                    response=response.content,
                    **cost_meta,
                )

                results.append({
                    "ticket": ticket.id,
                    "status": "review",
                    **cost_meta,
                })
            else:
                self._tickets.update(ticket.id, status="blocked")
                results.append({
                    "ticket": ticket.id,
                    "status": "blocked",
                    "error": response.content,
                })

        proxy.close()
        return {"executed": len(results), "results": results}

    def status(self) -> dict:
        """Full project status: health + tickets + budget + algo progress."""
        return {
            "project": str(self.path),
            "health": self._status_health(),
            "tickets": self._status_tickets(),
            "infra": self._status_infra(),
            "algo": self._status_algo(),
        }

    def _status_health(self) -> dict:
        """Get project health metrics."""
        report = self._last_report or self.analyze(full=False)
        return {
            "grade": report.grade,
            "cc_avg": report.cc_avg,
            "vallm_pass_rate": report.vallm_pass_rate,
            "files": report.files,
            "lines": report.lines,
        }

    def _status_tickets(self) -> dict:
        """Get ticket board status."""
        board = self._tickets.board()
        return {
            "open": len(board.get("open", [])),
            "in_progress": len(board.get("in_progress", [])),
            "review": len(board.get("review", [])),
            "done": len(board.get("done", [])),
            "blocked": len(board.get("blocked", [])),
        }

    def _status_infra(self) -> dict:
        """Get infrastructure status (proxy, docker, tools, costs)."""
        from algitex.tools.proxy import Proxy
        from algitex.tools import discover_tools

        # Proxy status
        proxy = Proxy(self.config.proxy)
        budget = proxy.budget()
        proxy_healthy = proxy.health()
        proxy.close()

        # Docker status
        docker_status = {"available": [], "running": []}
        try:
            from algitex.tools.docker import DockerToolManager
            docker_mgr = DockerToolManager(self.config)
            docker_status["available"] = docker_mgr.list_tools()
            docker_status["running"] = docker_mgr.list_running()
        except Exception:
            pass  # Docker tools not available

        # Tools status
        tools = discover_tools()

        # Cost ledger
        total_cost = sum(
            t.meta.get("cost_usd", 0) for t in self._tickets.list() if t.meta
        )

        return {
            "proxy": {"healthy": proxy_healthy},
            "docker": docker_status,
            "tools": {name: str(s) for name, s in tools.items()},
            "cost_ledger": {
                "total_spent_usd": total_cost,
                "budget_remaining": budget,
            },
        }

    def _status_algo(self) -> dict:
        """Get progressive algorithmization status."""
        return self.algo.report()

    def run_workflow(self, workflow_path: str, *, dry_run: bool = False) -> dict:
        """Execute a Propact Markdown workflow."""
        from algitex.propact import Workflow

        wf = Workflow(workflow_path)
        errors = wf.validate()
        if errors:
            return {"success": False, "errors": errors}

        result = wf.execute(dry_run=dry_run, proxy_url=self.config.proxy.url)

        # Create tickets for failed steps
        for step in result.steps:
            if step.status == "failed":
                self._tickets.add(
                    f"Workflow step failed: {step.title}",
                    description=step.result[:500],
                    priority="high",
                    type="bug",
                    source="propact",
                    tags=["workflow", workflow_path],
                )

        return {
            "success": result.success,
            "title": result.title,
            "steps_done": result.steps_done,
            "steps_failed": result.steps_failed,
            "total_cost_usd": result.total_cost_usd,
            "elapsed_ms": result.total_elapsed_ms,
        }

    def ask(self, prompt: str, **kwargs) -> str:
        """Quick LLM query with planfile-aware routing."""
        from algitex.tools.proxy import Proxy

        with Proxy(self.config.proxy) as proxy:
            resp = proxy.ask(prompt, **kwargs)
            # Feed to algo loop
            self.algo.add_trace(
                prompt=prompt,
                response=resp.content,
                model=resp.model,
                cost_usd=resp.cost_usd,
            )
            return resp.content

    def add_ticket(self, title: str, **kwargs) -> Ticket:
        return self._tickets.add(title, **kwargs)

    def generate_todo(self, filename: str = "TODO.md") -> dict:
        """Generate TODO.md from analysis results.
        
        Creates a TODO.md file with code issues found during analysis.
        Uses the last analysis report if available, otherwise runs a new analysis.
        
        Args:
            filename: Name of the TODO file to create (default: TODO.md)
            
        Returns:
            dict with count of issues created and the filename
        """
        from pathlib import Path
        
        # Get analysis report
        if not self._last_report:
            self.analyze()
        
        report = self._last_report
        issues = []
        
        # Add issues from complexity hotspots (use god_functions if available)
        hotspots = getattr(report, 'complexity_hotspots', None) or getattr(report, 'god_functions', [])
        for hotspot in hotspots[:5]:
            if isinstance(hotspot, dict):
                issues.append({
                    "description": f"Refactor high complexity function {hotspot.get('function', 'unknown')} (CC={hotspot.get('complexity', 0)})",
                    "file": hotspot.get("file", ""),
                    "line": hotspot.get("line", 1),
                    "priority": "high" if hotspot.get("complexity", 0) > 10 else "normal"
                })
            else:
                # hotspot is a string (god_functions format)
                issues.append({
                    "description": f"Refactor complex function: {hotspot}",
                    "file": str(hotspot).split(":")[0] if ":" in str(hotspot) else "",
                    "line": 1,
                    "priority": "normal"
                })
        
        # Add generic code quality issues
        generic_issues = [
            {"description": "Add type hints to all public functions", "file": "main.py", "line": 1, "priority": "normal"},
            {"description": "Add docstrings to all public functions", "file": "main.py", "line": 1, "priority": "normal"},
        ]
        
        for issue in generic_issues:
            if not any(i["file"] == issue["file"] and i["line"] == issue["line"] for i in issues):
                issues.append(issue)
        
        # Write TODO.md
        todo_path = self.path / filename
        with open(todo_path, 'w') as f:
            f.write("# TODO - Code Issues\n\n")
            f.write(f"Generated from analysis (Grade: {report.grade})\n\n")
            f.write("## Current Issues\n\n")
            for i, issue in enumerate(issues, 1):
                priority = issue.get("priority", "normal")
                file_path = issue.get("file", "")
                line = issue.get("line", "")
                desc = issue["description"]
                f.write(f"- [ ] {file_path}:{line} - {desc} [priority:{priority}]\n")
        
        return {
            "filename": str(todo_path),
            "count": len(issues),
            "grade": report.grade
        }

    # ── Private helpers ───────────────────────────────────

    def _build_prompt(self, ticket: Ticket) -> str:
        return (
            f"Task: {ticket.title}\n"
            f"Type: {ticket.type}\n"
            f"Priority: {ticket.priority}\n"
            f"Description: {ticket.description or 'See title'}\n"
            f"Project: {self.path.name}\n"
            f"Instructions: Provide a concrete solution."
        )

    def _select_tier(self, ticket: Ticket) -> str:
        mapping = {
            "critical": "deep",
            "high": "complex",
            "normal": "standard",
            "low": "cheap",
        }
        return mapping.get(ticket.priority, "standard")

    def _generate_strategy(self, sprints: int, focus: str) -> Optional[dict]:
        import shutil, subprocess, json
        if not shutil.which("planfile"):
            return None
        try:
            result = subprocess.run(
                ["planfile", "strategy", "generate", str(self.path),
                 "--sprints", str(sprints), "--focus", focus, "--json"],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception:
            pass
        return None


# Backward compatibility exports
__all__ = ["Project"]
