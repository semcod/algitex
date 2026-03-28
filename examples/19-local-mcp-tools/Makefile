.PHONY: help run setup start stop status logs clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

run: ## Run the example
	./run.sh

setup: ## Build and start local MCP tools
	@echo "Building local MCP tools..."
	@cd ../.. && docker compose --profile tools build
	@echo ""
	@echo "Starting MCP tools..."
	@cd ../.. && docker compose --profile tools up -d
	@echo ""
	@echo "✅ Tools started! Check status with: make status"

start: ## Start MCP tools (if already built)
	@cd ../.. && docker compose --profile tools up -d
	@echo "✅ Tools started"

stop: ## Stop MCP tools
	@cd ../.. && docker compose --profile tools down
	@echo "⏹️  Tools stopped"

status: ## Check MCP tools status
	@echo "=== MCP Tools Status ==="
	@docker ps --filter "name=-mcp" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "No MCP containers found"

logs: ## View logs from all MCP tools
	@cd ../.. && docker compose --profile tools logs -f

logs-code2llm: ## View code2llm logs
	@cd ../.. && docker compose logs -f code2llm-mcp

logs-vallm: ## View vallm logs
	@cd ../.. && docker compose logs -f vallm-mcp

clean: ## Stop and remove MCP tools
	@cd ../.. && docker compose --profile tools down -v
	@echo "🧹 Tools cleaned up"

test-code2llm: ## Test code2llm endpoint
	@echo "Testing code2llm..."
	@curl -s http://localhost:8081/health 2>/dev/null || echo "❌ code2llm not responding"

test-vallm: ## Test vallm endpoint
	@echo "Testing vallm..."
	@curl -s http://localhost:8080/health 2>/dev/null || echo "❌ vallm not responding"

test-planfile: ## Test planfile endpoint
	@echo "Testing planfile..."
	@curl -s http://localhost:8201/health 2>/dev/null || echo "❌ planfile not responding"
