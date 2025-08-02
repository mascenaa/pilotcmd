# Makefile for PilotCmd

.PHONY: help install test lint format clean dev build

help:
	@echo "🚁 PilotCmd Development Commands"
	@echo ""
	@echo "  install     Install in development mode"
	@echo "  test        Run tests"
	@echo "  lint        Run linting checks"
	@echo "  format      Format code with black and isort"
	@echo "  clean       Clean build artifacts"
	@echo "  dev         Setup development environment"
	@echo "  build       Build package"
	@echo "  demo        Run demo commands"

install:
	pip install -e .[dev]

test:
	pytest tests/ -v --cov=pilotcmd --cov-report=html

lint:
	flake8 src/pilotcmd tests/
	mypy src/pilotcmd

format:
	black src/pilotcmd tests/
	isort src/pilotcmd tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

dev:
	python setup_dev.py

build:
	python -m build

demo:
	@echo "🎬 Running PilotCmd demo commands..."
	@echo ""
	pilotcmd "show current directory" --dry-run
	@echo ""
	pilotcmd "list Python files" --dry-run
	@echo ""
	pilotcmd "check system information" --dry-run
