.PHONY: install run test test-cov lint format clean help

# Default target
help:
	@echo "Available commands:"
	@echo "  make install         - Install dependencies using Poetry"
	@echo "  make run             - Run the application"
	@echo "  make cli             - Run the CLI interface"
	@echo "  make test            - Run tests"
	@echo "  make test-cov        - Run tests with coverage report"
	@echo "  make lint            - Run linter"
	@echo "  make format          - Format code"
	@echo "  make clean           - Clean up build artifacts"

# Install dependencies
install:
	poetry install

# Run the main application
run:
	poetry run python -m kcd_dice_game.main

# Run the CLI interface
cli:
	poetry run python -m kcd_dice_game.cli

# Run tests
test:
	poetry run pytest

# Run tests with coverage report
test-cov:
	poetry run pytest --cov=kcd_dice_game tests/
	@echo "HTML coverage report available at: htmlcov/index.html"

# Format code
format:
	poetry run black src/kcd_dice_game/ tests/

# Clean up build artifacts
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

t:
	poetry run python -m kcd_dice_game.t

# Run linter
lint:
	ruff src/kcd_dice_game/ tests/