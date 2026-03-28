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


class Pipeline:
    """Composable workflow: chain steps fluently."""

    def __init__(self, path: str = ".", config: Optional[Config] = None):
        self.project = Project(path, config)
        self._steps: list[dict] = []
        self._results: dict = {}
        self.docker_mgr: Optional[DockerToolManager] = None

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
        
        result = self._execute_with_docker(tool, max_tickets)
        self._results["execution"] = result
        self._steps.append({"step": "execute", "tool": tool, "count": result["executed"]})
        return self

    def validate(self) -> Pipeline:
        """Step: re-analyze to check improvements."""
        report = self.project.analyze(full=True)
        self._results["validation"] = report
        prev = self._results.get("analysis")
        improved = prev and report.cc_avg < prev.cc_avg
        self._steps.append({
            "step": "validate",
            "grade": report.grade,
            "improved": improved,
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
        """Get pipeline results."""
        return {
            "project": str(self.project.path),
            "steps": self._steps,
            "results": {
                k: (v.summary() if hasattr(v, "summary") else v)
                for k, v in self._results.items()
            },
        }

    def _execute_with_docker(self, tool: str, max_tickets: int) -> dict:
        """Execute tickets using Docker tools."""
        executed = 0
        errors = []
        
        try:
            # Get open tickets
            tickets = self.project._tickets.list(status="open")[:max_tickets]
            
            for ticket in tickets:
                try:
                    # Spawn the tool if not running
                    if tool not in self.docker_mgr.list_running():
                        self.docker_mgr.spawn(tool)
                    
                    # Build prompt from ticket
                    prompt = self._build_fix_prompt(ticket)
                    files = ticket.get("files_to_modify", [])
                    
                    # Call tool based on its transport type
                    rt = self.docker_mgr._running.get(tool)
                    if rt.tool.is_mcp:
                        result = self.docker_mgr.call_tool(tool, "aider_ai_code", {
                            "prompt": prompt,
                            "relative_editable_files": files,
                            "model": self.project.config.proxy.default_tier,
                        })
                    elif rt.tool.is_rest:
                        result = self.docker_mgr.call_tool(tool, "chat", {
                            "model": self.project.config.proxy.default_tier,
                            "messages": [{"role": "user", "content": prompt}],
                        })
                    
                    # Validate with vallm if available
                    if "vallm" in self.docker_mgr.list_tools():
                        validation = self.docker_mgr.call_tool(
                            "vallm", "batch", {"path": "/project", "format": "json"}
                        )
                        if validation.get("passed", True):
                            # Update ticket status
                            self.docker_mgr.call_tool("planfile-mcp", "planfile_update_ticket", {
                                "ticket_id": ticket["id"],
                                "status": "done",
                                "resolution": {"tool": tool, "validation": "passed"},
                            })
                            executed += 1
                        else:
                            errors.append(f"Ticket {ticket['id']} failed validation")
                    else:
                        executed += 1
                        
                except Exception as e:
                    errors.append(f"Ticket {ticket['id']}: {str(e)}")
                    
        finally:
            # Cleanup Docker containers
            if self.docker_mgr:
                self.docker_mgr.teardown_all()
                
        return {"executed": executed, "errors": errors}
    
    def _build_fix_prompt(self, ticket: dict) -> str:
        """Build a fix prompt from ticket data."""
        prompt = f"Fix: {ticket.get('title', '')}\n\n"
        if ticket.get('description'):
            prompt += f"Description: {ticket['description']}\n\n"
        if ticket.get('files_to_modify'):
            prompt += f"Files to modify: {', '.join(ticket['files_to_modify'])}\n\n"
        prompt += "Please fix this issue following the project's coding standards."
        return prompt
