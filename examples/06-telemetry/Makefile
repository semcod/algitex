.PHONY: help run setup clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

run: ## Run the telemetry demo
	./run.sh

setup: ## Create .env from .env.example (optional)
	@if [ ! -f .env ]; then \
		cp .env.example .env 2>/dev/null || echo "No .env.example found"; \
	else \
		echo ".env already exists"; \
	fi

clean: ## Remove generated files
	rm -f .env
