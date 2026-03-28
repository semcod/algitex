.PHONY: help run setup check clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

run: ## Run the example
	./run.sh

setup: check ## Setup environment (pull models)
	@echo "Setting up Ollama..."
	@command -v ollama >/dev/null 2>&1 || { echo "Ollama not found. Install from https://ollama.com"; exit 1; }
	@echo "Pulling qwen2.5-coder:7b (this may take a while)..."
	-ollama pull qwen2.5-coder:7b 2>/dev/null || echo "⚠️  Could not pull model (Ollama may not be running)"
	@echo ""
	@echo "Setup complete!"
	@echo "Start Ollama with: ollama serve"

check: ## Check Ollama status
	@echo "Checking Ollama..."
	@command -v ollama >/dev/null 2>&1 && echo "✅ Ollama CLI found" || echo "❌ Ollama CLI not found"
	@ollama list >/dev/null 2>&1 && echo "✅ Ollama service running" || echo "❌ Ollama service not running (start with: ollama serve)"

clean: ## Clean up (nothing to clean for local example)
	@echo "Nothing to clean for local Ollama example"

models: ## List available models
	@ollama list 2>/dev/null || echo "Ollama not running. Start with: ollama serve"
