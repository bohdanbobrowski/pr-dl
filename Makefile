.SILENT: format, check, test, integration_test, unit_test, unit_coverage, unit_coverage_html, clear_win
.PHONY: format, check, test, integration_test, unit_test, unit_coverage, unit_coverage_html, clear_win

precommit: format check test

format:
	ruff format .
	ruff check . --fix

check:
	mypy .

test:
	pytest tests
