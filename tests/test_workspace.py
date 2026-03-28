"""Tests for workspace module."""

import pytest
import tempfile
import shutil
from pathlib import Path
import yaml

from algitex.tools.workspace import Workspace, RepoConfig, init_workspace


class TestWorkspace:
    """Test the Workspace class."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp(prefix="workspace_test_")
        
        # Create workspace config
        config = {
            "workspace": {
                "name": "test-workspace",
                "repos": [
                    {
                        "name": "core",
                        "path": f"{temp_dir}/core",
                        "git_url": "https://github.com/test/core",
                        "priority": 1
                    },
                    {
                        "name": "service",
                        "path": f"{temp_dir}/service",
                        "git_url": "https://github.com/test/service",
                        "priority": 2,
                        "depends_on": ["core"]
                    },
                    {
                        "name": "frontend",
                        "path": f"{temp_dir}/frontend",
                        "git_url": "https://github.com/test/frontend",
                        "priority": 3,
                        "depends_on": ["service"]
                    }
                ]
            }
        }
        
        config_path = Path(temp_dir) / "workspace.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config, f)
        
        yield str(config_path)
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_workspace_loading(self, temp_workspace):
        """Test loading workspace configuration."""
        workspace = Workspace(temp_workspace)
        
        assert len(workspace.repos) == 3
        assert "core" in workspace.repos
        assert "service" in workspace.repos
        assert "frontend" in workspace.repos
        
        # Check dependencies
        assert workspace.repos["service"].depends_on == ["core"]
        assert workspace.repos["frontend"].depends_on == ["service"]
        assert workspace.repos["core"].depends_on == []
    
    def test_topological_sort(self, temp_workspace):
        """Test topological sorting of repositories."""
        workspace = Workspace(temp_workspace)
        
        sorted_repos = workspace._topo_sort()
        names = [r.name for r in sorted_repos]
        
        # Core should come first
        assert names[0] == "core"
        # Service should come after core
        assert names.index("service") > names.index("core")
        # Frontend should come last
        assert names[-1] == "frontend"
    
    def test_dependency_validation(self, temp_workspace):
        """Test dependency validation."""
        workspace = Workspace(temp_workspace)
        
        # Should not raise for valid dependencies
        workspace._validate_dependencies()
        
        # Add invalid dependency
        workspace.repos["frontend"].depends_on.append("nonexistent")
        
        with pytest.raises(ValueError, match="depends on non-existent repo"):
            workspace._validate_dependencies()
    
    def test_get_execution_plan(self, temp_workspace):
        """Test getting execution plan."""
        workspace = Workspace(temp_workspace)
        
        plan = workspace.get_execution_plan()
        
        assert plan == ["core", "service", "frontend"]
    
    def test_find_repos_by_tag(self, temp_workspace):
        """Test finding repositories by tag."""
        workspace = Workspace(temp_workspace)
        
        # Add tags
        workspace.repos["core"].tags = ["library"]
        workspace.repos["service"].tags = ["service", "api"]
        workspace.repos["frontend"].tags = ["frontend", "web"]
        
        # Find by tag
        services = workspace.find_repos_by_tag("service")
        assert len(services) == 1
        assert services[0].name == "service"
        
        libraries = workspace.find_repos_by_tag("library")
        assert len(libraries) == 1
        assert libraries[0].name == "core"
    
    def test_status(self, temp_workspace):
        """Test workspace status reporting."""
        workspace = Workspace(temp_workspace)
        
        status = workspace.status()
        
        assert "workspace" in status
        assert "repositories" in status
        assert status["workspace"]["name"] == "test-workspace"
        assert status["workspace"]["repos"] == 3
        
        # Check repo status
        repo_status = status["repositories"]["core"]
        assert repo_status["git_url"] == "https://github.com/test/core"
        assert repo_status["priority"] == 1
        assert repo_status["dependencies"] == []
    
    def test_dependency_graph(self, temp_workspace):
        """Test getting dependency graph."""
        workspace = Workspace(temp_workspace)
        
        graph = workspace.get_dependency_graph()
        
        assert graph == {
            "core": [],
            "service": ["core"],
            "frontend": ["service"]
        }


class TestWorkspaceInit:
    """Test workspace initialization utilities."""
    
    def test_init_workspace(self):
        """Test workspace initialization."""
        temp_dir = tempfile.mkdtemp(prefix="workspace_init_test_")
        
        try:
            config_path = Path(temp_dir) / "test-workspace.yaml"
            init_workspace("test-workspace", str(config_path))
            
            assert config_path.exists()
            
            with open(config_path) as f:
                config = yaml.safe_load(f)
            
            assert "workspace" in config
            assert config["workspace"]["name"] == "test-workspace"
            assert len(config["workspace"]["repos"]) == 3
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_repo_config_creation(self):
        """Test RepoConfig dataclass."""
        repo = RepoConfig(
            name="test",
            path="./test",
            git_url="https://github.com/test/test",
            priority=1,
            depends_on=["base"],
            tags=["service"]
        )
        
        assert repo.name == "test"
        assert repo.priority == 1
        assert repo.depends_on == ["base"]
        assert repo.tags == ["service"]
        assert repo.path == str(Path("./test").resolve())


class TestWorkspaceIntegration:
    """Integration tests for workspace operations."""
    
    @pytest.fixture
    def mock_workspace(self, tmp_path):
        """Create a mock workspace with fake repos."""
        # Create fake repo directories
        repos = ["core", "service", "frontend"]
        for repo in repos:
            repo_path = tmp_path / repo
            repo_path.mkdir()
            (repo_path / "pyproject.toml").write_text("[tool.black]\nline-length = 88")
        
        # Create workspace config
        config = {
            "workspace": {
                "name": "mock-workspace",
                "repos": [
                    {
                        "name": "core",
                        "path": str(tmp_path / "core"),
                        "git_url": "https://github.com/test/core",
                        "priority": 1
                    },
                    {
                        "name": "service",
                        "path": str(tmp_path / "service"),
                        "git_url": "https://github.com/test/service",
                        "priority": 2,
                        "depends_on": ["core"]
                    },
                    {
                        "name": "frontend",
                        "path": str(tmp_path / "frontend"),
                        "git_url": "https://github.com/test/frontend",
                        "priority": 3,
                        "depends_on": ["service"]
                    }
                ]
            }
        }
        
        config_path = tmp_path / "workspace.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config, f)
        
        return str(config_path)
    
    def test_analyze_all_mock(self, mock_workspace):
        """Test analyzing all repositories (mocked)."""
        workspace = Workspace(mock_workspace)
        
        # Mock the analyze method
        with pytest.MonkeyPatch().context() as m:
            def mock_analyze(self, full=True):
                return type('MockReport', (), {
                    'grade': 'B',
                    'alerts': [type('Alert', (), {'severity': 'medium'})()],
                    'hotspots': []
                })()
            
            m.setattr("algitex.Project.analyze", mock_analyze)
            
            results = workspace.analyze_all()
            
            assert len(results) == 3
            assert all(r["status"] == "success" for r in results.values())
    
    def test_plan_all_mock(self, mock_workspace):
        """Test planning across all repositories (mocked)."""
        workspace = Workspace(mock_workspace)
        
        with pytest.MonkeyPatch().context() as m:
            def mock_plan(self, sprints=2):
                return [
                    type('MockTicket', (), {
                        'id': 'TICKET-1',
                        'title': 'Test ticket',
                        'priority': 'medium'
                    })()
                ]
            
            m.setattr("algitex.Project.plan", mock_plan)
            
            all_tickets = workspace.plan_all()
            
            assert len(all_tickets) == 3
            for repo_name, tickets in all_tickets.items():
                assert len(tickets) == 1
                assert tickets[0]["id"] == "TICKET-1"
                assert tickets[0]["repo"] == repo_name
