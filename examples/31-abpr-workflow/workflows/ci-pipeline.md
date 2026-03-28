# CI/CD Pipeline Check

Automated checks suitable for GitHub Actions / GitLab CI.

## Run tests

```propact:shell
python3 -m pytest tests/ -v --tb=short 2>&1 || true
```

## Check code formatting

```propact:shell
python3 -m ruff format --check src/ tests/ 2>&1 || echo "⚠️ Formatting issues found"
```

## Check linting

```propact:shell
python3 -m ruff check src/ tests/ 2>&1 || echo "⚠️ Lint issues found"
```

## Generate health report

```propact:shell
python3 -c "
from algitex import Project
p = Project('.')
r = p.analyze(full=False)
print(f'Grade: {r.grade} | CC̄={r.cc_avg:.1f} | Files: {r.files}')
if r.grade in ('C', 'D'):
    print('⚠️ Quality below target — consider algitex plan')
    exit(1)
print('✅ Quality check passed')
"
```

## Show algo progress

```propact:shell
python3 -c "
from algitex.algo import Loop
report = Loop('.').report()
print(f'Algo stage: {report[\"stage\"]}')
print(f'Deterministic: {report[\"deterministic_ratio\"]}')
print(f'Saved: \${report[\"saved_cost_usd\"]:.2f}')
"
```
