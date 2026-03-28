.PHONY: run setup todo fix clean status

run: status
	@echo ""
	@echo "=== Full Aider + Ollama Workflow Demo ==="
	@echo ""
	@echo "Step 1: Analyzing and creating TODO.md..."
	python -c "from algitex.tools.analysis import Analyzer; from algitex.tools.todo_parser import TodoParser; import os; a = Analyzer('.'); r = a.full(); t = TodoParser('TODO.md'); t.from_analysis(r)" 2>/dev/null || echo "⚠️  Using sample TODO.md"; python generate_todo.py 2>/dev/null || true
	@echo ""
	@echo "Step 2: Reviewing TODO.md..."
	@head -30 TODO.md || echo "No TODO.md found"
	@echo ""
	@echo "Step 3: Running auto_fix.py (dry-run)..."
	python auto_fix.py --dry-run
	@echo ""
	@echo "✅ Demo complete!"
	@echo ""
	@echo "To actually fix issues:"
	@echo "  python auto_fix.py           # Fix all"
	@echo "  python auto_fix.py --limit 5  # Fix first 5"

setup:
	@echo "Checking prerequisites..."
	@python main.py

todo:
	@echo "Running: algitex analyze && generate TODO"
	algitex analyze || python generate_todo.py

fix:
	@echo "Running: python auto_fix.py"
	python auto_fix.py

clean:
	@echo "Cleaning up..."
	@rm -f TODO.md
	@git checkout buggy_code.py 2>/dev/null || true
	@echo "✅ Cleaned"

status:
	@python main.py
