.PHONY: help run test clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

run: ## Run the code health monitoring demo
	python main.py

test: ## Run tests (none for this example)
	@echo "No tests for this example"

clean: ## Clean up generated files
	@echo "Nothing to clean"
