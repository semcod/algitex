"""Test examples 30-32: Parallel Execution, ABPR Workflow, and Workspace Coordination."""
import os
import sys
import yaml
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

# Add examples to path
examples_dir = Path(__file__).parent.parent / "examples"

sys.path.insert(0, str(examples_dir))
sys.path.insert(0, str(examples_dir / "30-parallel-execution"))
sys.path.insert(0, str(examples_dir / "31-abpr-workflow"))
sys.path.insert(0, str(examples_dir / "32-workspace-coordination"))


class Test30ParallelExecution:
    """Test parallel execution examples."""
    
    def test_parallel_refactoring_imports(self):
        """Test that parallel refactoring example imports correctly."""
        try:
            import parallel_refactoring
            assert parallel_refactoring is not None
        except ImportError as e:
            pytest.fail(f"Failed to import parallel_refactoring: {e}")
    
    def test_parallel_multi_tool_imports(self):
        """Test that parallel multi-tool example imports correctly."""
        try:
            import parallel_multi_tool
            assert parallel_multi_tool is not None
        except ImportError as e:
            pytest.fail(f"Failed to import parallel_multi_tool: {e}")
    
    def test_parallel_real_world_imports(self):
        """Test that parallel real-world example imports correctly."""
        try:
            import parallel_real_world
            assert parallel_real_world is not None
        except ImportError as e:
            pytest.fail(f"Failed to import parallel_real_world: {e}")
    
    @patch('algitex.tools.parallel.ParallelExecutor.execute')
    @patch('algitex.tools.parallel.RegionExtractor')
    @patch('algitex.tools.parallel.TaskPartitioner')
    @patch('algitex.Project')
    def test_parallel_refactoring_main_logic(self, mock_project, mock_partitioner, mock_extractor, mock_execute):
        """Test the main logic of parallel refactoring example."""
        from parallel_refactoring import main
        
        # Mock project health
        mock_health = Mock()
        mock_health.cc_avg = 3.3
        mock_health.criticals = 22
        mock_health.god_functions = ["func1", "func2"]
        mock_project.return_value.analyze.return_value = mock_health
        
        # Mock region extractor
        mock_extract_instance = Mock()
        mock_extractor.return_value = mock_extract_instance
        mock_extract_instance.extract_all.return_value = [
            Mock(file="test.py", name="func1", key="test.py::func1")
        ]
        
        # Mock partitioner
        mock_partition_instance = Mock()
        mock_partitioner.return_value = mock_partition_instance
        mock_partition_instance.partition.return_value = {0: ["PLF-001"]}
        
        # Mock executor execute method directly
        mock_execute.return_value = [
            Mock(status="clean", agent_id="0", ticket_id=["PLF-001"], conflicts=[])
        ]
        
        # Run main (should not crash)
        with patch('parallel_refactoring.print'):
            main()
    
    def test_parallel_multi_tool_tickets_structure(self):
        """Test that multi-tool example has correct ticket structure."""
        import parallel_multi_tool
        
        # Check that tickets have required fields
        tickets = parallel_multi_tool.tickets if hasattr(parallel_multi_tool, 'tickets') else []
        
        for ticket in tickets:
            assert "id" in ticket
            assert "title" in ticket
            assert "llm_hints" in ticket
            assert "model_tier" in ticket["llm_hints"]


class Test31ABPRWorkflow:
    """Test ABPR workflow examples."""
    
    def test_abpr_pipeline_imports(self):
        """Test that ABPR pipeline example imports correctly."""
        try:
            import abpr_pipeline
            assert abpr_pipeline is not None
        except ImportError as e:
            pytest.fail(f"Failed to import abpr_pipeline: {e}")
    
    @patch('algitex.Loop')
    @patch('algitex.Project')
    def test_abpr_pipeline_stages(self, mock_project, mock_loop):
        """Test ABPR pipeline stages execution."""
        from abpr_pipeline import abpr_pipeline
        
        # Mock project
        mock_health = Mock()
        mock_health.cc_avg = 3.3
        mock_health.criticals = 22
        mock_health.god_functions = ["func1", "func2"]
        mock_project.return_value.analyze.return_value = mock_health
        
        # Mock loop
        mock_patterns = [
            Mock(name="validate_input", frequency=12),
            Mock(name="handle_error", frequency=8)
        ]
        mock_loop.return_value.extract.return_value = mock_patterns
        mock_loop.return_value.generate_rules.return_value = [
            Mock(name="validate_rule", confidence=0.85)
        ]
        mock_loop.return_value.report.return_value = Mock(
            rule_coverage=0.73, cost_saved=12.34
        )
        
        # Mock validation
        mock_project.return_value.execute.return_value = Mock(passed=True)
        
        # Run pipeline (should not crash)
        with patch('abpr_pipeline.print'):
            abpr_pipeline()
    
    def test_workflow_files_exist(self):
        """Test that workflow files exist in the correct location."""
        workflows_dir = examples_dir / "31-abpr-workflow" / "workflows"
        assert workflows_dir.exists(), "workflows directory should exist"
        
        fix_auth_md = workflows_dir / "fix-auth.md"
        assert fix_auth_md.exists(), "fix-auth.md should exist"
        
        # Check workflow content
        content = fix_auth_md.read_text()
        assert "## 1. Analyze codebase" in content
        assert "## 2. Run tests" in content
        assert "## 3. Localize root cause" in content


class Test32WorkspaceCoordination:
    """Test workspace coordination examples."""
    
    def test_workspace_parallel_imports(self):
        """Test that workspace parallel example imports correctly."""
        try:
            import workspace_parallel
            assert workspace_parallel is not None
        except ImportError as e:
            pytest.fail(f"Failed to import workspace_parallel: {e}")
    
    def test_workspace_yaml_structure(self):
        """Test that workspace.yaml has correct structure."""
        workspace_yaml = examples_dir / "32-workspace-coordination" / "workspace.yaml"
        assert workspace_yaml.exists(), "workspace.yaml should exist"
        
        with open(workspace_yaml) as f:
            config = yaml.safe_load(f)
        
        # Check required top-level keys
        assert "workspace" in config
        assert "repos" in config
        
        # Check workspace section
        workspace = config["workspace"]
        assert "name" in workspace
        assert "description" in workspace
        
        # Check repos structure
        repos = config["repos"]
        assert isinstance(repos, list)
        assert len(repos) > 0
        
        for repo in repos:
            assert "name" in repo
            assert "path" in repo
            assert "priority" in repo or "depends_on" in repo
    
    def test_workspace_parallel_main_logic(self):
        """Test the main logic of workspace parallel example."""
        # Change to the example directory first
        original_cwd = os.getcwd()
        try:
            os.chdir(examples_dir / "32-workspace-coordination")
            
            # Patch Workspace BEFORE importing the module
            with patch('workspace_parallel.Workspace') as mock_workspace:
                # Import main after patching
                from workspace_parallel import main
                
                # Mock workspace
                mock_ws = Mock()
                mock_workspace.return_value = mock_ws
                
                # Mock analyze_all results
                mock_ws.analyze_all.return_value = {
                    "algitex": {"cc": 3.3, "criticals": 22, "loc": 12551, "files": 61},
                    "code2llm": {"cc": 4.8, "criticals": 52, "loc": 18340, "files": 102},
                    "vallm": {"cc": 3.5, "criticals": 12, "loc": 8604, "files": 56}
                }
                
                # Mock plan_all results
                mock_ws.plan_all.return_value = {
                    "algitex": [Mock()],
                    "code2llm": [Mock(), Mock()],
                    "vallm": [Mock()]
                }
                
                # Mock execute_all results
                mock_ws.execute_all.return_value = [
                    {"repo": "algitex", "status": "success", "executed": 1, "errors": [], "tickets": ["PLF-001"], "cost": 2.5},
                    {"repo": "code2llm", "status": "success", "executed": 2, "errors": [], "tickets": ["PLF-002", "PLF-003"], "cost": 5.0},
                    {"repo": "vallm", "status": "success", "executed": 1, "errors": [], "tickets": ["PLF-004"], "cost": 2.5}
                ]
                
                # Run main (should not crash)
                with patch('workspace_parallel.print'):
                    main()
        finally:
            os.chdir(original_cwd)
    
    def test_workspace_dependency_order(self):
        """Test that workspace dependencies are correctly ordered."""
        workspace_yaml = examples_dir / "32-workspace-coordination" / "workspace.yaml"
        
        with open(workspace_yaml) as f:
            config = yaml.safe_load(f)
        
        repos = config["repos"]
        
        # Create dependency map
        deps = {}
        for repo in repos:
            deps[repo["name"]] = repo.get("depends_on", [])
        
        # Check that planfile depends on code2llm and vallm
        assert "code2llm" in deps.get("planfile", [])
        assert "vallm" in deps.get("planfile", [])
        
        # Check that llx depends on planfile
        assert "planfile" in deps.get("llx", [])
        
        # Check that proxym depends on llx and planfile
        assert "llx" in deps.get("proxym", [])
        assert "planfile" in deps.get("proxym", [])


class TestExampleStructure:
    """Test that all examples have correct structure."""
    
    @pytest.mark.parametrize("example_dir", [
        "30-parallel-execution",
        "31-abpr-workflow", 
        "32-workspace-coordination"
    ])
    def test_required_files_exist(self, example_dir):
        """Test that each example has required files."""
        example_path = examples_dir / example_dir
        
        # Check directory exists
        assert example_path.exists(), f"{example_dir} should exist"
        
        # Check required files
        required_files = ["README.md", "main.py", "Makefile"]
        for file in required_files:
            file_path = example_path / file
            assert file_path.exists(), f"{example_dir}/{file} should exist"
    
    def test_makefiles_have_targets(self):
        """Test that all Makefiles have standard targets."""
        for example_dir in ["30-parallel-execution", "31-abpr-workflow", "32-workspace-coordination"]:
            makefile_path = examples_dir / example_dir / "Makefile"
            content = makefile_path.read_text()
            
            # Check for standard targets
            assert "help:" in content, f"{example_dir}/Makefile should have help target"
            assert "run:" in content, f"{example_dir}/Makefile should have run target"
            assert "clean:" in content, f"{example_dir}/Makefile should have clean target"
    
    def test_readme_structure(self):
        """Test that all READMEs have proper structure."""
        for example_dir in ["30-parallel-execution", "31-abpr-workflow", "32-workspace-coordination"]:
            readme_path = examples_dir / example_dir / "README.md"
            content = readme_path.read_text()
            
            # Check for navigation hint
            assert "cd examples" in content or f"cd {example_dir}" in content
            
            # Check for key sections
            assert "#" in content  # Should have headers
            assert "```" in content  # Should have code blocks


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
