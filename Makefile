# Makefile for the siftingio Python SDK.
#
# Publishing reads the PyPI token from the environment — never hardcode it here.
# Set it for the session (don't commit it anywhere):
#
#     export TWINE_PASSWORD='pypi-...'      # the token value
#     make publish-test                     # upload to TestPyPI first
#     make publish                          # upload to real PyPI
#
# TWINE_USERNAME defaults to __token__ (correct for API-token auth).

PY        := .venv/bin/python
PIP       := .venv/bin/pip
VENV      := .venv

export TWINE_USERNAME ?= __token__

.PHONY: help venv install test lint typecheck check build dist-check \
        publish-test publish clean

help:
	@echo "Targets:"
	@echo "  venv         Create the virtualenv (.venv)"
	@echo "  install      Install the package + dev tools (editable)"
	@echo "  test         Run the test suite"
	@echo "  lint         Run ruff"
	@echo "  typecheck    Run mypy (strict)"
	@echo "  check        lint + typecheck + test"
	@echo "  build        Build sdist + wheel into dist/"
	@echo "  dist-check   Validate built artifacts with twine check"
	@echo "  publish-test Upload to TestPyPI  (needs TWINE_PASSWORD)"
	@echo "  publish      Upload to PyPI      (needs TWINE_PASSWORD)"
	@echo "  clean        Remove build artifacts and caches"

$(VENV):
	python3 -m venv $(VENV)

venv: $(VENV)

install: venv
	$(PIP) install -e ".[dev]"

test:
	$(PY) -m pytest -q

lint:
	$(PY) -m ruff check src

typecheck:
	$(PY) -m mypy src/siftingio

check: lint typecheck test

build: clean
	$(PY) -m build

dist-check:
	$(PY) -m twine check dist/*

# Gated on a green build + metadata check so a bad artifact never ships.
publish-test: check build dist-check
	@test -n "$$TWINE_PASSWORD" || { echo "ERROR: set TWINE_PASSWORD to your TestPyPI token"; exit 1; }
	$(PY) -m twine upload --repository testpypi dist/*

publish: check build dist-check
	@test -n "$$TWINE_PASSWORD" || { echo "ERROR: set TWINE_PASSWORD to your PyPI token"; exit 1; }
	$(PY) -m twine upload dist/*

clean:
	rm -rf dist build *.egg-info src/*.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
