.PHONY: help run setup up down status logs test clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

run: ## Run the example
	./run.sh

setup: ## Setup complete local stack
	@echo "Building and starting self-hosted stack..."
	@cd ../.. && make setup || docker compose --profile tools build

up: ## Start all services
	@echo "Starting self-hosted stack..."
	@cd ../.. && docker compose --profile tools up -d
	@echo ""
	@echo "✅ Stack started!"
	@echo "Services:"
	@echo "  - code2llm-mcp: http://localhost:8081"
	@echo "  - vallm-mcp:    http://localhost:8080"
	@echo "  - planfile-mcp: http://localhost:8201"
	@echo "  - aider-mcp:    http://localhost:3000"
	@echo "  - proxym:       http://localhost:4000"
	@echo ""
	@echo "Check status: make status"

down: ## Stop all services
	@cd ../.. && docker compose --profile tools down
	@echo "⏹️  Stack stopped"

status: ## Check all services status
	@echo "=== Self-Hosted Stack Status ==="
	@echo ""
	@docker ps --filter "name=-mcp\|proxym\|redis" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "No services running"

logs: ## View all logs
	@cd ../.. && docker compose --profile tools logs -f

logs-%: ## View specific service logs (e.g., logs-code2llm)
	@cd ../.. && docker compose logs -f $*

test: ## Test all endpoints
	@echo "Testing endpoints..."
	@echo ""
	@echo "code2llm-mcp (8081):"
	@curl -s http://localhost:8081/health 2>/dev/null && echo " ✅" || echo " ❌"
	@echo "vallm-mcp (8080):"
	@curl -s http://localhost:8080/health 2>/dev/null && echo " ✅" || echo " ❌"
	@echo "planfile-mcp (8201):"
	@curl -s http://localhost:8201/health 2>/dev/null && echo " ✅" || echo " ❌"
	@echo "aider-mcp (3000):"
	@curl -s http://localhost:3000/health 2>/dev/null && echo " ✅" || echo " ❌"
	@echo "proxym (4000):"
	@curl -s http://localhost:4000/health 2>/dev/null && echo " ✅" || echo " ❌"

clean: ## Clean everything (DANGER: removes data)
	@cd ../.. && docker compose --profile tools down -v --rmi local
	@echo "🧹 Stack cleaned (volumes removed)"

restart: down up ## Restart all services

build: ## Rebuild all images
	@cd ../.. && docker compose --profile tools build --no-cache
	@echo "🔨 Images rebuilt"
