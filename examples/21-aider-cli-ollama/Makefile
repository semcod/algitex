.PHONY: run setup todo fix clean status

run:
	python main.py

setup:
	@echo "Checking prerequisites..."
	@python -c "from algitex import Project; p = Project('.'); p.print_service_status()"

todo:
	@echo "Generating TODO.md..."
	@python -c "from algitex import Project; p = Project('.'); r = p.generate_todo(); print(f'Created {r[\"filename\"]} with {r[\"count\"]} issues')"

fix:
	@echo "Fixing issues with algitex..."
	@python -c "from algitex import Project; p = Project('.'); p.fix_issues()"

clean:
	@echo "Cleaning up..."
	@rm -f TODO.md
	@git checkout buggy_code.py 2>/dev/null || true
	@echo "✅ Cleaned"

status:
	@python main.py
