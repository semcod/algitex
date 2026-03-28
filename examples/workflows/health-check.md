# Health Check Workflow

Run basic health checks on the current project.

## Check Python version

```propact:shell
python3 --version
```

## Check project structure

```propact:shell
find . -name "*.py" -not -path "./.devloop/*" -not -path "./__pycache__/*" | head -20
```

## Count lines of code

```propact:shell
find . -name "*.py" -not -path "./.devloop/*" | xargs wc -l 2>/dev/null | tail -1
```

## Check for syntax errors

```propact:shell
python3 -m py_compile src/devloop/__init__.py 2>&1 && echo "✅ No syntax errors" || echo "❌ Syntax errors found"
```

## List installed devloop tools

```propact:shell
python3 -c "from devloop.tools import discover_tools; [print(f'  {s}') for s in discover_tools().values()]"
```
