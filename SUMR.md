# algitex

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Quality Pipeline (`pyqual.yaml`)](#quality-pipeline-pyqualyaml)
- [Dependencies](#dependencies)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `algitex`
- **version**: `0.1.61`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Taskfile.yml, Makefile, testql(3), app.doql.less, pyqual.yaml, goal.yaml, .env.example, Dockerfile, docker-compose.yml, project/(6 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: algitex;
  version: 0.1.61;
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

## Call Graph

*421 nodes · 500 edges · 121 modules · CC̄=2.6*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `print` *(in Taskfile)* | 0 | 2106 | 0 | **2106** |
| `main` *(in examples.31-abpr-workflow.main)* | 12 ⚠ | 0 | 77 | **77** |
| `main` *(in examples.30-parallel-execution.main)* | 13 ⚠ | 0 | 55 | **55** |
| `main` *(in examples.20-self-hosted-pipeline.main)* | 2 | 0 | 49 | **49** |
| `main` *(in examples.30-parallel-execution.parallel_real_world)* | 13 ⚠ | 0 | 43 | **43** |
| `demo_docker_operations` *(in examples.14-docker-mcp.main)* | 7 | 0 | 40 | **40** |
| `_parse_batch_response` *(in src.algitex.tools.autofix.batch_backend.BatchFixBackend)* | 16 ⚠ | 0 | 40 | **40** |
| `set` *(in src.algitex.tools.ollama_cache.LLMCache)* | 1 | 33 | 7 | **40** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/algitex
# nodes: 421 | edges: 500 | modules: 121
# CC̄=2.6

HUBS[20]:
  Taskfile.print
    CC=0  in:2106  out:0  total:2106
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
  src.algitex.tools.autofix.batch_backend.BatchFixBackend._parse_batch_response
    CC=16  in:0  out:40  total:40
  src.algitex.tools.ollama_cache.LLMCache.set
    CC=1  in:33  out:7  total:40
  examples.05-cost-tracking.main.main
    CC=8  in:0  out:40  total:40
  examples.18-ollama-local.main.main
    CC=7  in:0  out:39  total:39
  examples.16-test-workflow.main.demo_test_workflow
    CC=5  in:0  out:37  total:37
  src.algitex.tools.tickets.Tickets.list
    CC=4  in:36  out:1  total:37
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
  examples.02-algo-loop.main.main
    CC=11  in:0  out:33  total:33
  examples.27-unified-autofix.main.main
    CC=4  in:0  out:33  total:33
  src.algitex.todo.hybrid.HybridAutofix.fix_all
    CC=3  in:0  out:31  total:31

MODULES:
  Taskfile  [1 funcs]
    print  CC=0  out:0
  docker.planfile-mcp.planfile_mcp_server  [3 funcs]
    _load_tickets  CC=6  out:7
    _save_tickets  CC=2  out:8
    planfile_create_ticket  CC=2  out:10
  docker.proxym.proxym_mcp_server  [9 funcs]
    _call_anthropic  CC=6  out:22
    _call_gemini  CC=5  out:14
    _call_openai  CC=3  out:13
    chat_completion  CC=9  out:11
    count_tokens  CC=2  out:4
    create_rest_api  CC=1  out:16
    list_models  CC=4  out:7
    run_rest_server  CC=1  out:7
    simple_prompt  CC=1  out:2
  docker.vallm.vallm_mcp_server  [8 funcs]
    analyze_complexity  CC=9  out:16
    calculate_quality_score  CC=1  out:12
    create_rest_api  CC=1  out:17
    run_rest_server  CC=1  out:7
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
  src.algitex.cli.todo  [7 funcs]
    _render_todo_stats  CC=3  out:18
    _tf_classify_tasks  CC=7  out:3
    _tf_execute_phased  CC=25  out:23
    _tf_parse_and_filter  CC=6  out:2
    todo_benchmark  CC=2  out:9
    todo_fix_parallel  CC=1  out:7
    todo_stats  CC=3  out:6
  src.algitex.cli.todo.logic  [1 funcs]
    validate_task  CC=13  out:8
  src.algitex.cli.todo_verify  [2 funcs]
    _validate_tasks  CC=15  out:12
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
    _classify_message  CC=48  out:2
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
  src.algitex.todo.fixer  [16 funcs]
    _categorize  CC=1  out:1
    _compute_category_stats  CC=2  out:1
    _compute_tier_stats  CC=2  out:2
    _execute_parallel_fixes  CC=8  out:9
    _group_tasks_by_file  CC=2  out:2
    _print_execution_summary  CC=3  out:6
    _print_pre_execution_summary  CC=10  out:22
    _process_exec_batch  CC=6  out:16
    _process_fstring_batch  CC=6  out:16
    _process_magic_batch  CC=11  out:17
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
  src.algitex.todo.repair  [5 funcs]
    _find_import_insert_point  CC=3  out:3
    _simple_fstring_rewrite  CC=1  out:13
    repair_fstring  CC=12  out:12
    repair_magic_number  CC=8  out:13
    repair_module_block  CC=5  out:4
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
  src.algitex.tools.autofix.batch_backend  [11 funcs]
    _build_batch_prompt  CC=4  out:9
    _create_backup  CC=5  out:12
    _fix_batch_group  CC=10  out:22
    _fix_individual  CC=5  out:14
    _parse_batch_response  CC=16  out:40
    _preflight_syntax_check  CC=10  out:23
    _process_group  CC=11  out:22
    _update_todo_mark_completed  CC=9  out:17
    _validate_and_rollback  CC=11  out:22
    _verify_tasks_exist  CC=10  out:14
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
  src.algitex.tools.ide  [7 funcs]
    fix_file  CC=4  out:7
    batch_fix  CC=3  out:6
    chat  CC=5  out:5
    fix_file  CC=5  out:9
    list_tools  CC=1  out:2
    setup_tool  CC=5  out:8
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
  src.algitex.tools.mcp_defaults  [1 funcs]
    build_default_services  CC=1  out:5
  src.algitex.tools.mcp_lifecycle  [3 funcs]
    restart_service  CC=1  out:4
    start_service  CC=11  out:15
    stop_service  CC=6  out:11
  src.algitex.tools.mcp_orchestrator  [3 funcs]
    _register_default_services  CC=1  out:2
    start_all  CC=11  out:11
    stop_all  CC=4  out:4
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

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/algitex
# nodes: 421 | edges: 500 | modules: 121
# CC̄=2.6

HUBS[20]:
  Taskfile.print
    CC=0  in:2106  out:0  total:2106
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
  src.algitex.tools.autofix.batch_backend.BatchFixBackend._parse_batch_response
    CC=16  in:0  out:40  total:40
  src.algitex.tools.ollama_cache.LLMCache.set
    CC=1  in:33  out:7  total:40
  examples.05-cost-tracking.main.main
    CC=8  in:0  out:40  total:40
  examples.18-ollama-local.main.main
    CC=7  in:0  out:39  total:39
  examples.16-test-workflow.main.demo_test_workflow
    CC=5  in:0  out:37  total:37
  src.algitex.tools.tickets.Tickets.list
    CC=4  in:36  out:1  total:37
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
  examples.02-algo-loop.main.main
    CC=11  in:0  out:33  total:33
  examples.27-unified-autofix.main.main
    CC=4  in:0  out:33  total:33
  src.algitex.todo.hybrid.HybridAutofix.fix_all
    CC=3  in:0  out:31  total:31

MODULES:
  Taskfile  [1 funcs]
    print  CC=0  out:0
  docker.planfile-mcp.planfile_mcp_server  [3 funcs]
    _load_tickets  CC=6  out:7
    _save_tickets  CC=2  out:8
    planfile_create_ticket  CC=2  out:10
  docker.proxym.proxym_mcp_server  [9 funcs]
    _call_anthropic  CC=6  out:22
    _call_gemini  CC=5  out:14
    _call_openai  CC=3  out:13
    chat_completion  CC=9  out:11
    count_tokens  CC=2  out:4
    create_rest_api  CC=1  out:16
    list_models  CC=4  out:7
    run_rest_server  CC=1  out:7
    simple_prompt  CC=1  out:2
  docker.vallm.vallm_mcp_server  [8 funcs]
    analyze_complexity  CC=9  out:16
    calculate_quality_score  CC=1  out:12
    create_rest_api  CC=1  out:17
    run_rest_server  CC=1  out:7
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
  src.algitex.cli.todo  [7 funcs]
    _render_todo_stats  CC=3  out:18
    _tf_classify_tasks  CC=7  out:3
    _tf_execute_phased  CC=25  out:23
    _tf_parse_and_filter  CC=6  out:2
    todo_benchmark  CC=2  out:9
    todo_fix_parallel  CC=1  out:7
    todo_stats  CC=3  out:6
  src.algitex.cli.todo.logic  [1 funcs]
    validate_task  CC=13  out:8
  src.algitex.cli.todo_verify  [2 funcs]
    _validate_tasks  CC=15  out:12
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
    _classify_message  CC=48  out:2
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
  src.algitex.todo.fixer  [16 funcs]
    _categorize  CC=1  out:1
    _compute_category_stats  CC=2  out:1
    _compute_tier_stats  CC=2  out:2
    _execute_parallel_fixes  CC=8  out:9
    _group_tasks_by_file  CC=2  out:2
    _print_execution_summary  CC=3  out:6
    _print_pre_execution_summary  CC=10  out:22
    _process_exec_batch  CC=6  out:16
    _process_fstring_batch  CC=6  out:16
    _process_magic_batch  CC=11  out:17
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
  src.algitex.todo.repair  [5 funcs]
    _find_import_insert_point  CC=3  out:3
    _simple_fstring_rewrite  CC=1  out:13
    repair_fstring  CC=12  out:12
    repair_magic_number  CC=8  out:13
    repair_module_block  CC=5  out:4
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
  src.algitex.tools.autofix.batch_backend  [11 funcs]
    _build_batch_prompt  CC=4  out:9
    _create_backup  CC=5  out:12
    _fix_batch_group  CC=10  out:22
    _fix_individual  CC=5  out:14
    _parse_batch_response  CC=16  out:40
    _preflight_syntax_check  CC=10  out:23
    _process_group  CC=11  out:22
    _update_todo_mark_completed  CC=9  out:17
    _validate_and_rollback  CC=11  out:22
    _verify_tasks_exist  CC=10  out:14
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
  src.algitex.tools.ide  [7 funcs]
    fix_file  CC=4  out:7
    batch_fix  CC=3  out:6
    chat  CC=5  out:5
    fix_file  CC=5  out:9
    list_tools  CC=1  out:2
    setup_tool  CC=5  out:8
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
  src.algitex.tools.mcp_defaults  [1 funcs]
    build_default_services  CC=1  out:5
  src.algitex.tools.mcp_lifecycle  [3 funcs]
    restart_service  CC=1  out:4
    start_service  CC=11  out:15
    stop_service  CC=6  out:11
  src.algitex.tools.mcp_orchestrator  [3 funcs]
    _register_default_services  CC=1  out:2
    start_all  CC=11  out:11
    stop_all  CC=4  out:4
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

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 319f 66757L | python:193,shell:27,yaml:20,yml:4,txt:2,toml:1 | 2026-04-25
# CC̄=2.6 | critical:10/1760 | dups:3 | cycles:0

HEALTH[11]:
  🔴 DUP   3 classes duplicated
  🟡 CC    _parse_batch_response CC=16 (limit:15)
  🟡 CC    _validate_tasks CC=15 (limit:15)
  🟡 CC    _run_with_dashboard CC=15 (limit:15)
  🟡 CC    _tf_execute_phased CC=25 (limit:15)
  🟡 CC    todo_hybrid CC=15 (limit:15)
  🟡 CC    todo_verify_prefact CC=29 (limit:15)
  🟡 CC    fix_file CC=25 (limit:15)
  🟡 CC    _classify_message CC=48 (limit:15)
  🟡 CC    _apply_magic_name CC=16 (limit:15)
  🟡 CC    parse_file CC=24 (limit:15)

REFACTOR[2]:
  1. rm duplicates  (-3 dup classes)
  2. split 10 high-CC methods  (CC>15)

PIPELINES[956]:
  [1] Src [main]: main → print
      PURITY: 100% pure
  [2] Src [format_price]: format_price
      PURITY: 100% pure
  [3] Src [process]: process
      PURITY: 100% pure
  [4] Src [load]: load
      PURITY: 100% pure
  [5] Src [add]: add
      PURITY: 100% pure

LAYERS:
  scripts/                        CC̄=8.2    ←in:0  →out:10  !! split
  │ !! generate_lib_docs          276L  0C    7m  CC=24     ←0
  │ fix_readme                  33L  0C    1m  CC=1      ←0
  │
  src/                            CC̄=3.5    ←in:0  →out:0  ×DUP
  │ !! todo                      1159L  0C   21m  CC=29     ←0
  │ !! batch_backend              826L  2C   16m  CC=16     ←0
  │ !! fixer                      550L  1C   17m  CC=25     ←7
  │ !! executor                   497L  2C   29m  CC=16     ←0
  │ hybrid                     479L  4C   10m  CC=12     ←0
  │ benchmark                  464L  4C   19m  CC=14     ←0
  │ mcp                        448L  2C   18m  CC=11     ←0  ×DUP
  │ __init__                   439L  1C   22m  CC=6      ←0
  │ ide                        430L  6C   22m  CC=8      ←0  ×DUP
  │ batch                      421L  4C   20m  CC=7      ←0
  │ __init__                   419L  3C   18m  CC=10     ←0
  │ dashboard                  414L  4C   24m  CC=8      ←1
  │ services                   413L  3C   20m  CC=9      ←0
  │ micro                      406L  1C    9m  CC=12     ←0
  │ cicd                       403L  1C   11m  CC=5      ←1
  │ ollama                     400L  4C   16m  CC=10     ←0
  │ benchmark                  393L  6C   17m  CC=5      ←1
  │ config                     387L  1C   16m  CC=7      ←0
  │ __init__                   367L  5C   12m  CC=9      ←0
  │ todo_runner                353L  1C   12m  CC=13     ←0
  │ workspace                  344L  2C   20m  CC=5      ←1
  │ metrics                    337L  4C   15m  CC=9      ←0
  │ __init__                   331L  5C   19m  CC=14     ←2
  │ __init__                   320L  3C   19m  CC=4      ←0
  │ __init__                   305L  1C   14m  CC=12     ←0
  │ docker                     298L  3C   20m  CC=8      ←0
  │ docker_transport           294L  1C   17m  CC=8      ←1
  │ audit                      286L  3C   13m  CC=10     ←0
  │ todo_local                 283L  2C   11m  CC=11     ←0
  │ prefact_integration        276L  3C   18m  CC=8      ←0
  │ shared_rules               275L  7C   18m  CC=12     ←1
  │ repair                     269L  0C    7m  CC=12     ←1
  │ executor                   260L  1C   11m  CC=6      ←0
  │ feedback                   252L  4C   12m  CC=8      ←0
  │ tickets                    247L  2C   11m  CC=5      ←19
  │ !! classifier                 245L  0C    8m  CC=48     ←1
  │ benchmark                  244L  1C    6m  CC=6      ←2
  │ todo_executor              240L  2C   12m  CC=13     ←0
  │ ollama_cache               238L  3C   14m  CC=12     ←21
  │ batch_logger               235L  3C   17m  CC=10     ←0
  │ __init__                   232L  0C   11m  CC=2      ←0
  │ verify                     228L  1C    7m  CC=10     ←1
  │ todo_parser                223L  2C    8m  CC=11     ←1
  │ context                    207L  3C   14m  CC=7      ←0
  │ todo_actions               200L  0C    7m  CC=13     ←1
  │ microtask                  198L  0C   10m  CC=7      ←0
  │ verifier                   197L  3C    8m  CC=12     ←0
  │ fallback_backend           196L  2C    7m  CC=10     ←0
  │ __init__                   196L  3C    2m  CC=3      ←2
  │ core                       195L  0C   11m  CC=5      ←0
  │ analysis                   183L  3C    8m  CC=7      ←0
  │ metrics                    172L  0C    4m  CC=10     ←0
  │ config                     170L  4C    7m  CC=10     ←9
  │ dashboard                  169L  0C    3m  CC=6      ←0
  │ openrouter_backend         168L  1C   12m  CC=4      ←0
  │ benchmark                  166L  0C    5m  CC=6      ←0
  │ aider_backend              164L  1C   11m  CC=3      ←0
  │ proxy_backend              163L  1C   12m  CC=3      ←0
  │ logging                    157L  1C   11m  CC=3      ←2
  │ extractor                  156L  1C    7m  CC=12     ←0
  │ classify                   156L  1C    3m  CC=9      ←6
  │ tiering                    156L  1C    8m  CC=6      ←0
  │ telemetry                  152L  2C    9m  CC=4      ←0
  │ parallel                   152L  0C    6m  CC=11     ←0
  │ proxy                      145L  2C    9m  CC=9      ←0
  │ __init__                   134L  0C    1m  CC=1      ←2
  │ ollama_backend             126L  1C    7m  CC=6      ←0
  │ prompts                    126L  2C    6m  CC=7      ←0
  │ http_checks                125L  1C    5m  CC=5      ←1
  │ slicer                     121L  1C    7m  CC=13     ←0
  │ partitioner                118L  1C    7m  CC=10     ←0
  │ __init__                   115L  1C    4m  CC=4      ←3
  │ mcp_lifecycle              114L  1C    6m  CC=11     ←0
  │ docker                     104L  0C    5m  CC=3      ←0
  │ ide_base                   103L  1C    6m  CC=5      ←0  ×DUP
  │ backend                    103L  1C    5m  CC=10     ←0
  │ ide_claude                 102L  1C    5m  CC=5      ←0  ×DUP
  │ mcp_orchestrator           100L  1C   11m  CC=11     ←0  ×DUP
  │ nlp                         97L  0C    7m  CC=4      ←0
  │ micro_utils                 90L  0C    7m  CC=11     ←2
  │ !! todo_verify                 76L  0C    2m  CC=15     ←0
  │ micro_prompts               69L  1C    2m  CC=9      ←0
  │ algo                        68L  0C    4m  CC=3      ←0
  │ micro_extractor             65L  1C    1m  CC=11     ←0
  │ ide_aider                   63L  1C    2m  CC=5      ←0
  │ local_checks                63L  1C    3m  CC=4      ←1
  │ batch                       60L  1C    3m  CC=8      ←0
  │ benchmark                   58L  1C    4m  CC=2      ←0
  │ fs_utils                    57L  0C    2m  CC=10     ←1
  │ models                      57L  4C    1m  CC=1      ←0
  │ mcp_defaults                52L  0C    1m  CC=1      ←1
  │ autofix                     52L  1C    5m  CC=8      ←1
  │ ticket                      50L  0C    3m  CC=4      ←0
  │ ide                         47L  1C    6m  CC=1      ←1
  │ logic                       46L  0C    2m  CC=13     ←0
  │ mcp                         46L  1C    8m  CC=2      ←1
  │ checker                     44L  1C    2m  CC=7      ←0
  │ base                        44L  2C    2m  CC=1      ←0
  │ workflow                    42L  0C    2m  CC=3      ←0
  │ ollama                      39L  1C    5m  CC=2      ←0
  │ micro_models                39L  2C    0m  CC=0.0    ←0
  │ __init__                    38L  0C    0m  CC=0.0    ←0
  │ config                      36L  1C    5m  CC=2      ←1
  │ __init__                    36L  0C    0m  CC=0.0    ←0
  │ models                      32L  1C    1m  CC=1      ←0
  │ todo_utils                  31L  0C    1m  CC=9      ←1
  │ render                      30L  0C    1m  CC=3      ←0
  │ services                    28L  1C    4m  CC=2      ←1
  │ mcp_models                  26L  1C    1m  CC=3      ←0
  │ ide_models                  20L  1C    1m  CC=2      ←0
  │ models                      13L  1C    0m  CC=0.0    ←0
  │ file_ops                    11L  0C    2m  CC=2      ←0
  │ pipeline                     5L  0C    0m  CC=0.0    ←0
  │ loop                         4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ workflow                     2L  0C    0m  CC=0.0    ←0
  │
  docker/                         CC̄=3.4    ←in:0  →out:0
  │ proxym_mcp_server          387L  0C   10m  CC=9      ←0
  │ vallm_mcp_server           361L  0C    8m  CC=9      ←0
  │ code2llm_mcp_server        323L  0C    9m  CC=10     ←0
  │ code2llm_server            283L  1C    9m  CC=10     ←0
  │ planfile_mcp_server        276L  0C   10m  CC=7      ←0
  │ vallm_server               274L  1C    9m  CC=9      ←0
  │ proxym_server              256L  1C    7m  CC=6      ←0
  │ docker-compose.yml         182L  0C    0m  CC=0.0    ←0
  │ aider_mcp_server           156L  0C    5m  CC=2      ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=2.7    ←in:0  →out:0
  │ main                       438L  0C    6m  CC=8      ←0
  │ main                       411L  0C    8m  CC=3      ←0
  │ main                       404L  0C   11m  CC=9      ←0
  │ main                       397L  0C    5m  CC=5      ←0
  │ main                       334L  2C   10m  CC=2      ←0
  │ main                       301L  0C    8m  CC=4      ←0
  │ main                       274L  0C    8m  CC=2      ←0
  │ main                       241L  0C    8m  CC=7      ←0
  │ main                       240L  0C    5m  CC=6      ←0
  │ main                       224L  0C   10m  CC=10     ←0
  │ main                       219L  0C    7m  CC=6      ←0
  │ main                       206L  0C    4m  CC=3      ←0
  │ parallel_real_world        201L  0C    2m  CC=13     ←0
  │ main                       195L  0C    9m  CC=8      ←0
  │ main                       192L  0C    3m  CC=5      ←0
  │ main                       164L  0C    3m  CC=5      ←0
  │ planfile.yaml              162L  0C    0m  CC=0.0    ←0
  │ main                       159L  0C    8m  CC=7      ←0
  │ main                       158L  0C    3m  CC=7      ←0
  │ main                       146L  0C    1m  CC=12     ←0
  │ main                       141L  0C    1m  CC=13     ←0
  │ main                       140L  0C    5m  CC=2      ←0
  │ main                       140L  0C    2m  CC=3      ←0
  │ main                       138L  0C    5m  CC=2      ←0
  │ parallel_refactoring       134L  0C    1m  CC=10     ←0
  │ main                       133L  0C    6m  CC=2      ←0
  │ buggy_code                 129L  1C   12m  CC=3      ←0
  │ main                       125L  0C    5m  CC=7      ←0
  │ main                       114L  0C    2m  CC=3      ←0
  │ main                       112L  0C    5m  CC=2      ←0
  │ main                       108L  0C    6m  CC=1      ←0
  │ buggy_code                 108L  1C   10m  CC=7      ←0
  │ main                       104L  0C    2m  CC=3      ←0
  │ main                       103L  0C    5m  CC=1      ←0
  │ main                       100L  0C    1m  CC=11     ←0
  │ main                       100L  0C    1m  CC=8      ←0
  │ workspace.yaml              93L  0C    0m  CC=0.0    ←0
  │ main                        88L  0C    1m  CC=2      ←0
  │ abpr_pipeline               88L  0C    1m  CC=10     ←0
  │ buggy_code                  82L  1C    8m  CC=3      ←0
  │ prefact.yaml                82L  0C    0m  CC=0.0    ←0
  │ workspace_parallel          78L  0C    1m  CC=5      ←0
  │ buggy_code                  76L  0C    7m  CC=6      ←0
  │ main                        76L  0C    2m  CC=5      ←0
  │ main                        69L  0C    1m  CC=4      ←0
  │ parallel_multi_tool         67L  0C    1m  CC=2      ←0
  │ main                        66L  0C    1m  CC=9      ←0
  │ mcp_orchestrator            63L  0C    1m  CC=9      ←0
  │ main                        62L  0C    1m  CC=6      ←0
  │ run.sh                      61L  0C    0m  CC=0.0    ←0
  │ buggy_code                  56L  1C    6m  CC=6      ←0
  │ main                        53L  0C    1m  CC=2      ←0
  │ buggy_code                  53L  1C    6m  CC=6      ←0
  │ main                        53L  0C    1m  CC=3      ←0
  │ buggy_code                  51L  1C    6m  CC=6      ←0
  │ main                        50L  0C    1m  CC=3      ←0
  │ main                        47L  0C    1m  CC=2      ←0
  │ main                        46L  0C    1m  CC=4      ←0
  │ main                        43L  0C    1m  CC=2      ←0
  │ main                        38L  0C    1m  CC=1      ←0
  │ run.sh                      36L  0C    0m  CC=0.0    ←0
  │ file1                       31L  0C    3m  CC=6      ←0
  │ complex_module              28L  0C    2m  CC=8      ←0
  │ run.sh                      28L  0C    0m  CC=0.0    ←0
  │ run.sh                      28L  0C    0m  CC=0.0    ←0
  │ file3                       26L  1C    3m  CC=5      ←0
  │ run.sh                      25L  0C    0m  CC=0.0    ←0
  │ file2                       24L  0C    3m  CC=2      ←0
  │ file2                       22L  0C    3m  CC=1      ←0
  │ file1                       19L  0C    3m  CC=1      ←0
  │ calculator                  18L  0C    4m  CC=2      ←0
  │ calculator                  14L  0C    1m  CC=6      ←0
  │ app                         14L  1C    1m  CC=1      ←0
  │ file3                       12L  0C    1m  CC=1      ←0
  │ main                         9L  0C    1m  CC=1      ←0
  │ run.sh                       9L  0C    0m  CC=0.0    ←0
  │ run.sh                       9L  0C    0m  CC=0.0    ←0
  │ run.sh                       9L  0C    0m  CC=0.0    ←0
  │ run.sh                       9L  0C    0m  CC=0.0    ←0
  │ main                         6L  0C    1m  CC=1      ←0
  │ run.sh                       6L  0C    0m  CC=0.0    ←0
  │ run.sh                       6L  0C    0m  CC=0.0    ←0
  │ run.sh                       6L  0C    0m  CC=0.0    ←0
  │ run.sh                       6L  0C    0m  CC=0.0    ←0
  │ run.sh                       6L  0C    0m  CC=0.0    ←0
  │ run.sh                       6L  0C    0m  CC=0.0    ←0
  │ run.sh                       6L  0C    0m  CC=0.0    ←0
  │ run.sh                       5L  0C    0m  CC=0.0    ←0
  │ run.sh                       5L  0C    0m  CC=0.0    ←0
  │ run.sh                       5L  0C    0m  CC=0.0    ←0
  │ run.sh                       5L  0C    0m  CC=0.0    ←0
  │ run.sh                       5L  0C    0m  CC=0.0    ←0
  │ run.sh                       5L  0C    0m  CC=0.0    ←0
  │ run.sh                       5L  0C    0m  CC=0.0    ←0
  │ run.sh                       5L  0C    0m  CC=0.0    ←0
  │ run.sh                       5L  0C    0m  CC=0.0    ←0
  │ run.sh                       3L  0C    0m  CC=0.0    ←0
  │ requirements.txt             2L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! planfile.yaml            20325L  0C    0m  CC=0.0    ←0
  │ !! goal.yaml                  513L  0C    0m  CC=0.0    ←0
  │ docker-tools.yaml          489L  0C    0m  CC=0.0    ←0
  │ Taskfile.yml               274L  0C    1m  CC=0.0    ←86
  │ docker-compose.yml         192L  0C    0m  CC=0.0    ←0
  │ docker-compose.mcp.yml     156L  0C    0m  CC=0.0    ←0
  │ prefact.yaml                82L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              77L  0C    0m  CC=0.0    ←0
  │ project.sh                  47L  0C    0m  CC=0.0    ←0
  │ pyqual.yaml                 18L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │
  project/                        CC̄=0.0    ←in:0  →out:0
  │ !! calls.yaml                6492L  0C    0m  CC=0.0    ←0
  │ !! map.toon.yaml             1389L  0C  424m  CC=0.0    ←0
  │ !! calls.toon.yaml            633L  0C    0m  CC=0.0    ←0
  │ analysis.toon.yaml         491L  0C    0m  CC=0.0    ←0
  │ duplication.toon.yaml      387L  0C    0m  CC=0.0    ←0
  │ validation.toon.yaml       126L  0C    0m  CC=0.0    ←0
  │ analysis_refactored.toon.yaml   121L  0C    0m  CC=0.0    ←0
  │ evolution.toon.yaml         82L  0C    0m  CC=0.0    ←0
  │ project.toon.yaml           56L  0C    0m  CC=0.0    ←0
  │ prompt.txt                  47L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-api-smoke.testql.toon.yaml    32L  0C    0m  CC=0.0    ←0
  │ generated-from-pytests.testql.toon.yaml    22L  0C    0m  CC=0.0    ←0
  │ generated-cli-tests.testql.toon.yaml    12L  0C    0m  CC=0.0    ←0
  │
  ── zero ──
     Dockerfile                                0L
     Makefile                                  0L
     docker/aider-mcp/Dockerfile               0L
     docker/code2llm/Dockerfile                0L
     docker/mcp/audio/Dockerfile               0L
     docker/mcp/brave-search/Dockerfile        0L
     docker/mcp/browser/Dockerfile             0L
     docker/mcp/docker-ai/Dockerfile           0L
     docker/mcp/duckduckgo/Dockerfile          0L
     docker/mcp/fetch/Dockerfile               0L
     docker/mcp/filesystem/Dockerfile          0L
     docker/mcp/git/Dockerfile                 0L
     docker/mcp/github/Dockerfile              0L
     docker/mcp/image/Dockerfile               0L
     docker/mcp/jira/Dockerfile                0L
     docker/mcp/kubernetes/Dockerfile          0L
     docker/mcp/mail/Dockerfile                0L
     docker/mcp/mysql/Dockerfile               0L
     docker/mcp/pdf/Dockerfile                 0L
     docker/mcp/playwright/Dockerfile          0L
     docker/mcp/postgres/Dockerfile            0L
     docker/mcp/redis/Dockerfile               0L
     docker/mcp/security-lint/Dockerfile       0L
     docker/mcp/slack/Dockerfile               0L
     docker/mcp/sqlite/Dockerfile              0L
     docker/mcp/time/Dockerfile                0L
     docker/mcp/video/Dockerfile               0L
     docker/mcp/wikipedia/Dockerfile           0L
     docker/planfile-mcp/Dockerfile            0L
     docker/proxym/Dockerfile                  0L
     docker/vallm/Dockerfile                   0L
     examples/01-quickstart/Makefile           0L
     examples/02-algo-loop/Makefile            0L
     examples/03-pipeline/Makefile             0L
     examples/04-ide-integration/Makefile      0L
     examples/05-cost-tracking/Makefile        0L
     examples/06-telemetry/Makefile            0L
     examples/07-context/Makefile              0L
     examples/08-feedback/Makefile             0L
     examples/09-workspace/Makefile            0L
     examples/10-cicd/Makefile                 0L
     examples/11-aider-mcp/Makefile            0L
     examples/14-docker-mcp/Makefile           0L
     examples/14-docker-mcp/sample_docker_project/Dockerfile  0L
     examples/15-github-mcp/Makefile           0L
     examples/16-test-workflow/Makefile        0L
     examples/18-ollama-local/Makefile         0L
     examples/19-local-mcp-tools/Makefile      0L
     examples/20-self-hosted-pipeline/Makefile  0L
     examples/21-aider-cli-ollama/Makefile     0L
     examples/22-claude-code-ollama/Makefile   0L
     examples/23-continue-dev-ollama/Makefile  0L
     examples/24-ollama-batch/Makefile         0L
     examples/25-local-model-comparison/Makefile  0L
     examples/26-litellm-proxy-ollama/Makefile  0L
     examples/28-mcp-orchestration/Makefile    0L
     examples/30-parallel-execution/Makefile   0L
     examples/31-abpr-workflow/Makefile        0L
     examples/32-workspace-coordination/Makefile  0L
     examples/33-hybrid-autofix/Makefile       0L
     examples/35-sprint3-patterns/Makefile     0L
     examples/36-dashboard/Makefile            0L
     examples/37-benchmarks/Makefile           0L
     examples/38-new-modules/Makefile          0L
     examples/39-microtask-pipeline/Makefile   0L
     examples/40-three-tier-autofix/Makefile   0L
     examples/41-god-module-splitting/Makefile  0L
     examples/42-duplicate-removal/Makefile    0L
     examples/43-code-health/Makefile          0L
     examples/44-plugin-system/Makefile        0L

COUPLING:
                                                                Taskfile                         src.algitex           examples.31-abpr-workflow               examples.09-workspace  examples.32-workspace-coordination       examples.42-duplicate-removal                    examples.10-cicd           examples.44-plugin-system            examples.18-ollama-local              examples.37-benchmarks      examples.40-three-tier-autofix      examples.30-parallel-execution                examples.08-feedback                 examples.07-context    examples.41-god-module-splitting
                            Taskfile                                  ──                                ←516                                 ←81                                 ←71                                 ←68                                 ←68                                 ←65                                 ←64                                 ←61                                 ←60                                 ←60                                 ←56                                 ←57                                 ←53                                 ←53  hub
                         src.algitex                                 516                                  ──                                                                      ←2                                                                                                          ←1                                                                                                                                                                                  ←3                                                                                                              hub
           examples.31-abpr-workflow                                  81                                                                      ──                                                                                                                                                                                                                                                                                                                                                                                                                                                  !! fan-out
               examples.09-workspace                                  71                                   2                                                                      ──                                                                                                                                                                                                                                                                                                                                                                                                              !! fan-out
  examples.32-workspace-coordination                                  68                                                                                                                                              ──                                                                                                                                                                                                                                                                                                                                                                          !! fan-out
       examples.42-duplicate-removal                                  68                                                                                                                                                                                  ──                                                                                                                                                                                                                                                                                                                                      !! fan-out
                    examples.10-cicd                                  65                                   1                                                                                                                                                                                  ──                                                                                                                                                                                                                                                                                                  !! fan-out
           examples.44-plugin-system                                  64                                                                                                                                                                                                                                                          ──                                                                                                                                                                                                                                                              !! fan-out
            examples.18-ollama-local                                  61                                                                                                                                                                                                                                                                                              ──                                                                                                                                                                                                                          !! fan-out
              examples.37-benchmarks                                  60                                                                                                                                                                                                                                                                                                                                  ──                                                                                                                                                                                      !! fan-out
      examples.40-three-tier-autofix                                  60                                                                                                                                                                                                                                                                                                                                                                      ──                                                                                                                                                  !! fan-out
      examples.30-parallel-execution                                  56                                   3                                                                                                                                                                                                                                                                                                                                                                      ──                                                                                                              !! fan-out
                examples.08-feedback                                  57                                                                                                                                                                                                                                                                                                                                                                                                                                              ──                                                                          !! fan-out
                 examples.07-context                                  53                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  ──                                      !! fan-out
    examples.41-god-module-splitting                                  53                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      ──  !! fan-out
  CYCLES: none
  HUB: Taskfile/ (fan-in=2106)
  HUB: src.algitex/ (fan-in=20)
  SMELL: examples.01-quickstart/ fan-out=15 → split needed
  SMELL: examples.04-ide-integration/ fan-out=17 → split needed
  SMELL: examples.35-sprint3-patterns/ fan-out=36 → split needed
  SMELL: examples.06-telemetry/ fan-out=31 → split needed
  SMELL: examples.22-claude-code-ollama/ fan-out=12 → split needed
  SMELL: examples.08-feedback/ fan-out=57 → split needed
  SMELL: examples.12-filesystem-mcp/ fan-out=22 → split needed
  SMELL: examples.42-duplicate-removal/ fan-out=68 → split needed
  SMELL: examples.21-aider-cli-ollama/ fan-out=17 → split needed
  SMELL: examples.27-unified-autofix/ fan-out=21 → split needed
  SMELL: examples.43-code-health/ fan-out=51 → split needed
  SMELL: examples.16-test-workflow/ fan-out=28 → split needed
  SMELL: examples.30-parallel-execution/ fan-out=59 → split needed
  SMELL: examples.11-aider-mcp/ fan-out=17 → split needed
  SMELL: examples.19-local-mcp-tools/ fan-out=22 → split needed
  SMELL: examples.25-local-model-comparison/ fan-out=16 → split needed
  SMELL: examples.37-benchmarks/ fan-out=60 → split needed
  SMELL: examples.02-algo-loop/ fan-out=22 → split needed
  SMELL: examples.33-hybrid-autofix/ fan-out=48 → split needed
  SMELL: examples.40-three-tier-autofix/ fan-out=60 → split needed
  SMELL: examples.41-god-module-splitting/ fan-out=53 → split needed
  SMELL: examples.31-abpr-workflow/ fan-out=81 → split needed
  SMELL: examples.44-plugin-system/ fan-out=64 → split needed
  SMELL: examples.13-vallm/ fan-out=23 → split needed
  SMELL: examples.05-cost-tracking/ fan-out=14 → split needed
  SMELL: examples.14-docker-mcp/ fan-out=27 → split needed
  SMELL: examples.36-dashboard/ fan-out=45 → split needed
  SMELL: examples.23-continue-dev-ollama/ fan-out=18 → split needed
  SMELL: examples.38-new-modules/ fan-out=37 → split needed
  SMELL: examples.39-microtask-pipeline/ fan-out=46 → split needed
  SMELL: examples.18-ollama-local/ fan-out=61 → split needed
  SMELL: examples.03-pipeline/ fan-out=10 → split needed
  SMELL: examples.17-docker-workflow/ fan-out=28 → split needed
  SMELL: scripts/ fan-out=10 → split needed
  SMELL: examples.07-context/ fan-out=53 → split needed
  SMELL: examples.34-batch-fix/ fan-out=30 → split needed
  SMELL: examples.10-cicd/ fan-out=66 → split needed
  SMELL: examples.09-workspace/ fan-out=73 → split needed
  SMELL: examples.20-self-hosted-pipeline/ fan-out=45 → split needed
  SMELL: src.algitex/ fan-out=516 → split needed
  SMELL: examples.26-litellm-proxy-ollama/ fan-out=11 → split needed
  SMELL: examples.32-workspace-coordination/ fan-out=68 → split needed
  SMELL: examples.24-ollama-batch/ fan-out=13 → split needed
  SMELL: examples.15-github-mcp/ fan-out=24 → split needed
  SMELL: examples.28-mcp-orchestration/ fan-out=26 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 53 groups | 197f 33774L | 2026-04-25

SUMMARY:
  files_scanned: 197
  total_lines:   33774
  dup_groups:    53
  dup_fragments: 136
  saved_lines:   963
  scan_ms:       4969

HOTSPOTS[7] (files with most duplication):
  examples/34-batch-fix/main.py  dup=131L  groups=1  frags=3  (0.4%)
  examples/44-plugin-system/main.py  dup=89L  groups=2  frags=3  (0.3%)
  src/algitex/tools/autofix/openrouter_backend.py  dup=87L  groups=9  frags=9  (0.3%)
  src/algitex/tools/autofix/proxy_backend.py  dup=87L  groups=9  frags=9  (0.3%)
  examples/43-code-health/main.py  dup=80L  groups=2  frags=3  (0.2%)
  src/algitex/tools/ide.py  dup=77L  groups=7  frags=9  (0.2%)
  examples/42-duplicate-removal/main.py  dup=71L  groups=2  frags=3  (0.2%)

DUPLICATES[53] (ranked by impact):
  [ca1e6dbe10b6ef80] !! STRU  demo_split_strategy  L=27 N=5 saved=108 sim=1.00
      examples/41-god-module-splitting/main.py:62-88  (demo_split_strategy)
      examples/43-code-health/main.py:46-74  (demo_analysis_pipeline)
      examples/43-code-health/main.py:245-276  (demo_health_improvement_workflow)
      examples/44-plugin-system/main.py:35-60  (demo_plugin_architecture)
      examples/44-plugin-system/main.py:231-274  (demo_plugin_configuration)
  [d05413b8b4b40ceb] ! STRU  demo_batch_dry_run  L=44 N=3 saved=88 sim=1.00
      examples/34-batch-fix/main.py:15-58  (demo_batch_dry_run)
      examples/34-batch-fix/main.py:61-120  (demo_batch_execute)
      examples/34-batch-fix/main.py:123-149  (demo_custom_batch_size)
  [c40ca68f0d44e67c] ! STRU  demo_orchestrator_pattern  L=21 N=5 saved=84 sim=1.00
      examples/35-sprint3-patterns/main.py:94-114  (demo_orchestrator_pattern)
      examples/36-dashboard/main.py:13-28  (demo_dashboard_live)
      examples/37-benchmarks/main.py:23-37  (demo_benchmark_cache)
      examples/37-benchmarks/main.py:70-84  (demo_benchmark_full)
      examples/39-microtask-pipeline/main.py:11-25  (demo_microtask_classify)
  [6b3d1cfc8b2cc23c] ! STRU  demo_dashboard_monitor  L=13 N=5 saved=52 sim=1.00
      examples/36-dashboard/main.py:31-43  (demo_dashboard_monitor)
      examples/37-benchmarks/main.py:40-52  (demo_benchmark_tiers)
      examples/37-benchmarks/main.py:55-67  (demo_benchmark_memory)
      examples/39-microtask-pipeline/main.py:46-58  (demo_microtask_run)
      examples/40-three-tier-autofix/main.py:96-108  (demo_dashboard_integration)
  [710a27b3c2b3101b] ! STRU  main  L=19 N=3 saved=38 sim=1.00
      examples/42-duplicate-removal/main.py:252-270  (main)
      examples/43-code-health/main.py:279-297  (main)
      examples/44-plugin-system/main.py:312-330  (main)
  [709c400dfaedb8df] ! EXAC  stop_service  L=36 N=2 saved=36 sim=1.00
      src/algitex/tools/mcp.py:179-214  (stop_service)
      src/algitex/tools/mcp_lifecycle.py:79-108  (stop_service)
  [58296bc54788ae2d] ! EXAC  _register_default_tools  L=34 N=2 saved=34 sim=1.00
      src/algitex/tools/ide.py:42-75  (_register_default_tools)
      src/algitex/tools/ide_base.py:19-52  (_register_default_tools)
  [c259276e9eedc2a3] ! STRU  main  L=17 N=3 saved=34 sim=1.00
      examples/36-dashboard/main.py:92-108  (main)
      examples/38-new-modules/main.py:120-136  (main)
      examples/39-microtask-pipeline/main.py:83-99  (main)
  [edc3dcd4ecca81f3] ! STRU  run_rest_server  L=8 N=5 saved=32 sim=1.00
      docker/aider-mcp/aider_mcp_server.py:135-142  (run_rest_server)
      docker/code2llm/code2llm_mcp_server.py:300-307  (run_rest_server)
      docker/planfile-mcp/planfile_mcp_server.py:255-262  (run_rest_server)
      docker/proxym/proxym_mcp_server.py:366-373  (run_rest_server)
      docker/vallm/vallm_mcp_server.py:340-347  (run_rest_server)
  [7cf3ece087e18f18] ! STRU  create_sample_project  L=32 N=2 saved=32 sim=1.00
      examples/11-aider-mcp/main.py:13-44  (create_sample_project)
      examples/13-vallm/main.py:13-59  (create_sample_code)
  [aaae754bdb04529d]   STRU  ticket  L=3 N=10 saved=27 sim=1.00
      src/algitex/cli/__init__.py:72-74  (ticket)
      src/algitex/cli/__init__.py:78-80  (algo)
      src/algitex/cli/__init__.py:84-86  (workflow)
      src/algitex/cli/__init__.py:90-92  (docker)
      src/algitex/cli/__init__.py:96-98  (todo)
      src/algitex/cli/__init__.py:102-104  (microtask)
      src/algitex/cli/__init__.py:108-110  (nlp)
      src/algitex/cli/__init__.py:114-116  (metrics)
      src/algitex/cli/__init__.py:120-122  (benchmark)
      src/algitex/cli/__init__.py:126-128  (dashboard)
  [2f3dff302f70b194]   STRU  _process_fstring_batch  L=26 N=2 saved=26 sim=1.00
      src/algitex/todo/fixer.py:361-386  (_process_fstring_batch)
      src/algitex/todo/fixer.py:389-414  (_process_exec_batch)
  [6d2cf7e32322cdcc]   EXAC  setup_tool  L=22 N=2 saved=22 sim=1.00
      src/algitex/tools/ide.py:93-114  (setup_tool)
      src/algitex/tools/ide_base.py:66-85  (setup_tool)
  [5107e45da0c04760]   STRU  demo_detection_with_redup  L=22 N=2 saved=22 sim=1.00
      examples/42-duplicate-removal/main.py:63-84  (demo_detection_with_redup)
      examples/42-duplicate-removal/main.py:134-163  (demo_algitex_integration)
  [596ac93ad0a535f0]   STRU  _dry_run_result  L=11 N=3 saved=22 sim=1.00
      src/algitex/tools/autofix/aider_backend.py:130-140  (_dry_run_result)
      src/algitex/tools/autofix/openrouter_backend.py:146-156  (_dry_run_result)
      src/algitex/tools/autofix/proxy_backend.py:141-151  (_dry_run_result)
  [768cd0bf16ab6b80]   STRU  _error_result  L=11 N=3 saved=22 sim=1.00
      src/algitex/tools/autofix/aider_backend.py:154-164  (_error_result)
      src/algitex/tools/autofix/openrouter_backend.py:158-168  (_error_result)
      src/algitex/tools/autofix/proxy_backend.py:153-163  (_error_result)
  [6979784d0ad924df]   STRU  demo_tier_micro  L=20 N=2 saved=20 sim=1.00
      examples/40-three-tier-autofix/main.py:33-52  (demo_tier_micro)
      examples/40-three-tier-autofix/main.py:55-74  (demo_tier_big)
  [5ee9cc973b6804a8]   STRU  _first_int  L=9 N=3 saved=18 sim=1.00
      src/algitex/todo/classify.py:110-118  (_first_int)
      src/algitex/todo/micro_utils.py:29-37  (extract_first_int)
      src/algitex/todo/tiering.py:103-111  (_first_int)
  [839cd36428c7aebb]   EXAC  _execute_fix  L=17 N=2 saved=17 sim=1.00
      src/algitex/tools/autofix/openrouter_backend.py:57-73  (_execute_fix)
      src/algitex/tools/autofix/proxy_backend.py:54-70  (_execute_fix)
  [44d93aac5aa7e69e]   STRU  demo_microtask_plan  L=16 N=2 saved=16 sim=1.00
      examples/39-microtask-pipeline/main.py:28-43  (demo_microtask_plan)
      examples/40-three-tier-autofix/main.py:77-93  (demo_all_tiers)
  [5da66828a1eaa088]   EXAC  _build_prompt  L=14 N=2 saved=14 sim=1.00
      src/algitex/tools/autofix/openrouter_backend.py:79-92  (_build_prompt)
      src/algitex/tools/autofix/proxy_backend.py:76-89  (_build_prompt)
  [0ae0f4af213387dc]   STRU  run  L=7 N=3 saved=14 sim=1.00
      docker/code2llm/code2llm_server.py:271-277  (run)
      docker/proxym/proxym_server.py:244-250  (run)
      docker/vallm/vallm_server.py:262-268  (run)
  [96909fae1e52693c]   EXAC  calculate  L=13 N=2 saved=13 sim=1.00
      examples/23-continue-dev-ollama/buggy_code.py:6-18  (calculate)
      examples/26-litellm-proxy-ollama/buggy_code.py:6-18  (calculate)
  [acbc59834cf5586d]   EXAC  fix  L=12 N=2 saved=12 sim=1.00
      src/algitex/tools/autofix/openrouter_backend.py:31-42  (fix)
      src/algitex/tools/autofix/proxy_backend.py:31-42  (fix)
  [bd0cd68e3dfa5861]   STRU  __init__  L=3 N=5 saved=12 sim=1.00
      src/algitex/tools/ide.py:138-140  (__init__)
      src/algitex/tools/ide.py:257-259  (__init__)
      src/algitex/tools/ide.py:310-312  (__init__)
      src/algitex/tools/ide_aider.py:15-17  (__init__)
      src/algitex/tools/ide_claude.py:15-17  (__init__)
  [9436f369f5266c7f]   EXAC  load_env  L=11 N=2 saved=11 sim=1.00
      examples/04-ide-integration/main.py:21-31  (load_env)
      examples/17-docker-workflow/main.py:18-28  (load_env)
  [94d80d6507ff413f]   EXAC  _ensure_model  L=10 N=2 saved=10 sim=1.00
      src/algitex/tools/autofix/batch_backend.py:817-826  (_ensure_model)
      src/algitex/tools/autofix/ollama_backend.py:85-94  (_ensure_model)
  [7bcbd20526a649ee]   STRU  _success_result  L=10 N=2 saved=10 sim=1.00
      src/algitex/tools/autofix/openrouter_backend.py:135-144  (_success_result)
      src/algitex/tools/autofix/proxy_backend.py:130-139  (_success_result)
  [966057c00b7a6275]   EXAC  process_items  L=8 N=2 saved=8 sim=1.00
      examples/23-continue-dev-ollama/buggy_code.py:21-28  (process_items)
      examples/26-litellm-proxy-ollama/buggy_code.py:21-28  (process_items)
  [bff6f36aacdabe6a]   EXAC  _resolve_path  L=8 N=2 saved=8 sim=1.00
      src/algitex/microtask/executor.py:444-451  (_resolve_path)
      src/algitex/microtask/slicer.py:46-53  (_resolve_path)
  [c2153e9cc4c6eb5f]   EXAC  _setup_signal_handlers  L=8 N=2 saved=8 sim=1.00
      src/algitex/tools/mcp.py:53-60  (_setup_signal_handlers)
      src/algitex/tools/mcp_orchestrator.py:24-32  (_setup_signal_handlers)
  [95f62e1f9fe66e00]   STRU  show_cli_usage  L=8 N=2 saved=8 sim=1.00
      examples/17-docker-workflow/main.py:101-108  (show_cli_usage)
      examples/36-dashboard/main.py:46-68  (demo_dashboard_export)
  [4b2b6221531fa626]   STRU  find_import_insert_point  L=8 N=2 saved=8 sim=1.00
      src/algitex/todo/micro_utils.py:19-26  (find_import_insert_point)
      src/algitex/todo/repair.py:20-27  (_find_import_insert_point)
  [b88f1be5bbe725cb]   EXAC  bad_error_handling  L=6 N=2 saved=6 sim=1.00
      examples/18-ollama-local/buggy_code.py:65-70  (bad_error_handling)
      examples/21-aider-cli-ollama/buggy_code.py:89-94  (bad_error_handling)
  [a8c9e73e4f29c027]   EXAC  _extract_code  L=6 N=2 saved=6 sim=1.00
      src/algitex/tools/autofix/openrouter_backend.py:124-129  (_extract_code)
      src/algitex/tools/autofix/proxy_backend.py:119-124  (_extract_code)
  [4e747b302409b9e2]   EXAC  restart_service  L=6 N=2 saved=6 sim=1.00
      src/algitex/tools/mcp.py:216-221  (restart_service)
      src/algitex/tools/mcp_lifecycle.py:110-114  (restart_service)
  [41447c1cd48e222b]   STRU  format_value  L=6 N=2 saved=6 sim=1.00
      src/algitex/tools/logging.py:115-120  (format_value)
      src/algitex/tools/logging.py:123-128  (format_result)
  [8bbc01c07a65bbf2]   EXAC  divide  L=4 N=2 saved=4 sim=1.00
      examples/21-aider-cli-ollama/buggy_code.py:53-56  (divide)
      examples/22-claude-code-ollama/buggy_code.py:39-41  (divide)
  [9041454cac40ebe4]   EXAC  check_mcp_service  L=4 N=2 saved=4 sim=1.00
      src/algitex/tools/services/http_checks.py:122-125  (check_mcp_service)
      src/algitex/tools/services.py:177-180  (check_mcp_service)
  [fe906fa614b4fe91]   STRU  __init__  L=4 N=2 saved=4 sim=1.00
      docker/code2llm/code2llm_server.py:32-35  (__init__)
      docker/vallm/vallm_server.py:28-31  (__init__)
  [7dc040b9bd7dbb63]   STRU  load  L=4 N=2 saved=4 sim=1.00
      examples/22-claude-code-ollama/buggy_code.py:33-36  (load)
      examples/26-litellm-proxy-ollama/buggy_code.py:31-34  (load_file)
  [6b55f2c1e7063172]   STRU  connect  L=4 N=2 saved=4 sim=1.00
      examples/34-batch-fix/sample_code/file2.py:4-7  (connect)
      examples/34-batch-fix/sample_code/file2.py:9-12  (retry)
  [36de84d7e7f7450b]   EXAC  divide_numbers  L=3 N=2 saved=3 sim=1.00
      examples/18-ollama-local/buggy_code.py:34-36  (divide_numbers)
      examples/26-litellm-proxy-ollama/buggy_code.py:37-39  (divide_numbers)
  [4691acbd8fe86074]   EXAC  __enter__  L=3 N=2 saved=3 sim=1.00
      src/algitex/dashboard.py:316-318  (__enter__)
      src/algitex/dashboard.py:370-372  (__enter__)
  [d182f36f3929d9f0]   EXAC  _read_file  L=3 N=2 saved=3 sim=1.00
      src/algitex/tools/autofix/openrouter_backend.py:75-77  (_read_file)
      src/algitex/tools/autofix/proxy_backend.py:72-74  (_read_file)
  [d13c1673351a0d46]   EXAC  _write_file  L=3 N=2 saved=3 sim=1.00
      src/algitex/tools/autofix/openrouter_backend.py:131-133  (_write_file)
      src/algitex/tools/autofix/proxy_backend.py:126-128  (_write_file)
  [d4eb332cab42c22e]   EXAC  __post_init__  L=3 N=2 saved=3 sim=1.00
      src/algitex/tools/ide.py:30-32  (__post_init__)
      src/algitex/tools/ide_models.py:18-20  (__post_init__)
  [ceb71006739f56b2]   EXAC  __init__  L=3 N=2 saved=3 sim=1.00
      src/algitex/tools/ide.py:38-40  (__init__)
      src/algitex/tools/ide_base.py:15-17  (__init__)
  [79e5a86747b02bec]   EXAC  list_tools  L=3 N=2 saved=3 sim=1.00
      src/algitex/tools/ide.py:116-118  (list_tools)
      src/algitex/tools/ide_base.py:87-89  (list_tools)
  [a71363a8d280ed16]   EXAC  setup_environment  L=3 N=2 saved=3 sim=1.00
      src/algitex/tools/ide.py:142-144  (setup_environment)
      src/algitex/tools/ide_claude.py:19-21  (setup_environment)
  [10d7a0e802d64c8a]   EXAC  handler  L=3 N=2 saved=3 sim=1.00
      src/algitex/tools/mcp.py:55-57  (handler)
      src/algitex/tools/mcp_orchestrator.py:27-29  (handler)
  [7ec49a990d4c1e94]   EXAC  close  L=3 N=2 saved=3 sim=1.00
      src/algitex/tools/ollama.py:332-334  (close)
      src/algitex/tools/services.py:355-357  (close)
  [f981e3e3f45b5f0c]   EXAC  status_icon  L=3 N=2 saved=3 sim=1.00
      src/algitex/tools/services/models.py:19-21  (status_icon)
      src/algitex/tools/services.py:34-36  (status_icon)

REFACTOR[53] (ranked by priority):
  [1] ○ extract_function   → examples/utils/demo_split_strategy.py
      WHY: 5 occurrences of 27-line block across 3 files — saves 108 lines
      FILES: examples/41-god-module-splitting/main.py, examples/43-code-health/main.py, examples/44-plugin-system/main.py
  [2] ○ extract_function   → examples/34-batch-fix/utils/demo_batch_dry_run.py
      WHY: 3 occurrences of 44-line block across 1 files — saves 88 lines
      FILES: examples/34-batch-fix/main.py
  [3] ○ extract_function   → examples/utils/demo_orchestrator_pattern.py
      WHY: 5 occurrences of 21-line block across 4 files — saves 84 lines
      FILES: examples/35-sprint3-patterns/main.py, examples/36-dashboard/main.py, examples/37-benchmarks/main.py, examples/39-microtask-pipeline/main.py
  [4] ○ extract_function   → examples/utils/demo_dashboard_monitor.py
      WHY: 5 occurrences of 13-line block across 4 files — saves 52 lines
      FILES: examples/36-dashboard/main.py, examples/37-benchmarks/main.py, examples/39-microtask-pipeline/main.py, examples/40-three-tier-autofix/main.py
  [5] ○ extract_function   → examples/utils/main.py
      WHY: 3 occurrences of 19-line block across 3 files — saves 38 lines
      FILES: examples/42-duplicate-removal/main.py, examples/43-code-health/main.py, examples/44-plugin-system/main.py
  [6] ◐ extract_function   → src/algitex/tools/utils/stop_service.py
      WHY: 2 occurrences of 36-line block across 2 files — saves 36 lines
      FILES: src/algitex/tools/mcp.py, src/algitex/tools/mcp_lifecycle.py
  [7] ◐ extract_class      → src/algitex/tools/utils/_register_default_tools.py
      WHY: 2 occurrences of 34-line block across 2 files — saves 34 lines
      FILES: src/algitex/tools/ide.py, src/algitex/tools/ide_base.py
  [8] ○ extract_function   → examples/utils/main.py
      WHY: 3 occurrences of 17-line block across 3 files — saves 34 lines
      FILES: examples/36-dashboard/main.py, examples/38-new-modules/main.py, examples/39-microtask-pipeline/main.py
  [9] ○ extract_function   → docker/utils/run_rest_server.py
      WHY: 5 occurrences of 8-line block across 5 files — saves 32 lines
      FILES: docker/aider-mcp/aider_mcp_server.py, docker/code2llm/code2llm_mcp_server.py, docker/planfile-mcp/planfile_mcp_server.py, docker/proxym/proxym_mcp_server.py, docker/vallm/vallm_mcp_server.py
  [10] ◐ extract_function   → examples/utils/create_sample_project.py
      WHY: 2 occurrences of 32-line block across 2 files — saves 32 lines
      FILES: examples/11-aider-mcp/main.py, examples/13-vallm/main.py
  [11] ○ extract_function   → src/algitex/cli/utils/ticket.py
      WHY: 10 occurrences of 3-line block across 1 files — saves 27 lines
      FILES: src/algitex/cli/__init__.py
  [12] ○ extract_function   → src/algitex/todo/utils/_process_fstring_batch.py
      WHY: 2 occurrences of 26-line block across 1 files — saves 26 lines
      FILES: src/algitex/todo/fixer.py
  [13] ○ extract_class      → src/algitex/tools/utils/setup_tool.py
      WHY: 2 occurrences of 22-line block across 2 files — saves 22 lines
      FILES: src/algitex/tools/ide.py, src/algitex/tools/ide_base.py
  [14] ○ extract_function   → examples/42-duplicate-removal/utils/demo_detection_with_redup.py
      WHY: 2 occurrences of 22-line block across 1 files — saves 22 lines
      FILES: examples/42-duplicate-removal/main.py
  [15] ○ extract_function   → src/algitex/tools/autofix/utils/_dry_run_result.py
      WHY: 3 occurrences of 11-line block across 3 files — saves 22 lines
      FILES: src/algitex/tools/autofix/aider_backend.py, src/algitex/tools/autofix/openrouter_backend.py, src/algitex/tools/autofix/proxy_backend.py
  [16] ○ extract_function   → src/algitex/tools/autofix/utils/_error_result.py
      WHY: 3 occurrences of 11-line block across 3 files — saves 22 lines
      FILES: src/algitex/tools/autofix/aider_backend.py, src/algitex/tools/autofix/openrouter_backend.py, src/algitex/tools/autofix/proxy_backend.py
  [17] ○ extract_function   → examples/40-three-tier-autofix/utils/demo_tier_micro.py
      WHY: 2 occurrences of 20-line block across 1 files — saves 20 lines
      FILES: examples/40-three-tier-autofix/main.py
  [18] ○ extract_function   → src/algitex/todo/utils/_first_int.py
      WHY: 3 occurrences of 9-line block across 3 files — saves 18 lines
      FILES: src/algitex/todo/classify.py, src/algitex/todo/micro_utils.py, src/algitex/todo/tiering.py
  [19] ○ extract_function   → src/algitex/tools/autofix/utils/_execute_fix.py
      WHY: 2 occurrences of 17-line block across 2 files — saves 17 lines
      FILES: src/algitex/tools/autofix/openrouter_backend.py, src/algitex/tools/autofix/proxy_backend.py
  [20] ○ extract_function   → examples/utils/demo_microtask_plan.py
      WHY: 2 occurrences of 16-line block across 2 files — saves 16 lines
      FILES: examples/39-microtask-pipeline/main.py, examples/40-three-tier-autofix/main.py
  [21] ○ extract_function   → src/algitex/tools/autofix/utils/_build_prompt.py
      WHY: 2 occurrences of 14-line block across 2 files — saves 14 lines
      FILES: src/algitex/tools/autofix/openrouter_backend.py, src/algitex/tools/autofix/proxy_backend.py
  [22] ○ extract_function   → docker/utils/run.py
      WHY: 3 occurrences of 7-line block across 3 files — saves 14 lines
      FILES: docker/code2llm/code2llm_server.py, docker/proxym/proxym_server.py, docker/vallm/vallm_server.py
  [23] ○ extract_function   → examples/utils/calculate.py
      WHY: 2 occurrences of 13-line block across 2 files — saves 13 lines
      FILES: examples/23-continue-dev-ollama/buggy_code.py, examples/26-litellm-proxy-ollama/buggy_code.py
  [24] ○ extract_function   → src/algitex/tools/autofix/utils/fix.py
      WHY: 2 occurrences of 12-line block across 2 files — saves 12 lines
      FILES: src/algitex/tools/autofix/openrouter_backend.py, src/algitex/tools/autofix/proxy_backend.py
  [25] ○ extract_function   → src/algitex/tools/utils/__init__.py
      WHY: 5 occurrences of 3-line block across 3 files — saves 12 lines
      FILES: src/algitex/tools/ide.py, src/algitex/tools/ide_aider.py, src/algitex/tools/ide_claude.py
  [26] ○ extract_function   → examples/utils/load_env.py
      WHY: 2 occurrences of 11-line block across 2 files — saves 11 lines
      FILES: examples/04-ide-integration/main.py, examples/17-docker-workflow/main.py
  [27] ○ extract_function   → src/algitex/tools/autofix/utils/_ensure_model.py
      WHY: 2 occurrences of 10-line block across 2 files — saves 10 lines
      FILES: src/algitex/tools/autofix/batch_backend.py, src/algitex/tools/autofix/ollama_backend.py
  [28] ○ extract_function   → src/algitex/tools/autofix/utils/_success_result.py
      WHY: 2 occurrences of 10-line block across 2 files — saves 10 lines
      FILES: src/algitex/tools/autofix/openrouter_backend.py, src/algitex/tools/autofix/proxy_backend.py
  [29] ○ extract_function   → examples/utils/process_items.py
      WHY: 2 occurrences of 8-line block across 2 files — saves 8 lines
      FILES: examples/23-continue-dev-ollama/buggy_code.py, examples/26-litellm-proxy-ollama/buggy_code.py
  [30] ○ extract_function   → src/algitex/microtask/utils/_resolve_path.py
      WHY: 2 occurrences of 8-line block across 2 files — saves 8 lines
      FILES: src/algitex/microtask/executor.py, src/algitex/microtask/slicer.py
  [31] ○ extract_class      → src/algitex/tools/utils/_setup_signal_handlers.py
      WHY: 2 occurrences of 8-line block across 2 files — saves 8 lines
      FILES: src/algitex/tools/mcp.py, src/algitex/tools/mcp_orchestrator.py
  [32] ○ extract_function   → examples/utils/show_cli_usage.py
      WHY: 2 occurrences of 8-line block across 2 files — saves 8 lines
      FILES: examples/17-docker-workflow/main.py, examples/36-dashboard/main.py
  [33] ○ extract_function   → src/algitex/todo/utils/find_import_insert_point.py
      WHY: 2 occurrences of 8-line block across 2 files — saves 8 lines
      FILES: src/algitex/todo/micro_utils.py, src/algitex/todo/repair.py
  [34] ○ extract_function   → examples/utils/bad_error_handling.py
      WHY: 2 occurrences of 6-line block across 2 files — saves 6 lines
      FILES: examples/18-ollama-local/buggy_code.py, examples/21-aider-cli-ollama/buggy_code.py
  [35] ○ extract_function   → src/algitex/tools/autofix/utils/_extract_code.py
      WHY: 2 occurrences of 6-line block across 2 files — saves 6 lines
      FILES: src/algitex/tools/autofix/openrouter_backend.py, src/algitex/tools/autofix/proxy_backend.py
  [36] ○ extract_function   → src/algitex/tools/utils/restart_service.py
      WHY: 2 occurrences of 6-line block across 2 files — saves 6 lines
      FILES: src/algitex/tools/mcp.py, src/algitex/tools/mcp_lifecycle.py
  [37] ○ extract_function   → src/algitex/tools/utils/format_value.py
      WHY: 2 occurrences of 6-line block across 1 files — saves 6 lines
      FILES: src/algitex/tools/logging.py
  [38] ○ extract_function   → examples/utils/divide.py
      WHY: 2 occurrences of 4-line block across 2 files — saves 4 lines
      FILES: examples/21-aider-cli-ollama/buggy_code.py, examples/22-claude-code-ollama/buggy_code.py
  [39] ○ extract_function   → src/algitex/tools/utils/check_mcp_service.py
      WHY: 2 occurrences of 4-line block across 2 files — saves 4 lines
      FILES: src/algitex/tools/services.py, src/algitex/tools/services/http_checks.py
  [40] ○ extract_function   → docker/utils/__init__.py
      WHY: 2 occurrences of 4-line block across 2 files — saves 4 lines
      FILES: docker/code2llm/code2llm_server.py, docker/vallm/vallm_server.py
  [41] ○ extract_function   → examples/utils/load.py
      WHY: 2 occurrences of 4-line block across 2 files — saves 4 lines
      FILES: examples/22-claude-code-ollama/buggy_code.py, examples/26-litellm-proxy-ollama/buggy_code.py
  [42] ○ extract_function   → examples/34-batch-fix/sample_code/utils/connect.py
      WHY: 2 occurrences of 4-line block across 1 files — saves 4 lines
      FILES: examples/34-batch-fix/sample_code/file2.py
  [43] ○ extract_function   → examples/utils/divide_numbers.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: examples/18-ollama-local/buggy_code.py, examples/26-litellm-proxy-ollama/buggy_code.py
  [44] ○ extract_function   → src/algitex/utils/__enter__.py
      WHY: 2 occurrences of 3-line block across 1 files — saves 3 lines
      FILES: src/algitex/dashboard.py
  [45] ○ extract_function   → src/algitex/tools/autofix/utils/_read_file.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: src/algitex/tools/autofix/openrouter_backend.py, src/algitex/tools/autofix/proxy_backend.py
  [46] ○ extract_function   → src/algitex/tools/autofix/utils/_write_file.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: src/algitex/tools/autofix/openrouter_backend.py, src/algitex/tools/autofix/proxy_backend.py
  [47] ○ extract_class      → src/algitex/tools/utils/__post_init__.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: src/algitex/tools/ide.py, src/algitex/tools/ide_models.py
  [48] ○ extract_class      → src/algitex/tools/utils/__init__.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: src/algitex/tools/ide.py, src/algitex/tools/ide_base.py
  [49] ○ extract_class      → src/algitex/tools/utils/list_tools.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: src/algitex/tools/ide.py, src/algitex/tools/ide_base.py
  [50] ○ extract_class      → src/algitex/tools/utils/setup_environment.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: src/algitex/tools/ide.py, src/algitex/tools/ide_claude.py
  [51] ○ extract_function   → src/algitex/tools/utils/handler.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: src/algitex/tools/mcp.py, src/algitex/tools/mcp_orchestrator.py
  [52] ○ extract_function   → src/algitex/tools/utils/close.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: src/algitex/tools/ollama.py, src/algitex/tools/services.py
  [53] ○ extract_class      → src/algitex/tools/utils/status_icon.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: src/algitex/tools/services.py, src/algitex/tools/services/models.py

QUICK_WINS[34] (low risk, high savings — do first):
  [1] extract_function   saved=108L  → examples/utils/demo_split_strategy.py
      FILES: main.py, main.py, main.py
  [2] extract_function   saved=88L  → examples/34-batch-fix/utils/demo_batch_dry_run.py
      FILES: main.py
  [3] extract_function   saved=84L  → examples/utils/demo_orchestrator_pattern.py
      FILES: main.py, main.py, main.py +1
  [4] extract_function   saved=52L  → examples/utils/demo_dashboard_monitor.py
      FILES: main.py, main.py, main.py +1
  [5] extract_function   saved=38L  → examples/utils/main.py
      FILES: main.py, main.py, main.py
  [8] extract_function   saved=34L  → examples/utils/main.py
      FILES: main.py, main.py, main.py
  [9] extract_function   saved=32L  → docker/utils/run_rest_server.py
      FILES: aider_mcp_server.py, code2llm_mcp_server.py, planfile_mcp_server.py +2
  [11] extract_function   saved=27L  → src/algitex/cli/utils/ticket.py
      FILES: __init__.py
  [12] extract_function   saved=26L  → src/algitex/todo/utils/_process_fstring_batch.py
      FILES: fixer.py
  [13] extract_class      saved=22L  → src/algitex/tools/utils/setup_tool.py
      FILES: ide.py, ide_base.py

EFFORT_ESTIMATE (total ≈ 35.3h):
  hard   demo_split_strategy                 saved=108L  ~216min
  hard   demo_batch_dry_run                  saved=88L  ~264min
  hard   demo_orchestrator_pattern           saved=84L  ~168min
  hard   demo_dashboard_monitor              saved=52L  ~104min
  medium main                                saved=38L  ~76min
  hard   stop_service                        saved=36L  ~108min
  hard   _register_default_tools             saved=34L  ~102min
  medium main                                saved=34L  ~68min
  medium run_rest_server                     saved=32L  ~64min
  hard   create_sample_project               saved=32L  ~96min
  ... +43 more (~850min)

METRICS-TARGET:
  dup_groups:  53 → 0
  saved_lines: 963 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 1488 func | 118f | 2026-04-25

NEXT[10] (ranked by impact):
  [1] !! SPLIT           src/algitex/cli/todo.py
      WHY: 1159L, 0 classes, max CC=29
      EFFORT: ~4h  IMPACT: 33611

  [2] !! SPLIT           src/algitex/todo/fixer.py
      WHY: 550L, 1 classes, max CC=25
      EFFORT: ~4h  IMPACT: 13750

  [3] !! SPLIT           src/algitex/tools/autofix/batch_backend.py
      WHY: 826L, 2 classes, max CC=16
      EFFORT: ~4h  IMPACT: 13216

  [4] !! SPLIT-FUNC      todo_verify_prefact  CC=29  fan=22
      WHY: CC=29 exceeds 15
      EFFORT: ~1h  IMPACT: 638

  [5] !  SPLIT-FUNC      _run_with_dashboard  CC=15  fan=29
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 435

  [6] !! SPLIT-FUNC      fix_file  CC=25  fan=17
      WHY: CC=25 exceeds 15
      EFFORT: ~1h  IMPACT: 425

  [7] !! SPLIT-FUNC      _tf_execute_phased  CC=25  fan=12
      WHY: CC=25 exceeds 15
      EFFORT: ~1h  IMPACT: 300

  [8] !  SPLIT-FUNC      BatchFixBackend._parse_batch_response  CC=16  fan=18
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 288

  [9] !  SPLIT-FUNC      MicroTaskExecutor._apply_magic_name  CC=16  fan=16
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 256

  [10] !  SPLIT-FUNC      todo_hybrid  CC=15  fan=14
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 210


RISKS[3]:
  ⚠ Splitting src/algitex/cli/todo.py may break 21 import paths
  ⚠ Splitting src/algitex/tools/autofix/batch_backend.py may break 16 import paths
  ⚠ Splitting src/algitex/todo/fixer.py may break 17 import paths

METRICS-TARGET:
  CC̄:          2.5 → ≤1.8
  max-CC:      48 → ≤20
  god-modules: 3 → 0
  high-CC(≥15): 9 → ≤4
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  prev CC̄=2.5 → now CC̄=2.5
```

### Validation (`project/validation.toon.yaml`)

```toon markpact:analysis path=project/validation.toon.yaml
# vallm batch | 493f | 211✓ 9⚠ 16✗ | 2026-03-29

SUMMARY:
  scanned: 493  passed: 211 (42.8%)  warnings: 9  errors: 16  unsupported: 266

WARNINGS[9]{path,score}:
  src/algitex/cli/todo.py,0.87
    issues[7]{rule,severity,message,line}:
      complexity.cyclomatic,warning,_tf_execute_phased has cyclomatic complexity 25 (max: 15),626
      complexity.cyclomatic,warning,todo_verify_prefact has cyclomatic complexity 29 (max: 15),1027
      complexity.maintainability,warning,Low maintainability index: 12.7 (threshold: 20),
      complexity.lizard_cc,warning,_run_with_dashboard.run_phases: CC=27 exceeds limit 15,101
      complexity.lizard_cc,warning,_run_with_dashboard: CC=16 exceeds limit 15,45
      complexity.lizard_cc,warning,_tf_execute_phased: CC=25 exceeds limit 15,626
      complexity.lizard_cc,warning,todo_verify_prefact: CC=29 exceeds limit 15,1027
  src/algitex/microtask/executor.py,0.96
    issues[3]{rule,severity,message,line}:
      complexity.cyclomatic,warning,_apply_magic_name has cyclomatic complexity 16 (max: 15),372
      complexity.maintainability,warning,Low maintainability index: 8.3 (threshold: 20),
      complexity.lizard_cc,warning,_apply_magic_name: CC=16 exceeds limit 15,372
  scripts/generate_lib_docs.py,0.97
    issues[2]{rule,severity,message,line}:
      complexity.cyclomatic,warning,parse_file has cyclomatic complexity 24 (max: 15),54
      complexity.lizard_cc,warning,parse_file: CC=24 exceeds limit 15,54
  src/algitex/microtask/classifier.py,0.97
    issues[2]{rule,severity,message,line}:
      complexity.cyclomatic,warning,_classify_message has cyclomatic complexity 48 (max: 15),105
      complexity.lizard_cc,warning,_classify_message: CC=48 exceeds limit 15,105
  src/algitex/todo/fixer.py,0.97
    issues[2]{rule,severity,message,line}:
      complexity.cyclomatic,warning,fix_file has cyclomatic complexity 25 (max: 15),201
      complexity.lizard_cc,warning,fix_file: CC=25 exceeds limit 15,201
  tests/test_e2e_integration.py,0.97
    issues[2]{rule,severity,message,line}:
      complexity.cyclomatic,warning,test_complete_pipeline_flow has cyclomatic complexity 16 (max: 15),167
      complexity.lizard_length,warning,sample_project: 120 lines exceeds limit 100,28
  src/algitex/todo/micro.py,0.98
    issues[1]{rule,severity,message,line}:
      complexity.maintainability,warning,Low maintainability index: 9.9 (threshold: 20),
  src/algitex/tools/autofix/batch_backend.py,0.98
    issues[1]{rule,severity,message,line}:
      complexity.cyclomatic,warning,_parse_batch_response has cyclomatic complexity 16 (max: 15),642
  tests/test_parallel.py,0.98
    issues[1]{rule,severity,message,line}:
      complexity.cyclomatic,warning,test_extract_functions_and_classes has cyclomatic complexity 19 (max: 15),14

ERRORS[16]{path,score}:
  tests/test_examples_30_32.py,0.76
    issues[9]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'parallel_refactoring' not found,53
      python.import.resolvable,error,Module 'parallel_multi_tool' not found,85
      python.import.resolvable,error,Module 'abpr_pipeline' not found,112
      python.import.resolvable,error,Module 'parallel_refactoring' not found,26
      python.import.resolvable,error,Module 'parallel_multi_tool' not found,34
      python.import.resolvable,error,Module 'parallel_real_world' not found,42
      python.import.resolvable,error,Module 'abpr_pipeline' not found,103
      python.import.resolvable,error,Module 'workspace_parallel' not found,162
      python.import.resolvable,error,Module 'workspace_parallel' not found,204
  docker/aider-mcp/aider_mcp_server.py,0.81
    issues[4]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'mcp.server.fastmcp' not found,12
      python.import.resolvable,error,Module 'fastapi' not found,13
      python.import.resolvable,error,Module 'fastapi.responses' not found,14
      python.import.resolvable,error,Module 'uvicorn' not found,15
  examples/16-test-workflow/sample_test_project/tests/test_calculator.py,0.86
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'calculator' not found,6
  docker/proxym/proxym_mcp_server.py,0.87
    issues[4]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'mcp.server.fastmcp' not found,14
      python.import.resolvable,error,Module 'fastapi' not found,15
      python.import.resolvable,error,Module 'fastapi.responses' not found,16
      python.import.resolvable,error,Module 'uvicorn' not found,17
  docker/planfile-mcp/planfile_mcp_server.py,0.88
    issues[3]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'mcp.server.fastmcp' not found,15
      python.import.resolvable,error,Module 'fastapi' not found,16
      python.import.resolvable,error,Module 'uvicorn' not found,17
  docker/proxym/proxym_server.py,0.88
    issues[3]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'fastapi' not found,14
      python.import.resolvable,error,Module 'fastapi.responses' not found,15
      python.import.resolvable,error,Module 'uvicorn' not found,16
  docker/vallm/vallm_mcp_server.py,0.88
    issues[3]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'mcp.server.fastmcp' not found,15
      python.import.resolvable,error,Module 'fastapi' not found,16
      python.import.resolvable,error,Module 'uvicorn' not found,17
  docker/vallm/vallm_server.py,0.90
    issues[2]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'fastapi' not found,14
      python.import.resolvable,error,Module 'uvicorn' not found,15
  docker/code2llm/code2llm_mcp_server.py,0.91
    issues[3]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'mcp.server.fastmcp' not found,16
      python.import.resolvable,error,Module 'fastapi' not found,17
      python.import.resolvable,error,Module 'uvicorn' not found,18
  docker/code2llm/code2llm_server.py,0.93
    issues[2]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'fastapi' not found,16
      python.import.resolvable,error,Module 'uvicorn' not found,17
  tests/test_shared_rules.py,0.93
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'isort' not found,129
  src/algitex/tools/context.py,0.94
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'qdrant_client' not found,178
  src/algitex/nlp/__init__.py,0.95
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'isort' not found,264
  src/algitex/shared_rules.py,0.95
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'isort' not found,176
  src/algitex/tools/telemetry.py,0.95
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'langfuse' not found,97
  src/algitex/tools/batch.py,0.96
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'tqdm' not found,34

UNSUPPORTED[5]{bucket,count}:
  *.md,182
  Dockerfile*,31
  *.txt,2
  *.yml,3
  other,48
```

## Intent

Progressive algorithmization toolchain — from LLM to deterministic code, from proxy to tickets
