.PHONY: help run setup clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

run: ## Run the pipeline demo
	./run.sh

setup: ## Create .env from .env.example (optional)
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env - edit it if you have proxym running"; \
	else \
		echo ".env already exists"; \
	fi

clean: ## Remove generated files
	rm -f .env
