.PHONY: run setup proxy test fix stop clean

run: setup
	@echo ""
	@echo "=== LiteLLM Proxy + Ollama Workflow ==="
	@echo ""
	@echo "Step 1: Checking prerequisites..."
	@python main.py
	@echo ""
	@echo "Step 2: Run these commands in separate terminals:"
	@echo ""
	@echo "Terminal 1 - Start proxy:"
	@echo "  make proxy"
	@echo ""
	@echo "Terminal 2 - Fix code:"
	@echo "  make fix"
	@echo ""

setup:
	@echo "Checking prerequisites..."
	@python main.py || true

proxy:
	@echo "Starting LiteLLM proxy on port 4000..."
	@echo "Press Ctrl+C to stop"
	litellm --config litellm_config.yaml --port 4000

test:
	@echo "Testing proxy connection..."
	@curl -s http://localhost:4000/v1/models | python -m json.tool || echo "Proxy not running. Start with: make proxy"

fix:
	@echo "Running auto_fix.py..."
	python auto_fix.py

stop:
	@echo "Stopping LiteLLM proxy..."
	@pkill -f "litellm --config litellm_config.yaml" 2>/dev/null || echo "Proxy not running"

clean:
	@echo "Cleaning up..."
	@rm -f TODO.md
	@rm -f buggy_code.py.fixed
	@echo "✅ Cleaned"
