.PHONY: run setup todo batch clean

run: setup
	@python main.py

setup:
	@echo "Checking prerequisites..."
	@python main.py || true

todo:
	prefact -a

batch:
	python batch_fix.py

clean:
	@rm -f TODO.md
	@git checkout buggy_code.py 2>/dev/null || true
