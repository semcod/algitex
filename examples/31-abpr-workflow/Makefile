.PHONY: help run test clean workflow

# Default target
help:
	@echo "ABPR (Abduction-Based Procedural Refinement) Examples"
	@echo ""
	@echo "Targets:"
	@echo "  run        - Run the main ABPR demo"
	@echo "  test       - Run all ABPR examples"
	@echo "  workflow   - Run a specific workflow"
	@echo "  clean      - Clean temporary files"
	@echo ""
	@echo "Examples:"
	@echo "  make run"
	@echo "  make workflow WORKFLOW=fix-auth"
	@echo "  python abpr_pipeline.py"

# Run the main demo
run:
	@echo "Running ABPR pipeline demo..."
	python main.py

# Run all examples
test:
	@echo "Running all ABPR examples..."
	@echo ""
	@echo "1. Main demo:"
	python main.py
	@echo ""
	@echo "2. ABPR pipeline:"
	python abpr_pipeline.py
	@echo ""
	@echo "3. Available workflows:"
	@ls workflows/*.md 2>/dev/null || echo "  No workflow files found"

# Run a specific workflow
workflow:
	@if [ -z "$(WORKFLOW)" ]; then \
		echo "Usage: make workflow WORKFLOW=<workflow-name>"; \
		echo "Available workflows:"; \
		ls workflows/*.md 2>/dev/null | sed 's/workflows\///g' | sed 's/.md$$//g'; \
	else \
		if [ -f "workflows/$(WORKFLOW).md" ]; then \
			echo "Running workflow: $(WORKFLOW)"; \
			algitex workflow run workflows/$(WORKFLOW).md --ticket DEMO-001; \
		else \
			echo "Workflow not found: workflows/$(WORKFLOW).md"; \
		fi; \
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

# Show workflow files
list-workflows:
	@echo "Available workflows:"
	@for f in workflows/*.md 2>/dev/null; do \
		if [ -f "$$f" ]; then \
			echo "  - $$(basename $$f .md)"; \
		fi; \
	done
