.PHONY: help install test lint docker-up docker-down docker-test clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Development ───────────────────────────────────────

install: ## Install in dev mode
	pip install -e ".[dev]"

test: ## Run all tests
	python -m pytest tests/ -v --tb=short

test-fast: ## Run tests without slow integration tests
	python -m pytest tests/ -v --tb=short -m "not slow"

test-cov: ## Run tests with coverage
	python -m pytest tests/ -v --cov=algitex --cov-report=html --cov-report=term

lint: ## Run linting
	ruff check src/ tests/
	ruff format --check src/ tests/

format: ## Auto-format code
	ruff format src/ tests/

typecheck: ## Run mypy
	mypy src/algitex/

# ── Docker ────────────────────────────────────────────

docker-build: ## Build algitex image
	docker build -t algitex:latest .

docker-test: ## Run tests inside Docker
	docker build --target test -t algitex:test .

docker-up: ## Start full stack (proxym + ollama + redis)
	docker compose up -d
	@echo "\n✅ Stack running. proxym at http://localhost:4000"
	@echo "   Run: docker compose exec algitex algitex status"

docker-tools: ## Start with MCP tools (aider, github)
	docker compose --profile tools up -d

docker-full: ## Start everything (+ langfuse monitoring)
	docker compose --profile full up -d

docker-down: ## Stop all services
	docker compose --profile full down

docker-logs: ## Follow proxym logs
	docker compose logs -f proxym

docker-shell: ## Open shell in algitex container
	docker compose exec algitex bash

# ── Examples ──────────────────────────────────────────

example-quick: ## Run quickstart example
	python examples/01_quickstart.py

example-algo: ## Run algo loop example
	python examples/02_algo_loop.py

example-workflow: ## Run workflow example
	algitex workflow run examples/workflows/health-check.md

example-pipeline: ## Run pipeline example
	python examples/03_pipeline.py

# ── Maintenance ───────────────────────────────────────

clean: ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info src/*.egg-info .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

release: ## Build and check package
	pip install build twine
	python -m build
	twine check dist/*
