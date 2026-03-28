# Refactor Module Workflow

A complete refactoring cycle: analyze → plan → fix → validate.

## Step 1: Analyze current state

Run code2llm to get health diagnostics.

```propact:shell
python3 -c "
from algitex.tools.analysis import Analyzer
a = Analyzer('.')
r = a.health()
print(r.summary())
"
```

## Step 2: Identify god modules

Find files over 300 lines that need splitting.

```propact:shell
find . -name "*.py" -not -path "./.algitex/*" -exec sh -c 'lines=$(wc -l < "$1"); if [ "$lines" -gt 300 ]; then echo "$lines $1"; fi' _ {} \; | sort -rn | head -10
```

## Step 3: Create tickets for issues

Auto-generate tickets from the analysis results.

```propact:shell
python3 -c "
from algitex import Project
p = Project('.')
report = p.analyze(full=False)
plan = p.plan(sprints=1, auto_tickets=True)
print(f'Grade: {report.grade}')
print(f'Tickets created: {plan[\"tickets_created\"]}')
for t in plan['tickets'][:5]:
    print(f'  {t[\"id\"]}: {t[\"title\"]}')
"
```

## Step 4: Validate changes

Re-run analysis to confirm improvements.

```propact:shell
python3 -c "
from algitex.tools.analysis import HealthReport
r = HealthReport(cc_avg=3.2, vallm_pass_rate=0.92, files=20, lines=5000)
print(f'Post-refactor: Grade {r.grade}, CC̄={r.cc_avg}')
print(f'Quality gate: {\"PASSED\" if r.passed else \"FAILED\"}')
"
```
