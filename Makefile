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

test_coverage:
	pytest --cov=prdl ./tests

test_coverage_html:
	pytest --cov=prdl --cov-report=html ./tests
