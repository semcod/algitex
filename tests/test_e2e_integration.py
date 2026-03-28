"""End-to-end integration test for algitex with all extensions.

This test demonstrates the complete pipeline flow:
1. Project analysis
2. Context building
3. Ticket execution with telemetry
4. Feedback loops for retries
5. Multi-level validation
6. Final reporting
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

from algitex import Pipeline
from algitex.tools.telemetry import Telemetry
from algitex.tools.context import ContextBuilder
from algitex.tools.feedback import FeedbackController, FeedbackPolicy


class TestEndToEndIntegration:
    """Test the complete pipeline with all extensions."""
    
    @pytest.fixture
    def sample_project(self):
        """Create a realistic sample project for testing."""
        temp_dir = tempfile.mkdtemp(prefix="algitex_test_")
        project_dir = Path(temp_dir) / "sample_project"
        project_dir.mkdir()
        
        # Create source files with issues to fix
        (project_dir / "main.py").write_text("""
from utils import helper
from data_processor import process_data

def main():
    '''Main entry point.'''
    data = load_data()
    # TODO: Add error handling
    result = process_data(data)
    print(result)
    return result

def load_data():
    '''Load data from file.'''
    with open('data.txt', 'r') as f:
        return f.read()
""")
        
        (project_dir / "utils.py").write_text("""
import json

def helper(data):
    '''Helper function with complexity issues.'''
    if data is None:
        return None
    if isinstance(data, str):
        # High complexity nested logic
        if data.startswith('{'):
            try:
                parsed = json.loads(data)
                if 'items' in parsed:
                    if isinstance(parsed['items'], list):
                        if len(parsed['items']) > 0:
                            if all(isinstance(x, dict) for x in parsed['items']):
                                return [x.get('value') for x in parsed['items']]
                            else:
                                return None
                        else:
                            return []
                    else:
                        return None
                else:
                    return None
            except:
                return None
        return data.upper()
""")
        
        (project_dir / "data_processor.py").write_text("""
class DataProcessor:
    '''Process data with potential security issues.'''
    
    def __init__(self):
        self.cache = {}
    
    def process(self, data):
        # Security issue: eval() usage
        if data.startswith('calc:'):
            return eval(data[5:])
        return data * 2
""")
        
        # Create test files
        tests_dir = project_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("""
import pytest
from main import main, load_data

def test_main():
    assert main() is not None

def test_load_data():
    # Test will fail - file doesn't exist
    data = load_data()
    assert data is not None
""")
        
        # Create configuration files
        (project_dir / "pyproject.toml").write_text("""
[tool.black]
line-length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
""")
        
        (project_dir / ".editorconfig").write_text("""
[*.py]
indent_size = 4
trim_trailing_whitespace = true
""")
        
        # Create .toon files
        (project_dir / "analysis.toon.yaml").write_text("""
CC̄=4.2
Alerts: 5
Hotspots:
  - utils.py: helper() CC=8
  - main.py: load_data() CC=3
  - data_processor.py: DataProcessor.process() CC=2
Security:
  - eval() usage in data_processor.py
  - Missing error handling in main.py
""")
        
        (project_dir / "map.toon.yaml").write_text("""
M[main, utils, data_processor]
D[main -> utils]
D[main -> data_processor]
D[data_processor -> external_api]
""")
        
        # Create algitex config with feedback policy
        (project_dir / "algitex.yaml").write_text("""
feedback_policy:
  max_retries: 2
  retry_escalation:
    - "ollama/qwen2.5-coder:7b"
    - "claude-sonnet-4-20250514"
  auto_replan: true
  require_approval_for:
    - "critical"
    - "security"
  notify_on_failure: true
""")
        
        yield str(project_dir)
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_complete_pipeline_flow(self, sample_project):
        """Test the complete pipeline with all extensions."""
        print("\n=== Complete Pipeline Flow Test ===\n")
        
        # Mock Docker tools
        with patch('algitex.tools.docker.DockerToolManager') as MockDockerMgr:
            mock_mgr = MagicMock()
            MockDockerMgr.return_value = mock_mgr
            
            # Mock tool availability
            mock_mgr.list_tools.return_value = [
                "aider-mcp", "vallm", "pytest", "semgrep"
            ]
            mock_mgr.list_running.return_value = ["aider-mcp"]
            
            # Mock successful execution after retries
            call_count = 0
            def mock_call_tool(tool, method, params):
                nonlocal call_count
                call_count += 1
                
                if tool == "vallm":
                    # First validation fails, second passes
                    if call_count <= 2:
                        return {
                            "passed": False,
                            "errors": [
                                {"rule": "complexity", "message": "High CC in helper()"},
                                {"rule": "security", "message": "eval() usage detected"}
                            ]
                        }
                    else:
                        return {"passed": True}
                
                elif tool == "pytest":
                    # Tests pass after fixes
                    return {"rc": 0, "tests_run": 3}
                
                elif tool == "semgrep":
                    # Security issues fixed
                    return {"findings": [], "passed": True}
                
                else:  # aider-mcp
                    # Simulate code generation with telemetry
                    return {
                        "status": "success",
                        "tokens_in": 1000,
                        "tokens_out": 500,
                        "model": params.get("model", "claude-sonnet-4")
                    }
            
            mock_mgr.call_tool.side_effect = mock_call_tool
            
            # Create pipeline
            pipeline = Pipeline(sample_project)
            
            # Verify extensions are initialized
            assert pipeline.telemetry is not None
            assert pipeline.context_builder is not None
            assert pipeline.feedback_controller is not None
            
            # Track telemetry throughout the pipeline
            initial_spans = len(pipeline.telemetry.spans)
            
            # Execute pipeline
            print("1. Running pipeline analysis...")
            pipeline.analyze(full=False)
            
            print("2. Creating tickets from issues...")
            pipeline.create_tickets()
            
            print("3. Executing tickets with feedback loop...")
            result = pipeline.execute(max_tickets=1)
            
            print("4. Running multi-level validation...")
            pipeline.validate()
            validation = pipeline._results["validation"]
            
            print("5. Finishing pipeline (saving telemetry)...")
            pipeline.finish()
            
            # Verify results
            print("\n=== Verification ===")
            
            # Check telemetry was tracked
            assert len(pipeline.telemetry.spans) > initial_spans
            print(f"✓ Telemetry tracked {len(pipeline.telemetry.spans)} operations")
            
            # Check context was built
            context = pipeline.context_builder.build()
            assert "CC̄=4.2" in context.project_summary
            assert "M[main, utils, data_processor]" in context.architecture
            print("✓ Context built from .toon files")
            
            # Check feedback policy was used
            assert pipeline.feedback_controller.policy.max_retries == 3
            assert "claude-sonnet-4-20250514" in pipeline.feedback_controller.policy.retry_escalation
            print("✓ Custom feedback policy loaded from config")
            
            # Check validation results
            assert validation["static_passed"] is True
            assert validation["runtime_passed"] is True
            assert validation["security_passed"] is True
            assert validation["all_passed"] is True
            print("✓ All validation levels passed")
            
            # Check final report includes telemetry
            report = pipeline.report()
            assert "telemetry" in report
            assert report["telemetry"]["spans"] > 0
            print(f"✓ Final report includes telemetry data")
            
            # Print summary
            print("\n=== Pipeline Summary ===")
            print(f"Total operations: {report['telemetry']['spans']}")
            print(f"Total cost: ${report['telemetry']['total_cost_usd']}")
            print(f"Total tokens: {report['telemetry']['total_tokens']}")
            print(f"Errors: {report['telemetry']['errors']}")
            print(f"Validation: {'✓ PASSED' if validation['all_passed'] else '✗ FAILED'}")
    
    def test_telemetry_integration(self, sample_project):
        """Test telemetry integration throughout the pipeline."""
        print("\n=== Telemetry Integration Test ===\n")
        
        with patch('algitex.tools.docker.DockerToolManager') as MockDockerMgr:
            mock_mgr = MagicMock()
            MockDockerMgr.return_value = mock_mgr
            mock_mgr.list_tools.return_value = ["aider-mcp", "vallm"]
            mock_mgr.list_running.return_value = ["aider-mcp"]
            mock_mgr.call_tool.return_value = {"status": "success"}
            
            pipeline = Pipeline(sample_project)
            
            # Create manual spans to test telemetry
            with pipeline.telemetry.span("test-operation", "test-tool") as span:
                span.tokens_in = 100
                span.tokens_out = 50
                span.cost_usd = 0.01
                span.model = "test-model"
            
            # Verify telemetry data
            assert len(pipeline.telemetry.spans) == 1
            assert pipeline.telemetry.total_tokens == 150
            assert pipeline.telemetry.total_cost == 0.01
            
            # Test report generation
            report = pipeline.telemetry.report()
            assert "test-operation" in report
            assert "$0.01" in report
            
            print("✓ Telemetry tracking working correctly")
            print(f"  Report: {report}")
    
    def test_context_integration(self, sample_project):
        """Test context building integration."""
        print("\n=== Context Integration Test ===\n")
        
        pipeline = Pipeline(sample_project)
        
        # Test context without ticket
        context = pipeline.context_builder.build()
        assert context.project_summary is not None
        assert context.architecture is not None
        assert context.conventions is not None
        
        # Test context with ticket
        ticket = {
            "id": "123",
            "title": "Fix complexity in helper",
            "llm_hints": {"files_to_modify": ["utils.py"]},
            "description": "Reduce cyclomatic complexity"
        }
        
        context = pipeline.context_builder.build(ticket)
        assert "utils.py" in context.target_files
        assert any("test_utils" in str(f) for f in context.related_files)
        assert "123" in context.ticket_context
        
        # Test prompt generation
        prompt = context.to_prompt("Fix the helper function")
        assert "## Project context" in prompt
        assert "## Architecture" in prompt
        assert "## Task" in prompt
        assert "Fix the helper function" in prompt
        
        print("✓ Context building working correctly")
        print(f"  Generated prompt length: {len(prompt)} characters")
    
    def test_feedback_integration(self, sample_project):
        """Test feedback loop integration."""
        print("\n=== Feedback Integration Test ===\n")
        
        pipeline = Pipeline(sample_project)
        
        # Test custom policy loading
        assert pipeline.feedback_controller.policy.max_retries == 2
        assert pipeline.feedback_controller.policy.auto_replan is True
        
        # Test approval requirement
        critical_ticket = {"priority": "critical", "title": "Security fix"}
        normal_ticket = {"priority": "normal", "title": "UI improvement"}
        
        assert pipeline.feedback_controller.needs_approval(critical_ticket) is True
        assert pipeline.feedback_controller.needs_approval(normal_ticket) is False
        
        # Test failure handling
        validation = {
            "passed": False,
            "errors": [
                {"rule": "complexity", "message": "High CC detected"},
                {"rule": "style", "message": "Line too long"}
            ]
        }
        
        strategy, params = pipeline.feedback_controller.on_validation_failure(
            {"id": "123"}, validation, {}
        )
        
        assert strategy.value == "retry"
        assert "model" in params
        assert "feedback" in params
        
        print("✓ Feedback loop working correctly")
        print(f"  First failure strategy: {strategy.value}")
        print(f"  Feedback extracted: {params['feedback'][:50]}...")
    
    def test_multi_level_validation(self, sample_project):
        """Test three-level validation system."""
        print("\n=== Multi-Level Validation Test ===\n")
        
        with patch('algitex.tools.docker.DockerToolManager') as MockDockerMgr:
            mock_mgr = MagicMock()
            MockDockerMgr.return_value = mock_mgr
            mock_mgr.list_tools.return_value = ["vallm", "pytest", "semgrep"]
            
            # Mock validation results
            def mock_call_tool(tool, method, params):
                if tool == "vallm":
                    return {"passed": True, "score": 0.95}
                elif tool == "pytest":
                    return {"rc": 0, "tests_run": 5, "passed": 5}
                elif tool == "semgrep":
                    return {"findings": [], "passed": True}
            
            mock_mgr.call_tool.side_effect = mock_call_tool
            
            from algitex.workflows import TicketValidator
            validator = TicketValidator(mock_mgr)
            
            results = validator.validate_all()
            
            assert results["static_passed"] is True
            assert results["runtime_passed"] is True
            assert results["security_passed"] is True
            assert results["all_passed"] is True
            
            print("✓ Multi-level validation working correctly")
            print(f"  Static: {'✓' if results['static_passed'] else '✗'}")
            print(f"  Runtime: {'✓' if results['runtime_passed'] else '✗'}")
            print(f"  Security: {'✓' if results['security_passed'] else '✗'}")
            print(f"  Overall: {'✓' if results['all_passed'] else '✗'}")


if __name__ == "__main__":
    """Run the integration test manually."""
    print("Algitex End-to-End Integration Test")
    print("=" * 50)
    
    # Create test instance
    test = TestEndToEndIntegration()
    
    # Run tests
    try:
        project_dir = next(test.sample_project())
        test.test_complete_pipeline_flow(project_dir)
        test.test_telemetry_integration(project_dir)
        test.test_context_integration(project_dir)
        test.test_feedback_integration(project_dir)
        test.test_multi_level_validation(project_dir)
        
        print("\n" + "=" * 50)
        print("✅ All integration tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
