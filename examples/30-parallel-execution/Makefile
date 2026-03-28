.PHONY: help run test clean

# Default target
help:
	@echo "Parallel Execution Examples"
	@echo ""
	@echo "Targets:"
	@echo "  run      - Run the main parallel execution demo"
	@echo "  test     - Run all parallel execution examples"
	@echo "  clean    - Clean temporary files"
	@echo ""
	@echo "Examples:"
	@echo "  make run"
	@echo "  python parallel_refactoring.py"
	@echo "  python parallel_multi_tool.py"
	@echo "  python parallel_real_world.py"

# Run the main demo
run:
	@echo "Running parallel execution demo..."
	python main.py

# Run all examples
test:
	@echo "Running all parallel execution examples..."
	@echo ""
	@echo "1. Main demo:"
	python main.py
	@echo ""
	@echo "2. Parallel refactoring:"
	python parallel_refactoring.py
	@echo ""
	@echo "3. Multi-tool parallel:"
	python parallel_multi_tool.py
	@echo ""
	@echo "4. Real-world scenario:"
	python parallel_real_world.py

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

# Real execution (with actual changes)
execute:
	@echo "⚠️  This will make actual changes to the codebase!"
	@echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
	@sleep 5
	python main.py --execute
