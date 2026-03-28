"""Integration tests for algitex pipeline with extensions."""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from algitex import Pipeline
from algitex.tools.feedback import FeedbackController, FeedbackPolicy


class TestPipelineIntegration:
    """Test the full pipeline with all extensions integrated."""
    
    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure for testing."""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        
        # Create a simple Python project
        (project_dir / "main.py").write_text("""
def hello():
    return "Hello, World!"

def calculate(x, y):
    # This has high complexity
    if x > 0:
        if y > 0:
            if x > y:
                result = x + y
            else:
                result = x - y
        else:
            result = x * y
    else:
        result = 0
    return result
""")
        
        (project_dir / "utils.py").write_text("""
def helper():
    return 42
""")
        
        # Create test directory
        tests_dir = project_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("""
def test_hello():
    from main import hello
    assert hello() == "Hello, World!"
""")
        
        # Create config files
        (project_dir / "pyproject.toml").write_text("""
[tool.black]
line-length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
""")
        
        return str(project_dir)
    
    def test_pipeline_initialization(self, temp_project):
        """Test that pipeline initializes with all extensions."""
        pipeline = Pipeline(temp_project)
        
        # Check that all modules are initialized
        assert pipeline.telemetry is not None
        assert pipeline.context_builder is not None
        assert pipeline.feedback_controller is not None
        assert pipeline.telemetry.project == "test_project"
    
    def test_telemetry_tracking(self, temp_project):
        """Test that telemetry tracks operations correctly."""
        pipeline = Pipeline(temp_project)
        
        # Create some spans
        span1 = pipeline.telemetry.span("test-op-1", "test-tool")
        span1.finish(tokens_in=100, tokens_out=50, cost_usd=0.01)
        
        span2 = pipeline.telemetry.span("test-op-2", "test-tool")
        span2.finish(tokens_in=200, tokens_out=100, cost_usd=0.02)
        
        # Check aggregates
        assert pipeline.telemetry.total_cost == 0.03
        assert pipeline.telemetry.total_tokens == 450
        assert pipeline.telemetry.error_count == 0
        
        # Generate report
        report = pipeline.telemetry.report()
        assert "test-op-1" in report
        assert "2 operations" in report
        assert "$0.03" in report
    
    def test_context_building(self, temp_project):
        """Test context building for tickets."""
        pipeline = Pipeline(temp_project)
        
        ticket = {
            "id": "ticket1",
            "title": "Fix bug",
            "llm_hints": {"files_to_modify": ["main.py"]},
            "description": "Fix the calculate function"
        }
        
        context = pipeline.context_builder.build(ticket)
        
        assert context.target_files == ["main.py"]
        assert any("test_main.py" in str(f) for f in context.related_files)
        assert "ticket1" in context.ticket_context
        assert "Fix bug" in context.ticket_context
    
    def test_feedback_policies(self, temp_project):
        """Test feedback controller policies."""
        # Test default policy
        pipeline = Pipeline(temp_project)
        controller = pipeline.feedback_controller
        
        assert controller.policy.max_retries == 3
        assert controller.policy.auto_replan is True
        assert controller.policy.require_approval_for == ["critical"]
        
        # Test with custom policy
        from algitex.tools.feedback import FeedbackPolicy
        custom_policy = FeedbackPolicy(
            max_retries=5,
            require_approval_for=["critical", "breaking"]
        )
        
        pipeline2 = Pipeline(temp_project)
        pipeline2.feedback_controller = FeedbackController(custom_policy)
        
        assert pipeline2.feedback_controller.policy.max_retries == 5
        assert "breaking" in pipeline2.feedback_controller.policy.require_approval_for
    
    def test_error_handling(self, temp_project):
        """Test error handling in pipeline."""
        pipeline = Pipeline(temp_project)
        
        # Create a span that errors
        span = pipeline.telemetry.span("error-test", "tool")
        span.finish(status="error", error="Test error")
        
        # Check error tracking
        assert pipeline.telemetry.error_count == 1
        
        # Generate report should include errors
        report = pipeline.telemetry.report()
        assert "1 errors" in report


class TestPipelineWithRealFiles:
    """Test pipeline with actual file operations (no Docker)."""
    
    @pytest.fixture
    def simple_project(self, tmp_path):
        """Create a minimal project for file-based testing."""
        project_dir = tmp_path / "simple"
        project_dir.mkdir()
        
        # Create analysis.toon.yaml
        (project_dir / "analysis.toon.yaml").write_text("""
CC̄=3.5
Alerts: 2
Hotspots:
  - main.py: calculate() CC=8
""")
        
        # Create map.toon.yaml
        (project_dir / "map.toon.yaml").write_text("""
M[main, utils]
D[main -> utils]
""")
        
        # Create source files
        (project_dir / "main.py").write_text("""
import utils

def main():
    return utils.helper()
""")
        
        (project_dir / "utils.py").write_text("""
def helper():
    return 42
""")
        
        return str(project_dir)
    
    def test_context_reads_toon_files(self, simple_project):
        """Test that context builder reads .toon files."""
        pipeline = Pipeline(simple_project)
        
        # Build context without ticket
        context = pipeline.context_builder.build()
        
        # Should have read the toon files
        assert "CC̄=3.5" in context.project_summary
        assert "M[main, utils]" in context.architecture
    
    def test_context_finds_related_files(self, simple_project):
        """Test that context builder finds related files."""
        pipeline = Pipeline(simple_project)
        
        ticket = {
            "id": "1",
            "llm_hints": {"files_to_modify": ["main.py"]}
        }
        
        context = pipeline.context_builder.build(ticket)
        
        # Should find utils.py as related
        assert any("utils" in str(f) for f in context.related_files)
        assert "main.py" in context.target_files
