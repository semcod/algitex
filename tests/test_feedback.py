"""Unit tests for algitex feedback module."""

import pytest
from unittest.mock import MagicMock, patch, call
from algitex.tools.feedback import (
    FailureStrategy, FeedbackPolicy, FeedbackController, 
    FeedbackLoop
)


class TestFailureStrategy:
    """Test the FailureStrategy enum."""
    
    def test_strategies(self):
        """Test all strategy values."""
        assert FailureStrategy.RETRY.value == "retry"
        assert FailureStrategy.REPLAN.value == "replan"
        assert FailureStrategy.ESCALATE.value == "escalate"
        assert FailureStrategy.SKIP.value == "skip"


class TestFeedbackPolicy:
    """Test the FeedbackPolicy class."""
    
    def test_default_policy(self):
        """Test default policy values."""
        policy = FeedbackPolicy()
        
        assert policy.max_retries == 3
        assert len(policy.retry_escalation) == 3
        assert "ollama/qwen2.5-coder:7b" in policy.retry_escalation
        assert "gemini/gemini-2.5-pro" in policy.retry_escalation
        assert "claude-sonnet-4-20250514" in policy.retry_escalation
        assert policy.auto_replan is True
        assert policy.require_approval_for == ["critical"]
        assert policy.notify_on_failure is True
    
    def test_custom_policy(self):
        """Test custom policy values."""
        policy = FeedbackPolicy(
            max_retries=5,
            retry_escalation=["model1", "model2"],
            auto_replan=False,
            require_approval_for=["critical", "breaking"],
            notify_on_failure=False
        )
        
        assert policy.max_retries == 5
        assert policy.retry_escalation == ["model1", "model2"]
        assert policy.auto_replan is False
        assert policy.require_approval_for == ["critical", "breaking"]
        assert policy.notify_on_failure is False


class TestFeedbackController:
    """Test the FeedbackController class."""
    
    def test_controller_creation(self):
        """Test creating controller with default policy."""
        controller = FeedbackController()
        assert controller.policy.max_retries == 3
        assert controller._attempt == 0
        assert controller._ticket_attempts == {}
    
    def test_controller_custom_policy(self):
        """Test creating controller with custom policy."""
        policy = FeedbackPolicy(max_retries=5)
        controller = FeedbackController(policy)
        assert controller.policy.max_retries == 5
    
    def test_needs_approval(self):
        """Test checking if approval is needed."""
        controller = FeedbackController()
        
        # Critical ticket needs approval
        critical_ticket = {"priority": "critical"}
        assert controller.needs_approval(critical_ticket) is True
        
        # Breaking ticket doesn't need approval by default
        breaking_ticket = {"priority": "breaking"}
        assert controller.needs_approval(breaking_ticket) is False
        
        # Normal ticket doesn't need approval
        normal_ticket = {"priority": "normal"}
        assert controller.needs_approval(normal_ticket) is False
        
        # Missing priority defaults to no approval
        no_priority = {}
        assert controller.needs_approval(no_priority) is False
    
    def test_extract_feedback(self):
        """Test extracting feedback from validation errors."""
        controller = FeedbackController()
        
        # No errors
        validation = {"errors": []}
        feedback = controller._extract_feedback(validation)
        assert "quality issues" in feedback
        
        # With errors
        validation = {
            "errors": [
                {"rule": "complexity", "message": "Function too complex"},
                {"rule": "naming", "message": "Variable name unclear"},
                {"rule": "style", "message": "Missing docstring"}
            ]
        }
        feedback = controller._extract_feedback(validation)
        assert "complexity: Function too complex" in feedback
        assert "naming: Variable name unclear" in feedback
        assert "style: Missing docstring" in feedback
    
    def test_on_validation_failure_retry(self):
        """Test retry strategy on validation failure."""
        policy = FeedbackPolicy(max_retries=2, retry_escalation=["model1", "model2"])
        controller = FeedbackController(policy)
        
        ticket = {"id": "ticket1"}
        validation = {"errors": [{"rule": "test", "message": "Error"}]}
        
        # First failure - should retry with first model
        strategy, params = controller.on_validation_failure(ticket, validation, {})
        assert strategy == FailureStrategy.RETRY
        assert params["model"] == "model1"
        assert params["attempt"] == 1
        assert "feedback" in params
        
        # Second failure - should retry with second model
        strategy, params = controller.on_validation_failure(ticket, validation, {})
        assert strategy == FailureStrategy.RETRY
        assert params["model"] == "model2"
        assert params["attempt"] == 2
        
        # Third failure - should move to replan
        strategy, params = controller.on_validation_failure(ticket, validation, {})
        assert strategy == FailureStrategy.REPLAN
        assert params["reason"] == "All retry models failed"
    
    def test_on_validation_failure_escalate(self):
        """Test escalation when retries exhausted."""
        policy = FeedbackPolicy(max_retries=1, auto_replan=False)
        controller = FeedbackController(policy)
        
        ticket = {"id": "ticket1"}
        validation = {"errors": [{"rule": "test", "message": "Error"}]}
        
        # First failure - retry
        controller.on_validation_failure(ticket, validation, {})
        
        # Second failure - escalate (no auto_replan)
        strategy, params = controller.on_validation_failure(ticket, validation, {})
        assert strategy == FailureStrategy.ESCALATE
        assert params["ticket_id"] == "ticket1"
        assert params["attempts"] == 2
    
    def test_on_success(self):
        """Test handling successful validation."""
        controller = FeedbackController()
        
        ticket = {"id": "ticket1"}
        result = {"status": "success"}
        
        # First, fail once to increment counter
        controller.on_validation_failure(ticket, {"errors": []}, {})
        assert controller._ticket_attempts.get("ticket1") == 1
        
        # Then succeed - should reset counter
        returned = controller.on_success(ticket, result)
        assert returned is result
        assert controller._ticket_attempts.get("ticket1") == 0
    
    def test_multiple_tickets(self):
        """Test tracking attempts for multiple tickets."""
        controller = FeedbackController()
        
        ticket1 = {"id": "ticket1"}
        ticket2 = {"id": "ticket2"}
        validation = {"errors": [{"rule": "test", "message": "Error"}]}
        
        # Fail ticket1 twice
        controller.on_validation_failure(ticket1, validation, {})
        controller.on_validation_failure(ticket1, validation, {})
        
        # Fail ticket2 once
        controller.on_validation_failure(ticket2, validation, {})
        
        # Check individual counters
        assert controller._ticket_attempts["ticket1"] == 2
        assert controller._ticket_attempts["ticket2"] == 1


class TestFeedbackLoop:
    """Test the FeedbackLoop class."""
    
    @pytest.fixture
    def mock_deps(self):
        """Create mocked dependencies for feedback loop."""
        controller = MagicMock()
        tickets = MagicMock()
        docker_mgr = MagicMock()
        return controller, tickets, docker_mgr
    
    @pytest.fixture
    def mock_loop(self, mock_deps):
        """Create a feedback loop with mocked dependencies."""
        controller, tickets, docker_mgr = mock_deps
        
        loop = FeedbackLoop(controller, tickets, docker_mgr)
        loop.controller = controller
        loop.tickets = tickets
        loop.docker_mgr = docker_mgr
        
        return loop
    
    def test_loop_creation(self, mock_loop):
        """Test creating feedback loop."""
        assert mock_loop.controller is not None
        assert mock_loop.tickets is not None
        assert mock_loop.docker_mgr is not None
    
    def test_needs_approval_flow(self, mock_loop):
        """Test flow when approval is needed."""
        ticket = {"id": "ticket1", "title": "Critical fix", "priority": "critical"}
        
        mock_loop.controller.needs_approval.return_value = True
        
        result = mock_loop.execute_with_feedback(ticket, "aider-mcp")
        
        assert result["status"] == "awaiting_approval"
        mock_loop.tickets.add.assert_called_once()
        
        # Check approval ticket was created
        call_args = mock_loop.tickets.add.call_args[0][0]
        assert "Approve: Critical fix" in call_args["title"]
        assert call_args["priority"] == "high"
    
    def test_successful_execution(self, mock_loop, mock_deps):
        """Test successful execution flow."""
        ticket = {"id": "ticket1", "title": "Simple fix"}
        
        # Mock approval not needed
        mock_loop.controller.needs_approval.return_value = False
        
        # Mock successful execution and validation
        with patch.object(mock_loop, '_execute_single', return_value={"status": "executed"}):
            with patch.object(mock_loop, '_validate_result', return_value={"passed": True}):
                mock_loop.controller.on_success.return_value = {"status": "success"}
                
                result = mock_loop.execute_with_feedback(ticket, "aider-mcp")
                
                assert result["status"] == "success"
    
    def test_retry_flow(self, mock_loop, mock_deps):
        """Test retry flow on validation failure."""
        ticket = {"id": "ticket1", "title": "Complex fix"}
        
        # Setup mocks
        mock_loop.controller.needs_approval.return_value = False
        
        # Track validation calls to alternate between failure and success
        call_count = [0]
        def mock_validate(result):
            call_count[0] += 1
            if call_count[0] == 1:
                return {"passed": False, "errors": []}  # First call fails
            return {"passed": True}  # Second call succeeds
        
        with patch.object(mock_loop, '_execute_single', return_value={"status": "executed"}):
            with patch.object(mock_loop, '_validate_result', side_effect=mock_validate):
                # First call - retry
                mock_loop.controller.on_validation_failure.return_value = (
                    FailureStrategy.RETRY, 
                    {"model": "better-model", "feedback": "Fix this"}
                )
                mock_loop.controller.on_success.return_value = {"status": "success"}
                
                result = mock_loop.execute_with_feedback(ticket, "aider-mcp")
                
                # Should have attempted execution
                assert "feedback" in ticket
                assert ticket["feedback"] == "Fix this"
                assert result["status"] == "success"
    
    def test_escalate_flow(self, mock_loop, mock_deps):
        """Test escalation flow."""
        ticket = {"id": "ticket1", "title": "Impossible fix"}
        
        # Setup mocks
        mock_loop.controller.needs_approval.return_value = False
        
        with patch.object(mock_loop, '_execute_single', return_value={"status": "executed"}):
            with patch.object(mock_loop, '_validate_result', return_value={"passed": False, "errors": []}):
                # Return escalate strategy
                mock_loop.controller.on_validation_failure.return_value = (
                    FailureStrategy.ESCALATE,
                    {"attempts": 3, "last_errors": ["Cannot fix"]}
                )
                
                result = mock_loop.execute_with_feedback(ticket, "aider-mcp")
                
                assert result["status"] == "escalated"
                assert result["attempts"] == 3
                mock_loop.tickets.add.assert_called_once()
                
                # Check escalation ticket
                call_args = mock_loop.tickets.add.call_args[0][0]
                assert "Manual fix needed" in call_args["title"]
                assert call_args["priority"] == "critical"
    
    def test_skip_flow(self, mock_loop, mock_deps):
        """Test skip flow."""
        ticket = {"id": "ticket1", "title": "Minor fix"}
        
        # Setup mocks
        mock_loop.controller.needs_approval.return_value = False
        
        with patch.object(mock_loop, '_execute_single', return_value={"status": "executed"}):
            with patch.object(mock_loop, '_validate_result', return_value={"passed": False, "errors": []}):
                # Return skip strategy
                mock_loop.controller.on_validation_failure.return_value = (
                    FailureStrategy.SKIP,
                    {}
                )
                
                result = mock_loop.execute_with_feedback(ticket, "aider-mcp")
                
                assert result["status"] == "skipped"
    
    def test_execute_single_mcp(self, mock_loop):
        """Test executing single ticket with MCP tool."""
        ticket = {
            "id": "ticket1",
            "title": "Fix bug",
            "description": "Critical issue",
            "files_to_modify": ["main.py"]
        }
        
        # Mock Docker tool
        mock_tool = MagicMock()
        mock_tool.is_mcp = True
        mock_tool.is_rest = False
        
        mock_rt = MagicMock()
        mock_rt.tool = mock_tool
        
        mock_loop.docker_mgr.list_running.return_value = ["aider-mcp"]
        mock_loop.docker_mgr._running.get.return_value = mock_rt
        mock_loop.docker_mgr.call_tool.return_value = {
            "status": "success",
            "tokens_in": 100,
            "tokens_out": 50
        }
        
        result = mock_loop._execute_single(ticket, "aider-mcp")
        
        assert result["status"] == "success"
        mock_loop.docker_mgr.call_tool.assert_called_once()
        
        # Check call arguments - call_tool(tool, method, kwargs_dict)
        call_args = mock_loop.docker_mgr.call_tool.call_args
        assert call_args[0][0] == "aider-mcp"  # tool name
        assert call_args[0][1] == "aider_ai_code"  # method
        kwargs = call_args[0][2]  # kwargs dict
        assert "Fix bug" in kwargs["prompt"]
        assert "main.py" in kwargs["relative_editable_files"]
    
    def test_execute_single_rest(self, mock_loop):
        """Test executing single ticket with REST tool."""
        ticket = {
            "id": "ticket1",
            "title": "Fix bug",
            "files_to_modify": ["main.py"]
        }
        
        # Mock Docker tool
        mock_tool = MagicMock()
        mock_tool.is_mcp = False
        mock_tool.is_rest = True
        
        mock_rt = MagicMock()
        mock_rt.tool = mock_tool
        
        mock_loop.docker_mgr.list_running.return_value = ["ollama"]
        mock_loop.docker_mgr._running.get.return_value = mock_rt
        mock_loop.docker_mgr.call_tool.return_value = {"status": "success"}
        
        result = mock_loop._execute_single(ticket, "ollama")
        
        assert result["status"] == "success"
        
        # Check call arguments for REST API - call_tool(tool, method, kwargs_dict)
        call_args = mock_loop.docker_mgr.call_tool.call_args
        assert call_args[0][1] == "chat"  # method
        kwargs = call_args[0][2]  # kwargs dict
        assert "messages" in kwargs
        assert kwargs["messages"][0]["role"] == "user"
    
    def test_execute_single_with_feedback(self, mock_loop):
        """Test executing with previous feedback."""
        ticket = {
            "id": "ticket1",
            "title": "Fix bug",
            "feedback": "Previous attempt failed because of complexity"
        }
        
        # Mock setup
        mock_tool = MagicMock()
        mock_tool.is_mcp = True
        mock_tool.is_rest = False
        
        mock_rt = MagicMock()
        mock_rt.tool = mock_tool
        
        mock_loop.docker_mgr.list_running.return_value = ["aider-mcp"]
        mock_loop.docker_mgr._running.get.return_value = mock_rt
        mock_loop.docker_mgr.call_tool.return_value = {"status": "success"}
        
        result = mock_loop._execute_single(ticket, "aider-mcp")
        
        # Check that feedback was included in prompt
        mock_loop.docker_mgr.call_tool.assert_called_once()
        call_args = mock_loop.docker_mgr.call_tool.call_args
        prompt = call_args[0][2]["prompt"]
        assert "Previous feedback" in prompt
        assert "Previous attempt failed because of complexity" in prompt
    
    def test_validate_result_with_vallm(self, mock_loop):
        """Test validation with vallm available."""
        mock_loop.docker_mgr.list_tools.return_value = ["vallm", "aider-mcp"]
        mock_loop.docker_mgr.call_tool.return_value = {
            "passed": True,
            "score": 0.95
        }
        
        result = mock_loop._validate_result({"status": "executed"})
        
        assert result["passed"] is True
        assert result["score"] == 0.95
        mock_loop.docker_mgr.call_tool.assert_called_once_with(
            "vallm", "batch", {"path": "/project", "format": "json"}
        )
    
    def test_validate_result_without_vallm(self, mock_loop):
        """Test validation without vallm."""
        mock_loop.docker_mgr.list_tools.return_value = ["aider-mcp"]
        
        result = mock_loop._validate_result({"status": "executed"})
        
        assert result["passed"] is True
        mock_loop.docker_mgr.call_tool.assert_not_called()
    
    def test_mark_ticket_done(self, mock_loop):
        """Test marking ticket as done."""
        ticket = {"id": "ticket1"}
        validation = {"passed": True, "score": 0.95}
        
        # Mock the attempts counter to return 0
        mock_loop.controller._ticket_attempts.get.return_value = 0
        
        mock_loop._mark_ticket_done(ticket, "aider-mcp", validation)
        
        mock_loop.docker_mgr.call_tool.assert_called_once()
        call_args = mock_loop.docker_mgr.call_tool.call_args[0]
        
        assert call_args[0] == "planfile-mcp"
        assert call_args[1] == "planfile_update_ticket"
        assert call_args[2]["ticket_id"] == "ticket1"
        assert call_args[2]["status"] == "done"
        assert call_args[2]["resolution"]["tool"] == "aider-mcp"
        assert call_args[2]["resolution"]["validation"] == "unknown"  # Default status
        assert call_args[2]["resolution"]["attempts"] == 0
    
    def test_mark_ticket_skipped(self, mock_loop):
        """Test marking ticket as skipped."""
        ticket = {"id": "ticket1"}
        
        mock_loop._mark_ticket_skipped(ticket, "Too complex")
        
        mock_loop.docker_mgr.call_tool.assert_called_once_with(
            "planfile-mcp", "planfile_update_ticket", {
                "ticket_id": "ticket1",
                "status": "skipped",
                "resolution": {"reason": "Too complex"}
            }
        )
