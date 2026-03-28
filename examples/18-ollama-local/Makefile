.PHONY: help run setup clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

run: ## Run the Ollama local example
	./run.sh

setup: ## Create .env from .env.example and check Ollama
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env - edit with your configuration"; \
	else \
		echo ".env already exists"; \
	fi
	@echo "Checking Ollama..."
	@ollama --version || (echo "❌ Ollama not installed" && exit 1)
	@echo "✅ Ollama found"

clean: ## Remove generated files
	rm -f .env
