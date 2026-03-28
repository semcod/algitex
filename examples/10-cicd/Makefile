.PHONY: help run clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

run: ## Run the CI/CD demo
	./run.sh

clean: ## Remove generated files
	rm -rf sample-ci-project/
	rm -rf complete-ci-project/
	rm -rf multi-platform-project/
