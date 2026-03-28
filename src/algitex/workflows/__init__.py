"""Pipeline — for users who want custom workflows.

Usage:
    from algitex import Pipeline

    result = (
        Pipeline("./my-app")
        .analyze()
        .create_tickets()
        .execute(max_tickets=5)
        .validate()
        .sync("github")
        .report()
    )
"""

from __future__ import annotations

from typing import Optional

from algitex.project import Project
from algitex.config import Config
from algitex.tools.docker import DockerToolManager
from algitex.tools.telemetry import Telemetry
from algitex.tools.context import ContextBuilder
from algitex.tools.feedback import FeedbackController, FeedbackLoop


class Pipeline:
    """Composable workflow: chain steps fluently."""

    def __init__(self, path: str = ".", config: Optional[Config] = None):
        self.project = Project(path, config)
        self._steps: list[dict] = []
        self._results: dict = {}
        self.docker_mgr: Optional[DockerToolManager] = None
        
        # Initialize new modules
        self.telemetry = Telemetry(self.project.path.name)
        self.context_builder = ContextBuilder(path)
        self.feedback_controller = FeedbackController(
            self.project.config.feedback_policy if hasattr(self.project.config, 'feedback_policy') else None
        )

    def analyze(self, full: bool = True) -> Pipeline:
        """Step: analyze project health."""
        report = self.project.analyze(full=full)
        self._results["analysis"] = report
        self._steps.append({"step": "analyze", "grade": report.grade})
        return self

    def create_tickets(self) -> Pipeline:
        """Step: auto-create tickets from analysis."""
        report = self._results.get("analysis")
        if not report:
            report = self.project.analyze()
            self._results["analysis"] = report

        tickets = self.project._tickets.from_analysis(report)
        self._results["tickets_created"] = tickets
        self._steps.append({"step": "create_tickets", "count": len(tickets)})
        return self

    def execute(self, max_tickets: int = 10, tool: str = "aider-mcp") -> Pipeline:
        """Step: execute open tickets via Docker tool."""
        if not self.docker_mgr:
            self.docker_mgr = DockerToolManager(self.project.config)
        
        executor = TicketExecutor(self.docker_mgr, self.project, self.telemetry, self.context_builder, self.feedback_controller)
        result = executor.execute_tickets(tool, max_tickets)
        
        self._results["execution"] = result
        self._steps.append({"step": "execute", "tool": tool, "count": result["executed"]})
        return self

    def validate(self) -> Pipeline:
        """Step: multi-level validation (static + runtime + security)."""
        if not self.docker_mgr:
            self.docker_mgr = DockerToolManager(self.project.config)
        
        validator = TicketValidator(self.docker_mgr)
        validation_results = validator.validate_all()
        
        self._results["validation"] = validation_results
        self._steps.append({
            "step": "validate",
            "static_passed": validation_results.get("static_passed", False),
            "runtime_passed": validation_results.get("runtime_passed", False),
            "security_passed": validation_results.get("security_passed", True),
            "all_passed": validation_results.get("all_passed", False),
        })
        return self

    def sync(self, backend: Optional[str] = None) -> Pipeline:
        """Step: sync tickets to external system."""
        if backend:
            self.project.config.tickets.backend = backend
        result = self.project.sync()
        self._results["sync"] = result
        self._steps.append({"step": "sync", "backend": backend or "local"})
        return self

    def report(self) -> dict:
        """Get pipeline results including telemetry."""
        telemetry_summary = self.telemetry.summary()
        
        return {
            "project": str(self.project.path),
            "steps": self._steps,
            "results": {
                k: (v.summary() if hasattr(v, "summary") else v)
                for k, v in self._results.items()
            },
            "telemetry": telemetry_summary,
        }
    
    def finish(self) -> Pipeline:
        """Finalize pipeline run - save telemetry and push to observability."""
        self.telemetry.save()
        self.telemetry.push_to_langfuse()
        print(self.telemetry.report())
        return self


class TicketExecutor:
    """Handles ticket execution with Docker tools, telemetry, context, and feedback."""
    
    def __init__(self, docker_mgr: DockerToolManager, project: Project, 
                 telemetry: Telemetry, context_builder: ContextBuilder, 
                 feedback_controller: FeedbackController):
        self.docker_mgr = docker_mgr
        self.project = project
        self.telemetry = telemetry
        self.context_builder = context_builder
        self.feedback_controller = feedback_controller
        self.feedback_loop = FeedbackLoop(feedback_controller, project._tickets, docker_mgr)
    
    def execute_tickets(self, tool: str, max_tickets: int) -> dict:
        """Execute tickets using the specified tool."""
        executed = 0
        errors = []
        
        try:
            tickets = self._get_open_tickets(max_tickets)
            
            for ticket in tickets:
                try:
                    result = self._execute_single_ticket(tool, ticket)
                    if result["success"]:
                        executed += 1
                    else:
                        errors.append(result["error"])
                except Exception as e:
                    errors.append(f"Ticket {ticket.id}: {str(e)}")
                    
        finally:
            self.docker_mgr.teardown_all()
            
        return {"executed": executed, "errors": errors}
    
    def _get_open_tickets(self, max_tickets: int) -> list:
        """Get open tickets from the project."""
        return self.project._tickets.list(status="open")[:max_tickets]
    
    def _execute_single_ticket(self, tool: str, ticket: Ticket) -> dict:
        """Execute a single ticket with full context and telemetry."""
        # Create telemetry span
        span = self.telemetry.span(f"execute-{ticket.id}", tool)
        
        try:
            # Build rich context for the LLM
            context = self.context_builder.build(ticket)
            
            # Ensure tool is running
            if tool not in self.docker_mgr.list_running():
                self.docker_mgr.spawn(tool)
            
            # Call the tool with enhanced prompt
            result = self._call_tool_with_context(tool, ticket, context)
            
            # Update telemetry with token usage if available
            if hasattr(result, 'get'):
                span.tokens_in = result.get("tokens_in", 0)
                span.tokens_out = result.get("tokens_out", 0)
                span.cost_usd = result.get("cost_usd", 0)
                span.model = result.get("model", "")
            
            # Use feedback loop for validation and retry logic
            feedback_result = self.feedback_loop.execute_with_feedback(ticket, tool)
            
            span.finish(status="ok")
            return feedback_result
            
        except Exception as e:
            span.finish(status="error", error=str(e))
            raise
    
    def _call_tool_with_context(self, tool: str, ticket: Ticket, context) -> dict:
        """Call the appropriate Docker tool with rich context."""
        # Build enhanced prompt using context
        base_prompt = self._build_fix_prompt(ticket)
        enhanced_prompt = context.to_prompt(base_prompt)
        
        files = ticket.meta.get("files_to_modify", [])
        
        rt = self.docker_mgr._running.get(tool)
        if rt.tool.is_mcp:
            return self.docker_mgr.call_tool(tool, "aider_ai_code", {
                "prompt": enhanced_prompt,
                "relative_editable_files": files,
                "model": self.project.config.proxy.default_tier,
            })
        elif rt.tool.is_rest:
            return self.docker_mgr.call_tool(tool, "chat", {
                "model": self.project.config.proxy.default_tier,
                "messages": [{"role": "user", "content": enhanced_prompt}],
            })
    
    def _validate_with_vallm(self, ticket: dict, result: dict) -> dict:
        """Validate ticket execution with vallm."""
        validation = self.docker_mgr.call_tool(
            "vallm", "batch", {"path": "/project", "format": "json"}
        )
        
        if validation.get("passed", True):
            self._mark_ticket_done(ticket, "aider-mcp", "passed")
            return {"success": True}
        else:
            error = f"Ticket {ticket.id} failed validation"
            return {"success": False, "error": error}
    
    def _mark_ticket_done(self, ticket: Ticket, tool: str, validation: str):
        """Mark ticket as done in planfile."""
        self.docker_mgr.call_tool("planfile-mcp", "planfile_update_ticket", {
            "ticket_id": ticket.id,
            "status": "done",
            "resolution": {"tool": tool, "validation": validation},
        })
    
    def _build_fix_prompt(self, ticket: Ticket) -> str:
        """Build a fix prompt from ticket data."""
        prompt = f"Fix: {ticket.title}\n\n"
        if ticket.description:
            prompt += f"Description: {ticket.description}\n\n"
        if ticket.meta.get("files_to_modify"):
            prompt += f"Files to modify: {', '.join(ticket.meta['files_to_modify'])}\n\n"
        prompt += "Please fix this issue following the project's coding standards."
        return prompt


class TicketValidator:
    """Multi-level validation: static analysis, runtime tests, security scanning."""
    
    def __init__(self, docker_mgr: DockerToolManager):
        self.docker_mgr = docker_mgr
    
    def validate_all(self) -> dict:
        """Run all validation levels."""
        results = {
            "static_passed": True,
            "runtime_passed": True,
            "security_passed": True,
            "all_passed": True,
            "details": {}
        }
        
        # 1. Static validation with vallm
        if "vallm" in self.docker_mgr.list_tools():
            static = self.docker_mgr.call_tool(
                "vallm", "batch", {"path": "/project", "format": "json"}
            )
            results["static_passed"] = static.get("passed", True)
            results["details"]["static"] = static
        
        # 2. Runtime validation with pytest
        if "pytest" in self.docker_mgr.list_tools():
            runtime = self.docker_mgr.call_tool(
                "pytest", "python -m pytest /project/tests -v --tb=short --json-report", {}
            )
            results["runtime_passed"] = runtime.get("rc", 1) == 0
            results["details"]["runtime"] = runtime
        
        # 3. Security validation with semgrep
        if "semgrep" in self.docker_mgr.list_tools():
            security = self._run_security_scan()
            results["security_passed"] = security.get("passed", True)
            results["details"]["security"] = security
        
        # Overall result
        results["all_passed"] = all([
            results["static_passed"],
            results["runtime_passed"],
            results["security_passed"]
        ])
        
        return results
    
    def _run_security_scan(self) -> dict:
        """Run SAST with semgrep."""
        try:
            result = self.docker_mgr.call_tool(
                "semgrep", "semgrep scan /src --json --config auto", {}
            )
            import json
            findings = json.loads(result.get("stdout", "{}")).get("results", [])
            
            # Create tickets for critical findings
            critical_count = 0
            for finding in findings[:5]:  # Limit to top 5
                if finding.get("severity") == "ERROR":
                    critical_count += 1
                    # Would create ticket here via tickets manager
                    
            return {
                "passed": critical_count == 0,
                "findings": len(findings),
                "critical": critical_count
            }
        except Exception as e:
            return {"passed": False, "error": str(e)}
