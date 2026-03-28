"""Project — the single object you need to know.

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
from typing import List, Optional

from algitex.config import Config
from algitex.tools.analysis import Analyzer, HealthReport
from algitex.tools.tickets import Tickets, Ticket
from algitex.algo import Loop
from algitex.tools.ollama import OllamaClient, OllamaService
from algitex.tools.services import ServiceChecker
from algitex.tools.autofix import AutoFix
from algitex.tools.batch import BatchProcessor, FileBatchProcessor
from algitex.tools.benchmark import ModelBenchmark, Task
from algitex.tools.ide import IDEHelper, ClaudeCodeHelper, AiderHelper, EditorIntegration
from algitex.tools.config import ConfigManager
from algitex.tools.mcp import MCPOrchestrator


class Project:
    """One project, all tools, zero boilerplate."""

    def __init__(self, path: str = ".", config: Optional[Config] = None):
        self.path = Path(path).resolve()
        self.config = config or Config.load()
        self.config.project_path = str(self.path)

        self._analyzer = Analyzer(str(self.path))
        self._tickets = Tickets(str(self.path), self.config.tickets)
        self._last_report: Optional[HealthReport] = None

        # New: progressive algorithmization loop
        self.algo = Loop(str(self.path))
        
        # New: service management and autofix
        self.services = ServiceChecker()
        self.ollama = OllamaService()
        self.autofix = AutoFix(str(self.path / "TODO.md"))
        
        # New: batch processing and benchmarking
        self.batch = FileBatchProcessor(
            ollama_client=self.ollama.client,
            output_dir=str(self.path / ".batch_results")
        )
        self.benchmark = ModelBenchmark(self.ollama.client)
        
        # New: IDE integration
        self.ide = IDEHelper()
        self.claude = ClaudeCodeHelper()
        self.aider = AiderHelper()
        self.editor = EditorIntegration()
        
        # New: configuration and MCP management
        self.config_manager = ConfigManager()
        self.mcp = MCPOrchestrator()

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
        from algitex.tools.proxy import Proxy
        from algitex.tools import discover_tools

        report = self._last_report or self.analyze(full=False)
        board = self._tickets.board()

        proxy = Proxy(self.config.proxy)
        budget = proxy.budget()
        proxy_healthy = proxy.health()
        proxy.close()

        tools = discover_tools()
        algo_report = self.algo.report()
        
        # Docker tools status
        docker_status = {"available": [], "running": []}
        try:
            from algitex.tools.docker import DockerToolManager
            docker_mgr = DockerToolManager(self.config)
            docker_status["available"] = docker_mgr.list_tools()
            docker_status["running"] = docker_mgr.list_running()
        except Exception:
            pass  # Docker tools not available

        # Cost ledger
        total_cost = sum(
            t.meta.get("cost_usd", 0) for t in self._tickets.list() if t.meta
        )

        return {
            "project": str(self.path),
            "health": {
                "grade": report.grade,
                "cc_avg": report.cc_avg,
                "vallm_pass_rate": report.vallm_pass_rate,
                "files": report.files,
                "lines": report.lines,
            },
            "tickets": {
                "open": len(board.get("open", [])),
                "in_progress": len(board.get("in_progress", [])),
                "review": len(board.get("review", [])),
                "done": len(board.get("done", [])),
                "blocked": len(board.get("blocked", [])),
            },
            "cost_ledger": {
                "total_spent_usd": total_cost,
                "budget_remaining": budget,
            },
            "algo": algo_report,
            "proxy": {"healthy": proxy_healthy},
            "tools": {name: str(s) for name, s in tools.items()},
            "docker": docker_status,
        }

    # ── Propact workflows ─────────────────────────────────

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

    # ── Convenience shortcuts ─────────────────────────────

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

    def sync(self) -> dict:
        return self._tickets.sync()

    # ── Service Management ────────────────────────────────

    def check_services(self, services: Optional[dict] = None) -> dict:
        """Check status of all services."""
        statuses = self.services.check_all(services)
        return {s.name: s.to_dict() for s in statuses}
    
    def print_service_status(self, show_details: bool = False):
        """Print service status in a formatted way."""
        statuses = self.services.check_all()
        self.services.print_status(statuses, show_details)
    
    def ensure_service(self, service: str, timeout_seconds: int = 60) -> bool:
        """Wait for a service to become healthy."""
        return self.services.wait_for_services([service], timeout_seconds)
    
    # ── AutoFix ───────────────────────────────────────────

    def fix_issues(
        self,
        limit: Optional[int] = None,
        backend: str = "auto",
        filter_file: Optional[str] = None
    ) -> dict:
        """Fix issues from TODO.md."""
        results = self.autofix.fix_all(limit=limit, backend=backend, filter_file=filter_file)
        
        # Sync with tickets system if any fixes were made
        if any(r.success for r in results):
            self.sync()
        
        return {
            "total": len(results),
            "fixed": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "results": [r.to_dict() for r in results]
        }
    
    def fix_issue(self, task_id: str, backend: str = "auto") -> Optional[dict]:
        """Fix a specific issue by task ID."""
        result = self.autofix.fix_issue(task_id, backend)
        if result and result.success:
            self.sync()
            return result.to_dict()
        return None
    
    def list_todo_tasks(self) -> list:
        """List all pending TODO tasks."""
        tasks = self.autofix.list_tasks()
        return [t.to_dict() for t in tasks]
    
    # ── Ollama Integration ─────────────────────────────────

    def check_ollama(self) -> dict:
        """Check Ollama status and available models."""
        status = self.services.check_ollama()
        return status.to_dict()
    
    def list_ollama_models(self) -> list:
        """List available Ollama models."""
        models = self.ollama.client.list_models()
        return [{"name": m.name, "size": m.size, "modified_at": m.modified_at} for m in models]
    
    def pull_ollama_model(self, model: str) -> bool:
        """Pull an Ollama model."""
        return self.ollama.ensure_model(model)
    
    def generate_with_ollama(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None
    ) -> str:
        """Generate text using Ollama."""
        response = self.ollama.client.generate(prompt, model=model, system=system)
        return str(response)
    
    # ── Batch Processing ────────────────────────────────────
    
    def batch_analyze(
        self,
        directory: str = ".",
        pattern: str = "*.py",
        parallelism: Optional[int] = None,
        rate_limit: Optional[float] = None
    ) -> dict:
        """Batch analyze files in directory."""
        # Update processor config if provided
        if parallelism:
            self.batch.parallelism = parallelism
        if rate_limit:
            self.batch.rate_limit = rate_limit
        
        # Process files
        results = self.batch.process_directory(directory, pattern)
        
        # Convert to dict
        return {
            "total": len(results),
            "successful": len([r for r in results if r.success]),
            "failed": len([r for r in results if not r.success]),
            "results": [r.to_dict() for r in results]
        }
    
    def create_batch_processor(
        self,
        worker_func,
        parallelism: int = 4,
        rate_limit: float = 2.0,
        **kwargs
    ) -> BatchProcessor:
        """Create a custom batch processor."""
        return BatchProcessor(
            worker_func=worker_func,
            parallelism=parallelism,
            rate_limit=rate_limit,
            output_dir=str(self.path / ".batch_results"),
            **kwargs
        )
    
    # ── Model Benchmarking ─────────────────────────────────
    
    def benchmark_models(
        self,
        models: List[str],
        tasks: Optional[List[str]] = None
    ) -> dict:
        """Benchmark models on tasks."""
        results = self.benchmark.compare_models(models, tasks)
        
        # Convert to dict
        return results.to_dict()
    
    def add_benchmark_task(
        self,
        task_id: str,
        name: str,
        prompt: str,
        expected_keywords: List[str]
    ):
        """Add a custom benchmark task."""
        self.benchmark.add_custom_task(
            task_id=task_id,
            name=name,
            prompt=prompt,
            expected_keywords=expected_keywords
        )
    
    def print_benchmark_results(self, results: dict, format: str = "table"):
        """Print benchmark results from dict."""
        # Convert back to BenchmarkResults
        from algitex.tools.benchmark import BenchmarkResults, TaskResult
        
        benchmark_results = BenchmarkResults()
        for r in results["results"]:
            result = TaskResult(
                model=r["model"],
                task_id=r["task_id"],
                success=r["success"],
                time_seconds=r["time_seconds"],
                tokens_estimated=r["tokens_estimated"],
                quality_score=r["quality_score"],
                response=r.get("response_preview", ""),
                error=r.get("error")
            )
            benchmark_results.results.append(result)
        
        self.benchmark.print_results(benchmark_results, format)
    
    # ── IDE Integration ─────────────────────────────────────
    
    def setup_ide(self, tool_name: str) -> bool:
        """Setup IDE tool."""
        return self.ide.setup_tool(tool_name)
    
    def fix_with_claude(
        self,
        file_path: str,
        instruction: str,
        model: str = "qwen2.5-coder:7b"
    ) -> bool:
        """Fix file using Claude Code."""
        return self.claude.fix_file(file_path, instruction, model)
    
    def fix_with_aider(
        self,
        file_path: str,
        instruction: str,
        model: str = "qwen2.5-coder:7b"
    ) -> bool:
        """Fix file using Aider."""
        return self.aider.fix_file(file_path, instruction, model)
    
    def detect_editor(self) -> Optional[str]:
        """Detect which editor is available."""
        return self.editor.detect_editor()
    
    def get_ide_status(self) -> dict:
        """Get status of all IDE tools."""
        return self.ide.get_tool_status()
    
    # ── Configuration Management ───────────────────────────
    
    def setup_configs(self, tools: List[str] = None) -> bool:
        """Setup project configurations."""
        return self.config_manager.setup_project_configs(self.path, tools)
    
    def install_continue_config(self, models: List[str] = None) -> bool:
        """Install Continue.dev configuration."""
        return self.config_manager.install_continue_config(models)
    
    def install_vscode_settings(self) -> bool:
        """Install VS Code settings."""
        return self.config_manager.install_vscode_settings(self.path)
    
    def generate_env_file(self, services: Dict[str, str] = None) -> bool:
        """Generate .env file."""
        if services is None:
            services = {
                "ollama": "http://localhost:11434",
                "litellm": "http://localhost:4000"
            }
        return self.config_manager.generate_env_file(services, self.path / ".env")
    
    # ── MCP Service Orchestration ────────────────────────────
    
    def start_mcp_services(self, services: List[str] = None) -> bool:
        """Start MCP services."""
        return self.mcp.start_all(services)
    
    def stop_mcp_services(self) -> bool:
        """Stop all MCP services."""
        return self.mcp.stop_all()
    
    def restart_mcp_service(self, service: str) -> bool:
        """Restart a specific MCP service."""
        return self.mcp.restart_service(service)
    
    def wait_for_mcp_ready(self, timeout: int = 60) -> bool:
        """Wait for MCP services to be ready."""
        return self.mcp.wait_for_ready(timeout=timeout)
    
    def get_mcp_status(self) -> dict:
        """Get MCP services status."""
        return {
            name: status.to_dict()
            for name, status in self.mcp.check_health().items()
        }
    
    def print_mcp_status(self):
        """Print MCP services status."""
        self.mcp.print_status()
    
    def generate_mcp_config(self) -> bool:
        """Generate MCP client configuration."""
        return self.mcp.generate_mcp_config(self.path / "mcp_config.json")

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
