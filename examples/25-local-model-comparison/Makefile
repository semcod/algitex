.PHONY: run setup benchmark results clean

run:
	@python main.py

setup:
	@echo "Checking available models..."
	@curl -s http://localhost:11434/api/tags | python -m json.tool | grep '"name"' || echo "Ollama not running"

benchmark:
	python benchmark.py

results:
	@ls -t benchmark_*.json 2>/dev/null | head -1 | xargs cat || echo "No results found. Run: make benchmark"

clean:
	@rm -f benchmark_*.json
