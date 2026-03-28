"""CI/CD generation for algitex pipelines.

Generate GitHub Actions / GitLab CI workflows with quality gates.
"""

from __future__ import annotations

,os
from pathlib import Path
from typing import Dict, Optional
import yaml


class CICDGenerator:
    """Generate CI/CD pipelines for algitex projects."""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load algitex configuration."""
        config_path = self.project_path / "algitex.yaml"
        
        if config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f) or {}
        
        return {}
    
    def generate_github_actions(self, output_path: Optional[str] = None) -> str:
        """Generate GitHub Actions workflow with quality gates."""
        workflow = {
            "name": "algitex Quality Gate",
            "on": {
                "push": {"branches": ["main", "develop"]},
                "pull_request": {"branches": ["main"]}
            },
            "jobs": {
                "quality": {
                    "runs-on": "ubuntu-latest",
                    "services": {
                        "postgres": {
                            "image": "postgres:15",
                            "env": {"POSTGRES_PASSWORD": "postgres"},
                            "options": "--health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5"
                        }
                    },
                    "steps": [
                        {
                            "name": "Checkout",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Setup Python",
                            "uses": "actions/setup-python@v4",
                            "with": {"python-version": "3.11"}
                        },
                        {
                            "name": "Install algitex",
                            "run": "pip install algitex code2llm vallm"
                        },
                        {
                            "name": "Run algitex analyze",
                            "run": "algitex analyze . --quick"
                        },
                        {
                            "name": "Check complexity",
                            "run": self._get_complexity_check()
                        },
                        {
                            "name": "Run vallm validation",
                            "run": "vallm batch . --exit-code"
                        },
                        {
                            "name": "Run security scan",
                            "uses": "semgrep/semgrep-action@v1",
                            "with": {
                                "config": "auto"
                            }
                        },
                        {
                            "name": "Run tests",
                            "run": "python -m pytest tests/ -v --junitxml=test-results.xml"
                        },
                        {
                            "name": "Upload test results",
                            "uses": "actions/upload-artifact@v3",
                            "if": "always()",
                            "with": {
                                "name": "test-results",
                                "path": "test-results.xml"
                            }
                        },
                        {
                            "name": "Generate coverage",
                            "run": "python -m pytest --cov=. --cov-report=xml"
                        },
                        {
                            "name": "Upload coverage",
                            "uses": "codecov/codecov-action@v3",
                            "with": {
                                "file": "coverage.xml"
                            }
                        }
                    ]
                }
            }
        }
        
        # Add custom steps from config
        if "ci_cd" in self.config:
            custom_steps = self.config["ci_cd"].get("steps", [])
            workflow["jobs"]["quality"]["steps"].extend(custom_steps)
        
        # Add environment variables
        if "env" in self.config.get("ci_cd", {}):
            workflow["env"] = self.config["ci_cd"]["env"]
        
        # Convert to YAML
        workflow_yaml = yaml.dump(workflow, default_flow_style=False, sort_keys=False)
        
        # Save to file
        if output_path is None:
            output_path = self.project_path / ".github" / "workflows" / "algitex.yml"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            f.write(workflow_yaml)
        
        return str(output_path)
    
    def generate_gitlab_ci(self, output_path: Optional[str] = None) -> str:
        """Generate GitLab CI configuration."""
        ci_config = {
            "stages": ["analyze", "test", "security", "deploy"],
            "variables": {
                "PYTHON_VERSION": "3.11"
            },
            "analyze": {
                "stage": "analyze",
                "image": "python:$PYTHON_VERSION",
                "before_script": [
                    "pip install algitex code2llm vallm"
                ],
                "script": [
                    "algitex analyze . --quick",
                    self._get_complexity_check(),
                    "vallm batch . --exit-code"
                ],
                "artifacts": {
                    "reports": {"junit": "analysis-results.xml"},
                    "paths": ["analysis.toon.yaml"]
                }
            },
            "test": {
                "stage": "test",
                "image": "python:$PYTHON_VERSION",
                "script": [
                    "pip install pytest pytest-cov",
                    "python -m pytest tests/ -v --junitxml=test-results.xml --cov=. --cov-report=xml"
                ],
                "artifacts": {
                    "reports": {"junit": "test-results.xml", "coverage_report": {"coverage_format": "cobertura", "path": "coverage.xml"}}
                }
            },
            "coverage_check": {
                "stage": "test",
                "image": "python:$PYTHON_VERSION",
                "script": [
                    f"pip install pytest-cov",
                    f"python -m pytest --cov=. --cov-fail-under={self.config.get('ci_cd', {}).get('coverage_threshold', 80)}"
                ],
                "allow_failure": True
            },
            "security": {
                "stage": "security",
                "image": "semgrep/semgrep:latest",
                "script": [
                    "semgrep --config=auto --json --output=semgrep.json . || true",
                    "semgrep --config=auto --error --severity=ERROR ."
                ],
                "artifacts": {
                    "paths": ["semgrep.json"]
                }
            }
        }
        
        # Add custom configuration
        if "ci_cd" in self.config:
            if "stages" in self.config["ci_cd"]:
                ci_config["stages"].extend(self.config["ci_cd"]["stages"])
            if "variables" in self.config["ci_cd"]:
                ci_config["variables"].update(self.config["ci_cd"]["variables"])
        
        # Convert to YAML
        ci_yaml = yaml.dump(ci_config, default_flow_style=False, sort_keys=False)
        
        # Save to file
        if output_path is None:
            output_path = self.project_path / ".gitlab-ci.yml"
        
        output_path = Path(output_path)
        
        with open(output_path, "w") as f:
            f.write(ci_yaml)
        
        return str(output_path)
    
    def _get_complexity_check(self) -> str:
        """Get complexity check command based on configuration."""
        max_cc = self.config.get("ci_cd", {}).get("max_complexity", 3.5)
        
        return f"""
CC=$(grep 'CC̄=' analysis.toon.yaml 2>/dev/null | head -1 | awk -F= '{{print $2}}' || echo "0")
if (( $(echo "$CC > {max_cc}" | bc -l) )); then
  echo "complexity too high: $CC > {max_cc}"
  exit 1
else
  echo "complexity OK: $CC ≤ {max_cc}"
fi
        """.strip()
    
    def generate_dockerfile(self, output_path: Optional[str] = None) -> str:
        """Generate Dockerfile for algitex project."""
        dockerfile = """# Generated by algitex CI/CD generator
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install algitex
RUN pip install algitex code2llm vallm

# Copy project
COPY . /app
WORKDIR /app

# Run analysis on build
RUN algitex analyze . --quick

# Default command
CMD ["python", "-m", "algitex", "status"]
        """
        
        # Save to file
        if output_path is None:
            output_path = self.project_path / "Dockerfile"
        
        output_path = Path(output_path)
        
        with open(output_path, "w") as f:
            f.write(dockerfile)
        
        return str(output_path)
    
    def generate_precommit_config(self, output_path: Optional[str] = None) -> str:
        """Generate pre-commit configuration."""
        precommit_config = {
            "repos": [
                {
                    "repo": "https://github.com/pre-commit/pre-commit-hooks",
                    "rev": "v4.4.0",
                    "hooks": [
                        {"id": "trailing-whitespace"},
                        {"id": "end-of-file-fixer"},
                        {"id": "check-yaml"},
                        {"id": "check-added-large-files"},
                        {"id": "check-merge-conflict"}
                    ]
                },
                {
                    "repo": "https://github.com/psf/black",
                    "rev": "23.3.0",
                    "hooks": [
                        {"id": "black"}
                    ]
                },
                {
                    "repo": "https://github.com/pycqa/isort",
                    "rev": "5.12.0",
                    "hooks": [
                        {"id": "isort"}
                    ]
                },
                {
                    "repo": "local",
                    "hooks": [
                        {
                            "id": "algitex-analyze",
                            "name": "algitex analyze",
                            "entry": "algitex",
                            "args": ["analyze", ".", "--quick"],
                            "language": "system",
                            "pass_filenames": False,
                            "always_run": True
                        }
                    ]
                }
            ]
        }
        
        # Convert to YAML
        config_yaml = yaml.dump(precommit_config, default_flow_style=False, sort_keys=False)
        
        # Save to file
        if output_path is None:
            output_path = self.project_path / ".pre-commit-config.yaml"
        
        output_path = Path(output_path)
        
        with open(output_path, "w") as f:
            f.write(config_yaml)
        
        return str(output_path)
    
    def generate_all(self, github: bool = True, gitlab: bool = False, 
                    dockerfile: bool = True, precommit: bool = True) -> Dict[str, str]:
        """Generate all CI/CD configurations."""
        generated = {}
        
        if github:
            generated["github"] = self.generate_github_actions()
        
        if gitlab:
            generated["gitlab"] = self.generate_gitlab_ci()
        
        if dockerfile:
            generated["dockerfile"] = self.generate_dockerfile()
        
        if precommit:
            generated["precommit"] = self.generate_precommit_config()
        
        return generated
    
    def update_config(self, config: Dict) -> None:
        """Update CI/CD configuration."""
        if "ci_cd" not in self.config:
            self.config["ci_cd"] = {}
        
        self.config["ci_cd"].update(config)
        
        # Save to algitex.yaml
        config_path = self.project_path / "algitex.yaml"
        
        with open(config_path, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False)


# CLI convenience functions
def init_ci_cd(project_path: str = ".", platform: str = "github") -> None:
    """Initialize CI/CD for a project."""
    generator = CICDGenerator(project_path)
    
    if platform == "github":
        path = generator.generate_github_actions()
        print(f"Created GitHub Actions workflow: {path}")
    elif platform == "gitlab":
        path = generator.generate_gitlab_ci()
        print(f"Created GitLab CI configuration: {path}")
    else:
        raise ValueError(f"Unsupported platform: {platform}")
    
    # Also generate Dockerfile and pre-commit
    generator.generate_dockerfile()
    generator.generate_precommit_config()
    
    print("\nAlso created:")
    print("  - Dockerfile")
    print("  - .pre-commit-config.yaml")
    print("\nTo activate pre-commit:")
    print("  pre-commit install")


def create_quality_gate_config(max_cc: float = 3.5, 
                             require_tests: bool = True,
                             security_scan: bool = True) -> Dict:
    """Create a quality gate configuration."""
    config = {
        "max_complexity": max_cc,
        "require_tests": require_tests,
        "security_scan": security_scan,
        "env": {
            "LANGFUSE_DATABASE_URL": "${{ secrets.LANGFUSE_DATABASE_URL }}"
        },
        "steps": [
            {
                "name": "Upload to Langfuse",
                "run": "algitex telemetry push",
                "if": "always()"
            }
        ]
    }
    
    return config
