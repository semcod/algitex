.PHONY: help run test clean analyze

# Default target
help:
	@echo "Workspace Coordination Examples"
	@echo ""
	@echo "Targets:"
	@echo "  run      - Run the workspace coordination demo"
	@echo "  test     - Run all workspace examples"
	@echo "  analyze  - Analyze workspace (no changes)"
	@echo "  clean    - Clean temporary files"
	@echo ""
	@echo "Examples:"
	@echo "  make run"
	@echo "  python workspace_parallel.py"

# Run the main demo
run:
	@echo "Running workspace coordination demo..."
	python main.py

# Run all examples
test:
	@echo "Running all workspace examples..."
	@echo ""
	@echo "1. Main demo:"
	python main.py
	@echo ""
	@echo "2. Workspace parallel execution:"
	python workspace_parallel.py

# Analyze only (no changes)
analyze:
	@echo "Analyzing workspace (read-only)..."
	@if [ -f "workspace.yaml" ]; then \
		echo "Workspace configuration:"; \
		grep -E "^(name|description|role):" workspace.yaml | sed 's/^/  /'; \
	else \
		echo "No workspace.yaml found"; \
	fi

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	rm -rf .algitex/
	rm -rf __pycache__/
	rm -rf *.pyc
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Install dependencies
install:
	@echo "Installing algitex in development mode..."
	pip install -e ../../

# Show workspace structure
show-workspace:
	@echo "Workspace structure from workspace.yaml:"
	@if [ -f "workspace.yaml" ]; then \
		python -c "import yaml; d=yaml.safe_load(open('workspace.yaml')); \
		print(f'Workspace: {d[\"workspace\"][\"name\"]}'); \
		print(f'Repositories: {len(d[\"repos\"])}'); \
		for r in d[\"repos\"]: \
			deps = f' (deps: {r.get(\"depends_on\", [])})' if r.get('depends_on') else ''; \
			print(f'  - {r[\"name\"]} P{r.get(\"priority\", 0)}{deps}'); \
		"; \
	else \
		echo "No workspace.yaml found"; \
	fi

# Real workspace execution (requires actual repos)
execute:
	@echo "⚠️  This requires actual repositories to be configured!"
	@echo "Ensure workspace.yaml points to valid repository paths."
	@echo ""
	@echo "Commands for real execution:"
	@echo "  algitex workspace analyze"
	@echo "  algitex workspace plan --sprints 2"
	@echo "  algitex workspace go --parallel"
