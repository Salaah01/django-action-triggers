.PHONY: test
test:
	pytest

.PHONY: test-cov
test-cov:
	pytest --cov=. || true
	coverage html

lint: **/*.py
	ruff check .

format: **/*.py
	ruff check . --fix
	isort .

typecheck: **/*.py
	mypy .
