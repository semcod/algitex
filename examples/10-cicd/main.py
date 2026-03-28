"""Example: Using CI/CD module for automated quality gates.

This example demonstrates how to:
1. Generate GitHub Actions workflows
2. Create GitLab CI configurations
3. Set up quality gates with complexity checks
4. Generate Dockerfiles and pre-commit hooks
"""

import tempfile
import shutil
from pathlib import Path
from algitex.tools.cicd import CICDGenerator, init_ci_cd, create_quality_gate_config


def basic_github_actions_example():
    """Generate basic GitHub Actions workflow."""
    print("=== Basic GitHub Actions Example ===\n")
    
    # Create a temporary project
    project_dir = Path("sample-ci-project")
    project_dir.mkdir(exist_ok=True)
    
    # Create sample algitex config
    (project_dir / "algitex.yaml").write_text("""
feedback_policy:
  max_retries: 3
  retry_escalation:
    - "ollama/qwen2.5-coder:7b"
    - "claude-sonnet-4-20250514"

ci_cd:
  max_complexity: 3.5
  require_tests: true
  security_scan: true
  env:
    LANGFUSE_DATABASE_URL: "${{ secrets.LANGFUSE_DATABASE_URL }}"
""")
    
    # Generate GitHub Actions
    generator = CICDGenerator(str(project_dir))
    workflow_path = generator.generate_github_actions()
    
    print(f"Generated GitHub Actions workflow: {workflow_path}")
    
    # Show the generated content
    with open(workflow_path) as f:
        content = f.read()
    
    print("\nGenerated workflow content:")
    print("-" * 60)
    print(content[:500] + "..." if len(content) > 500 else content)
    print("-" * 60)
    
    return str(project_dir)


def gitlab_ci_example():
    """Generate GitLab CI configuration."""
    print("\n=== GitLab CI Example ===\n")
    
    project_dir = Path("sample-ci-project")
    
    # Generate GitLab CI
    generator = CICDGenerator(str(project_dir))
    ci_path = generator.generate_gitlab_ci()
    
    print(f"Generated GitLab CI: {ci_path}")
    
    # Show the generated content
    with open(ci_path) as f:
        content = f.read()
    
    print("\nGenerated CI configuration:")
    print("-" * 60)
    print(content[:400] + "..." if len(content) > 400 else content)
    print("-" * 60)
    
    return ci_path


def quality_gates_example():
    """Example of configuring quality gates."""
    print("\n=== Quality Gates Configuration ===\n")
    
    # Create different quality gate configurations
    configs = {
        "strict": {
            "max_cc": 2.5,
            "require_tests": True,
            "security_scan": True,
            "coverage_threshold": 90
        },
        "standard": {
            "max_cc": 3.5,
            "require_tests": True,
            "security_scan": True,
            "coverage_threshold": 80
        },
        "lenient": {
            "max_cc": 5.0,
            "require_tests": False,
            "security_scan": True,
            "coverage_threshold": 70
        }
    }
    
    print("Quality Gate Configurations:")
    print("-" * 60)
    
    for level, config in configs.items():
        print(f"\n{level.capitalize()} Quality Gate:")
        print(f"  Max Complexity: {config['max_cc']}")
        print(f"  Tests Required: {config['require_tests']}")
        print(f"  Security Scan: {config['security_scan']}")
        print(f"  Coverage Threshold: {config['coverage_threshold']}%")
    
    # Generate quality gate for GitHub Actions
    # Remove unsupported parameter
    standard_config = configs["standard"].copy()
    del standard_config["coverage_threshold"]
    quality_config = create_quality_gate_config(**standard_config)
    
    print("\nGenerated Quality Gate Configuration:")
    print("-" * 60)
    
    import yaml
    print(yaml.dump(quality_config, default_flow_style=False))
    
    return quality_config


def dockerfile_example():
    """Generate Dockerfile for algitex project."""
    print("\n=== Dockerfile Generation ===\n")
    
    project_dir = Path("sample-ci-project")
    
    # Generate Dockerfile
    generator = CICDGenerator(str(project_dir))
    dockerfile_path = generator.generate_dockerfile()
    
    print(f"Generated Dockerfile: {dockerfile_path}")
    
    # Show the content
    with open(dockerfile_path) as f:
        content = f.read()
    
    print("\nDockerfile content:")
    print("-" * 60)
    print(content)
    print("-" * 60)
    
    # Also create .dockerignore
    (project_dir / ".dockerignore").write_text("""
.git
.gitignore
.pytest_cache
.coverage
.algitex/telemetry
__pycache__
*.pyc
.env
""")
    
    print("\nAlso created .dockerignore for optimized builds")
    
    return dockerfile_path


def precommit_hooks_example():
    """Generate pre-commit configuration."""
    print("\n=== Pre-commit Hooks Example ===\n")
    
    project_dir = Path("sample-ci-project")
    
    # Generate pre-commit config
    generator = CICDGenerator(str(project_dir))
    precommit_path = generator.generate_precommit_config()
    
    print(f"Generated pre-commit config: {precommit_path}")
    
    # Show the content
    with open(precommit_path) as f:
        content = f.read()
    
    print("\nPre-commit configuration:")
    print("-" * 60)
    print(content)
    print("-" * 60)
    
    print("\nTo activate pre-commit hooks:")
    print("  $ pre-commit install")
    print("  $ pre-commit run --all-files")
    
    return precommit_path


def complete_ci_cd_setup():
    """Example of complete CI/CD setup."""
    print("\n=== Complete CI/CD Setup ===\n")
    
    # Create project structure
    project_dir = Path("complete-ci-project")
    project_dir.mkdir(exist_ok=True)
    
    # Create comprehensive algitex config
    (project_dir / "algitex.yaml").write_text("""
project:
  name: "my-awesome-project"
  
feedback_policy:
  max_retries: 3
  retry_escalation:
    - "ollama/qwen2.5-coder:7b"
    - "claude-sonnet-4-20250514"
  require_approval_for:
    - "critical"
    - "security"

ci_cd:
  max_complexity: 3.5
  require_tests: true
  security_scan: true
  coverage_threshold: 80
  env:
    LANGFUSE_DATABASE_URL: "${{ secrets.LANGFUSE_DATABASE_URL }}"
    CODECOV_TOKEN: "${{ secrets.CODECOV_TOKEN }}"
  steps:
    - name: "Upload telemetry to Langfuse"
      run: "algitex telemetry push"
      if: "always()"
    - name: "Notify Slack on failure"
      if: "failure()"
      uses: "8398a7/action-slack@v3"
      with:
        status: "failure"
        text: "Pipeline failed for ${{ github.repository }}"
""")
    
    # Generate all CI/CD files
    generator = CICDGenerator(str(project_dir))
    generated = generator.generate_all(
        github=True,
        gitlab=True,
        dockerfile=True,
        precommit=True
    )
    
    print("Generated CI/CD files:")
    print("-" * 40)
    for name, path in generated.items():
        print(f"  {name}: {path}")
    
    # Create additional files
    (project_dir / "requirements.txt").write_text("""
algitex>=0.1.0
code2llm>=0.1.0
vallm>=0.1.0
pytest>=7.0.0
pytest-cov>=4.0.0
black>=23.0.0
isort>=5.12.0
""")
    
    (project_dir / "Makefile").write_text("""
.PHONY: test lint analyze ci

test:
	python -m pytest tests/ -v --cov=. --cov-report=html

lint:
	black --check .
	isort --check-only .
	flake8 .

analyze:
	algitex analyze .

ci: analyze test lint
	@echo "All checks passed!"
""")
    
    print("\nAdditional files created:")
    print("  - requirements.txt")
    print("  - Makefile")
    
    # Show directory structure
    print("\nProject structure:")
    print("  complete-ci-project/")
    print("  ├── .github/")
    print("  │   └── workflows/")
    print("  │       └── algitex.yml")
    print("  ├── .gitlab-ci.yml")
    print("  ├── Dockerfile")
    print("  ├── .dockerignore")
    print("  ├── .pre-commit-config.yaml")
    print("  ├── algitex.yaml")
    print("  ├── requirements.txt")
    print("  └── Makefile")
    
    return str(project_dir)


def multi_platform_ci_example():
    """Example of multi-platform CI/CD."""
    print("\n=== Multi-Platform CI/CD Example ===\n")
    
    project_dir = Path("multi-platform-project")
    project_dir.mkdir(exist_ok=True)
    
    # Create platform-specific configurations
    platforms = {
        "github": {
            "name": "GitHub Actions",
            "features": ["matrix builds", "caching", "secrets", "artifacts"]
        },
        "gitlab": {
            "name": "GitLab CI",
            "features": ["docker-in-docker", "custom runners", "parent-child pipelines"]
        },
        "azure": {
            "name": "Azure Pipelines",
            "features": ["multi-stage", "agent pools", "release pipelines"]
        }
    }
    
    print("Platform Features:")
    print("-" * 40)
    for platform, info in platforms.items():
        print(f"\n{info['name']}:")
        for feature in info['features']:
            print(f"  ✅ {feature}")
    
    # Generate for different platforms
    generator = CICDGenerator(str(project_dir))
    
    # GitHub with matrix strategy
    github_workflow = {
        "name": "algitex Multi-Platform CI",
        "on": {"push": {"branches": ["main"]}},
        "jobs": {
            "test": {
                "runs-on": "${{ matrix.os }}",
                "strategy": {
                    "matrix": {
                        "os": ["ubuntu-latest", "windows-latest", "macos-latest"],
                        "python-version": ["3.9", "3.10", "3.11"]
                    }
                },
                "steps": [
                    {"uses": "actions/checkout@v4"},
                    {"uses": "actions/setup-python@v4", "with": {"python-version": "${{ matrix.python-version }}"}},
                    {"run": "pip install algitex"},
                    {"run": "algitex analyze . --quick"},
                    {"run": "python -m pytest tests/"}
                ]
            }
        }
    }
    
    # Save advanced GitHub workflow
    github_path = project_dir / ".github" / "workflows" / "multi-platform.yml"
    github_path.parent.mkdir(parents=True, exist_ok=True)
    
    import yaml
    with open(github_path, "w") as f:
        yaml.dump(github_workflow, f, sort_keys=False)
    
    print(f"\nGenerated advanced GitHub workflow: {github_path}")
    
    return str(project_dir)


def cleanup_ci_projects():
    """Clean up all sample CI projects."""
    projects = ["sample-ci-project", "complete-ci-project", "multi-platform-project"]
    
    for project in projects:
        project_dir = Path(project)
        if project_dir.exists():
            shutil.rmtree(project_dir)
            print(f"✅ Cleaned up {project}")


if __name__ == "__main__":
    print("Algitex CI/CD Examples")
    print("=" * 50)
    
    try:
        # Run all examples
        basic_github_actions_example()
        gitlab_ci_example()
        quality_gates_example()
        dockerfile_example()
        precommit_hooks_example()
        complete_ci_cd_setup()
        multi_platform_ci_example()
        
    finally:
        cleanup_ci_projects()
    
    print("\n" + "=" * 50)
    print("All examples completed!")
    print("\nKey takeaways:")
    print("1. CI/CD generation is template-based and customizable")
    print("2. Quality gates enforce code standards automatically")
    print("3. Multiple platforms supported (GitHub, GitLab, Azure)")
    print("4. Pre-commit hooks catch issues early")
    print("5. Dockerfiles ensure consistent environments")
