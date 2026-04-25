# algitex

Progressive algorithmization toolchain — from LLM to deterministic code, from proxy to tickets

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Workflows](#workflows)
- [Quality Pipeline (`pyqual.yaml`)](#quality-pipeline-pyqualyaml)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Makefile Targets](#makefile-targets)
- [Code Analysis](#code-analysis)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `algitex`
- **version**: `0.1.63`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Taskfile.yml, Makefile, testql(3), app.doql.less, pyqual.yaml, goal.yaml, .env.example, Dockerfile, docker-compose.yml, project/(2 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: algitex;
  version: 0.1.63;
}

dependencies {
  runtime: "pyyaml>=6.0, httpx>=0.27, rich>=13.0, clickmd>=1.0, pydantic>=2.0, tabulate>=0.9";
  dev: "pytest, ruff, mypy";
}

database[name="redis"] {
  type: redis;
  url: env.REDIS_URL;
}

database[name="langfuse-db"] {
  type: postgresql;
  url: env.DATABASE_URL;
}

interface[type="api"] {
  type: rest;
  framework: fastapi;
}

interface[type="cli"] {
  framework: click;
}
interface[type="cli"] page[name="algitex"] {

}

integration[name="email"] {
  type: smtp;
}

integration[name="slack"] {
  type: webhook;
}

integration[name="github"] {
  type: scm;
}

workflow[name="install"] {
  trigger: manual;
  step-1: run cmd=pip install -e ".[dev]";
}

workflow[name="test"] {
  trigger: manual;
  step-1: run cmd=python -m pytest tests/ -v --tb=short;
}

workflow[name="test-fast"] {
  trigger: manual;
  step-1: run cmd=python -m pytest tests/ -v --tb=short -m "not slow";
}

workflow[name="test-cov"] {
  trigger: manual;
  step-1: run cmd=python -m pytest tests/ -v --cov=algitex --cov-report=html --cov-report=term;
}

workflow[name="lint"] {
  trigger: manual;
  step-1: run cmd=ruff check src/ tests/;
  step-2: run cmd=ruff format --check src/ tests/;
}

workflow[name="format"] {
  trigger: manual;
  step-1: run cmd=ruff format src/ tests/;
}

workflow[name="typecheck"] {
  trigger: manual;
  step-1: run cmd=mypy src/algitex/;
}

workflow[name="docker-build"] {
  trigger: manual;
  step-1: run cmd=docker build -t algitex:latest .;
}

workflow[name="docker-test"] {
  trigger: manual;
  step-1: run cmd=docker build --target test -t algitex:test .;
}

workflow[name="docker-up"] {
  trigger: manual;
  step-1: run cmd=docker compose up -d;
  step-2: run cmd=echo "\n✅ Stack running. proxym at http://localhost:4000";
  step-3: run cmd=echo "   Run: docker compose exec algitex algitex status";
}

workflow[name="docker-tools"] {
  trigger: manual;
  step-1: run cmd=docker compose --profile tools up -d;
}

workflow[name="docker-full"] {
  trigger: manual;
  step-1: run cmd=docker compose --profile full up -d;
}

workflow[name="docker-down"] {
  trigger: manual;
  step-1: run cmd=docker compose --profile full down;
}

workflow[name="docker-logs"] {
  trigger: manual;
  step-1: run cmd=docker compose logs -f proxym;
}

workflow[name="docker-shell"] {
  trigger: manual;
  step-1: run cmd=docker compose exec algitex bash;
}

workflow[name="example-quick"] {
  trigger: manual;
  step-1: run cmd=python examples/01_quickstart.py;
}

workflow[name="example-algo"] {
  trigger: manual;
  step-1: run cmd=python examples/02_algo_loop.py;
}

workflow[name="example-workflow"] {
  trigger: manual;
  step-1: run cmd=algitex workflow run examples/workflows/health-check.md;
}

workflow[name="example-pipeline"] {
  trigger: manual;
  step-1: run cmd=python examples/03_pipeline.py;
}

workflow[name="clean"] {
  trigger: manual;
  step-1: run cmd=rm -rf build/ dist/ *.egg-info src/*.egg-info .pytest_cache .mypy_cache .ruff_cache;
  step-2: run cmd=find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true;
}

workflow[name="release"] {
  trigger: manual;
  step-1: run cmd=pip install build twine;
  step-2: run cmd=python -m build;
  step-3: run cmd=twine check dist/*;
}

workflow[name="fmt"] {
  trigger: manual;
  step-1: run cmd=ruff format .;
}

workflow[name="build"] {
  trigger: manual;
  step-1: run cmd=python -m build;
}

workflow[name="up"] {
  trigger: manual;
  step-1: run cmd=docker compose up -d;
}

workflow[name="down"] {
  trigger: manual;
  step-1: run cmd=docker compose down;
}

workflow[name="logs"] {
  trigger: manual;
  step-1: run cmd=docker compose logs -f;
}

workflow[name="ps"] {
  trigger: manual;
  step-1: run cmd=docker compose ps;
}

workflow[name="help"] {
  trigger: manual;
  step-1: run cmd=echo "algitex — available tasks:";
  step-2: run cmd=echo "";
  step-3: run cmd=taskfile list;
}

workflow[name="health"] {
  trigger: manual;
  step-1: run cmd=docker compose ps;
  step-2: run cmd=docker compose exec app echo "Health check passed";
}

workflow[name="import-makefile-hint"] {
  trigger: manual;
  step-1: run cmd=echo 'Run: taskfile import Makefile to import existing targets.';
}

workflow[name="all"] {
  trigger: manual;
  step-1: run cmd=taskfile run install;
  step-2: run cmd=taskfile run lint;
  step-3: run cmd=taskfile run test;
}

workflow[name="sumd"] {
  trigger: manual;
  step-1: run cmd=echo "# $(basename $(pwd))" > SUMD.md
echo "" >> SUMD.md
echo "$(python3 -c "import tomllib; f=open('pyproject.toml','rb'); d=tomllib.load(f); print(d.get('project',{}).get('description','Project description'))" 2>/dev/null || echo 'Project description')" >> SUMD.md
echo "" >> SUMD.md
echo "## Contents" >> SUMD.md
echo "" >> SUMD.md
echo "- [Metadata](#metadata)" >> SUMD.md
echo "- [Architecture](#architecture)" >> SUMD.md
echo "- [Dependencies](#dependencies)" >> SUMD.md
echo "- [Source Map](#source-map)" >> SUMD.md
echo "- [Intent](#intent)" >> SUMD.md
echo "" >> SUMD.md
echo "## Metadata" >> SUMD.md
echo "" >> SUMD.md
echo "- **name**: \`$(basename $(pwd))\`" >> SUMD.md
echo "- **version**: \`$(python3 -c "import tomllib; f=open('pyproject.toml','rb'); d=tomllib.load(f); print(d.get('project',{}).get('version','unknown'))" 2>/dev/null || echo 'unknown')\`" >> SUMD.md
echo "- **python_requires**: \`>=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d. -f1,2)\`" >> SUMD.md
echo "- **license**: $(python3 -c "import tomllib; f=open('pyproject.toml','rb'); d=tomllib.load(f); print(d.get('project',{}).get('license',{}).get('text','MIT'))" 2>/dev/null || echo 'MIT')" >> SUMD.md
echo "- **ecosystem**: SUMD + DOQL + testql + taskfile" >> SUMD.md
echo "- **generated_from**: pyproject.toml, Taskfile.yml, Makefile, src/" >> SUMD.md
echo "" >> SUMD.md
echo "## Architecture" >> SUMD.md
echo "" >> SUMD.md
echo '```' >> SUMD.md
echo "SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)" >> SUMD.md
echo '```' >> SUMD.md
echo "" >> SUMD.md
echo "## Source Map" >> SUMD.md
echo "" >> SUMD.md
find . -name '*.py' -not -path './.venv/*' -not -path './venv/*' -not -path './__pycache__/*' -not -path './.git/*' | head -50 | sed 's|^./||' | sed 's|^|- |' >> SUMD.md
echo "Generated SUMD.md";
  step-2: run cmd=python3 -c "
import json, os, subprocess
from pathlib import Path
project_name = Path.cwd().name
py_files = list(Path('.').rglob('*.py'))
py_files = [f for f in py_files if not any(x in str(f) for x in ['.venv', 'venv', '__pycache__', '.git'])]
data = {
    'project_name': project_name,
    'description': 'SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization',
    'files': [{'path': str(f), 'type': 'python'} for f in py_files[:100]]
}
with open('sumd.json', 'w') as f:
    json.dump(data, f, indent=2)
print('Generated sumd.json')
" 2>/dev/null || echo 'Python generation failed, using fallback';
}

workflow[name="sumr"] {
  trigger: manual;
  step-1: run cmd=echo "# $(basename $(pwd)) - Summary Report" > SUMR.md
echo "" >> SUMR.md
echo "SUMR - Summary Report for project analysis" >> SUMR.md
echo "" >> SUMR.md
echo "## Contents" >> SUMR.md
echo "" >> SUMR.md
echo "- [Metadata](#metadata)" >> SUMR.md
echo "- [Quality Status](#quality-status)" >> SUMR.md
echo "- [Metrics](#metrics)" >> SUMR.md
echo "- [Refactoring Analysis](#refactoring-analysis)" >> SUMR.md
echo "- [Intent](#intent)" >> SUMR.md
echo "" >> SUMR.md
echo "## Metadata" >> SUMR.md
echo "" >> SUMR.md
echo "- **name**: \`$(basename $(pwd))\`" >> SUMR.md
echo "- **version**: \`$(python3 -c "import tomllib; f=open('pyproject.toml','rb'); d=tomllib.load(f); print(d.get('project',{}).get('version','unknown'))" 2>/dev/null || echo 'unknown')\`" >> SUMR.md
echo "- **generated_at**: \`$(date -Iseconds)\`" >> SUMR.md
echo "" >> SUMR.md
echo "## Quality Status" >> SUMR.md
echo "" >> SUMR.md
if [ -f pyqual.yaml ]; then
  echo "- **pyqual_config**: ✅ Present" >> SUMR.md
  echo "- **last_run**: $(stat -c %y .pyqual/pipeline.db 2>/dev/null | cut -d' ' -f1 || echo 'N/A')" >> SUMR.md
else
  echo "- **pyqual_config**: ❌ Missing" >> SUMR.md
fi
echo "" >> SUMR.md
echo "## Metrics" >> SUMR.md
echo "" >> SUMR.md
py_files=$(find . -name '*.py' -not -path './.venv/*' -not -path './venv/*' | wc -l)
echo "- **python_files**: $py_files" >> SUMR.md
lines=$(find . -name '*.py' -not -path './.venv/*' -not -path './venv/*' -exec cat {} \; 2>/dev/null | wc -l)
echo "- **total_lines**: $lines" >> SUMR.md
echo "" >> SUMR.md
echo "## Refactoring Analysis" >> SUMR.md
echo "" >> SUMR.md
echo "Run \`code2llm ./ -f evolution\` for detailed refactoring queue." >> SUMR.md
echo "Generated SUMR.md";
  step-2: run cmd=python3 -c "
import json, os, subprocess
from pathlib import Path
from datetime import datetime
project_name = Path.cwd().name
py_files = len([f for f in Path('.').rglob('*.py') if not any(x in str(f) for x in ['.venv', 'venv', '__pycache__', '.git'])])
data = {
    'project_name': project_name,
    'report_type': 'SUMR',
    'generated_at': datetime.now().isoformat(),
    'metrics': {
        'python_files': py_files,
        'has_pyqual_config': Path('pyqual.yaml').exists()
    }
}
with open('SUMR.json', 'w') as f:
    json.dump(data, f, indent=2)
print('Generated SUMR.json')
" 2>/dev/null || echo 'Python generation failed, using fallback';
}

deploy {
  target: docker-compose;
  compose_file: docker-compose.yml;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: .env;
  python_version: >=3.10;
}
```

## Interfaces

### CLI Entry Points

- `algitex`

### testql Scenarios

#### `testql-scenarios/generated-api-smoke.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-api-smoke.testql.toon.yaml
# SCENARIO: Auto-generated API Smoke Tests
# TYPE: api
# GENERATED: true

CONFIG[2]{key, value}:
  base_url, http://localhost:8101
  timeout_ms, 5000

API[21]{method, endpoint, expected_status}:
  GET, /health, 200
  POST, /validate, 201
  POST, /batch, 201
  POST, /score, 201
  POST, /validate/static, 201
  POST, /validate/runtime, 201
  POST, /validate/security, 201
  GET, /v1/models, 200
  POST, /v1/chat/completions, 201
  GET, /budget, 200
  GET, /models, 200
  POST, /chat, 201
  POST, /prompt, 201
  GET, /tickets, 200
  POST, /tickets, 201
  GET, /sprint, 200
  POST, /analyze, 201
  POST, /toon-export, 201
  POST, /evolution-export, 201
  POST, /generate-readme, 201

ASSERT[1]{field, operator, expected}:
  status, <, 400
```

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -malgitex
  timeout_ms, 10000

LOG[3]{message}:
  "Test CLI help command"
  "Test CLI version command"
  "Test CLI main workflow"
```

#### `testql-scenarios/generated-from-pytests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-from-pytests.testql.toon.yaml
# SCENARIO: Auto-generated from Python Tests
# TYPE: integration
# GENERATED: true

LOG[48]{message}:
  "Test: TestConfig_test_default"
  "Test: TestConfig_test_env_override"
  "Test: TestAlgoLoop_test_add_trace"
  "Test: TestAlgoLoop_test_report"
  "Test: TestAlgoLoop_test_persistence"
  "Test: TestPropactWorkflow_test_parse"
  "Test: TestPropactWorkflow_test_validate_good"
  "Test: test_default"
  "Test: test_env_override"
  "Test: test_add_trace"

INCLUDE[52]{file}:
  "/home/tom/github/semcod/algitex/tests/test_integration_extended.py"
  "/home/tom/github/semcod/algitex/tests/test_integration_extended.py"
  "/home/tom/github/semcod/algitex/tests/test_integration_extended.py"
  "/home/tom/github/semcod/algitex/tests/test_integration_extended.py"
  "/home/tom/github/semcod/algitex/tests/test_integration_extended.py"
```

## Workflows

### Taskfile Tasks (`Taskfile.yml`)

```yaml markpact:taskfile path=Taskfile.yml
version: '1'
name: algitex
description: Minimal Taskfile
variables:
  APP_NAME: algitex
environments:
  local:
    container_runtime: docker
    compose_command: docker compose
pipeline:
  python_version: "3.12"
  runner_image: ubuntu-latest
  branches: [main]
  cache: [~/.cache/pip]
  artifacts: [dist/]

  stages:
    - name: lint
      tasks: [lint]

    - name: test
      tasks: [test]

    - name: build
      tasks: [build]
      when: "branch:main"

tasks:
  install:
    desc: Install Python dependencies (editable)
    cmds:
    - pip install -e .[dev]
  test:
    desc: Run pytest suite
    cmds:
    - pytest -q
  lint:
    desc: Run ruff lint check
    cmds:
    - ruff check .
  fmt:
    desc: Auto-format with ruff
    cmds:
    - ruff format .
  build:
    desc: Build wheel + sdist
    cmds:
    - python -m build
  clean:
    desc: Remove build artefacts
    cmds:
    - rm -rf build/ dist/ *.egg-info
  up:
    desc: Start services via docker compose
    cmds:
    - docker compose up -d
  down:
    desc: Stop services
    cmds:
    - docker compose down
  logs:
    desc: Tail compose logs
    cmds:
    - docker compose logs -f
  ps:
    desc: Show running compose services
    cmds:
    - docker compose ps
  docker-build:
    desc: Build docker image
    cmds:
    - docker build -t algitex:latest .
  help:
    desc: '[imported from Makefile] help'
    cmds:
    - echo "algitex — available tasks:"
    - echo ""
    - taskfile list
  test-fast:
    desc: '[imported from Makefile] test-fast'
    cmds:
    - python -m pytest tests/ -v --tb=short -m "not slow"
  test-cov:
    desc: '[imported from Makefile] test-cov'
    cmds:
    - python -m pytest tests/ -v --cov=algitex --cov-report=html --cov-report=term
  format:
    desc: '[imported from Makefile] format'
    cmds:
    - ruff format src/ tests/
  typecheck:
    desc: '[imported from Makefile] typecheck'
    cmds:
    - mypy src/algitex/
  docker-test:
    desc: '[imported from Makefile] docker-test'
    cmds:
    - docker build --target test -t algitex:test .
  docker-up:
    desc: '[imported from Makefile] docker-up'
    cmds:
    - docker compose up -d
    - "echo \"\\n\u2705 Stack running. proxym at http://localhost:4000\""
    - 'echo "   Run: docker compose exec algitex algitex status"'
  docker-tools:
    desc: '[imported from Makefile] docker-tools'
    cmds:
    - docker compose --profile tools up -d
  docker-full:
    desc: '[imported from Makefile] docker-full'
    cmds:
    - docker compose --profile full up -d
  docker-down:
    desc: '[imported from Makefile] docker-down'
    cmds:
    - docker compose --profile full down
  docker-logs:
    desc: '[imported from Makefile] docker-logs'
    cmds:
    - docker compose logs -f proxym
  docker-shell:
    desc: '[imported from Makefile] docker-shell'
    cmds:
    - docker compose exec algitex bash
  example-quick:
    desc: '[imported from Makefile] example-quick'
    cmds:
    - python examples/01_quickstart.py
  example-algo:
    desc: '[imported from Makefile] example-algo'
    cmds:
    - python examples/02_algo_loop.py
  example-workflow:
    desc: '[imported from Makefile] example-workflow'
    cmds:
    - algitex workflow run examples/workflows/health-check.md
  example-pipeline:
    desc: '[imported from Makefile] example-pipeline'
    cmds:
    - python examples/03_pipeline.py
  release:
    desc: '[imported from Makefile] release'
    cmds:
    - pip install build twine
    - python -m build
    - twine check dist/*
  health:
    desc: '[from doql] workflow: health'
    cmds:
    - docker compose ps
    - docker compose exec app echo "Health check passed"
  import-makefile-hint:
    desc: '[from doql] workflow: import-makefile-hint'
    cmds:
    - 'echo ''Run: taskfile import Makefile to import existing targets.'''
  all:
    desc: Run install, lint, test
    cmds:
    - taskfile run install
    - taskfile run lint
    - taskfile run test
  sumd:
    desc: Generate SUMD (Structured Unified Markdown Descriptor) for AI-aware project description
    cmds:
    - |
      echo "# $(basename $(pwd))" > SUMD.md
      echo "" >> SUMD.md
      echo "$(python3 -c "import tomllib; f=open('pyproject.toml','rb'); d=tomllib.load(f); print(d.get('project',{}).get('description','Project description'))" 2>/dev/null || echo 'Project description')" >> SUMD.md
      echo "" >> SUMD.md
      echo "## Contents" >> SUMD.md
      echo "" >> SUMD.md
      echo "- [Metadata](#metadata)" >> SUMD.md
      echo "- [Architecture](#architecture)" >> SUMD.md
      echo "- [Dependencies](#dependencies)" >> SUMD.md
      echo "- [Source Map](#source-map)" >> SUMD.md
      echo "- [Intent](#intent)" >> SUMD.md
      echo "" >> SUMD.md
      echo "## Metadata" >> SUMD.md
      echo "" >> SUMD.md
      echo "- **name**: \`$(basename $(pwd))\`" >> SUMD.md
      echo "- **version**: \`$(python3 -c "import tomllib; f=open('pyproject.toml','rb'); d=tomllib.load(f); print(d.get('project',{}).get('version','unknown'))" 2>/dev/null || echo 'unknown')\`" >> SUMD.md
      echo "- **python_requires**: \`>=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d. -f1,2)\`" >> SUMD.md
      echo "- **license**: $(python3 -c "import tomllib; f=open('pyproject.toml','rb'); d=tomllib.load(f); print(d.get('project',{}).get('license',{}).get('text','MIT'))" 2>/dev/null || echo 'MIT')" >> SUMD.md
      echo "- **ecosystem**: SUMD + DOQL + testql + taskfile" >> SUMD.md
      echo "- **generated_from**: pyproject.toml, Taskfile.yml, Makefile, src/" >> SUMD.md
      echo "" >> SUMD.md
      echo "## Architecture" >> SUMD.md
      echo "" >> SUMD.md
      echo '```' >> SUMD.md
      echo "SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)" >> SUMD.md
      echo '```' >> SUMD.md
      echo "" >> SUMD.md
      echo "## Source Map" >> SUMD.md
      echo "" >> SUMD.md
      find . -name '*.py' -not -path './.venv/*' -not -path './venv/*' -not -path './__pycache__/*' -not -path './.git/*' | head -50 | sed 's|^./||' | sed 's|^|- |' >> SUMD.md
      echo "Generated SUMD.md"
    - |
      python3 -c "
      import json, os, subprocess
      from pathlib import Path
      project_name = Path.cwd().name
      py_files = list(Path('.').rglob('*.py'))
      py_files = [f for f in py_files if not any(x in str(f) for x in ['.venv', 'venv', '__pycache__', '.git'])]
      data = {
          'project_name': project_name,
          'description': 'SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization',
          'files': [{'path': str(f), 'type': 'python'} for f in py_files[:100]]
      }
      with open('sumd.json', 'w') as f:
          json.dump(data, f, indent=2)
      print('Generated sumd.json')
      " 2>/dev/null || echo 'Python generation failed, using fallback'
  sumr:
    desc: Generate SUMR (Summary Report) with project metrics and health status
    cmds:
    - |
      echo "# $(basename $(pwd)) - Summary Report" > SUMR.md
      echo "" >> SUMR.md
      echo "SUMR - Summary Report for project analysis" >> SUMR.md
      echo "" >> SUMR.md
      echo "## Contents" >> SUMR.md
      echo "" >> SUMR.md
      echo "- [Metadata](#metadata)" >> SUMR.md
      echo "- [Quality Status](#quality-status)" >> SUMR.md
      echo "- [Metrics](#metrics)" >> SUMR.md
      echo "- [Refactoring Analysis](#refactoring-analysis)" >> SUMR.md
      echo "- [Intent](#intent)" >> SUMR.md
      echo "" >> SUMR.md
      echo "## Metadata" >> SUMR.md
      echo "" >> SUMR.md
      echo "- **name**: \`$(basename $(pwd))\`" >> SUMR.md
      echo "- **version**: \`$(python3 -c "import tomllib; f=open('pyproject.toml','rb'); d=tomllib.load(f); print(d.get('project',{}).get('version','unknown'))" 2>/dev/null || echo 'unknown')\`" >> SUMR.md
      echo "- **generated_at**: \`$(date -Iseconds)\`" >> SUMR.md
      echo "" >> SUMR.md
      echo "## Quality Status" >> SUMR.md
      echo "" >> SUMR.md
      if [ -f pyqual.yaml ]; then
        echo "- **pyqual_config**: ✅ Present" >> SUMR.md
        echo "- **last_run**: $(stat -c %y .pyqual/pipeline.db 2>/dev/null | cut -d' ' -f1 || echo 'N/A')" >> SUMR.md
      else
        echo "- **pyqual_config**: ❌ Missing" >> SUMR.md
      fi
      echo "" >> SUMR.md
      echo "## Metrics" >> SUMR.md
      echo "" >> SUMR.md
      py_files=$(find . -name '*.py' -not -path './.venv/*' -not -path './venv/*' | wc -l)
      echo "- **python_files**: $py_files" >> SUMR.md
      lines=$(find . -name '*.py' -not -path './.venv/*' -not -path './venv/*' -exec cat {} \; 2>/dev/null | wc -l)
      echo "- **total_lines**: $lines" >> SUMR.md
      echo "" >> SUMR.md
      echo "## Refactoring Analysis" >> SUMR.md
      echo "" >> SUMR.md
      echo "Run \`code2llm ./ -f evolution\` for detailed refactoring queue." >> SUMR.md
      echo "Generated SUMR.md"
    - |
      python3 -c "
      import json, os, subprocess
      from pathlib import Path
      from datetime import datetime
      project_name = Path.cwd().name
      py_files = len([f for f in Path('.').rglob('*.py') if not any(x in str(f) for x in ['.venv', 'venv', '__pycache__', '.git'])])
      data = {
          'project_name': project_name,
          'report_type': 'SUMR',
          'generated_at': datetime.now().isoformat(),
          'metrics': {
              'python_files': py_files,
              'has_pyqual_config': Path('pyqual.yaml').exists()
          }
      }
      with open('SUMR.json', 'w') as f:
          json.dump(data, f, indent=2)
      print('Generated SUMR.json')
      " 2>/dev/null || echo 'Python generation failed, using fallback'
```

## Quality Pipeline (`pyqual.yaml`)

```yaml markpact:pyqual path=pyqual.yaml
pipeline:
  name: algitex-quality-loop
  profile: python-minimal

  metrics:
    cc_max: 15
    coverage_min: 35
    critical_max: 0

  stages:
    - name: test
      run: .venv/bin/pytest tests/ --cov=src/algitex --cov-report=json:.pyqual/coverage.json -q
      when: always

  env:
    LLM_MODEL: openrouter/qwen/qwen3-coder-next
    LLX_DEFAULT_TIER: balanced
    LLX_VERBOSE: true
```

## Configuration

```yaml
project:
  name: algitex
  version: 0.1.63
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
pyyaml>=6.0
httpx>=0.27
rich>=13.0
clickmd>=1.0
pydantic>=2.0
tabulate>=0.9
```

### Development

```text markpact:deps python scope=dev
pytest
ruff
mypy
```

## Deployment

```bash markpact:run
pip install algitex

# development install
pip install -e .[dev]
```

### Docker

- **base image**: `python:3.12-slim AS base`
- **entrypoint**: `["algitex"]`
- **label** `maintainer`: Tom Sapletta <tom@sapletta.com>
- **label** `org.opencontainers.image.source`: https://github.com/semcod/algitex

### Docker Compose (`docker-compose.yml`)

- **aider-mcp** image=`algitex/aider-mcp:latest`
- **planfile-mcp** image=`algitex/planfile-mcp:latest` ports: `9001:8201`
- **proxym** image=`algitex/proxym:latest` ports: `9002:4001`
- **vallm-mcp** image=`algitex/vallm-mcp:latest` ports: `8080:8080`
- **code2llm-mcp** image=`algitex/code2llm-mcp:latest` ports: `8081:8081`
- **mcp-github** image=`ghcr.io/github/github-mcp-server:latest`
- **mcp-fetch** image=`mcp/fetch:latest`
- **mcp-filesystem** image=`mcp/filesystem:latest`
- **mcp-git** image=`mcp/git:latest`
- **mcp-sqlite** image=`mcp/sqlite:latest`
- **mcp-time** image=`mcp/time:latest`

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | `*(not set)*` | ── LLM API Keys (at least one required) ───────────── |
| `OPENAI_API_KEY` | `*(not set)*` |  |
| `GOOGLE_API_KEY` | `*(not set)*` |  |
| `DEEPSEEK_API_KEY` | `*(not set)*` |  |
| `PROXYM_PORT` | `4000` | ── Proxym Gateway ──────────────────────────────────── |
| `PROXYM_API_KEY` | `sk-proxy-local-dev` |  |
| `PROXYM_DAILY_BUDGET` | `3.0` |  |
| `PROXYM_MONTHLY_BUDGET` | `60.0` |  |
| `GITHUB_TOKEN` | `*(not set)*` | ── Ticket Sync ─────────────────────────────────────── |
| `GITHUB_REPO` | `*(not set)*` |  |
| `OLLAMA_PORT` | `11434` | ── Ollama (local LLM) ─────────────────────────────── |
| `ALGITEX_VERBOSE` | `false` | ── algitex ─────────────────────────────────────────── |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`algitex`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `venv/lib/python3.13/site-packages/matplotlib/__init__.py:__version__`

## Makefile Targets

- `help`
- `install`
- `test`
- `test-fast`
- `test-cov`
- `lint`
- `format`
- `typecheck`
- `docker-build`
- `docker-test`
- `docker-up`
- `docker-tools`
- `docker-full`
- `docker-down`
- `docker-logs`
- `docker-shell`
- `example-quick`
- `example-algo`
- `example-workflow`
- `example-pipeline`
- `clean`
- `release`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# algitex | 238f 38900L | python:210,shell:27,less:1 | 2026-04-25
# stats: 541 func | 250 cls | 238 mod | CC̄=3.5 | critical:30 | cycles:0
# alerts[5]: CC _run_micro_dashboard=17; CC find_duplicate_blocks=14; CC main=13; CC generate_module_doc=13; fan-out main=18
# hotspots[5]: main fan=18; main fan=18; dashboard_export fan=17; find_duplicate_blocks fan=17; main fan=16
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[238]:
  app.doql.less,334
  docker/aider-mcp/aider_mcp_server.py,157
  docker/code2llm/code2llm_mcp_server.py,324
  docker/code2llm/code2llm_server.py,284
  docker/planfile-mcp/planfile_mcp_server.py,277
  docker/proxym/proxym_mcp_server.py,388
  docker/proxym/proxym_server.py,257
  docker/vallm/vallm_mcp_server.py,362
  docker/vallm/vallm_server.py,275
  examples/01-quickstart/main.py,54
  examples/01-quickstart/run.sh,6
  examples/02-algo-loop/main.py,101
  examples/02-algo-loop/run.sh,6
  examples/03-pipeline/main.py,63
  examples/03-pipeline/run.sh,6
  examples/04-ide-integration/main.py,160
  examples/04-ide-integration/run.sh,6
  examples/05-cost-tracking/main.py,101
  examples/05-cost-tracking/run.sh,6
  examples/06-telemetry/main.py,207
  examples/06-telemetry/run.sh,6
  examples/07-context/main.py,398
  examples/07-context/run.sh,6
  examples/08-feedback/main.py,439
  examples/08-feedback/run.sh,6
  examples/09-workspace/main.py,405
  examples/09-workspace/run.sh,6
  examples/10-cicd/main.py,412
  examples/10-cicd/run.sh,4
  examples/11-aider-mcp/main.py,105
  examples/11-aider-mcp/run.sh,7
  examples/11-aider-mcp/sample_project/calculator.py,15
  examples/12-filesystem-mcp/main.py,115
  examples/12-filesystem-mcp/run.sh,7
  examples/12-filesystem-mcp/sample_files/src/main.py,7
  examples/13-vallm/main.py,165
  examples/13-vallm/run.sh,7
  examples/13-vallm/sample_code/complex_module.py,29
  examples/14-docker-mcp/main.py,159
  examples/14-docker-mcp/run.sh,7
  examples/14-docker-mcp/sample_docker_project/app.py,15
  examples/15-github-mcp/main.py,141
  examples/15-github-mcp/run.sh,7
  examples/15-github-mcp/sample_github_project/main.py,10
  examples/16-test-workflow/main.py,193
  examples/16-test-workflow/run.sh,7
  examples/16-test-workflow/sample_test_project/src/calculator.py,19
  examples/16-test-workflow/sample_test_project/tests/test_calculator.py,38
  examples/17-docker-workflow/main.py,126
  examples/17-docker-workflow/run.sh,7
  examples/18-ollama-local/buggy_code.py,77
  examples/18-ollama-local/main.py,242
  examples/18-ollama-local/run.sh,26
  examples/19-local-mcp-tools/buggy_code.py,83
  examples/19-local-mcp-tools/main.py,77
  examples/19-local-mcp-tools/run.sh,29
  examples/20-self-hosted-pipeline/buggy_code.py,130
  examples/20-self-hosted-pipeline/main.py,89
  examples/20-self-hosted-pipeline/run.sh,37
  examples/21-aider-cli-ollama/buggy_code.py,109
  examples/21-aider-cli-ollama/main.py,51
  examples/21-aider-cli-ollama/run.sh,62
  examples/22-claude-code-ollama/buggy_code.py,57
  examples/22-claude-code-ollama/main.py,47
  examples/22-claude-code-ollama/run.sh,10
  examples/23-continue-dev-ollama/buggy_code.py,52
  examples/23-continue-dev-ollama/main.py,54
  examples/23-continue-dev-ollama/run.sh,10
  examples/24-ollama-batch/file1.py,32
  examples/24-ollama-batch/file2.py,25
  examples/24-ollama-batch/file3.py,27
  examples/24-ollama-batch/main.py,44
  examples/24-ollama-batch/run.sh,10
  examples/25-local-model-comparison/main.py,67
  examples/25-local-model-comparison/run.sh,10
  examples/26-litellm-proxy-ollama/buggy_code.py,54
  examples/26-litellm-proxy-ollama/main.py,39
  examples/26-litellm-proxy-ollama/run.sh,29
  examples/27-unified-autofix/main.py,70
  examples/28-mcp-orchestration/main.py,48
  examples/28-mcp-orchestration/mcp_orchestrator.py,64
  examples/30-parallel-execution/main.py,142
  examples/30-parallel-execution/parallel_multi_tool.py,68
  examples/30-parallel-execution/parallel_real_world.py,202
  examples/30-parallel-execution/parallel_refactoring.py,135
  examples/31-abpr-workflow/abpr_pipeline.py,89
  examples/31-abpr-workflow/main.py,147
  examples/32-workspace-coordination/main.py,196
  examples/32-workspace-coordination/workspace_parallel.py,79
  examples/33-hybrid-autofix/main.py,225
  examples/34-batch-fix/main.py,241
  examples/34-batch-fix/sample_code/file1.py,20
  examples/34-batch-fix/sample_code/file2.py,23
  examples/34-batch-fix/sample_code/file3.py,13
  examples/35-sprint3-patterns/main.py,139
  examples/36-dashboard/main.py,113
  examples/37-benchmarks/main.py,109
  examples/38-new-modules/main.py,141
  examples/39-microtask-pipeline/main.py,104
  examples/40-three-tier-autofix/main.py,134
  examples/41-god-module-splitting/main.py,220
  examples/42-duplicate-removal/main.py,275
  examples/43-code-health/main.py,302
  examples/44-plugin-system/main.py,335
  project.sh,47
  scripts/fix_readme.py,34
  scripts/generate_lib_docs.py,317
  src/algitex/__init__.py,37
  src/algitex/algo/__init__.py,368
  src/algitex/algo/loop.py,5
  src/algitex/benchmark.py,394
  src/algitex/cli/__init__.py,232
  src/algitex/cli/algo.py,69
  src/algitex/cli/benchmark.py,167
  src/algitex/cli/core.py,196
  src/algitex/cli/dashboard.py,170
  src/algitex/cli/docker.py,105
  src/algitex/cli/metrics.py,173
  src/algitex/cli/microtask.py,199
  src/algitex/cli/nlp.py,98
  src/algitex/cli/parallel.py,153
  src/algitex/cli/ticket.py,51
  src/algitex/cli/todo/file_ops.py,11
  src/algitex/cli/todo/logic.py,46
  src/algitex/cli/todo/render.py,30
  src/algitex/cli/todo.py,1076
  src/algitex/cli/todo_verify.py,92
  src/algitex/cli/workflow.py,43
  src/algitex/cli.py,41
  src/algitex/config.py,171
  src/algitex/dashboard.py,415
  src/algitex/metrics.py,338
  src/algitex/microtask/__init__.py,197
  src/algitex/microtask/classifier.py,220
  src/algitex/microtask/executor.py,518
  src/algitex/microtask/prompts.py,127
  src/algitex/microtask/slicer.py,122
  src/algitex/nlp/__init__.py,332
  src/algitex/prefact_integration.py,277
  src/algitex/project.py,31
  src/algitex/propact/__init__.py,420
  src/algitex/propact/workflow.py,3
  src/algitex/shared_rules.py,276
  src/algitex/todo/__init__.py,135
  src/algitex/todo/audit.py,287
  src/algitex/todo/benchmark.py,245
  src/algitex/todo/classify.py,157
  src/algitex/todo/fixer.py,555
  src/algitex/todo/hybrid.py,480
  src/algitex/todo/micro.py,407
  src/algitex/todo/micro_extractor.py,66
  src/algitex/todo/micro_models.py,40
  src/algitex/todo/micro_prompts.py,70
  src/algitex/todo/micro_utils.py,91
  src/algitex/todo/repair.py,270
  src/algitex/todo/tiering.py,157
  src/algitex/todo/verifier.py,198
  src/algitex/todo/verify.py,229
  src/algitex/tools/__init__.py,116
  src/algitex/tools/analysis.py,184
  src/algitex/tools/autofix/__init__.py,306
  src/algitex/tools/autofix/aider_backend.py,165
  src/algitex/tools/autofix/base.py,45
  src/algitex/tools/autofix/batch_backend/__init__.py,5
  src/algitex/tools/autofix/batch_backend/backend.py,104
  src/algitex/tools/autofix/batch_backend/fs_utils.py,58
  src/algitex/tools/autofix/batch_backend/models.py,14
  src/algitex/tools/autofix/batch_backend/todo_utils.py,32
  src/algitex/tools/autofix/batch_backend.py,803
  src/algitex/tools/autofix/batch_logger.py,236
  src/algitex/tools/autofix/fallback_backend.py,197
  src/algitex/tools/autofix/ollama_backend.py,127
  src/algitex/tools/autofix/openrouter_backend.py,169
  src/algitex/tools/autofix/proxy_backend.py,164
  src/algitex/tools/autofix.py,18
  src/algitex/tools/batch.py,422
  src/algitex/tools/benchmark.py,465
  src/algitex/tools/cicd.py,404
  src/algitex/tools/config.py,388
  src/algitex/tools/context.py,208
  src/algitex/tools/docker.py,299
  src/algitex/tools/docker_transport.py,295
  src/algitex/tools/feedback.py,253
  src/algitex/tools/ide.py,201
  src/algitex/tools/ide_aider.py,64
  src/algitex/tools/ide_base.py,104
  src/algitex/tools/ide_claude.py,103
  src/algitex/tools/ide_models.py,21
  src/algitex/tools/logging.py,158
  src/algitex/tools/mcp.py,431
  src/algitex/tools/mcp_defaults.py,53
  src/algitex/tools/mcp_lifecycle.py,115
  src/algitex/tools/mcp_models.py,27
  src/algitex/tools/ollama.py,401
  src/algitex/tools/ollama_cache.py,239
  src/algitex/tools/parallel/__init__.py,39
  src/algitex/tools/parallel/executor.py,261
  src/algitex/tools/parallel/extractor.py,157
  src/algitex/tools/parallel/models.py,58
  src/algitex/tools/parallel/partitioner.py,119
  src/algitex/tools/parallel.py,29
  src/algitex/tools/proxy.py,146
  src/algitex/tools/services/__init__.py,5
  src/algitex/tools/services/checker.py,45
  src/algitex/tools/services/http_checks.py,126
  src/algitex/tools/services/local_checks.py,64
  src/algitex/tools/services/models.py,33
  src/algitex/tools/services.py,414
  src/algitex/tools/telemetry.py,153
  src/algitex/tools/tickets.py,248
  src/algitex/tools/todo_actions.py,201
  src/algitex/tools/todo_executor.py,241
  src/algitex/tools/todo_local.py,284
  src/algitex/tools/todo_parser.py,224
  src/algitex/tools/todo_runner.py,354
  src/algitex/tools/workspace.py,345
  src/algitex/workflows/__init__.py,321
  src/algitex/workflows/pipeline.py,6
  tests/conftest.py,69
  tests/test_benchmark.py,199
  tests/test_cicd.py,379
  tests/test_cli.py,158
  tests/test_cli_metrics.py,139
  tests/test_context.py,279
  tests/test_core.py,215
  tests/test_dashboard.py,233
  tests/test_e2e_integration.py,452
  tests/test_examples_30_32.py,312
  tests/test_feedback.py,486
  tests/test_integration.py,342
  tests/test_integration_extended.py,217
  tests/test_metrics.py,230
  tests/test_ollama_cache.py,231
  tests/test_parallel.py,305
  tests/test_prefact_integration.py,219
  tests/test_shared_rules.py,283
  tests/test_telemetry.py,155
  tests/test_workspace.py,287
D:
  docker/aider-mcp/aider_mcp_server.py:
    e: aider_ai_code,aider_list_models,aider_chat,create_rest_api,run_rest_server
    aider_ai_code(prompt;relative_editable_files;model)
    aider_list_models()
    aider_chat(message;context)
    create_rest_api()
    run_rest_server()
  docker/code2llm/code2llm_mcp_server.py:
    e: _analyze_python_file,_calculate_complexity_metrics,_collect_project_metrics,analyze_project,generate_toon,generate_readme,evolution_export,create_rest_api,run_rest_server
    _analyze_python_file(py_file;root)
    _calculate_complexity_metrics(complexity_scores)
    _collect_project_metrics(root)
    analyze_project(path)
    generate_toon(path)
    generate_readme(path)
    evolution_export(path)
    create_rest_api()
    run_rest_server()
  docker/code2llm/code2llm_server.py:
    e: Code2LLMServer
    Code2LLMServer: __init__(0),create_fastapi_app(0),_analyze_python_file(2),_calculate_complexity_metrics(1),_collect_project_metrics(1),_analyze_project(1),_generate_toon(1),_generate_readme(1),run(0)  # Code analysis server for LLM context generation.
  docker/planfile-mcp/planfile_mcp_server.py:
    e: _load_tickets,_save_tickets,planfile_create_ticket,planfile_list_tickets,planfile_update_ticket,planfile_create_tickets_bulk,planfile_sprint_status,planfile_sync,create_rest_api,run_rest_server
    _load_tickets()
    _save_tickets()
    planfile_create_ticket(title;description;priority;tags)
    planfile_list_tickets(status;priority)
    planfile_update_ticket(ticket_id;status;resolution)
    planfile_create_tickets_bulk(tickets)
    planfile_sprint_status()
    planfile_sync()
    create_rest_api()
    run_rest_server()
  docker/proxym/proxym_mcp_server.py:
    e: count_tokens,list_models,chat_completion,_call_anthropic,_call_openai,_call_gemini,simple_prompt,get_budget_status,create_rest_api,run_rest_server
    count_tokens(text)
    list_models()
    chat_completion(messages;model;temperature;max_tokens)
    _call_anthropic(messages;model;temperature;max_tokens;input_tokens)
    _call_openai(messages;model;temperature;max_tokens;input_tokens)
    _call_gemini(messages;model;temperature;max_tokens;input_tokens)
    simple_prompt(prompt;model)
    get_budget_status()
    create_rest_api()
    run_rest_server()
  docker/proxym/proxym_server.py:
    e: ProxymServer
    ProxymServer: __init__(0),create_fastapi_app(0),_call_anthropic(2),_call_openai(2),_mock_response(2),_track_cost(2),run(0)  # LLM proxy with budget tracking.
  docker/vallm/vallm_mcp_server.py:
    e: validate_static,validate_runtime,validate_security,validate_all,analyze_complexity,calculate_quality_score,create_rest_api,run_rest_server
    validate_static(path)
    validate_runtime(path)
    validate_security(path)
    validate_all(path)
    analyze_complexity(path)
    calculate_quality_score(path)
    create_rest_api()
    run_rest_server()
  docker/vallm/vallm_server.py:
    e: VallmServer
    VallmServer: __init__(0),create_fastapi_app(0),_run_validate(1),_validate_static(1),_validate_runtime(1),_validate_security(1),_analyze_complexity(1),_parse_radon_complexities(1),run(0)  # Validation server with multiple validation levels.
  examples/01-quickstart/main.py:
    e: main
    main()
  examples/02-algo-loop/main.py:
    e: main
    main()
  examples/03-pipeline/main.py:
    e: main
    main()
  examples/04-ide-integration/main.py:
    e: load_env,roo_code_config,cline_config,continuedev_config,aider_env,cursor_config,claude_code_env,main
    load_env()
    roo_code_config()
    cline_config()
    continuedev_config()
    aider_env()
    cursor_config()
    claude_code_env()
    main()
  examples/05-cost-tracking/main.py:
    e: main
    main()
  examples/06-telemetry/main.py:
    e: basic_telemetry_example,context_manager_example,multi_model_comparison,budget_tracking_example
    basic_telemetry_example()
    context_manager_example()
    multi_model_comparison()
    budget_tracking_example()
  examples/07-context/main.py:
    e: basic_context_example,context_optimization_example,semantic_search_example,prompt_engineering_example,cleanup_example_projects
    basic_context_example()
    context_optimization_example()
    semantic_search_example()
    prompt_engineering_example()
    cleanup_example_projects()
  examples/08-feedback/main.py:
    e: basic_feedback_example,custom_policy_example,feedback_extraction_example,feedback_loop_simulation,escalation_scenarios,cost_optimization_example
    basic_feedback_example()
    custom_policy_example()
    feedback_extraction_example()
    feedback_loop_simulation()
    escalation_scenarios()
    cost_optimization_example()
  examples/09-workspace/main.py:
    e: create_sample_workspace,workspace_management_example,cross_repo_analysis_example,cross_repo_planning_example,workspace_execution_example,_analyze_workspace_structure,_analyze_impact,_analyze_parallel_execution,_calculate_metrics,advanced_workspace_features,cleanup_sample_workspace
    create_sample_workspace()
    workspace_management_example()
    cross_repo_analysis_example()
    cross_repo_planning_example()
    workspace_execution_example()
    _analyze_workspace_structure(workspace)
    _analyze_impact(workspace)
    _analyze_parallel_execution(workspace)
    _calculate_metrics(workspace)
    advanced_workspace_features()
    cleanup_sample_workspace()
  examples/10-cicd/main.py:
    e: basic_github_actions_example,gitlab_ci_example,quality_gates_example,dockerfile_example,precommit_hooks_example,complete_ci_cd_setup,multi_platform_ci_example,cleanup_ci_projects
    basic_github_actions_example()
    gitlab_ci_example()
    quality_gates_example()
    dockerfile_example()
    precommit_hooks_example()
    complete_ci_cd_setup()
    multi_platform_ci_example()
    cleanup_ci_projects()
  examples/11-aider-mcp/main.py:
    e: create_sample_project,demo_refactoring
    create_sample_project()
    demo_refactoring()
  examples/11-aider-mcp/sample_project/calculator.py:
    e: calc
    calc(a;b;op)
  examples/12-filesystem-mcp/main.py:
    e: create_sample_files,demo_file_operations
    create_sample_files()
    demo_file_operations()
  examples/12-filesystem-mcp/sample_files/src/main.py:
    e: main
    main()
  examples/13-vallm/main.py:
    e: create_sample_code,run_local_validation,demo_validation
    create_sample_code()
    run_local_validation(code_dir)
    demo_validation()
  examples/13-vallm/sample_code/complex_module.py:
    e: process_data,calculate
    process_data(data)
    calculate(x;y;operation)
  examples/14-docker-mcp/main.py:
    e: create_sample_docker_project,run_docker_command,demo_docker_operations
    create_sample_docker_project()
    run_docker_command(cmd;cwd)
    demo_docker_operations()
  examples/14-docker-mcp/sample_docker_project/app.py:
    e: Handler
    Handler: do_GET(0)
  examples/15-github-mcp/main.py:
    e: create_sample_project,demo_github_workflow
    create_sample_project()
    demo_github_workflow()
  examples/15-github-mcp/sample_github_project/main.py:
    e: calculate
    calculate(x;y)
  examples/16-test-workflow/main.py:
    e: create_sample_project,run_tests,demo_test_workflow
    create_sample_project()
    run_tests(project_dir)
    demo_test_workflow()
  examples/16-test-workflow/sample_test_project/src/calculator.py:
    e: add,subtract,multiply,divide
    add(x;y)
    subtract(x;y)
    multiply(x;y)
    divide(x;y)
  examples/16-test-workflow/sample_test_project/tests/test_calculator.py:
    e: test_add,test_subtract,test_multiply,test_divide,test_divide_by_zero
    test_add()
    test_subtract()
    test_multiply()
    test_divide()
    test_divide_by_zero()
  examples/17-docker-workflow/main.py:
    e: load_env,check_required_env,show_workflow,demo_with_docker_tools,show_cli_usage
    load_env()
    check_required_env()
    show_workflow()
    demo_with_docker_tools()
    show_cli_usage()
  examples/18-ollama-local/buggy_code.py:
    e: calculate_statistics,find_user,process_file,divide_numbers,get_config,complex_function,bad_error_handling
    calculate_statistics(data)
    find_user(users;name)
    process_file(filename)
    divide_numbers(a;b)
    get_config(key)
    complex_function(data)
    bad_error_handling()
  examples/18-ollama-local/main.py:
    e: check_ollama,list_models,generate_code,analyze_code,demo_code_generation,demo_code_analysis,demo_cost_comparison,main
    check_ollama()
    list_models()
    generate_code(prompt;model)
    analyze_code(code;model)
    demo_code_generation()
    demo_code_analysis()
    demo_cost_comparison()
    main()
  examples/19-local-mcp-tools/buggy_code.py:
    e: process_items,load_data,cache_result,parse_date,recursive_function,BadClass
    BadClass: __init__(1),add_item(1),__eq__(1)  # Class with multiple issues.
    process_items(items)
    load_data(source)
    cache_result(func)
    parse_date(date_string)
    recursive_function(n)
  examples/19-local-mcp-tools/main.py:
    e: check_services,main
    check_services()
    main()
  examples/20-self-hosted-pipeline/buggy_code.py:
    e: fetch_user_data,calculate_discount,log_activity,parse_config,authenticate_user,get_stored_password,process_large_file,generate_report,cleanup_old_files,UserManager
    UserManager: __init__(0),add_user(2),get_user(1)  # Manages user operations.
    fetch_user_data(user_id;db_connection)
    calculate_discount(price;user_type)
    log_activity(user_id;action)
    parse_config(config_string)
    authenticate_user(username;password)
    get_stored_password(username)
    process_large_file(filepath)
    generate_report(data;format)
    cleanup_old_files(directory;days)
  examples/20-self-hosted-pipeline/main.py:
    e: main
    main()
  examples/21-aider-cli-ollama/buggy_code.py:
    e: calculate_price,process_users,format_message,load_data,divide,complex_function,bad_error_handling,UserManager
    UserManager: __init__(1),add(1),get(1)  # Manage users.
    calculate_price(qty;price;discount)
    process_users(users)
    format_message(name;value)
    load_data(filename)
    divide(a;b)
    complex_function(data;threshold;multiplier;offset)
    bad_error_handling()
  examples/21-aider-cli-ollama/main.py:
    e: main
    main()
  examples/22-claude-code-ollama/buggy_code.py:
    e: calc,process,load,divide,Manager
    Manager: __init__(1),add(1)
    calc(x;y;op)
    process(items)
    load(path)
    divide(a;b)
  examples/22-claude-code-ollama/main.py:
    e: main
    main()
  examples/23-continue-dev-ollama/buggy_code.py:
    e: calculate,process_items,load_file,divide_numbers,DataManager
    DataManager: __init__(1),add(1)
    calculate(x;y;operation)
    process_items(data)
    load_file(path)
    divide_numbers(a;b)
  examples/23-continue-dev-ollama/main.py:
    e: main
    main()
  examples/24-ollama-batch/file1.py:
    e: bad_function_1,bad_function_2,bad_function_3
    bad_function_1(x;y)
    bad_function_2(data)
    bad_function_3(a;b;c;d;e)
  examples/24-ollama-batch/file2.py:
    e: unused_imports,magic_numbers,no_error_handling
    unused_imports()
    magic_numbers()
    no_error_handling()
  examples/24-ollama-batch/file3.py:
    e: complex_logic,BadClass
    BadClass: __init__(1),process(0)
    complex_logic(n)
  examples/24-ollama-batch/main.py:
    e: main
    main()
  examples/25-local-model-comparison/main.py:
    e: main
    main()
  examples/26-litellm-proxy-ollama/buggy_code.py:
    e: calculate,process_items,load_file,divide_numbers,DataManager
    DataManager: __init__(1),add(1)
    calculate(x;y;operation)
    process_items(data)
    load_file(path)
    divide_numbers(a;b)
  examples/26-litellm-proxy-ollama/main.py:
    e: main
    main()
  examples/27-unified-autofix/main.py:
    e: main
    main()
  examples/28-mcp-orchestration/main.py:
    e: main
    main()
  examples/28-mcp-orchestration/mcp_orchestrator.py:
    e: main
    main()
  examples/30-parallel-execution/main.py:
    e: main
    main()
  examples/30-parallel-execution/parallel_multi_tool.py:
    e: main
    main()
  examples/30-parallel-execution/parallel_real_world.py:
    e: setup_sample_project,main
    setup_sample_project(base_dir)
    main()
  examples/30-parallel-execution/parallel_refactoring.py:
    e: main
    main()
  examples/31-abpr-workflow/abpr_pipeline.py:
    e: abpr_pipeline
    abpr_pipeline(project_path)
  examples/31-abpr-workflow/main.py:
    e: main
    main()
  examples/32-workspace-coordination/main.py:
    e: load_workspace_config,main,_print_repo_overview,_group_repos_by_priority,_show_analysis_phase,_check_quality_gates,_show_planning_phase,_show_execution_phase,_show_execution_summary
    load_workspace_config()
    main()
    _print_repo_overview(repos)
    _group_repos_by_priority(repos)
    _show_analysis_phase(repos;mock_health)
    _check_quality_gates(config;mock_health)
    _show_planning_phase(mock_health)
    _show_execution_phase(by_priority;tickets)
    _show_execution_summary(repos;by_priority;results)
  examples/32-workspace-coordination/workspace_parallel.py:
    e: main
    main()
  examples/33-hybrid-autofix/main.py:
    e: demo_dry_run,demo_verify_first,demo_benchmark,demo_mechanical_only,demo_full_hybrid,demo_ollama_local,main,_parse_args,_validate_env,_run_demos
    demo_dry_run(todo_file)
    demo_verify_first(todo_file)
    demo_benchmark(todo_file)
    demo_mechanical_only(todo_file)
    demo_full_hybrid(todo_file;workers;rate_limit)
    demo_ollama_local(todo_file)
    main()
    _parse_args()
    _validate_env(args)
    _run_demos(args)
  examples/34-batch-fix/main.py:
    e: demo_batch_dry_run,demo_batch_execute,demo_custom_batch_size,demo_comparison,main
    demo_batch_dry_run()
    demo_batch_execute()
    demo_custom_batch_size()
    demo_comparison()
    main()
  examples/34-batch-fix/sample_code/file1.py:
    e: greet,format_price,build_path
    greet(name)
    format_price(amount;currency)
    build_path(base;filename)
  examples/34-batch-fix/sample_code/file2.py:
    e: connect,retry,calculate
    connect()
    retry()
    calculate()
  examples/34-batch-fix/sample_code/file3.py:
    e: hello
    hello()
  examples/35-sprint3-patterns/main.py:
    e: demo_dict_dispatch,demo_strategy_pattern,demo_pipeline_pattern,demo_orchestrator_pattern,main
    demo_dict_dispatch()
    demo_strategy_pattern()
    demo_pipeline_pattern()
    demo_orchestrator_pattern()
    main()
  examples/36-dashboard/main.py:
    e: demo_dashboard_live,demo_dashboard_monitor,demo_dashboard_export,demo_dashboard_with_todo,main
    demo_dashboard_live()
    demo_dashboard_monitor()
    demo_dashboard_export()
    demo_dashboard_with_todo()
    main()
  examples/37-benchmarks/main.py:
    e: demo_benchmark_quick,demo_benchmark_cache,demo_benchmark_tiers,demo_benchmark_memory,demo_benchmark_full,main
    demo_benchmark_quick()
    demo_benchmark_cache()
    demo_benchmark_tiers()
    demo_benchmark_memory()
    demo_benchmark_full()
    main()
  examples/38-new-modules/main.py:
    e: demo_classify_module,demo_repair_module,demo_verify_module,demo_combined_workflow,main
    demo_classify_module()
    demo_repair_module()
    demo_verify_module()
    demo_combined_workflow()
    main()
  examples/39-microtask-pipeline/main.py:
    e: demo_microtask_classify,demo_microtask_plan,demo_microtask_run,demo_workflow,main
    demo_microtask_classify()
    demo_microtask_plan()
    demo_microtask_run()
    demo_workflow()
    main()
  examples/40-three-tier-autofix/main.py:
    e: demo_tier_algorithm,demo_tier_micro,demo_tier_big,demo_all_tiers,demo_dashboard_integration,main
    demo_tier_algorithm()
    demo_tier_micro()
    demo_tier_big()
    demo_all_tiers()
    demo_dashboard_integration()
    main()
  examples/41-god-module-splitting/main.py:
    e: demo_god_module_problem,demo_split_strategy,demo_before_and_after,demo_import_compatibility,demo_real_metrics,demo_how_to_split_your_module,main
    demo_god_module_problem()
    demo_split_strategy()
    demo_before_and_after()
    demo_import_compatibility()
    demo_real_metrics()
    demo_how_to_split_your_module()
    main()
  examples/42-duplicate-removal/main.py:
    e: demo_duplicate_problem,demo_detection_with_redup,demo_extraction_strategy,demo_algitex_integration,demo_real_world_example,demo_prevention_strategies,demo_metrics_and_roi,main
    demo_duplicate_problem()
    demo_detection_with_redup()
    demo_extraction_strategy()
    demo_algitex_integration()
    demo_real_world_example()
    demo_prevention_strategies()
    demo_metrics_and_roi()
    main()
  examples/43-code-health/main.py:
    e: demo_health_metrics,demo_analysis_pipeline,demo_health_report,demo_historical_tracking,demo_ci_integration,demo_regression_prevention,demo_health_improvement_workflow,main
    demo_health_metrics()
    demo_analysis_pipeline()
    demo_health_report()
    demo_historical_tracking()
    demo_ci_integration()
    demo_regression_prevention()
    demo_health_improvement_workflow()
    main()
  examples/44-plugin-system/main.py:
    e: demo_plugin_architecture,demo_builtin_plugins,demo_creating_tool_plugin,demo_creating_backend_plugin,demo_hook_system,demo_plugin_configuration,demo_plugin_marketplace,main,ToolPlugin,BackendPlugin
    ToolPlugin: execute(1)  # Protocol for tool plugins.
    BackendPlugin: generate(1)  # Protocol for LLM backend plugins.
    demo_plugin_architecture()
    demo_builtin_plugins()
    demo_creating_tool_plugin()
    demo_creating_backend_plugin()
    demo_hook_system()
    demo_plugin_configuration()
    demo_plugin_marketplace()
    main()
  scripts/fix_readme.py:
    e: fix_readme
    fix_readme(path)
  scripts/generate_lib_docs.py:
    e: extract_docstring,get_function_signature,_parse_function_node,_parse_class_node,_parse_import_node,_parse_export_node,parse_file,generate_module_doc,scan_package,generate_index,main
    extract_docstring(node)
    get_function_signature(node)
    _parse_function_node(node)
    _parse_class_node(node)
    _parse_import_node(node)
    _parse_export_node(node)
    parse_file(filepath)
    generate_module_doc(module_name;module_path;parsed)
    scan_package(src_dir;output_dir)
    generate_index(output_dir;modules)
    main()
  src/algitex/__init__.py:
  src/algitex/algo/__init__.py:
    e: TraceEntry,Pattern,Rule,LoopState,Loop
    TraceEntry: to_dict(0)  # Single LLM interaction trace.
    Pattern:  # Extracted repeating pattern from traces.
    Rule:  # Deterministic replacement for an LLM pattern.
    LoopState: deterministic_ratio(0),stage_name(0)  # Current state of the progressive algorithmization loop.
    Loop: __init__(1),discover(1),add_trace(2),extract(1),generate_rules(1),_llm_generate_rule(2),route(1),optimize(0),report(0),_load(0),_save(0)  # The progressive algorithmization engine.
  src/algitex/algo/loop.py:
  src/algitex/benchmark.py:
    e: run_quick_benchmark,BenchmarkResult,BenchmarkSuite,BenchmarkRunner,CacheBenchmark,TierBenchmark,MemoryBenchmark
    BenchmarkResult: to_dict(0)  # Single benchmark run result.
    BenchmarkSuite: add(1),summary(0),print_table(0)  # Collection of benchmark results.
    BenchmarkRunner: __init__(1),_measure_memory(1),run(3),run_suite(2),print_report(0),export_json(1)  # Main benchmark runner with memory tracking.
    CacheBenchmark: bench_cache_hit_rate(3),bench_cache_deduplication(2)  # Benchmarks for LLM cache performance.
    TierBenchmark: bench_algorithmic_fix(0),bench_micro_llm_simulated(0),compare_tiers(0)  # Benchmarks for three-tier performance comparison.
    MemoryBenchmark: profile_large_file_parsing(1)  # Memory profiling benchmarks.
    run_quick_benchmark()
  src/algitex/cli/__init__.py:
    e: app,ticket,algo,workflow,docker,todo,microtask,nlp,metrics,benchmark,dashboard
    app(ctx)
    ticket()
    algo()
    workflow()
    docker()
    todo()
    microtask()
    nlp()
    metrics()
    benchmark()
    dashboard()
  src/algitex/cli/algo.py:
    e: algo_discover,algo_extract,algo_rules,algo_report
    algo_discover(path)
    algo_extract(path;min_freq)
    algo_rules(path;no_llm)
    algo_report(path)
  src/algitex/cli/benchmark.py:
    e: benchmark_cache,benchmark_tiers,benchmark_memory,benchmark_full,benchmark_quick
    benchmark_cache(entries;lookups)
    benchmark_tiers()
    benchmark_memory(lines)
    benchmark_full(export;quick)
    benchmark_quick()
  src/algitex/cli/core.py:
    e: init,_init_project_dir,_init_config,_print_tools_status,analyze,plan,go,status,tools,ask,sync
    init(path)
    _init_project_dir(path)
    _init_config(project_path)
    _print_tools_status()
    analyze(path;quick)
    plan(path;sprints;focus)
    go(path;dry_run)
    status(path)
    tools()
    ask(prompt;tier)
    sync()
  src/algitex/cli/dashboard.py:
    e: dashboard_live,dashboard_monitor,dashboard_export
    dashboard_live(duration;refresh;demo)
    dashboard_monitor(cache;metrics)
    dashboard_export(format;output;duration)
  src/algitex/cli/docker.py:
    e: docker_list,docker_spawn,docker_call,docker_teardown,docker_caps
    docker_list()
    docker_spawn(tool_name)
    docker_call(tool_name;action;input)
    docker_teardown(tool_name)
    docker_caps(tool_name)
  src/algitex/cli/metrics.py:
    e: metrics_show,metrics_clear,metrics_cache,metrics_compare
    metrics_show(storage;export)
    metrics_clear(storage;cache)
    metrics_cache(dir;list_entries;clear_cache)
    metrics_compare(storage)
  src/algitex/cli/microtask.py:
    e: microtask_classify,microtask_plan,microtask_run,_filter_tasks,_print_summary,_print_task_table,_print_plan_table,_print_file_batches,_print_phase_results,_shorten_path
    microtask_classify(todo_path)
    microtask_plan(todo_path)
    microtask_run(todo_path;algo_only;tier;dry_run;workers;llm_workers;rate_limit)
    _filter_tasks(tasks)
    _print_summary(tasks)
    _print_task_table(tasks)
    _print_plan_table(tasks)
    _print_file_batches(tasks)
    _print_phase_results(results)
    _shorten_path(path;max_len)
  src/algitex/cli/nlp.py:
    e: nlp_docstrings,nlp_imports,nlp_duplicates,nlp_dead_code,_print_docstring_changes,_print_dead_code,_print_duplicates
    nlp_docstrings(path;fix)
    nlp_imports(path;sort)
    nlp_duplicates(path;min_lines)
    nlp_dead_code(path)
    _print_docstring_changes(changes)
    _print_dead_code(results)
    _print_duplicates(duplicates)
  src/algitex/cli/parallel.py:
    e: _load_tickets,_extract_and_partition,_display_partition_plan,_execute_parallel,_display_results,parallel
    _load_tickets(project_path)
    _extract_and_partition(project_path;open_tickets;agents;verbose)
    _display_partition_plan(groups;open_tickets)
    _execute_parallel(project_path;open_tickets;agents;tool)
    _display_results(results;verbose)
    parallel(path;agents;tool;dry_run;verbose)
  src/algitex/cli/ticket.py:
    e: ticket_add,ticket_list,ticket_board
    ticket_add(title;priority;type)
    ticket_list(status)
    ticket_board()
  src/algitex/cli/todo/file_ops.py:
    e: read_todo_file,write_todo_file
    read_todo_file(file)
    write_todo_file(file;content)
  src/algitex/cli/todo/logic.py:
    e: parse_todo_tasks,validate_task
    parse_todo_tasks(todo_lines)
    validate_task(task)
  src/algitex/cli/todo/render.py:
    e: render_todo_stats
    render_todo_stats(file;tasks)
  src/algitex/cli/todo.py:
    e: _render_todo_stats,_init_todo_dashboard,_run_algo_dashboard,_run_micro_dashboard,_run_big_dashboard,_run_with_dashboard,_run_hybrid_with_dashboard,_run_batch_with_dashboard,todo_stats,todo_verify,todo_fix_parallel,todo_list,todo_run,_format_todo_help,todo_fix,_tf_parse_and_filter,_tf_classify_tasks,_tf_execute_phased,_tf_build_phases,_tf_run_algorithm,_aggregate_micro_results,_mark_micro_completed,_tf_run_micro,_tf_run_big,_tf_validate_results,_tf_print_report,_tf_run_legacy,todo_benchmark,_print_hybrid_banner,_update_todo_hybrid,todo_hybrid,todo_batch,todo_verify_prefact
    _render_todo_stats(file;tasks)
    _init_todo_dashboard(algo_tasks;micro_tasks;big_tasks;algo;micro;all_phases)
    _run_algo_dashboard(dashboard;file;algo_tasks;algo;workers;dry_run;results)
    _run_micro_dashboard(dashboard;file;micro_tasks;micro;micro_workers;model;dry_run;cache;results)
    _run_big_dashboard(dashboard;file;big_tasks;all_phases;workers;backend;rate_limit;proxy_url;dry_run;results)
    _run_with_dashboard(file;tasks;algo;micro;all_phases;workers;micro_workers;model;backend;rate_limit;proxy_url;dry_run)
    _run_hybrid_with_dashboard(file;fixer;hybrid;dry_run)
    _run_batch_with_dashboard(backend_fixer;tasks;parallel;dry_run)
    todo_stats(file)
    todo_verify(file)
    todo_fix_parallel(file;workers;dry_run;category)
    todo_list(file)
    todo_run(file;tool;dry_run;limit)
    _format_todo_help()
    todo_fix(file;tool;task_id;limit;dry_run;algo;micro;all_phases;dashboard;workers;micro_workers;model;backend;rate_limit;proxy_url;verbose)
    _tf_parse_and_filter(file;task_id;limit)
    _tf_classify_tasks(tasks)
    _tf_execute_phased(file;classified;algo;micro;all_phases;workers;micro_workers;model;backend;rate_limit;proxy_url;dry_run)
    _tf_build_phases(classified;algo;micro;all_phases)
    _tf_run_algorithm(file;tasks;workers)
    _aggregate_micro_results(micro_results)
    _mark_micro_completed(file;dry_run;micro_results;tasks)
    _tf_run_micro(file;tasks;_workers;micro_workers;model)
    _tf_run_big(file;tasks;workers;_micro_workers;_model;backend;proxy_url;rate_limit;dry_run)
    _tf_validate_results(results)
    _tf_print_report(report)
    _tf_run_legacy(file;tasks;tool;dry_run)
    todo_benchmark(limit;file;workers;compare)
    _print_hybrid_banner(hybrid;backend;tool;workers;rate_limit;proxy_url;fallback;verbose;dry_run)
    _update_todo_hybrid(file;dry_run;result)
    todo_hybrid(file;backend;tool;workers;rate_limit;proxy_url;hybrid;dashboard;fallback;verbose;dry_run)
    todo_batch(file;backend;model;batch_size;parallel;dry_run;verbose;prune;limit;no_log;dashboard)
    todo_verify_prefact(file;prune)
  src/algitex/cli/todo_verify.py:
    e: todo_verify_prefact,_validate_tasks
    todo_verify_prefact(file;prune)
    _validate_tasks(tasks)
  src/algitex/cli/workflow.py:
    e: workflow_run,workflow_validate
    workflow_run(path;dry_run)
    workflow_validate(path)
  src/algitex/cli.py:
  src/algitex/config.py:
    e: _find_config,_merge_yaml,ProxyConfig,TicketConfig,AnalysisConfig,Config
    ProxyConfig: from_env(1)  # Proxym gateway settings.
    TicketConfig: from_env(1)  # Planfile ticket system settings.
    AnalysisConfig: from_env(1)  # Code analysis tool settings.
    Config: load(2),save(1)  # Unified config for the entire algitex stack.
    _find_config(explicit)
    _merge_yaml(cfg;path)
  src/algitex/dashboard.py:
    e: show_quick_dashboard,TierState,CacheState,LiveDashboard,SimpleProgressTracker
    TierState: percent(0),eta_seconds(0)  # State tracking for a single tier.
    CacheState: hit_rate(0),size_mb(0)  # State tracking for cache metrics.
    LiveDashboard: __init__(1),_create_layout(0),_render_header(0),_render_cache_panel(0),_render_tiers_panel(0),_render_footer(0),_render(0),_update_loop(0),start(0),_run_live(0),stop(0),update_cache_stats(4),update_tier_progress(7),set_on_update(1),__enter__(0),__exit__(0)  # Live Rich dashboard for monitoring algitex operations.
    SimpleProgressTracker: __init__(1),start(0),add_task(2),update(3),stop(0),__enter__(0),__exit__(0)  # Simplified progress tracking without full dashboard.
    show_quick_dashboard(duration)
  src/algitex/metrics.py:
    e: get_metrics,reset_metrics,LLMCall,FixResult,MetricsCollector,MetricsReporter
    LLMCall: to_dict(0)  # Single LLM call record.
    FixResult:  # Single fix execution record.
    MetricsCollector: __init__(1),record_llm_call(8),record_fix(7),get_tier_stats(0),estimate_cost(0),get_summary(0),save(0),load(0),reset(0)  # Collect metrics during algitex operations.
    MetricsReporter: __init__(1),print_dashboard(1),export_csv(1)  # Generate reports and dashboards from metrics.
    get_metrics()
    reset_metrics()
  src/algitex/microtask/__init__.py:
    e: group_tasks_by_file,TaskType,MicroTask,MicroTaskBatch
    TaskType: tier(0),model_hint(0),max_context_tokens(0),max_output_tokens(0)  # Classification tiers for micro tasks.
    MicroTask: tier(0),is_algorithmic(0),needs_llm(0),span(0)  # Atomic unit of work for a single file change.
    MicroTaskBatch: algo_tasks(0),llm_tasks(0),stats(0)  # Tasks grouped by file for execution.
    group_tasks_by_file(tasks)
  src/algitex/microtask/classifier.py:
    e: classify_prefact_line,classify_todo_file,_classify_message,_resolve_file,_is_ignored_path,_first_int,_extract_function_name,_extract_suggestion
    classify_prefact_line(line;task_id;base_dir)
    classify_todo_file(path)
    _classify_message(message)
    _resolve_file(file_path;base_dir)
    _is_ignored_path(file_path)
    _first_int(text)
    _extract_function_name(message)
    _extract_suggestion(message)
  src/algitex/microtask/executor.py:
    e: PhaseResult,MicroTaskExecutor
    PhaseResult: throughput(0),as_dict(0)  # Summary for a single execution phase.
    MicroTaskExecutor: __init__(5),execute(2),group_by_file(1),_phase_algorithmic(2),_process_algorithmic_batch(2),_handle_unused_import(2),_handle_return_type(2),_handle_known_magic(2),_handle_fstring(2),_handle_sort_imports(2),_handle_trailing_whitespace(2),_phase_llm(4),_process_llm_batch(2),_supports_algorithmic(1),_apply_line_fix(2),_apply_fstring_fix(2),_apply_llm_response(2),_apply_magic_name(3),_replace_magic_number(4),_insert_constant(3),_write_if_valid(3),_apply_rewrite(3),_strip_trailing_whitespace(1),_todo_category(1),_resolve_path(1),_find_import_insert_point(1),_first_int(1),_sanitize_constant_name(2),_strip_code_fences(1),_validate_python(1),close(0)  # Execute micro tasks in three tiers: algorithmic, small LLM, 
  src/algitex/microtask/prompts.py:
    e: _SafeDict,PromptBuilder
    _SafeDict: __missing__(1)
    PromptBuilder: __init__(1),build(1),_select_model(1),_build_instruction(1),_build_user_prompt(2)  # Build compact chat prompts for local LLMs.
  src/algitex/microtask/slicer.py:
    e: ContextSlicer
    ContextSlicer: __init__(1),slice(1),_resolve_path(1),_extract_function(3),_expand_window(3),_extract_lines(3),_estimate_tokens(1)  # Extract the smallest useful context for a micro task.
  src/algitex/nlp/__init__.py:
    e: sort_imports_in_path,find_duplicate_blocks,_sort_imports,_fallback_sort_imports,_python_files,_is_ignored,_ensure_trailing_newline,_stable_line_hash,DocstringChange,DocstringShortener,DeadCodeDetector,_DuplicateWindow,_UsageCollector
    DocstringChange:  # Single docstring rewrite.
    DocstringShortener: shorten(1),fix_file(2),fix_path(2),_iter_docstring_nodes(1)  # Shorten verbose docstrings to one or two lines.
    DeadCodeDetector: scan(1)  # Detect top-level functions that appear unused.
    _DuplicateWindow:
    _UsageCollector: __init__(0),visit_ClassDef(1),visit_FunctionDef(1),visit_AsyncFunctionDef(1),visit_Name(1),visit_Attribute(1)
    sort_imports_in_path(path;apply)
    find_duplicate_blocks(project_path;min_lines)
    _sort_imports(source)
    _fallback_sort_imports(source)
    _python_files(path)
    _is_ignored(path)
    _ensure_trailing_newline(text)
    _stable_line_hash(line)
  src/algitex/prefact_integration.py:
    e: run_prefact_check,check_file_with_prefact,PrefactIssue,PrefactRuleAdapter,SharedRuleEngine
    PrefactIssue: to_dict(0)  # Issue found by prefact rule.
    PrefactRuleAdapter: __init__(1),_find_prefact(0),is_available(0),scan_file(1),scan_directory(1),_parse_issues(2),check_sorted_imports(1),check_relative_imports(1),get_rules_info(0)  # Adapter to run prefact rules from algitex.
    SharedRuleEngine: __init__(0),_register_builtin_rules(0),_check_unused_import_native(1),_check_return_type_native(1),analyze(1),get_all_issues(1)  # Unified rule engine combining algitex and prefact rules.
    run_prefact_check(file_path)
    check_file_with_prefact(file_path;rule)
  src/algitex/project.py:
  src/algitex/propact/__init__.py:
    e: WorkflowStep,WorkflowResult,Workflow
    WorkflowStep: to_dict(0)  # Single executable step in a Propact workflow.
    WorkflowResult: success(0)  # Result of workflow execution.
    Workflow: __init__(1),parse(0),_extract_steps_from_content(1),validate(0),_execute_step(3),_update_result(3),_handle_step_failure(2),execute(0),status(0),_exec_shell(1),_exec_rest(2),_parse_rest_block(2),_extract_proxy_cost(1),_exec_mcp(2),_exec_docker(2),_execute_with_manager(6),_exec_llm(2)  # Parse and execute Propact Markdown workflows.
  src/algitex/propact/workflow.py:
  src/algitex/shared_rules.py:
    e: get_registry,reset_registry,RuleContext,RuleViolation,FixStrategy,SharedRule,SortedImportsRule,RelativeImportRule,RuleRegistry
    RuleContext: __post_init__(0)  # Context for rule execution.
    RuleViolation: __post_init__(0),to_dict(0)  # Single rule violation.
    FixStrategy: apply(2),is_safe(2)  # Protocol for auto-fix implementations.
    SharedRule: rule_id(0),description(0),tier(0),fixable(0),severity(0),check(1),fix(2),_apply_fix(2)  # Abstract base class for rules shared between algitex and pre
    SortedImportsRule: check(1),_apply_fix(2)  # Rule: imports should be sorted (stdlib, third-party, local).
    RelativeImportRule: check(1)  # Rule: prefer absolute imports over relative.
    RuleRegistry: __init__(0),register(1),get(1),list_rules(1),check_file(2)  # Registry of shared rules.
    get_registry()
    reset_registry()
  src/algitex/todo/__init__.py:
    e: fix_todos
    fix_todos(todo_path;workers;dry_run;category;categories;tasks)
  src/algitex/todo/audit.py:
    e: AuditEntry,ChangeRecord,AuditLogger
    AuditEntry:  # Single audit entry for an operation.
    ChangeRecord:  # Record of a single file change for rollback.
    AuditLogger: __init__(1),_get_user(0),_hash_content(1),_generate_op_id(0),start_operation(4),log_change(4),complete_operation(4),_write_entry(2),get_history(3),get_last_operation(0),rollback_operation(1),rollback_last(0),print_summary(1)  # Comprehensive audit logging with rollback support.
  src/algitex/todo/benchmark.py:
    e: _benchmark_single,benchmark_sequential,benchmark_parallel,benchmark_fix,compare_modes,BenchmarkResult
    BenchmarkResult: avg_time_ms(0),median_time_ms(0),min_time_ms(0),max_time_ms(0),stdev_time_ms(0),throughput_tps(0),print_report(1)  # Benchmark results for fix operations.
    _benchmark_single(task;dry_run)
    benchmark_sequential(tasks;dry_run)
    benchmark_parallel(tasks;workers;dry_run)
    benchmark_fix(todo_path;limit;workers;dry_run;mode)
    compare_modes(todo_path;limit;workers;dry_run)
  src/algitex/todo/classify.py:
    e: _first_int,classify_message,classify_task,TaskTriage
    TaskTriage: tier_label(0),is_algorithmic(0),is_micro(0),is_big(0)  # Classification result for a single TODO task.
    _first_int(text)
    classify_message(message)
    classify_task(task)
  src/algitex/todo/fixer.py:
    e: parse_todo,_categorize,_group_tasks_by_file,_compute_category_stats,_compute_tier_stats,_print_pre_execution_summary,_print_execution_summary,_validate_file_with_vallm,_group_tasks_by_category,_process_line_tasks,fix_file,_extract_return_type,_get_repair_param,_record_fix_result,_process_magic_batch,_process_fstring_batch,_process_exec_batch,_execute_parallel_fixes,parallel_fix,mark_tasks_completed,parallel_fix_and_update,FixResult
    FixResult:  # Result of fixing a file.
    parse_todo(todo_path)
    _categorize(message)
    _group_tasks_by_file(tasks)
    _compute_category_stats(tasks)
    _compute_tier_stats(tasks)
    _print_pre_execution_summary(tasks;by_file;workers;dry_run)
    _print_execution_summary(total_fixed;total_skipped;total_errors;dry_run)
    _validate_file_with_vallm(path;original_content)
    _group_tasks_by_category(tasks)
    _process_line_tasks(path;tasks;result;dry_run;original_content)
    fix_file(file_path;tasks;dry_run)
    _extract_return_type(message)
    _get_repair_param(task)
    _record_fix_result(task;path;original_content;ok;result)
    _process_magic_batch(path;tasks;result;dry_run;original_content)
    _process_fstring_batch(path;tasks;result;dry_run;original_content)
    _process_exec_batch(path;tasks;result;dry_run;original_content)
    _execute_parallel_fixes(by_file;workers;dry_run)
    parallel_fix(todo_path;workers;dry_run;category_filter;categories;tasks)
    mark_tasks_completed(todo_path;completed_tasks)
    parallel_fix_and_update(todo_path;workers;dry_run;category_filter;categories;tasks)
  src/algitex/todo/hybrid.py:
    e: HybridResult,RateLimiter,LLMTask,HybridAutofix
    HybridResult:  # Result of hybrid fix operation.
    RateLimiter: __init__(2),acquire(0)  # Token bucket rate limiter for LLM calls.
    LLMTask:  # Task for LLM-based fixing.
    HybridAutofix: __init__(9),fix_mechanical(1),fix_complex(4),_process_llm_parallel(1),_fix_file_llm(2),_call_llm_backend(2),fix_all(1),print_summary(1)  # Hybrid autofix: parallel mechanical + rate-limited parallel 
  src/algitex/todo/micro.py:
    e: MicroFixer
    MicroFixer: __init__(4),fix_file(2),fix_task(1),run(3),fix_tasks_detailed(2),fix_tasks(2),_fix_magic_name(3),_apply_function_rewrite(5),_apply_magic_name(5)  # Execute micro-LLM fixes on a TODO file.
  src/algitex/todo/micro_extractor.py:
    e: FunctionExtractor
    FunctionExtractor: extract(2)  # Extract a single function or method around a task line.
  src/algitex/todo/micro_models.py:
    e: FunctionSnippet,MicroFixResult
    FunctionSnippet: line_count(0)  # Minimal source slice around a function or method.
    MicroFixResult:  # Result of a micro-LLM fix.
  src/algitex/todo/micro_prompts.py:
    e: MicroPromptBuilder
    MicroPromptBuilder: build(3),_build_user_prompt(3)  # Build narrow prompts for micro-LLM fixes.
  src/algitex/todo/micro_utils.py:
    e: find_import_insert_point,extract_first_int,normalise_model_name,strip_code_fences,sanitize_constant_name,validate_python,coerce_task
    find_import_insert_point(lines)
    extract_first_int(text)
    normalise_model_name(model)
    strip_code_fences(text)
    sanitize_constant_name(text;number)
    validate_python(source)
    coerce_task(task)
  src/algitex/todo/repair.py:
    e: _find_import_insert_point,repair_unused_import,repair_return_type,_simple_fstring_rewrite,repair_fstring,repair_magic_number,repair_module_block
    _find_import_insert_point(lines)
    repair_unused_import(path;name;line_idx)
    repair_return_type(path;suggested;line_idx)
    _simple_fstring_rewrite(line)
    repair_fstring(path;_unused;_unused2)
    repair_magic_number(path;number;line_idx;const_name)
    repair_module_block(path;_unused;_unused2)
  src/algitex/todo/tiering.py:
    e: _first_int,summarise_tasks,load_todo_tasks,filter_tasks,partition_tasks,TierSummary
    TierSummary: add(1),algorithmic(0),micro(0),big(0),tier_percent(1),top_categories(1)  # Aggregated classification summary for a TODO list.
    _first_int(text)
    summarise_tasks(tasks)
    load_todo_tasks(todo_path)
    filter_tasks(tasks)
    partition_tasks(tasks)
  src/algitex/todo/verifier.py:
    e: verify_todos,TodoTask,VerificationResult,TodoVerifier
    TodoTask:  # Single TODO task from prefact output.
    VerificationResult:  # Result of TODO verification.
    TodoVerifier: __init__(1),parse(0),verify(0),_verify_task(1),_check_by_type(1),_check_unused_import(2),print_report(0)  # Verify which TODO tasks from prefact are still valid.
    verify_todos(todo_path)
  src/algitex/todo/verify.py:
    e: verify_todos,_run_prefact_scan,_parse_todo_file,_diff_issues,_validate_task_against_file,_format_verify_report,prune_outdated_tasks,VerifyResult
    VerifyResult:  # Result of TODO verification.
    verify_todos(todo_path;project_path)
    _run_prefact_scan(project_path)
    _parse_todo_file(todo_path)
    _diff_issues(raw;existing)
    _validate_task_against_file(task)
    _format_verify_report(result)
    prune_outdated_tasks(todo_path;result)
  src/algitex/tools/__init__.py:
    e: discover_tools,require_tool,get_tool_module,ToolStatus
    ToolStatus: emoji(0),__str__(0)
    discover_tools()
    require_tool(name)
    get_tool_module(name)
  src/algitex/tools/analysis.py:
    e: _run_cli,HealthReport,Analyzer,CLIResult
    HealthReport: passed(0),grade(0),summary(0)  # Combined analysis result from all tools.
    Analyzer: __init__(1),health(0),full(0),_run_code2llm(1),_run_vallm(1),_run_redup(1)  # Unified interface for code analysis tools.
    CLIResult:
    _run_cli(cmd;cwd)
  src/algitex/tools/autofix/__init__.py:
    e: AutoFix
    AutoFix: __init__(5),ollama_service(0),ollama_backend(0),aider_backend(0),proxy_backend(0),check_backends(0),choose_backend(0),_convert_task(1),mark_task_done(1),fix_with_ollama(1),fix_with_aider(1),fix_with_proxy(1),fix_task(2),fix_all(3),fix_issue(2),print_summary(1),list_tasks(0),get_stats(0)  # Automated code fixing using various backends.
  src/algitex/tools/autofix/aider_backend.py:
    e: AiderBackend
    AiderBackend: __init__(1),fix(1),_validate_task(2),_ensure_git_repo(0),_build_command(1),_build_prompt(1),_execute_aider(2),_process_result(3),_dry_run_result(2),_timeout_result(2),_error_result(3)  # Fix issues using Aider CLI.
  src/algitex/tools/autofix/base.py:
    e: FixResult,AutoFixBackend
    FixResult: to_dict(0)  # Result of fixing an issue.
    AutoFixBackend: fix(1)  # Base class for autofix backends.
  src/algitex/tools/autofix/batch_backend/__init__.py:
  src/algitex/tools/autofix/batch_backend/backend.py:
    e: BatchFixBackend
    BatchFixBackend: __init__(5),fix_batch(2),_group_tasks(1),_verify_tasks_exist(1),_process_group(3)  # Backend do optymalizacji fixów przez grupowanie.
  src/algitex/tools/autofix/batch_backend/fs_utils.py:
    e: create_backup,preflight_syntax_check
    create_backup()
    preflight_syntax_check(tasks)
  src/algitex/tools/autofix/batch_backend/models.py:
    e: TaskGroup
    TaskGroup:  # Grupa podobnych zadań do batch fix.
  src/algitex/tools/autofix/batch_backend/todo_utils.py:
    e: update_todo_mark_completed
    update_todo_mark_completed(tasks;results;elapsed)
  src/algitex/tools/autofix/batch_backend.py:
    e: TaskGroup,BatchFixBackend
    TaskGroup:  # Grupa podobnych zadań do batch fix.
    BatchFixBackend: __init__(5),fix_batch(2),_update_todo_mark_completed(3),_create_backup(0),_preflight_syntax_check(1),_verify_tasks_exist(1),_group_tasks(1),_process_group(3),_fix_batch_group(1),_fix_individual(1),_fix_single(1),_build_batch_prompt(1),_call_llm(3),_parse_batch_response(2),_extract_fixed_sections(1),_write_file_fix(3),_mark_missing_as_failed(2),_validate_and_rollback(2),_ensure_model(0)  # Backend do optymalizacji fixów przez grupowanie.
  src/algitex/tools/autofix/batch_logger.py:
    e: get_logger,start_session,end_session,BatchLogEntry,BatchSessionLog,BatchLogger
    BatchLogEntry:  # Single entry in batch log.
    BatchSessionLog: add_entry(1),finalize(0),to_markdown(0),_render_header(0),_render_config(0),_render_summary(0),_render_details(0),save(1)  # Complete log of batch session.
    BatchLogger: __init__(3),start_group(4),end_group(2),set_totals(2),finalize(0),print_summary(0)  # Logger for batch operations with markdown output.
    get_logger()
    start_session(backend;batch_size;parallel)
    end_session()
  src/algitex/tools/autofix/fallback_backend.py:
    e: BackendStatus,FallbackBackend
    BackendStatus:  # Status of a backend.
    FallbackBackend: __init__(8),_get_backend(1),_mark_success(1),_mark_failure(2),_try_backend(2),fix(1),print_status(0)  # Backend with automatic failover to alternative LLM services.
  src/algitex/tools/autofix/ollama_backend.py:
    e: OllamaBackend
    OllamaBackend: __init__(5),fix(1),_is_healthy(0),_ensure_model(0),_apply_fix(2),_success_result(4),_error_result(3)  # Fix issues using Ollama local models.
  src/algitex/tools/autofix/openrouter_backend.py:
    e: OpenRouterBackend
    OpenRouterBackend: __init__(3),fix(1),_validate(2),_execute_fix(2),_read_file(1),_build_prompt(2),_call_api(1),_extract_code(1),_write_file(2),_success_result(2),_dry_run_result(2),_error_result(3)  # Fix issues using OpenRouter API directly.
  src/algitex/tools/autofix/proxy_backend.py:
    e: ProxyBackend
    ProxyBackend: __init__(2),fix(1),_validate(2),_execute_fix(2),_read_file(1),_build_prompt(2),_call_api(1),_extract_code(1),_write_file(2),_success_result(2),_dry_run_result(2),_error_result(3)  # Fix issues using LiteLLM proxy.
  src/algitex/tools/autofix.py:
  src/algitex/tools/batch.py:
    e: BatchResult,BatchStats,BatchProcessor,FileBatchProcessor
    BatchResult: to_dict(0)  # Result from batch processing.
    BatchStats: update(1)  # Statistics for batch processing.
    BatchProcessor: __init__(9),_rate_limit(0),_process_item(2),process(2),_prepare(1),_execute(2),_collect(1),_setup_progress_bar(1),_collect_results(3),_get_start_time(0),_print_summary(1),_save_results(0),get_successful(0),get_failed(0),filter_by_error(1)  # Generic batch processor with rate limiting and retries.
    FileBatchProcessor: __init__(4),find_files(3),process_directory(2)  # Specialized batch processor for files.
  src/algitex/tools/benchmark.py:
    e: Task,TaskResult,BenchmarkResults,ModelBenchmark
    Task: evaluate_quality(1)  # Benchmark task definition.
    TaskResult: tokens_per_second(0),to_dict(0)  # Result for a single model on a single task.
    BenchmarkResults: get_model_results(1),get_task_results(1),get_best_model(2),to_dict(0),get_summary(0)  # Complete benchmark results.
    ModelBenchmark: __init__(2),_add_default_tasks(0),add_task(1),add_custom_task(4),run_single_task(2),compare_models(3),print_results(2),_print_table(1),_print_summary(1),_print_detailed(1),save_results(2),load_results(1)  # Benchmark models on standardized tasks.
  src/algitex/tools/cicd.py:
    e: init_ci_cd,create_quality_gate_config,CICDGenerator
    CICDGenerator: __init__(1),_load_config(0),generate_github_actions(1),generate_gitlab_ci(1),_get_complexity_check(0),generate_dockerfile(1),generate_precommit_config(1),generate_all(4),update_config(1)  # Generate CI/CD pipelines for algitex projects.
    init_ci_cd(project_path;platform)
    create_quality_gate_config(max_cc;require_tests;security_scan)
  src/algitex/tools/config.py:
    e: ConfigManager
    ConfigManager: __init__(1),_ensure_dir(1),_backup_file(1),install_config(3),generate_continue_config(3),install_continue_config(2),generate_vscode_settings(2),install_vscode_settings(2),generate_env_file(2),generate_docker_compose(2),setup_project_configs(2),list_configs(1),_list_continue_configs(1),_list_vscode_configs(1),_list_env_configs(0),_list_docker_configs(0)  # Manages configuration files for various IDEs and tools.
  src/algitex/tools/context.py:
    e: CodeContext,ContextBuilder,SemanticCache
    CodeContext: to_prompt(1)  # Assembled context for an LLM coding task.
    ContextBuilder: __init__(1),build(2),_load_toon_summary(0),_load_architecture(0),_resolve_targets(1),_find_related(1),_load_conventions(0),_git_recent(0),_format_ticket(1)  # Build rich context for LLM coding tasks from .toon files + g
    SemanticCache: __init__(2),_get_client(0),search_similar_context(2),store_context(3)  # Optional semantic caching using Qdrant for context retrieval
  src/algitex/tools/docker.py:
    e: DockerTool,RunningTool,DockerToolManager
    DockerTool: is_mcp(0),is_rest(0)  # Single Docker-based tool declaration from docker-tools.yaml.
    RunningTool:  # A spawned Docker container with connection info.
    DockerToolManager: __init__(1),__enter__(0),__exit__(3),_load_tools(0),_read_yaml_with_expansion(1),_expand_tool_spec(1),_expand_env_vars(1),_expand_volumes(1),_load_state(0),_save_state(0),spawn(1),_wait_healthy(2),_get_http_client(0),call_tool(3),teardown(1),teardown_all(0),list_tools(0),list_running(0),get_capabilities(1),_query_stdio_capabilities(1)  # Spawn Docker containers, connect via MCP/REST, call tools, t
  src/algitex/tools/docker_transport.py:
    e: spawn_stdio,spawn_sse,spawn_rest,spawn_cli,call_stdio,call_sse,call_rest,call_cli,StdioTransport
    StdioTransport: __init__(1),send(2),_serialize(1),_write(2),_read_with_timeout(1),_wait_for_ready(2),_check_process_alive(1),_extract_length(1),_parse(1)  # Transport layer for JSON-RPC over stdin/stdout communication
    spawn_stdio(tool;env;running;save_state)
    spawn_sse(tool;env;running;save_state;wait_healthy)
    spawn_rest(tool;env;running;save_state)
    spawn_cli(tool;env;running;save_state)
    call_stdio(rt;tool;args;get_client)
    call_sse(rt;tool;args;get_client)
    call_rest(rt;tool;args;get_client)
    call_cli(rt;cmd;args;get_client)
  src/algitex/tools/feedback.py:
    e: FailureStrategy,FeedbackPolicy,FeedbackController,FeedbackLoop
    FailureStrategy:
    FeedbackPolicy: __post_init__(0)  # Policy configuration for feedback handling.
    FeedbackController: __init__(1),on_validation_failure(3),on_success(2),needs_approval(1),_extract_feedback(1)  # Orchestrate retry/replan/escalate decisions.
    FeedbackLoop: __init__(3),execute_with_feedback(2),_execute_single(2),_validate_result(1),_mark_ticket_done(3),_mark_ticket_skipped(2)  # Integrates feedback controller into the pipeline execution.
  src/algitex/tools/ide.py:
    e: AiderHelper,VSCodeHelper,EditorIntegration
    AiderHelper: __init__(0),fix_file(4)  # Helper for Aider integration.
    VSCodeHelper: __init__(0),open_file(2),install_extensions(1),recommended_extensions(0)  # Helper for VS Code integration.
    EditorIntegration: __init__(0),detect_editor(0),setup_best_integration(0),get_quick_fix_command(3)  # High-level editor integration manager.
  src/algitex/tools/ide_aider.py:
    e: AiderHelper
    AiderHelper: __init__(0),fix_file(4)  # Helper for Aider integration.
  src/algitex/tools/ide_base.py:
    e: IDEHelper
    IDEHelper: __init__(0),_register_default_tools(0),check_tool(1),setup_tool(1),list_tools(0),get_tool_status(0)  # Base class for IDE integrations.
  src/algitex/tools/ide_claude.py:
    e: ClaudeCodeHelper
    ClaudeCodeHelper: __init__(0),setup_environment(0),fix_file(4),chat(3),batch_fix(3)  # Helper for Claude Code (anthropic-curl) integration.
  src/algitex/tools/ide_models.py:
    e: IDETool
    IDETool: __post_init__(0)  # IDE tool configuration.
  src/algitex/tools/logging.py:
    e: set_verbose,log_calls,log_time,verbose,format_args,format_value,format_result,verbose_print,VerboseContext
    VerboseContext: __init__(1),__enter__(0),__exit__(3)  # Context manager for verbose logging in a block.
    set_verbose(enabled)
    log_calls(func)
    log_time(func)
    verbose(func)
    format_args(args;kwargs)
    format_value(value)
    format_result(result)
    verbose_print(msg;level)
  src/algitex/tools/mcp.py:
    e: MCPOrchestrator
    MCPOrchestrator: __init__(0),_setup_signal_handlers(0),_register_default_services(0),add_service(1),add_custom_service(3),start_service(1),stop_service(2),restart_service(1),start_all(1),stop_all(1),wait_for_ready(2),check_health(0),get_logs(2),list_services(0),get_service_info(1),print_status(0),generate_mcp_config(1)  # Orchestrates multiple MCP services.
  src/algitex/tools/mcp_defaults.py:
    e: build_default_services
    build_default_services()
  src/algitex/tools/mcp_lifecycle.py:
    e: MCPLifecycleManager
    MCPLifecycleManager: __init__(1),add_service(1),add_custom_service(3),start_service(1),stop_service(2),restart_service(1)  # Start/stop/restart operations for MCP services.
  src/algitex/tools/mcp_models.py:
    e: MCPService
    MCPService: __post_init__(0)  # Definition of an MCP service.
  src/algitex/tools/ollama.py:
    e: OllamaModel,OllamaResponse,OllamaClient,OllamaService
    OllamaModel: display_name(0)  # Information about an Ollama model.
    OllamaResponse: __str__(0)  # Response from Ollama API.
    OllamaClient: __init__(3),health(0),list_models(0),pull_model(1),generate(7),chat(6),fix_code(4),analyze_code(3),close(0),__enter__(0),__exit__(0)  # Client for interacting with Ollama API.
    OllamaService: __init__(1),ensure_model(1),get_recommended_models(0),auto_fix_file(4)  # High-level service for Ollama operations.
  src/algitex/tools/ollama_cache.py:
    e: CacheEntry,LLMCache,CachedOllamaClient
    CacheEntry: to_dict(0),from_dict(2)  # Single cache entry with metadata.
    LLMCache: __init__(2),_hash_prompt(2),_cache_path(1),get(2),set(5),clear(0),stats(0),list_entries(0)  # Disk-based cache for LLM responses.
    CachedOllamaClient: __init__(6),generate(2),get_metrics(0),clear_cache(0)  # OllamaClient with automatic response caching.
  src/algitex/tools/parallel/__init__.py:
  src/algitex/tools/parallel/executor.py:
    e: ParallelExecutor
    ParallelExecutor: __init__(2),execute(2),_dispatch_agents(3),_create_worktree(1),_run_agent(4),_merge_all(1),_detect_line_drift(1),_resolve_conflict(1),_changes_are_disjoint(2),_parse_diff_ranges(1),_cleanup_worktrees(0)  # Execute tickets in parallel using git worktrees + region loc
  src/algitex/tools/parallel/extractor.py:
    e: RegionExtractor
    RegionExtractor: __init__(1),extract_all(0),_should_skip_file(1),_extract_from_toon(1),_extract_from_file(1),_find_calls(1),_detect_shadow_conflicts(1)  # Extract lockable AST regions from Python files using map.too
  src/algitex/tools/parallel/models.py:
    e: RegionType,CodeRegion,TaskAssignment,MergeResult
    RegionType:  # Types of code regions that can be locked.
    CodeRegion: key(0),compute_signature_hash(1)  # An AST-level lockable region within a file.
    TaskAssignment:  # A ticket assigned to a specific agent with locked regions.
    MergeResult:  # Result of merging agent worktrees back to main.
  src/algitex/tools/parallel/partitioner.py:
    e: TaskPartitioner
    TaskPartitioner: __init__(1),partition(2),_compute_footprints(1),_build_conflict_graph(2),_greedy_coloring(4),_group_by_color(1),_regions_by_symbol(2)  # Partition tickets into non-conflicting groups for parallel e
  src/algitex/tools/parallel.py:
  src/algitex/tools/proxy.py:
    e: LLMResponse,Proxy
    LLMResponse: __str__(0)  # Simplified LLM response.
    Proxy: __init__(1),ask(1),budget(0),models(0),health(0),close(0),__enter__(0),__exit__(0)  # Simple wrapper around proxym gateway.
  src/algitex/tools/services/__init__.py:
  src/algitex/tools/services/checker.py:
    e: ServiceChecker
    ServiceChecker: __init__(1),check_all(1)  # Checker for various services used by algitex.
  src/algitex/tools/services/http_checks.py:
    e: HTTPServiceChecks
    HTTPServiceChecks: __init__(1),check_http_service(4),check_ollama(1),check_litellm_proxy(1),check_mcp_service(2)  # HTTP-based checks for external services.
  src/algitex/tools/services/local_checks.py:
    e: LocalSystemChecks
    LocalSystemChecks: __init__(1),check_command_exists(2),check_file_exists(2)  # Local command and file existence checks.
  src/algitex/tools/services/models.py:
    e: ServiceStatus
    ServiceStatus: status_icon(0),to_dict(0)  # Status of a single service.
  src/algitex/tools/services.py:
    e: ServiceStatus,ServiceChecker,ServiceDependency
    ServiceStatus: status_icon(0),to_dict(0)  # Status of a single service.
    ServiceChecker: __init__(1),check_http_service(4),check_ollama(1),check_litellm_proxy(1),check_mcp_service(2),check_command_exists(2),check_file_exists(2),check_all(1),_format_status_line(1),_print_status_details(1),print_status(2),get_unhealthy(1),wait_for_services(3),close(0),__enter__(0),__exit__(0)  # Checker for various services used by algitex.
    ServiceDependency: __init__(1),get_startup_order(1),check_with_dependencies(1)  # Manage service dependencies and startup order.
  src/algitex/tools/telemetry.py:
    e: TraceSpan,Telemetry
    TraceSpan: duration_s(0),finish(1),__enter__(0),__exit__(3)  # Single operation span.
    Telemetry: __init__(2),span(2),total_cost(0),total_tokens(0),total_duration(0),error_count(0),summary(0),push_to_langfuse(0),save(1),report(0)  # Track costs, tokens, time across an algitex pipeline run.
  src/algitex/tools/tickets.py:
    e: Ticket,Tickets
    Ticket: to_dict(0)  # A single work item.
    Tickets: __init__(2),add(1),from_analysis(1),list(1),update(1),sync(0),board(0),_load(0),_save(0),_planfile_add(1)  # Manage project tickets via planfile or local YAML.
  src/algitex/tools/todo_actions.py:
    e: nap_action,aider_action,ollama_action,filesystem_action,github_action,get_action_handler,determine_action
    nap_action(task)
    aider_action(task)
    ollama_action(task)
    filesystem_action(task)
    github_action(task)
    get_action_handler(tool)
    determine_action(task;tool)
  src/algitex/tools/todo_executor.py:
    e: TaskResult,TodoExecutor
    TaskResult:  # Result of executing a single task.
    TodoExecutor: __init__(2),__enter__(0),__exit__(3),run(3),_execute_task(3),_parse_action(1),_parse_fix_action(1),_parse_create_action(1),_parse_delete_action(1),_parse_read_action(1),_extract_output(1),get_summary(0)  # Execute todo tasks using Docker MCP tools.
  src/algitex/tools/todo_local.py:
    e: LocalTaskResult,LocalExecutor
    LocalTaskResult:  # Result of executing a single task locally.
    LocalExecutor: __init__(1),can_execute(1),_determine_fix_and_apply(2),execute(1),_fix_return_type(3),_has_return_type(2),_import_exists(3),_fix_unused_import(3),_fix_fstring(2),_fix_standalone_main(1),_add_main_block(1)  # Execute simple code fixes locally without Docker.
  src/algitex/tools/todo_parser.py:
    e: Task,TodoParser
    Task: to_dict(0)  # Single todo task extracted from file.
    TodoParser: __init__(1),parse(0),_parse_prefact(1),_parse_github(1),_parse_generic(1),_extract_location(1),get_stats(0)  # Parse todo lists from Markdown and text files.
  src/algitex/tools/todo_runner.py:
    e: TodoRunner
    TodoRunner: __init__(2),__enter__(0),__exit__(3),run_from_file(4),run(3),_execute_local(2),_execute_ollama(2),_build_ollama_prompt(2),_call_ollama_api(1),_execute_task(3),_format_output(1),get_summary(0)  # Execute todo tasks using Docker MCP tools with local fallbac
  src/algitex/tools/workspace.py:
    e: create_workspace_template,init_workspace,RepoConfig,Workspace
    RepoConfig: __post_init__(0)  # Configuration for a single repository in the workspace.
    Workspace: __init__(1),_load_config(0),_validate_dependencies(0),_topo_sort(0),clone_all(1),pull_all(0),analyze_all(1),plan_all(1),execute_all(2),validate_all(0),status(0),_get_repo_status(1),_get_git_status(1),_check_algitex_files(1),get_dependency_graph(0),find_repos_by_tag(1),get_execution_plan(0)  # Manage multiple repos as a single workspace.
    create_workspace_template(name;repos)
    init_workspace(name;config_path)
  src/algitex/workflows/__init__.py:
    e: Pipeline,TicketExecutor,TicketValidator
    Pipeline: __init__(2),analyze(1),create_tickets(0),execute(2),validate(0),sync(1),report(0),finish(0)  # Composable workflow: chain steps fluently.
    TicketExecutor: __init__(5),execute_tickets(2),_get_open_tickets(1),_execute_single_ticket(2),_call_tool_with_context(3),_validate_with_vallm(2),_mark_ticket_done(3),_build_fix_prompt(1)  # Handles ticket execution with Docker tools, telemetry, conte
    TicketValidator: __init__(1),validate_all(0),_run_security_scan(0)  # Multi-level validation: static analysis, runtime tests, secu
  src/algitex/workflows/pipeline.py:
  tests/conftest.py:
    e: clean_cwd,sample_workflow,sample_project
    clean_cwd(tmp_path;monkeypatch)
    sample_workflow(tmp_path)
    sample_project(tmp_path)
  tests/test_benchmark.py:
    e: TestBenchmarkResult,TestBenchmarkSuite,TestBenchmarkRunner,TestCacheBenchmark,TestTierBenchmark,TestMemoryBenchmark,TestRunQuickBenchmark
    TestBenchmarkResult: test_result_creation(0),test_result_to_dict(0)
    TestBenchmarkSuite: test_suite_creation(0),test_suite_add_result(0),test_suite_summary_empty(0),test_suite_summary_with_results(0)
    TestBenchmarkRunner: test_runner_creation(0),test_run_simple_benchmark(0),test_run_suite(0),test_export_json(0)
    TestCacheBenchmark: test_cache_hit_rate(0),test_cache_deduplication(0)
    TestTierBenchmark: test_algorithmic_fix(0),test_micro_llm_simulated(0),test_compare_tiers(0)
    TestMemoryBenchmark: test_profile_large_file_small(0),test_profile_large_file_medium(0)
    TestRunQuickBenchmark: test_quick_benchmark_runs(1)
  tests/test_cicd.py:
    e: TestCICDGenerator,TestCICDUtilities,TestCICDIntegration
    TestCICDGenerator: temp_project(0),test_generator_initialization(1),test_load_config_missing(1),test_generate_github_actions(1),test_generate_gitlab_ci(1),test_generate_dockerfile(1),test_generate_precommit_config(1),test_generate_all(1),test_custom_config_in_workflow(1),test_complexity_check_generation(1),test_update_config(1)  # Test the CICDGenerator class.
    TestCICDUtilities: test_init_ci_cd_github(1),test_init_ci_cd_gitlab(1),test_create_quality_gate_config(0)  # Test CI/CD utility functions.
    TestCICDIntegration: full_project(1),test_complete_ci_cd_generation(1),test_workflow_validation(1)  # Integration tests for CI/CD functionality.
  tests/test_cli.py:
    e: TestCLIBasic,TestCLITickets,TestCLIAlgo,TestCLIWorkflow,TestCLIAnalyze
    TestCLIBasic: test_help(0),test_tools(0),test_init(1),test_init_creates_yaml(1)
    TestCLITickets: test_ticket_add(2),test_ticket_add_with_priority(2),test_ticket_list_empty(2),test_ticket_list_with_data(2),test_ticket_board(2)
    TestCLIAlgo: test_algo_help(0),test_algo_discover(2),test_algo_extract_empty(2),test_algo_report(2)
    TestCLIWorkflow: test_workflow_help(0),test_workflow_validate_good(1),test_workflow_validate_bad(1),test_workflow_run_shell(2),test_workflow_run_dry(2)
    TestCLIAnalyze: test_analyze(2),test_plan(2)
  tests/test_cli_metrics.py:
    e: TestMetricsCLI,TestCacheCLI
    TestMetricsCLI: test_metrics_help(0),test_metrics_show_empty(0),test_metrics_cache_empty(0),test_metrics_cache_list_empty(0),test_metrics_clear(0),test_metrics_compare_empty(0),test_metrics_export_csv(0),test_metrics_cache_clear(0)
    TestCacheCLI: test_cache_stats_with_entries(0),test_cache_list_with_entries(0)
  tests/test_context.py:
    e: TestCodeContext,TestContextBuilder,TestSemanticCache
    TestCodeContext: test_code_context_creation(0),test_to_prompt(0)  # Test the CodeContext class.
    TestContextBuilder: temp_project(1),test_context_builder_creation(1),test_build_basic_context(1),test_load_toon_summary_missing(1),test_load_toon_summary_exists(1),test_load_architecture_missing(1),test_load_architecture_exists(1),test_resolve_targets(1),test_find_related_files(1),test_load_conventions(1),test_git_recent(1),test_git_recent_error(1),test_format_ticket(1),test_format_ticket_empty(1),test_build_with_ticket(1)  # Test the ContextBuilder class.
    TestSemanticCache: test_cache_creation(0),test_get_client_import_error(0),test_search_similar_context(0),test_store_context(0)  # Test the SemanticCache class.
  tests/test_core.py:
    e: TestConfig,TestToolDiscovery,TestTickets,TestHealthReport,TestAlgoLoop,TestPropactWorkflow,TestProject
    TestConfig: test_default(0),test_env_override(1),test_save_load(1)
    TestToolDiscovery: test_all_tools_registered(0),test_discover(0)
    TestTickets: test_add(1),test_from_analysis(1),test_persistence(1),test_board(1)
    TestHealthReport: test_grades(0),test_passed(0)
    TestAlgoLoop: test_init(1),test_discover(1),test_add_trace(1),test_extract_patterns(1),test_report(1),test_persistence(1)
    TestPropactWorkflow: test_parse(1),test_validate_good(1),test_validate_bad(1),test_execute_shell(1),test_dry_run(1)
    TestProject: test_init(1),test_algo_accessible(1),test_add_ticket(1)
  tests/test_dashboard.py:
    e: TestTierState,TestCacheState,TestLiveDashboard,TestSimpleProgressTracker,TestShowQuickDashboard,TestDashboardRender
    TestTierState: test_state_creation(0),test_percent_calculation(0),test_percent_zero_total(0),test_eta_calculation(0),test_eta_zero_throughput(0)
    TestCacheState: test_state_creation(0),test_hit_rate_calculation(0),test_hit_rate_zero_total(0),test_size_mb_calculation(0)
    TestLiveDashboard: test_dashboard_creation(0),test_update_cache_stats(0),test_update_tier_progress(0),test_update_unknown_tier(0),test_throughput_history(0),test_start_stop(0),test_context_manager(0),test_set_on_update(0)
    TestSimpleProgressTracker: test_tracker_creation(0),test_start_stop(0),test_add_task(0),test_update_task(0),test_update_unknown_task(0),test_context_manager(0)
    TestShowQuickDashboard: test_quick_dashboard_runs(1)
    TestDashboardRender: test_render_header(0),test_render_cache_panel(0),test_render_tiers_panel(0),test_render_footer(0)
  tests/test_e2e_integration.py:
    e: TestEndToEndIntegration
    TestEndToEndIntegration: sample_project(0),test_complete_pipeline_flow(1),test_telemetry_integration(1),test_context_integration(1),test_feedback_integration(1),test_multi_level_validation(1)  # Test the complete pipeline with all extensions.
  tests/test_examples_30_32.py:
    e: Test30ParallelExecution,Test31ABPRWorkflow,Test32WorkspaceCoordination,TestExampleStructure
    Test30ParallelExecution: test_parallel_refactoring_imports(0),test_parallel_multi_tool_imports(0),test_parallel_real_world_imports(0),test_parallel_refactoring_main_logic(4),test_parallel_multi_tool_tickets_structure(0)  # Test parallel execution examples.
    Test31ABPRWorkflow: test_abpr_pipeline_imports(0),test_abpr_pipeline_stages(2),test_workflow_files_exist(0)  # Test ABPR workflow examples.
    Test32WorkspaceCoordination: test_workspace_parallel_imports(0),test_workspace_yaml_structure(0),test_workspace_parallel_main_logic(0),test_workspace_dependency_order(0)  # Test workspace coordination examples.
    TestExampleStructure: test_required_files_exist(1),test_makefiles_have_targets(0),test_readme_structure(0)  # Test that all examples have correct structure.
  tests/test_feedback.py:
    e: TestFailureStrategy,TestFeedbackPolicy,TestFeedbackController,TestFeedbackLoop
    TestFailureStrategy: test_strategies(0)  # Test the FailureStrategy enum.
    TestFeedbackPolicy: test_default_policy(0),test_custom_policy(0)  # Test the FeedbackPolicy class.
    TestFeedbackController: test_controller_creation(0),test_controller_custom_policy(0),test_needs_approval(0),test_extract_feedback(0),test_on_validation_failure_retry(0),test_on_validation_failure_escalate(0),test_on_success(0),test_multiple_tickets(0)  # Test the FeedbackController class.
    TestFeedbackLoop: mock_deps(0),mock_loop(1),test_loop_creation(1),test_needs_approval_flow(1),test_successful_execution(2),test_retry_flow(2),test_escalate_flow(2),test_skip_flow(2),test_execute_single_mcp(1),test_execute_single_rest(1),test_execute_single_with_feedback(1),test_validate_result_with_vallm(1),test_validate_result_without_vallm(1),test_mark_ticket_done(1),test_mark_ticket_skipped(1)  # Test the FeedbackLoop class.
  tests/test_integration.py:
    e: TestProjectWorkflow,TestAlgoFullCycle,TestPropactWorkflowIntegration,TestPipelineIntegration,TestProxyMock,TestConfigIntegration,TestTicketsEdgeCases
    TestProjectWorkflow: test_analyze_plan_status(1),test_add_ticket_and_board(1),test_plan_generates_tickets_from_bad_report(1),test_cost_ledger_accumulates(1)  # Full project lifecycle: analyze → plan → tickets → status.
    TestAlgoFullCycle: test_full_algo_cycle(1),test_pattern_ordering_by_savings(1),test_min_frequency_filter(1)  # Full algo loop: discover → traces → extract → report.
    TestPropactWorkflowIntegration: test_multi_step_workflow(1),test_stop_on_error(1),test_continue_on_error(1),test_elapsed_time_tracked(1),test_workflow_title_extraction(1)  # Multi-step workflow execution.
    TestPipelineIntegration: test_analyze_and_report(1),test_full_pipeline_dry(1),test_pipeline_preserves_state(1)  # Pipeline composable steps.
    TestProxyMock: test_proxy_planfile_headers(0),test_llm_response_dataclass(0),test_proxy_health_offline(0),test_proxy_budget_offline(0)  # Proxy with mocked HTTP calls.
    TestConfigIntegration: test_full_config_load_save_roundtrip(1)
    TestTicketsEdgeCases: test_empty_board(1),test_update_nonexistent(1),test_sequential_ids(1),test_ticket_tags(1),test_ticket_meta_persists(1)
  tests/test_integration_extended.py:
    e: TestPipelineIntegration,TestPipelineWithRealFiles
    TestPipelineIntegration: temp_project(1),test_pipeline_initialization(1),test_telemetry_tracking(1),test_context_building(1),test_feedback_policies(1),test_error_handling(1)  # Test the full pipeline with all extensions integrated.
    TestPipelineWithRealFiles: simple_project(1),test_context_reads_toon_files(1),test_context_finds_related_files(1)  # Test pipeline with actual file operations (no Docker).
  tests/test_metrics.py:
    e: TestLLMCall,TestFixResult,TestMetricsCollector,TestMetricsReporter,TestGlobalMetrics
    TestLLMCall: test_call_creation(0),test_call_to_dict(0)
    TestFixResult: test_result_creation(0)
    TestMetricsCollector: test_record_llm_call(0),test_record_fix(0),test_tier_stats(0),test_estimate_cost(0),test_estimate_cost_cached(0),test_get_summary(0),test_save_and_load(0),test_reset(0)
    TestMetricsReporter: test_print_dashboard(1),test_export_csv(0)
    TestGlobalMetrics: test_get_metrics(0),test_reset_metrics(0)
  tests/test_ollama_cache.py:
    e: TestCacheEntry,TestLLMCache,TestCachedOllamaClient
    TestCacheEntry: test_cache_entry_creation(0),test_cache_entry_to_dict(0),test_cache_entry_from_dict(0)
    TestLLMCache: test_cache_creation(0),test_cache_set_and_get(0),test_cache_miss(0),test_cache_hit(0),test_cache_ttl_expiration(0),test_cache_clear(0),test_cache_deduplication_same_prompt(0),test_cache_different_models(0),test_cache_with_parameters(0),test_stats_calculation(0),test_list_entries(0)
    TestCachedOllamaClient: test_client_with_cache(0),test_client_metrics(0),test_client_clear_cache(0),test_client_disabled_cache(0)
  tests/test_parallel.py:
    e: sample_project,test_end_to_end_parallel_flow,TestRegionExtractor,TestTaskPartitioner,TestParallelExecutor
    TestRegionExtractor: test_extract_functions_and_classes(0),test_dependency_detection(0),test_shadow_conflict_detection(0)  # Test AST region extraction.
    TestTaskPartitioner: test_no_conflict_partitioning(0),test_conflict_partitioning(0),test_dependency_conflict(0)  # Test task partitioning logic.
    TestParallelExecutor: test_git_worktree_creation(2),test_line_range_detection(0)  # Test parallel execution orchestration.
    sample_project()
    test_end_to_end_parallel_flow(sample_project)
  tests/test_prefact_integration.py:
    e: TestPrefactIssue,TestPrefactRuleAdapter,TestSharedRuleEngine,TestHelperFunctions
    TestPrefactIssue: test_issue_creation(0),test_issue_to_dict(0)
    TestPrefactRuleAdapter: test_adapter_creation(0),test_is_available_no_prefact(0),test_find_prefact_success(1),test_scan_file_success(1),test_scan_file_failure(1),test_scan_directory(1),test_check_sorted_imports(1),test_check_relative_imports(1),test_get_rules_info(0)
    TestSharedRuleEngine: test_engine_creation(0),test_analyze_without_prefact(0),test_get_all_issues(0)
    TestHelperFunctions: test_run_prefact_check_success(1),test_run_prefact_check_no_prefact(0),test_check_file_with_prefact_unavailable(0),test_check_file_with_prefact_specific_rule(1),test_check_file_with_prefact_all_rules(1)
  tests/test_shared_rules.py:
    e: TestRuleContext,TestRuleViolation,TestSortedImportsRule,TestRelativeImportRule,TestRuleRegistry,TestGlobalRegistry
    TestRuleContext: test_context_creation(0),test_context_with_config(0)
    TestRuleViolation: test_violation_creation(0),test_violation_to_dict(0)
    TestSortedImportsRule: test_rule_properties(0),test_check_sorted_imports(0),test_check_unsorted_stdlib_imports(0),test_check_with_import_from(0),test_fix_with_isort(0),test_fix_without_isort(0)
    TestRelativeImportRule: test_rule_properties(0),test_check_no_relative_imports(0),test_check_relative_imports(0),test_check_absolute_imports_allowed(0)
    TestRuleRegistry: test_registry_creation(0),test_register_and_get(0),test_list_rules(0),test_check_file(0),test_check_file_not_found(0),test_check_file_syntax_error(0)
    TestGlobalRegistry: test_get_registry(0),test_reset_registry(0)
  tests/test_telemetry.py:
    e: TestTraceSpan,TestTelemetry
    TestTraceSpan: test_span_creation(0),test_span_finish(0)  # Test the TraceSpan class.
    TestTelemetry: test_telemetry_creation(0),test_telemetry_custom_run_id(0),test_create_span(0),test_aggregates(0),test_summary(0),test_save(1),test_report(0),test_push_to_langfuse(0),test_push_to_langfuse_optional(0)  # Test the Telemetry class.
  tests/test_workspace.py:
    e: TestWorkspace,TestWorkspaceInit,TestWorkspaceIntegration
    TestWorkspace: temp_workspace(0),test_workspace_loading(1),test_topological_sort(1),test_dependency_validation(1),test_get_execution_plan(1),test_find_repos_by_tag(1),test_status(1),test_dependency_graph(1)  # Test the Workspace class.
    TestWorkspaceInit: test_init_workspace(0),test_repo_config_creation(0)  # Test workspace initialization utilities.
    TestWorkspaceIntegration: mock_workspace(1),test_analyze_all_mock(1),test_plan_all_mock(1)  # Integration tests for workspace operations.
```

## Call Graph

*411 nodes · 500 edges · 120 modules · CC̄=2.5*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `print` *(in Taskfile)* | 0 | 2092 | 0 | **2092** |
| `main` *(in examples.31-abpr-workflow.main)* | 12 ⚠ | 0 | 77 | **77** |
| `main` *(in examples.30-parallel-execution.main)* | 13 ⚠ | 0 | 55 | **55** |
| `main` *(in examples.20-self-hosted-pipeline.main)* | 2 | 0 | 49 | **49** |
| `main` *(in examples.30-parallel-execution.parallel_real_world)* | 13 ⚠ | 0 | 43 | **43** |
| `demo_docker_operations` *(in examples.14-docker-mcp.main)* | 7 | 0 | 40 | **40** |
| `main` *(in examples.05-cost-tracking.main)* | 8 | 0 | 40 | **40** |
| `main` *(in examples.18-ollama-local.main)* | 7 | 0 | 39 | **39** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/algitex
# nodes: 411 | edges: 500 | modules: 120
# CC̄=2.5

HUBS[20]:
  Taskfile.print
    CC=0  in:2092  out:0  total:2092
  examples.31-abpr-workflow.main.main
    CC=12  in:0  out:77  total:77
  examples.30-parallel-execution.main.main
    CC=13  in:0  out:55  total:55
  examples.20-self-hosted-pipeline.main.main
    CC=2  in:0  out:49  total:49
  examples.30-parallel-execution.parallel_real_world.main
    CC=13  in:0  out:43  total:43
  examples.14-docker-mcp.main.demo_docker_operations
    CC=7  in:0  out:40  total:40
  examples.05-cost-tracking.main.main
    CC=8  in:0  out:40  total:40
  examples.18-ollama-local.main.main
    CC=7  in:0  out:39  total:39
  src.algitex.tools.ollama_cache.LLMCache.set
    CC=1  in:32  out:7  total:39
  examples.16-test-workflow.main.demo_test_workflow
    CC=5  in:0  out:37  total:37
  examples.31-abpr-workflow.abpr_pipeline.abpr_pipeline
    CC=10  in:0  out:36  total:36
  examples.13-vallm.main.demo_validation
    CC=5  in:0  out:35  total:35
  src.algitex.tools.autofix.batch_backend.backend.BatchFixBackend.fix_batch
    CC=10  in:0  out:35  total:35
  src.algitex.tools.autofix.batch_backend.BatchFixBackend.fix_batch
    CC=11  in:0  out:35  total:35
  examples.07-context.main.basic_context_example
    CC=2  in:0  out:34  total:34
  src.algitex.tools.tickets.Tickets.list
    CC=4  in:33  out:1  total:34
  examples.02-algo-loop.main.main
    CC=11  in:0  out:33  total:33
  examples.27-unified-autofix.main.main
    CC=4  in:0  out:33  total:33
  src.algitex.todo.hybrid.HybridAutofix.fix_all
    CC=3  in:0  out:31  total:31
  examples.12-filesystem-mcp.main.demo_file_operations
    CC=3  in:0  out:30  total:30

MODULES:
  Taskfile  [1 funcs]
    print  CC=0  out:0
  docker.vallm.vallm_mcp_server  [7 funcs]
    analyze_complexity  CC=9  out:16
    calculate_quality_score  CC=1  out:12
    create_rest_api  CC=1  out:17
    validate_all  CC=1  out:16
    validate_runtime  CC=9  out:9
    validate_security  CC=7  out:12
    validate_static  CC=9  out:15
  examples.01-quickstart.main  [1 funcs]
    main  CC=2  out:21
  examples.02-algo-loop.main  [1 funcs]
    main  CC=11  out:33
  examples.03-pipeline.main  [1 funcs]
    main  CC=6  out:27
  examples.04-ide-integration.main  [1 funcs]
    main  CC=4  out:26
  examples.05-cost-tracking.main  [1 funcs]
    main  CC=8  out:40
  examples.06-telemetry.main  [4 funcs]
    basic_telemetry_example  CC=2  out:30
    budget_tracking_example  CC=3  out:10
    context_manager_example  CC=2  out:11
    multi_model_comparison  CC=2  out:10
  examples.07-context.main  [5 funcs]
    basic_context_example  CC=2  out:34
    cleanup_example_projects  CC=4  out:3
    context_optimization_example  CC=5  out:25
    prompt_engineering_example  CC=1  out:26
    semantic_search_example  CC=1  out:18
  examples.08-feedback.main  [6 funcs]
    basic_feedback_example  CC=1  out:22
    cost_optimization_example  CC=7  out:19
    custom_policy_example  CC=1  out:12
    escalation_scenarios  CC=8  out:16
    feedback_extraction_example  CC=2  out:5
    feedback_loop_simulation  CC=2  out:24
  examples.09-workspace.main  [11 funcs]
    _analyze_impact  CC=3  out:4
    _analyze_parallel_execution  CC=4  out:7
    _analyze_workspace_structure  CC=8  out:10
    _calculate_metrics  CC=3  out:14
    advanced_workspace_features  CC=1  out:7
    cleanup_sample_workspace  CC=2  out:4
    create_sample_workspace  CC=1  out:17
    cross_repo_analysis_example  CC=9  out:16
    cross_repo_planning_example  CC=6  out:19
    workspace_execution_example  CC=8  out:17
  examples.10-cicd.main  [8 funcs]
    basic_github_actions_example  CC=2  out:16
    cleanup_ci_projects  CC=3  out:4
    complete_ci_cd_setup  CC=2  out:29
    dockerfile_example  CC=1  out:14
    gitlab_ci_example  CC=2  out:13
    multi_platform_ci_example  CC=3  out:15
    precommit_hooks_example  CC=1  out:15
    quality_gates_example  CC=2  out:16
  examples.11-aider-mcp.main  [2 funcs]
    create_sample_project  CC=1  out:4
    demo_refactoring  CC=3  out:22
  examples.12-filesystem-mcp.main  [2 funcs]
    create_sample_files  CC=1  out:7
    demo_file_operations  CC=3  out:30
  examples.12-filesystem-mcp.sample_files.src.main  [1 funcs]
    main  CC=1  out:1
  examples.13-vallm.main  [2 funcs]
    create_sample_code  CC=1  out:4
    demo_validation  CC=5  out:35
  examples.14-docker-mcp.main  [2 funcs]
    create_sample_docker_project  CC=1  out:5
    demo_docker_operations  CC=7  out:40
  examples.15-github-mcp.main  [2 funcs]
    create_sample_project  CC=1  out:6
    demo_github_workflow  CC=3  out:30
  examples.16-test-workflow.main  [2 funcs]
    create_sample_project  CC=1  out:8
    demo_test_workflow  CC=5  out:37
  examples.17-docker-workflow.main  [4 funcs]
    check_required_env  CC=3  out:6
    demo_with_docker_tools  CC=4  out:8
    show_cli_usage  CC=1  out:6
    show_workflow  CC=2  out:13
  examples.18-ollama-local.buggy_code  [1 funcs]
    complex_function  CC=6  out:6
  examples.18-ollama-local.main  [7 funcs]
    analyze_code  CC=5  out:5
    demo_code_analysis  CC=5  out:17
    demo_code_generation  CC=3  out:13
    demo_cost_comparison  CC=2  out:7
    generate_code  CC=4  out:3
    list_models  CC=4  out:4
    main  CC=7  out:39
  examples.19-local-mcp-tools.main  [2 funcs]
    check_services  CC=4  out:3
    main  CC=5  out:28
  examples.20-self-hosted-pipeline.buggy_code  [2 funcs]
    authenticate_user  CC=2  out:1
    get_stored_password  CC=1  out:0
  examples.20-self-hosted-pipeline.main  [1 funcs]
    main  CC=2  out:49
  examples.21-aider-cli-ollama.main  [1 funcs]
    main  CC=3  out:22
  examples.22-claude-code-ollama.main  [1 funcs]
    main  CC=4  out:18
  examples.23-continue-dev-ollama.main  [1 funcs]
    main  CC=3  out:23
  examples.24-ollama-batch.file3  [1 funcs]
    process  CC=5  out:1
  examples.24-ollama-batch.main  [1 funcs]
    main  CC=2  out:16
  examples.25-local-model-comparison.main  [1 funcs]
    main  CC=9  out:26
  examples.26-litellm-proxy-ollama.main  [1 funcs]
    main  CC=1  out:14
  examples.27-unified-autofix.main  [1 funcs]
    main  CC=4  out:33
  examples.28-mcp-orchestration.main  [1 funcs]
    main  CC=2  out:22
  examples.28-mcp-orchestration.mcp_orchestrator  [1 funcs]
    main  CC=9  out:21
  examples.30-parallel-execution.main  [1 funcs]
    main  CC=13  out:55
  examples.30-parallel-execution.parallel_multi_tool  [1 funcs]
    main  CC=2  out:4
  examples.30-parallel-execution.parallel_real_world  [2 funcs]
    main  CC=13  out:43
    setup_sample_project  CC=3  out:3
  examples.30-parallel-execution.parallel_refactoring  [1 funcs]
    main  CC=10  out:27
  examples.31-abpr-workflow.abpr_pipeline  [1 funcs]
    abpr_pipeline  CC=10  out:36
  examples.31-abpr-workflow.main  [1 funcs]
    main  CC=12  out:77
  examples.32-workspace-coordination.main  [9 funcs]
    _check_quality_gates  CC=8  out:9
    _group_repos_by_priority  CC=2  out:3
    _print_repo_overview  CC=3  out:9
    _show_analysis_phase  CC=4  out:15
    _show_execution_phase  CC=4  out:13
    _show_execution_summary  CC=3  out:24
    _show_planning_phase  CC=6  out:16
    load_workspace_config  CC=1  out:3
    main  CC=1  out:13
  examples.32-workspace-coordination.workspace_parallel  [1 funcs]
    main  CC=5  out:24
  examples.33-hybrid-autofix.main  [10 funcs]
    _parse_args  CC=1  out:10
    _run_demos  CC=10  out:6
    _validate_env  CC=7  out:20
    demo_benchmark  CC=1  out:5
    demo_dry_run  CC=1  out:8
    demo_full_hybrid  CC=1  out:9
    demo_mechanical_only  CC=1  out:6
    demo_ollama_local  CC=1  out:6
    demo_verify_first  CC=1  out:7
    main  CC=2  out:10
  examples.34-batch-fix.main  [5 funcs]
    demo_batch_dry_run  CC=1  out:5
    demo_batch_execute  CC=1  out:5
    demo_comparison  CC=1  out:4
    demo_custom_batch_size  CC=1  out:5
    main  CC=6  out:22
  examples.35-sprint3-patterns.main  [5 funcs]
    demo_dict_dispatch  CC=2  out:6
    demo_orchestrator_pattern  CC=1  out:12
    demo_pipeline_pattern  CC=2  out:4
    demo_strategy_pattern  CC=2  out:7
    main  CC=1  out:14
  examples.36-dashboard.main  [5 funcs]
    demo_dashboard_export  CC=1  out:6
    demo_dashboard_live  CC=1  out:12
    demo_dashboard_monitor  CC=1  out:10
    demo_dashboard_with_todo  CC=2  out:8
    main  CC=1  out:13
  examples.37-benchmarks.main  [6 funcs]
    demo_benchmark_cache  CC=1  out:12
    demo_benchmark_full  CC=1  out:12
    demo_benchmark_memory  CC=1  out:10
    demo_benchmark_quick  CC=1  out:7
    demo_benchmark_tiers  CC=1  out:10
    main  CC=1  out:14
  examples.38-new-modules.main  [5 funcs]
    demo_classify_module  CC=2  out:13
    demo_combined_workflow  CC=1  out:3
    demo_repair_module  CC=2  out:12
    demo_verify_module  CC=2  out:8
    main  CC=1  out:13
  examples.39-microtask-pipeline.main  [5 funcs]
    demo_microtask_classify  CC=1  out:12
    demo_microtask_plan  CC=1  out:13
    demo_microtask_run  CC=1  out:10
    demo_workflow  CC=1  out:2
    main  CC=1  out:13
  examples.40-three-tier-autofix.main  [6 funcs]
    demo_all_tiers  CC=1  out:13
    demo_dashboard_integration  CC=1  out:10
    demo_tier_algorithm  CC=2  out:9
    demo_tier_big  CC=2  out:9
    demo_tier_micro  CC=2  out:9
    main  CC=1  out:15
  examples.41-god-module-splitting.main  [7 funcs]
    demo_before_and_after  CC=6  out:15
    demo_god_module_problem  CC=1  out:9
    demo_how_to_split_your_module  CC=2  out:6
    demo_import_compatibility  CC=1  out:11
    demo_real_metrics  CC=2  out:10
    demo_split_strategy  CC=1  out:2
    main  CC=1  out:14
  examples.42-duplicate-removal.main  [8 funcs]
    demo_algitex_integration  CC=1  out:9
    demo_detection_with_redup  CC=1  out:9
    demo_duplicate_problem  CC=1  out:11
    demo_extraction_strategy  CC=2  out:9
    demo_metrics_and_roi  CC=2  out:10
    demo_prevention_strategies  CC=1  out:4
    demo_real_world_example  CC=2  out:11
    main  CC=1  out:15
  examples.43-code-health.main  [8 funcs]
    demo_analysis_pipeline  CC=1  out:2
    demo_ci_integration  CC=1  out:5
    demo_health_improvement_workflow  CC=1  out:2
    demo_health_metrics  CC=3  out:5
    demo_health_report  CC=4  out:10
    demo_historical_tracking  CC=2  out:18
    demo_regression_prevention  CC=2  out:5
    main  CC=1  out:15
  examples.44-plugin-system.main  [8 funcs]
    demo_builtin_plugins  CC=2  out:7
    demo_creating_backend_plugin  CC=1  out:11
    demo_creating_tool_plugin  CC=1  out:12
    demo_hook_system  CC=2  out:5
    demo_plugin_architecture  CC=1  out:2
    demo_plugin_configuration  CC=1  out:2
    demo_plugin_marketplace  CC=2  out:17
    main  CC=1  out:15
  project.map.toon  [3 funcs]
    mark_tasks_completed  CC=0  out:0
    parallel_fix  CC=0  out:0
    parse_todo  CC=0  out:0
  src.algitex.benchmark  [4 funcs]
    print_report  CC=5  out:10
    print_table  CC=2  out:9
    bench_algorithmic_fix  CC=2  out:9
    run_quick_benchmark  CC=3  out:19
  src.algitex.cli.benchmark  [2 funcs]
    benchmark_full  CC=3  out:16
    benchmark_quick  CC=1  out:3
  src.algitex.cli.core  [5 funcs]
    _init_config  CC=1  out:3
    _init_project_dir  CC=1  out:4
    _print_tools_status  CC=5  out:14
    init  CC=1  out:8
    tools  CC=5  out:11
  src.algitex.cli.dashboard  [1 funcs]
    dashboard_live  CC=6  out:13
  src.algitex.cli.microtask  [9 funcs]
    _filter_tasks  CC=7  out:0
    _print_file_batches  CC=2  out:14
    _print_plan_table  CC=3  out:12
    _print_summary  CC=3  out:23
    _print_task_table  CC=4  out:12
    _shorten_path  CC=2  out:1
    microtask_classify  CC=2  out:6
    microtask_plan  CC=3  out:11
    microtask_run  CC=2  out:17
  src.algitex.cli.nlp  [7 funcs]
    _print_dead_code  CC=2  out:8
    _print_docstring_changes  CC=2  out:8
    _print_duplicates  CC=4  out:11
    nlp_dead_code  CC=2  out:6
    nlp_docstrings  CC=1  out:6
    nlp_duplicates  CC=2  out:6
    nlp_imports  CC=2  out:15
  src.algitex.cli.parallel  [3 funcs]
    _extract_and_partition  CC=7  out:14
    _load_tickets  CC=2  out:4
    parallel  CC=7  out:23
  src.algitex.cli.todo.logic  [1 funcs]
    validate_task  CC=13  out:8
  src.algitex.cli.todo_verify  [2 funcs]
    _validate_tasks  CC=9  out:12
    todo_verify_prefact  CC=12  out:28
  src.algitex.config  [3 funcs]
    load  CC=2  out:8
    _find_config  CC=5  out:5
    _merge_yaml  CC=10  out:7
  src.algitex.dashboard  [1 funcs]
    show_quick_dashboard  CC=3  out:17
  src.algitex.microtask  [1 funcs]
    group_tasks_by_file  CC=3  out:4
  src.algitex.microtask.classifier  [6 funcs]
    _classify_message  CC=5  out:2
    _first_int  CC=3  out:3
    _is_ignored_path  CC=2  out:3
    _resolve_file  CC=3  out:4
    classify_prefact_line  CC=12  out:21
    classify_todo_file  CC=5  out:9
  src.algitex.microtask.executor  [3 funcs]
    _handle_sort_imports  CC=4  out:5
    _phase_algorithmic  CC=5  out:10
    _phase_llm  CC=5  out:11
  src.algitex.nlp  [10 funcs]
    scan  CC=6  out:10
    fix_path  CC=3  out:6
    __init__  CC=1  out:1
    _ensure_trailing_newline  CC=2  out:1
    _fallback_sort_imports  CC=6  out:16
    _is_ignored  CC=2  out:1
    _python_files  CC=6  out:4
    _sort_imports  CC=3  out:4
    find_duplicate_blocks  CC=14  out:24
    sort_imports_in_path  CC=6  out:8
  src.algitex.project  [1 funcs]
    _check_tools_status  CC=2  out:3
  src.algitex.shared_rules  [5 funcs]
    check  CC=6  out:4
    check_file  CC=6  out:9
    list_rules  CC=4  out:2
    check  CC=12  out:8
    get_registry  CC=2  out:5
  src.algitex.todo  [1 funcs]
    fix_todos  CC=1  out:1
  src.algitex.todo.audit  [1 funcs]
    print_summary  CC=6  out:8
  src.algitex.todo.benchmark  [6 funcs]
    print_report  CC=4  out:18
    _benchmark_single  CC=6  out:11
    benchmark_fix  CC=2  out:3
    benchmark_parallel  CC=5  out:9
    benchmark_sequential  CC=4  out:6
    compare_modes  CC=4  out:15
  src.algitex.todo.classify  [3 funcs]
    _first_int  CC=3  out:3
    classify_message  CC=9  out:7
    classify_task  CC=3  out:4
  src.algitex.todo.hybrid  [6 funcs]
    _call_llm_backend  CC=7  out:6
    _fix_file_llm  CC=8  out:10
    fix_all  CC=3  out:31
    fix_complex  CC=12  out:14
    fix_mechanical  CC=1  out:14
    print_summary  CC=4  out:29
  src.algitex.todo.micro  [8 funcs]
    __init__  CC=1  out:3
    _apply_function_rewrite  CC=3  out:13
    _apply_magic_name  CC=7  out:20
    _fix_magic_name  CC=5  out:15
    fix_file  CC=12  out:14
    fix_task  CC=8  out:22
    fix_tasks  CC=9  out:6
    fix_tasks_detailed  CC=12  out:13
  src.algitex.todo.micro_prompts  [1 funcs]
    _build_user_prompt  CC=9  out:2
  src.algitex.todo.micro_utils  [6 funcs]
    coerce_task  CC=11  out:14
    extract_first_int  CC=3  out:3
    find_import_insert_point  CC=3  out:3
    normalise_model_name  CC=2  out:2
    sanitize_constant_name  CC=3  out:6
    validate_python  CC=2  out:1
  src.algitex.todo.repair  [4 funcs]
    _find_import_insert_point  CC=3  out:3
    _simple_fstring_rewrite  CC=1  out:13
    repair_fstring  CC=12  out:12
    repair_magic_number  CC=8  out:13
  src.algitex.todo.tiering  [3 funcs]
    filter_tasks  CC=6  out:2
    partition_tasks  CC=2  out:3
    summarise_tasks  CC=2  out:3
  src.algitex.todo.verifier  [1 funcs]
    print_report  CC=4  out:11
  src.algitex.todo.verify  [6 funcs]
    _diff_issues  CC=8  out:12
    _parse_todo_file  CC=4  out:9
    _run_prefact_scan  CC=4  out:4
    _validate_task_against_file  CC=10  out:8
    prune_outdated_tasks  CC=4  out:8
    verify_todos  CC=1  out:3
  src.algitex.tools  [2 funcs]
    discover_tools  CC=3  out:5
    require_tool  CC=4  out:2
  src.algitex.tools.analysis  [4 funcs]
    _run_code2llm  CC=4  out:13
    _run_redup  CC=4  out:7
    _run_vallm  CC=4  out:8
    _run_cli  CC=7  out:8
  src.algitex.tools.autofix  [4 funcs]
    fix_all  CC=11  out:14
    fix_issue  CC=6  out:8
    mark_task_done  CC=8  out:9
    print_summary  CC=12  out:16
  src.algitex.tools.autofix.batch_backend  [13 funcs]
    _build_batch_prompt  CC=4  out:9
    _create_backup  CC=5  out:12
    _fix_batch_group  CC=10  out:22
    _fix_individual  CC=5  out:14
    _mark_missing_as_failed  CC=3  out:1
    _parse_batch_response  CC=8  out:22
    _preflight_syntax_check  CC=10  out:23
    _process_group  CC=11  out:22
    _update_todo_mark_completed  CC=9  out:17
    _validate_and_rollback  CC=11  out:22
  src.algitex.tools.autofix.batch_backend.backend  [1 funcs]
    fix_batch  CC=10  out:35
  src.algitex.tools.autofix.batch_backend.fs_utils  [2 funcs]
    create_backup  CC=5  out:12
    preflight_syntax_check  CC=10  out:15
  src.algitex.tools.autofix.batch_backend.todo_utils  [1 funcs]
    update_todo_mark_completed  CC=9  out:17
  src.algitex.tools.autofix.batch_logger  [1 funcs]
    print_summary  CC=1  out:8
  src.algitex.tools.autofix.fallback_backend  [7 funcs]
    __init__  CC=3  out:2
    _get_backend  CC=6  out:6
    _mark_failure  CC=1  out:2
    _mark_success  CC=1  out:2
    _try_backend  CC=4  out:10
    fix  CC=10  out:16
    print_status  CC=4  out:7
  src.algitex.tools.autofix.ollama_backend  [1 funcs]
    fix  CC=6  out:18
  src.algitex.tools.batch  [4 funcs]
    _prepare  CC=5  out:10
    _print_summary  CC=1  out:5
    _save_results  CC=3  out:9
    _setup_progress_bar  CC=5  out:2
  src.algitex.tools.benchmark  [6 funcs]
    get_summary  CC=14  out:17
    _print_detailed  CC=4  out:10
    _print_summary  CC=5  out:22
    _print_table  CC=7  out:18
    compare_models  CC=8  out:16
    save_results  CC=2  out:4
  src.algitex.tools.cicd  [2 funcs]
    create_quality_gate_config  CC=1  out:0
    init_ci_cd  CC=3  out:13
  src.algitex.tools.config  [4 funcs]
    generate_docker_compose  CC=7  out:5
    generate_env_file  CC=7  out:12
    install_config  CC=5  out:12
    setup_project_configs  CC=6  out:12
  src.algitex.tools.context  [1 funcs]
    _find_related  CC=7  out:12
  src.algitex.tools.docker  [3 funcs]
    list_running  CC=1  out:2
    list_tools  CC=1  out:2
    teardown_all  CC=2  out:2
  src.algitex.tools.ide  [2 funcs]
    fix_file  CC=4  out:7
    install_extensions  CC=3  out:4
  src.algitex.tools.ide_aider  [1 funcs]
    fix_file  CC=5  out:9
  src.algitex.tools.ide_base  [2 funcs]
    list_tools  CC=1  out:2
    setup_tool  CC=5  out:8
  src.algitex.tools.ide_claude  [3 funcs]
    batch_fix  CC=3  out:6
    chat  CC=5  out:5
    fix_file  CC=5  out:9
  src.algitex.tools.logging  [9 funcs]
    __enter__  CC=2  out:2
    __exit__  CC=3  out:3
    format_args  CC=3  out:6
    format_result  CC=2  out:2
    format_value  CC=2  out:2
    log_calls  CC=1  out:9
    log_time  CC=1  out:8
    verbose  CC=1  out:12
    verbose_print  CC=2  out:1
  src.algitex.tools.mcp  [9 funcs]
    generate_mcp_config  CC=4  out:6
    list_services  CC=1  out:2
    print_status  CC=6  out:8
    restart_service  CC=1  out:4
    start_all  CC=10  out:9
    start_service  CC=11  out:15
    stop_all  CC=3  out:5
    stop_service  CC=6  out:11
    wait_for_ready  CC=10  out:20
  src.algitex.tools.mcp_lifecycle  [3 funcs]
    restart_service  CC=1  out:4
    start_service  CC=11  out:15
    stop_service  CC=6  out:11
  src.algitex.tools.ollama  [2 funcs]
    auto_fix_file  CC=6  out:5
    ensure_model  CC=3  out:4
  src.algitex.tools.ollama_cache  [2 funcs]
    set  CC=1  out:7
    stats  CC=3  out:5
  src.algitex.tools.parallel.extractor  [2 funcs]
    _detect_shadow_conflicts  CC=12  out:14
    _find_calls  CC=6  out:10
  src.algitex.tools.parallel.partitioner  [2 funcs]
    _build_conflict_graph  CC=5  out:4
    _compute_footprints  CC=10  out:10
  src.algitex.tools.services  [3 funcs]
    _print_status_details  CC=8  out:9
    print_status  CC=6  out:12
    get_startup_order  CC=2  out:6
  src.algitex.tools.telemetry  [1 funcs]
    summary  CC=4  out:5
  src.algitex.tools.tickets  [1 funcs]
    list  CC=4  out:1
  src.algitex.tools.todo_actions  [2 funcs]
    determine_action  CC=2  out:2
    get_action_handler  CC=1  out:1
  src.algitex.tools.todo_parser  [4 funcs]
    _parse_generic  CC=6  out:12
    _parse_github  CC=4  out:10
    _parse_prefact  CC=5  out:12
    parse  CC=11  out:13
  src.algitex.tools.todo_runner  [1 funcs]
    _execute_task  CC=6  out:16
  src.algitex.tools.workspace  [10 funcs]
    _topo_sort  CC=3  out:5
    _validate_dependencies  CC=4  out:4
    analyze_all  CC=5  out:9
    clone_all  CC=3  out:8
    execute_all  CC=3  out:7
    plan_all  CC=4  out:6
    pull_all  CC=3  out:5
    validate_all  CC=3  out:10
    create_workspace_template  CC=1  out:1
    init_workspace  CC=1  out:8
  src.algitex.workflows  [1 funcs]
    finish  CC=1  out:4

EDGES:
  examples.34-batch-fix.main.demo_batch_dry_run → Taskfile.print
  examples.34-batch-fix.main.demo_batch_execute → Taskfile.print
  examples.34-batch-fix.main.demo_custom_batch_size → Taskfile.print
  examples.34-batch-fix.main.demo_comparison → Taskfile.print
  examples.34-batch-fix.main.main → Taskfile.print
  examples.22-claude-code-ollama.main.main → Taskfile.print
  examples.18-ollama-local.buggy_code.complex_function → Taskfile.print
  examples.18-ollama-local.main.list_models → Taskfile.print
  examples.18-ollama-local.main.demo_code_generation → Taskfile.print
  examples.18-ollama-local.main.demo_code_generation → examples.18-ollama-local.main.generate_code
  examples.18-ollama-local.main.demo_code_analysis → Taskfile.print
  examples.18-ollama-local.main.demo_code_analysis → examples.18-ollama-local.main.analyze_code
  examples.18-ollama-local.main.demo_cost_comparison → Taskfile.print
  examples.18-ollama-local.main.main → Taskfile.print
  examples.18-ollama-local.main.main → examples.18-ollama-local.main.list_models
  examples.18-ollama-local.main.main → examples.18-ollama-local.main.demo_code_generation
  examples.18-ollama-local.main.main → examples.18-ollama-local.main.demo_code_analysis
  examples.18-ollama-local.main.main → examples.18-ollama-local.main.demo_cost_comparison
  examples.01-quickstart.main.main → Taskfile.print
  examples.01-quickstart.main.main → src.algitex.tools.discover_tools
  examples.10-cicd.main.basic_github_actions_example → Taskfile.print
  examples.10-cicd.main.gitlab_ci_example → Taskfile.print
  examples.10-cicd.main.quality_gates_example → Taskfile.print
  examples.10-cicd.main.quality_gates_example → src.algitex.tools.cicd.create_quality_gate_config
  examples.10-cicd.main.dockerfile_example → Taskfile.print
  examples.10-cicd.main.precommit_hooks_example → Taskfile.print
  examples.10-cicd.main.complete_ci_cd_setup → Taskfile.print
  examples.10-cicd.main.multi_platform_ci_example → Taskfile.print
  examples.10-cicd.main.cleanup_ci_projects → Taskfile.print
  examples.11-aider-mcp.main.demo_refactoring → Taskfile.print
  examples.11-aider-mcp.main.demo_refactoring → examples.11-aider-mcp.main.create_sample_project
  examples.32-workspace-coordination.workspace_parallel.main → Taskfile.print
  examples.32-workspace-coordination.main.main → Taskfile.print
  examples.32-workspace-coordination.main.main → examples.32-workspace-coordination.main.load_workspace_config
  examples.32-workspace-coordination.main.main → examples.32-workspace-coordination.main._print_repo_overview
  examples.32-workspace-coordination.main.main → examples.32-workspace-coordination.main._show_analysis_phase
  examples.32-workspace-coordination.main.main → examples.32-workspace-coordination.main._check_quality_gates
  examples.32-workspace-coordination.main.main → examples.32-workspace-coordination.main._group_repos_by_priority
  examples.32-workspace-coordination.main._print_repo_overview → Taskfile.print
  examples.32-workspace-coordination.main._show_analysis_phase → Taskfile.print
  examples.32-workspace-coordination.main._show_analysis_phase → examples.32-workspace-coordination.main._group_repos_by_priority
  examples.32-workspace-coordination.main._check_quality_gates → Taskfile.print
  examples.32-workspace-coordination.main._show_planning_phase → Taskfile.print
  examples.32-workspace-coordination.main._show_execution_phase → Taskfile.print
  examples.32-workspace-coordination.main._show_execution_summary → Taskfile.print
  examples.30-parallel-execution.parallel_multi_tool.main → Taskfile.print
  examples.30-parallel-execution.parallel_real_world.main → Taskfile.print
  examples.30-parallel-execution.parallel_real_world.main → examples.30-parallel-execution.parallel_real_world.setup_sample_project
  examples.30-parallel-execution.parallel_refactoring.main → Taskfile.print
  examples.30-parallel-execution.main.main → Taskfile.print
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Api (1)

**`Auto-generated API Smoke Tests`**
- `GET /health` → `200`
- `POST /validate` → `201`
- `POST /batch` → `201`
- assert `status < 400`

### Cli (1)

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**

## Intent

Progressive algorithmization toolchain — from LLM to deterministic code, from proxy to tickets
