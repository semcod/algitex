# Makefile for Example 33: Hybrid AutoFix

.PHONY: help run dry-run verify benchmark mechanical hybrid ollama

help:
	@echo "Example 33: Hybrid AutoFix"
	@echo ""
	@echo "Available targets:"
	@echo "  make dry-run     - Preview changes (no actual fixes)"
	@echo "  make verify      - Verify TODO tasks validity"
	@echo "  make benchmark   - Benchmark performance"
	@echo "  make mechanical  - Fix only mechanical issues (fast)"
	@echo "  make hybrid      - Full hybrid (mechanical + LLM)"
	@echo "  make ollama      - Use Ollama backend (100% offline)"
	@echo "  make run         - Run all demos"
	@echo ""
	@echo "Options:"
	@echo "  WORKERS=4        - Number of parallel workers"
	@echo "  RATE=10          - LLM calls per second"

run:
	python main.py --demo all

dry-run:
	python main.py --demo dry-run

verify:
	python main.py --demo verify

benchmark:
	python main.py --demo benchmark

mechanical:
	python main.py --demo mechanical --execute

hybrid:
	python main.py --demo hybrid --execute --workers $(or $(WORKERS),4) --rate-limit $(or $(RATE),10)

ollama:
	python main.py --demo ollama --execute --workers $(or $(WORKERS),2) --rate-limit $(or $(RATE),5)
