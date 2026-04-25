## 1. Analyze codebase → structural trace

```propact:shell
code2llm ./src/auth -f toon,evolution --json > .algitex/auth.toon
```

## 2. Run tests → collect failure trace

```propact:shell
pytest tests/auth/ -v --tb=short --json-report --json-report-file=.algitex/auth-tests.json || true
```

## 3. Localize root cause (LLM as heuristic, not oracle)

```propact:llm
{
  "model": "balanced",
  "messages": [
    {
      "role": "system",
      "content": "You are a code analyst. From the .toon diagnostics and test results, find the MINIMAL root cause of auth failures. Return JSON with: {cause: str, file: str, function: str, fix_type: 'decorator'|'wrapper'|'guard'|'refactor'}"
    },
    {
      "role": "user",
      "content": "auth.toon: {{file:.algitex/auth.toon}}\ntest results: {{file:.algitex/auth-tests.json}}"
    }
  ]
}
```

## 4. Generate minimal fix (rule, not rewrite)

```propact:docker
tool: aider-mcp
action: aider_ai_code
input:
  prompt: |
    Based on the root cause analysis, apply the MINIMAL fix:
    - If fix_type is 'decorator': add a validation decorator
    - If fix_type is 'wrapper': wrap the function with error handling
    - If fix_type is 'guard': add input validation guards
    Do NOT rewrite the entire function. Change as few lines as possible.
  relative_editable_files:
    - src/auth/middleware.py
    - src/auth/token.py
  relative_readonly_files:
    - src/auth/__init__.py
    - tests/auth/test_token.py
```

# Static validation
vallm file ./src/auth/middleware.py --level 3
vallm file ./src/auth/token.py --level 3

# Runtime validation
pytest tests/auth/ -v --tb=short

# Security scan
semgrep scan ./src/auth/ --config auto --json
```

## 6. If failed → retry with feedback

```propact:shell
if [ "$?" != "0" ]; then
    echo "Validation failed, triggering feedback loop..."
    algitex algo feedback --ticket SEC-2026-01 --retry --escalate-model
fi
```

## 7. Update ticket and sync

```propact:docker
tool: planfile-mcp
action: planfile_update_ticket
input:
  ticket_id: SEC-2026-01
  status: done
  resolution:
    tool: aider-mcp
    validation: passed
    iterations: 1
```
