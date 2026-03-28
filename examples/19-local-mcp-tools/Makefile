.PHONY: help run setup clean up down

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

run: ## Run the local MCP tools example
	./run.sh

setup: ## Create .env from .env.example
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env - edit with your configuration"; \
	else \
		echo ".env already exists"; \
	fi

up: ## Start MCP services
	cd ../.. && docker compose up -d code2llm-mcp vallm-mcp planfile-mcp

down: ## Stop MCP services
	cd ../.. && docker compose down

clean: ## Remove generated files
	rm -f .env
