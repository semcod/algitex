.PHONY: run setup todo fix clean status

run: status
	@echo ""
	@echo "=== Full Aider + Ollama Workflow Demo ==="
	@echo ""
	@echo "Step 1: Creating TODO.md with prefact -a..."
	prefact -a || echo "⚠️  prefact failed, using sample TODO.md"
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
	@echo "Running: prefact -a"
	prefact -a

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
