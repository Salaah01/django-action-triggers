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

type-check: **/*.py
	mypy .

ci-install-deps-global:
	python -m pip install --upgrade pip
	pip install poetry
	poetry config virtualenvs.create false
	poetry install --no-root --all-extras
