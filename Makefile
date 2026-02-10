.PHONY: help build test lint clean install

help:
	@echo "cvewatch Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  build    - Build package"
	@echo "  test     - Run tests"
	@echo "  lint     - Run linter (ruff)"
	@echo "  clean    - Remove build artifacts"
	@echo "  install  - Install package in editable mode"

build:
	python -m build

test:
	pytest tests/ -v

lint:
	ruff check cvewatch/

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

install:
	pip install -e ".[dev]"
