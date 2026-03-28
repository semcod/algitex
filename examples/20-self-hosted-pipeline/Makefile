.PHONY: help run setup clean test status

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

run: ## Run the self-hosted pipeline example
	./run.sh

setup: ## Create .env from .env.example and check dependencies
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env - edit with your configuration"; \
	else \
		echo ".env already exists"; \
	fi
	@echo "Checking Docker..."
	@docker --version || (echo "❌ Docker not installed" && exit 1)
	@echo "Checking Docker Compose..."
	@docker compose version || (echo "❌ Docker Compose not installed" && exit 1)
	@echo "✅ All dependencies OK"

test: ## Test MCP services connectivity
	@echo "Testing MCP services..."
	@curl -s http://localhost:8081/health && echo " ✅ code2llm"
	@curl -s http://localhost:8080/health && echo " ✅ vallm"
	@curl -s http://localhost:8201/health && echo " ✅ planfile"
	@curl -s http://localhost:4000/health && echo " ✅ proxym"

status: ## Check stack status
	@echo "=== Self-Hosted Stack Status ==="
	@docker compose ps 2>/dev/null || echo "Stack not running. Run: make up"

up: ## Start the MCP stack
	cd ../.. && docker compose --profile tools up -d code2llm-mcp vallm-mcp planfile-mcp proxym

down: ## Stop the MCP stack
	cd ../.. && docker compose down

clean: ## Remove generated files
	rm -f .env
	@echo "Cleaned up"
