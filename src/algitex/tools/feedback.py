"""Feedback loop controller for algitex pipelines."""

from __future__,annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any, List, Tuple


class FailureStrategy(Enum):
    RETRY = "retry"           # Retry with different model/params
    REPLAN = "replan"         # Re-analyze and generate new fix
    ESCALATE = "escalate"     # Create ticket, notify human
    SKIP = "skip"             # Mark as skipped, continue


@dataclass
class FeedbackPolicy:
    """Policy configuration for feedback handling."""
    max_retries: int = 3
    retry_escalation: Optional[List[str]] = None  # ["cheap", "balanced", "premium"]
    auto_replan: bool = True
    require_approval_for: Optional[List[str]] = None  # ["critical", "breaking"]
    notify_on_failure: bool = True

    def __post_init__(self):
        if self.retry_escalation is None:
            self.retry_escalation = [
                "ollama/qwen2.5-coder:7b",
                "gemini/gemini-2.5-pro",
                "claude-sonnet-4-20250514",
            ]
        if self.require_approval_for is None:
            self.require_approval_for = ["critical"]


class FeedbackController:
    """Orchestrate retry/replan/escalate decisions."""

    def __init__(self, policy: Optional[FeedbackPolicy] = None):
        self.policy = policy or FeedbackPolicy()
        self._attempt = 0
        self._ticket_attempts: Dict[str, int] = {}

    def on_validation_failure(self, ticket: Dict[str, Any], validation_result: Dict[str, Any], 
                              context: Dict[str, Any]) -> Tuple[FailureStrategy, Dict[str, Any]]:
        """Decide what to do when vallm validation fails.

        Returns:
            (strategy, params) — what Pipeline should do next.
        """
        ticket_id = ticket.get("id", "unknown")
        self._ticket_attempts[ticket_id] = self._ticket_attempts.get(ticket_id, 0) + 1
        current_attempt = self._ticket_attempts[ticket_id]

        # Strategy 1: Retry with escalated model
        if current_attempt <= self.policy.max_retries:
            model_idx = min(current_attempt - 1, len(self.policy.retry_escalation) - 1)
            next_model = self.policy.retry_escalation[model_idx]
            return FailureStrategy.RETRY, {
                "model": next_model,
                "attempt": current_attempt,
                "feedback": self._extract_feedback(validation_result),
            }

        # Strategy 2: Re-plan (re-analyze, generate new approach)
        if self.policy.auto_replan and current_attempt == self.policy.max_retries + 1:
            return FailureStrategy.REPLAN, {
                "reason": "All retry models failed",
                "errors": validation_result.get("errors", []),
            }

        # Strategy 3: Escalate to human
        return FailureStrategy.ESCALATE, {
            "ticket_id": ticket_id,
            "attempts": current_attempt,
            "last_errors": validation_result.get("errors", []),
        }

    def on_success(self, ticket: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Reset attempt counter on success."""
        ticket_id = ticket.get("id", "unknown")
        self._ticket_attempts[ticket_id] = 0
        return result

    def needs_approval(self, ticket: Dict[str, Any]) -> bool:
        """Check if ticket requires human approval before execution."""
        priority = ticket.get("priority", "normal")
        return priority in self.policy.require_approval_for

    def _extract_feedback(self, validation_result: Dict[str, Any]) -> str:
        """Turn validation errors into actionable feedback for LLM."""
        errors = validation_result.get("errors", [])
        if not errors:
            return "Previous attempt had quality issues. Try a different approach."
        
        feedback_lines = []
        for e in errors[:5]:  # Limit to top 5 errors
            rule = e.get('rule', 'unknown')
            message = e.get('message', '')
            if message:
                feedback_lines.append(f"- {rule}: {message}")
        
        return "Fix these specific issues:\n" + "\n".join(feedback_lines)


class FeedbackLoop:
    """Integrates feedback controller into the pipeline execution."""
    
    def __init__(self, controller: FeedbackController, tickets_manager, docker_mgr):
        self.controller = controller
        self.tickets = tickets_manager
        self.docker_mgr = docker_mgr
        self._executor = None  # Will be set by Pipeline to avoid circular import
        
    def execute_with_feedback(self, ticket: Dict[str, Any], tool: str = "aider-mcp") -> Dict[str, Any]:
        """Execute a ticket with automatic retry/replan/escalate logic."""
        # Check if approval is needed
        if self.controller.needs_approval(ticket):
            approval_ticket = {
                "title": f"Approve: {ticket['title']}",
                "description": f"Ticket requires approval: {ticket.get('description', '')}",
                "priority": "high",
                "status": "open",
                "source": {"tool": "algitex", "type": "approval_request"},
                "related_ticket": ticket.get("id")
            }
            self.tickets.add(approval_ticket)
            return {"status": "awaiting_approval", "ticket_id": ticket.get("id")}
        
        # Main execution loop
        current_tool = tool
        while True:
            # Execute the ticket
            result = self._execute_single(ticket, current_tool)
            
            # Validate result
            validation = self._validate_result(result)
            
            if validation.get("passed", True):
                # Success - update ticket and return
                self._mark_ticket_done(ticket, tool, validation)
                return self.controller.on_success(ticket, result)
            
            # Failure - decide next action
            strategy, params = self.controller.on_validation_failure(
                ticket, validation, {"result": result}
            )
            
            if strategy == FailureStrategy.RETRY:
                # Update tool parameters for retry
                current_tool = params.get("model", current_tool)
                ticket["feedback"] = params.get("feedback", "")
                continue
                
            elif strategy == FailureStrategy.REPLAN:
                # Trigger re-analysis
                return {
                    "status": "replan_needed",
                    "reason": params.get("reason"),
                    "errors": params.get("errors", [])
                }
                
            elif strategy == FailureStrategy.ESCALATE:
                # Create escalation ticket
                escalation_ticket = {
                    "title": f"Manual fix needed: {ticket['title']}",
                    "description": f"Failed after {params.get('attempts')} attempts. Errors: {params.get('last_errors')}",
                    "priority": "critical",
                    "status": "open",
                    "source": {"tool": "algitex", "type": "escalation"},
                    "original_ticket": ticket.get("id")
                }
                self.tickets.add(escalation_ticket)
                return {
                    "status": "escalated",
                    "escalation_ticket": escalation_ticket,
                    **params
                }
                
            elif strategy == FailureStrategy.SKIP:
                self._mark_ticket_skipped(ticket, "Skipped after multiple failures")
                return {"status": "skipped", "ticket_id": ticket.get("id")}
    
    def _execute_single(self, ticket: Dict[str, Any], tool: str) -> Dict[str, Any]:
        """Execute a single ticket attempt."""
        # Ensure tool is running
        if tool not in self.docker_mgr.list_running():
            self.docker_mgr.spawn(tool)
        
        # Build basic prompt
        prompt = f"Fix: {ticket.get('title', '')}\n\n"
        if ticket.get('description'):
            prompt += f"Description: {ticket['description']}\n\n"
        if ticket.get('files_to_modify'):
            prompt += f"Files to modify: {', '.join(ticket['files_to_modify'])}\n\n"
        if ticket.get('feedback'):
            prompt += f"Previous feedback: {ticket['feedback']}\n\n"
        prompt += "Please fix this issue following the project's coding standards."
        
        files = ticket.get("files_to_modify", [])
        
        # Call the tool
        rt = self.docker_mgr._running.get(tool)
        if rt.tool.is_mcp:
            result = self.docker_mgr.call_tool(tool, "aider_ai_code", {
                "prompt": prompt,
                "relative_editable_files": files,
                "model": "claude-sonnet-4-20250514",  # Default model
            })
        elif rt.tool.is_rest:
            result = self.docker_mgr.call_tool(tool, "chat", {
                "model": "claude-sonnet-4-20250514",
                "messages": [{"role": "user", "content": prompt}],
            })
        else:
            # For CLI tools
            result = {"status": "executed", "tool": tool}
            
        return result
    
    def _validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the execution result."""
        # Check if vallm is available for validation
        if "vallm" in self.docker_mgr.list_tools():
            validation = self.docker_mgr.call_tool(
                "vallm", "batch", {"path": "/project", "format": "json"}
            )
            return validation
        
        # Default to passed if no validation available
        return {"passed": True}
    
    def _mark_ticket_done(self, ticket: Dict[str, Any], tool: str, validation: Dict[str, Any]):
        """Mark ticket as done."""
        self.docker_mgr.call_tool("planfile-mcp", "planfile_update_ticket", {
            "ticket_id": ticket["id"],
            "status": "done",
            "resolution": {
                "tool": tool,
                "validation": validation.get("status", "unknown"),
                "attempts": self.controller._ticket_attempts.get(ticket.get("id"), 0)
            },
        })
    
    def _mark_ticket_skipped(self, ticket: Dict[str, Any], reason: str):
        """Mark ticket as skipped."""
        self.docker_mgr.call_tool("planfile-mcp", "planfile_update_ticket", {
            "ticket_id": ticket["id"],
            "status": "skipped",
            "resolution": {"reason": reason},
        })
