# Makefile for Python Flask Project
# Similar to npm scripts in JavaScript projects

.PHONY: help install install-dev lint fix format check test clean run

# Default target
help:
	@echo "Available commands:"
	@echo "  make install     - Install production dependencies"
	@echo "  make install-dev - Install development dependencies (including linters)"
	@echo "  make lint        - Run all linters (similar to npm run lint)"
	@echo "  make fix         - Auto-fix code formatting issues"
	@echo "  make format      - Format code with Black"
	@echo "  make check       - Run type checking with mypy"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Clean cache files"
	@echo "  make run         - Start Flask development server"

# Install production dependencies
install:
	pip install -r requirements.txt

# Install development dependencies (linters, formatters, etc.)
install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	@echo "✅ Development tools installed!"
	@echo "Available linters: black, flake8, isort, mypy, bandit"

# Run all linters (similar to ESLint)
lint:
	@echo "🔍 Running code quality checks..."
	@chmod +x scripts/lint.sh
	@./scripts/lint.sh

# Auto-fix code formatting issues
fix:
	@echo "🔧 Auto-fixing code issues..."
	@chmod +x scripts/fix.sh
	@./scripts/fix.sh

# Format code with Black
format:
	@echo "🎨 Formatting code with Black..."
	black .

# Sort imports
sort-imports:
	@echo "📋 Sorting imports with isort..."
	isort .

# Type checking
check:
	@echo "🔍 Running type checking with mypy..."
	mypy .

# Security check
security:
	@echo "🔒 Running security check with Bandit..."
	bandit -r . -f text

# Run tests
test:
	@echo "🧪 Running tests..."
	python -m pytest tests/ -v

# Clean cache files
clean:
	@echo "🧹 Cleaning cache files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

# Start Flask development server
run:
	@echo "🚀 Starting Flask development server..."
	python app.py

# Setup pre-commit hooks
setup-hooks:
	@echo "🪝 Setting up pre-commit hooks..."
	pre-commit install
	@echo "✅ Git hooks installed! Code will be checked on every commit."

# Run pre-commit on all files
pre-commit-all:
	pre-commit run --all-files

# Development setup (run this once)
setup: install-dev setup-hooks
	@echo "🎉 Development environment setup complete!"
	@echo "Usage:"
	@echo "  make lint  - Check code quality"
	@echo "  make fix   - Auto-fix issues"
	@echo "  make run   - Start server"
