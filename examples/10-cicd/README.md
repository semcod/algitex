# CI/CD Examples

This example demonstrates how to use the cicd module to generate automated quality gates for algitex projects.

## Features Demonstrated

- GitHub Actions workflow generation
- GitLab CI configuration
- Dockerfile generation for consistent environments
- Pre-commit hooks for early quality checks
- Multi-platform CI/CD setup
- Quality gate configuration

## Running the Example

```bash
# Install dependencies
pip install algitex

# Run the CI/CD example
python main.py
```

## What You'll See

1. **GitHub Actions** - Workflow with quality gates and complexity checks
2. **GitLab CI** - Pipeline configuration with stages and artifacts
3. **Quality Gates** - Configurable thresholds for complexity, coverage, security
4. **Dockerfile** - Optimized container configuration
5. **Pre-commit Hooks** - Local quality checks before commits
6. **Complete Setup** - All configurations for a production-ready project

## Key Takeaways

- CI/CD generation is template-based and customizable
- Quality gates enforce code standards automatically
- Multiple platforms supported (GitHub, GitLab, Azure)
- Pre-commit hooks catch issues early
- Dockerfiles ensure consistent environments

## Configuration

Quality gates can be configured in `algitex.yaml`:

```yaml
ci_cd:
  max_complexity: 3.5
  require_tests: true
  security_scan: true
  coverage_threshold: 80
  env:
    LANGFUSE_DATABASE_URL: "${{ secrets.LANGFUSE_DATABASE_URL }}"
    CODECOV_TOKEN: "${{ secrets.CODECOV_TOKEN }}"
```

## Generated Files

- `.github/workflows/algitex.yml` - GitHub Actions workflow
- `.gitlab-ci.yml` - GitLab CI configuration
- `Dockerfile` - Container configuration
- `.pre-commit-config.yaml` - Pre-commit hooks
- `Makefile` - Common development tasks

## Quick Start

```bash
# Initialize CI/CD for your project
algitex init-cicd .

# Activate pre-commit hooks
pre-commit install

# Run all checks locally
make ci
```

## Use Cases

- **Enforce Standards** - Automatic quality checks on every PR
- **Multi-Platform** - Support for different CI/CD systems
- **Container Deployments** - Consistent Docker environments
- **Early Detection** - Pre-commit hooks catch issues before commit
