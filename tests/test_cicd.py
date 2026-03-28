"""Tests for CI/CD module."""

import pytest
import tempfile
import shutil
from pathlib import Path
import yaml

from algitex.tools.cicd import CICDGenerator, init_ci_cd, create_quality_gate_config


class TestCICDGenerator:
    """Test the CICDGenerator class."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project for testing."""
        temp_dir = tempfile.mkdtemp(prefix="cicd_test_")
        project_dir = Path(temp_dir) / "test-project"
        project_dir.mkdir()
        
        # Create algitex config
        (project_dir / "algitex.yaml").write_text("""
feedback_policy:
  max_retries: 3

ci_cd:
  max_complexity: 3.5
  require_tests: true
  security_scan: true
""")
        
        yield str(project_dir)
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_generator_initialization(self, temp_project):
        """Test CICDGenerator initialization."""
        generator = CICDGenerator(temp_project)
        
        assert generator.project_path == Path(temp_project).resolve()
        assert generator.config["feedback_policy"]["max_retries"] == 3
        assert generator.config["ci_cd"]["max_complexity"] == 3.5
    
    def test_load_config_missing(self, tmp_path):
        """Test loading config when algitex.yaml doesn't exist."""
        generator = CICDGenerator(str(tmp_path))
        
        assert generator.config == {}
    
    def test_generate_github_actions(self, temp_project):
        """Test GitHub Actions workflow generation."""
        generator = CICDGenerator(temp_project)
        
        workflow_path = generator.generate_github_actions()
        
        assert Path(workflow_path).exists()
        assert workflow_path.endswith(".github/workflows/algitex.yml")
        
        # Check workflow content
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        assert "name" in workflow
        assert workflow["name"] == "algitex Quality Gate"
        assert "on" in workflow
        assert "jobs" in workflow
        assert "quality" in workflow["jobs"]
        
        # Check for quality gate steps
        steps = workflow["jobs"]["quality"]["steps"]
        step_names = [s.get("name", "") for s in steps]
        
        assert any("algitex analyze" in str(s.get("run", "")) for s in steps)
        assert any("complexity" in str(s.get("run", "")) for s in steps)
    
    def test_generate_gitlab_ci(self, temp_project):
        """Test GitLab CI configuration generation."""
        generator = CICDGenerator(temp_project)
        
        ci_path = generator.generate_gitlab_ci()
        
        assert Path(ci_path).exists()
        assert ci_path.endswith(".gitlab-ci.yml")
        
        # Check CI content
        with open(ci_path) as f:
            ci_config = yaml.safe_load(f)
        
        assert "stages" in ci_config
        assert "analyze" in ci_config["stages"]
        assert "test" in ci_config["stages"]
        assert "security" in ci_config["stages"]
        
        # Check for jobs
        assert "analyze" in ci_config
        assert "test" in ci_config
        assert "security" in ci_config
    
    def test_generate_dockerfile(self, temp_project):
        """Test Dockerfile generation."""
        generator = CICDGenerator(temp_project)
        
        dockerfile_path = generator.generate_dockerfile()
        
        assert Path(dockerfile_path).exists()
        assert dockerfile_path.endswith("Dockerfile")
        
        # Check Dockerfile content
        with open(dockerfile_path) as f:
            content = f.read()
        
        assert "FROM python:3.11-slim" in content
        assert "algitex" in content
        assert "code2llm" in content
        assert "vallm" in content
    
    def test_generate_precommit_config(self, temp_project):
        """Test pre-commit configuration generation."""
        generator = CICDGenerator(temp_project)
        
        precommit_path = generator.generate_precommit_config()
        
        assert Path(precommit_path).exists()
        assert precommit_path.endswith(".pre-commit-config.yaml")
        
        # Check pre-commit content
        with open(precommit_path) as f:
            config = yaml.safe_load(f)
        
        assert "repos" in config
        assert len(config["repos"]) > 0
        
        # Check for algitex hook
        algitex_hook = None
        for repo in config["repos"]:
            if repo.get("repo") == "local":
                for hook in repo.get("hooks", []):
                    if hook.get("id") == "algitex-analyze":
                        algitex_hook = hook
                        break
        
        assert algitex_hook is not None
        assert algitex_hook["entry"] == "algitex"
    
    def test_generate_all(self, temp_project):
        """Test generating all CI/CD configurations."""
        generator = CICDGenerator(temp_project)
        
        generated = generator.generate_all(
            github=True,
            gitlab=True,
            dockerfile=True,
            precommit=True
        )
        
        assert len(generated) == 4
        assert "github" in generated
        assert "gitlab" in generated
        assert "dockerfile" in generated
        assert "precommit" in generated
        
        # Check all files exist
        for path in generated.values():
            assert Path(path).exists()
    
    def test_custom_config_in_workflow(self, temp_project):
        """Test custom configuration in generated workflow."""
        # Update config with custom steps
        config_path = Path(temp_project) / "algitex.yaml"
        config = yaml.safe_load(config_path.read_text())
        
        config["ci_cd"]["steps"] = [
            {
                "name": "Custom step",
                "run": "echo 'Custom step'"
            }
        ]
        
        config_path.write_text(yaml.dump(config))
        
        generator = CICDGenerator(temp_project)
        workflow_path = generator.generate_github_actions()
        
        # Check custom step is included
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        steps = workflow["jobs"]["quality"]["steps"]
        step_names = [s.get("name", "") for s in steps]
        
        assert "Custom step" in step_names
    
    def test_complexity_check_generation(self, temp_project):
        """Test complexity check command generation."""
        generator = CICDGenerator(temp_project)
        
        check = generator._get_complexity_check()
        
        assert "CC=" in check
        assert "3.5" in check
        assert "bc -l" in check
    
    def test_update_config(self, temp_project):
        """Test updating CI/CD configuration."""
        generator = CICDGenerator(temp_project)
        
        new_config = {
            "max_complexity": 4.0,
            "env": {
                "CUSTOM_VAR": "value"
            }
        }
        
        generator.update_config(new_config)
        
        assert generator.config["ci_cd"]["max_complexity"] == 4.0
        assert generator.config["ci_cd"]["env"]["CUSTOM_VAR"] == "value"


class TestCICDUtilities:
    """Test CI/CD utility functions."""
    
    def test_init_ci_cd_github(self, tmp_path):
        """Test initializing CI/CD for GitHub."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()
        
        with pytest.MonkeyPatch().context() as m:
            # Mock print to capture output
            outputs = []
            m.setattr("builtins.print", lambda *args: outputs.append(" ".join(map(str, args))))
            
            init_ci_cd(str(project_dir), "github")
            
            # Check files were created
            assert (project_dir / ".github" / "workflows" / "algitex.yml").exists()
            assert (project_dir / "Dockerfile").exists()
            assert (project_dir / ".pre-commit-config.yaml").exists()
            
            # Check output
            output_text = " ".join(outputs)
            assert "GitHub Actions workflow" in output_text
    
    def test_init_ci_cd_gitlab(self, tmp_path):
        """Test initializing CI/CD for GitLab."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()
        
        with pytest.MonkeyPatch().context() as m:
            outputs = []
            m.setattr("builtins.print", lambda *args: outputs.append(" ".join(map(str, args))))
            
            init_ci_cd(str(project_dir), "gitlab")
            
            # Check files were created
            assert (project_dir / ".gitlab-ci.yml").exists()
            assert (project_dir / "Dockerfile").exists()
            assert (project_dir / ".pre-commit-config.yaml").exists()
            
            # Check output
            output_text = " ".join(outputs)
            assert "GitLab CI configuration" in output_text
    
    def test_create_quality_gate_config(self):
        """Test quality gate configuration creation."""
        config = create_quality_gate_config(
            max_cc=4.0,
            require_tests=False,
            security_scan=True
        )
        
        assert config["max_complexity"] == 4.0
        assert config["require_tests"] is False
        assert config["security_scan"] is True
        assert "env" in config
        assert "steps" in config
        
        # Check default values
        default_config = create_quality_gate_config()
        assert default_config["max_complexity"] == 3.5
        assert default_config["require_tests"] is True
        assert default_config["security_scan"] is True


class TestCICDIntegration:
    """Integration tests for CI/CD functionality."""
    
    @pytest.fixture
    def full_project(self, tmp_path):
        """Create a full project with all configurations."""
        project_dir = tmp_path / "full-project"
        project_dir.mkdir()
        
        # Create comprehensive algitex config
        (project_dir / "algitex.yaml").write_text("""
project:
  name: "full-test-project"
  
feedback_policy:
  max_retries: 3
  retry_escalation:
    - "ollama/qwen2.5-coder:7b"
    - "claude-sonnet-4-20250514"

ci_cd:
  max_complexity: 3.0
  require_tests: true
  security_scan: true
  coverage_threshold: 85
  env:
    LANGFUSE_DATABASE_URL: "${{ secrets.LANGFUSE }}"
    CODECOV_TOKEN: "${{ secrets.CODECOV }}"
  steps:
    - name: "Upload coverage"
      run: "codecov"
      if: "always()"
""")
        
        # Create requirements.txt
        (project_dir / "requirements.txt").write_text("""
algitex>=0.1.0
pytest>=7.0.0
""")
        
        # Create test directory
        tests_dir = project_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "__init__.py").write_text("")
        
        return str(project_dir)
    
    def test_complete_ci_cd_generation(self, full_project):
        """Test complete CI/CD generation."""
        generator = CICDGenerator(full_project)
        
        # Generate all configurations
        generated = generator.generate_all(
            github=True,
            gitlab=True,
            dockerfile=True,
            precommit=True
        )
        
        # Verify all files exist and have content
        for name, path in generated.items():
            assert Path(path).exists()
            
            with open(path) as f:
                content = f.read()
            
            assert len(content) > 0
            
            # Check for project-specific values
            if name == "github":
                workflow = yaml.safe_load(content)
                assert "3.0" in str(workflow)  # max_complexity
            elif name == "gitlab":
                ci = yaml.safe_load(content)
                assert "85" in str(ci)  # coverage_threshold
    
    def test_workflow_validation(self, full_project):
        """Test that generated workflows are valid YAML."""
        generator = CICDGenerator(full_project)
        
        # Generate GitHub workflow
        workflow_path = generator.generate_github_actions()
        
        # Should be valid YAML
        with open(workflow_path) as f:
            yaml.safe_load(f)  # Will raise if invalid
        
        # Generate GitLab CI
        ci_path = generator.generate_gitlab_ci()
        
        with open(ci_path) as f:
            yaml.safe_load(f)  # Will raise if invalid
