.PHONY: install run clean test test-cov lint format venv help activate activate_windows

# Default target
help:
	@echo "Available commands:"
	@echo "  make install         - Install dependencies"
	@echo "  make run            - Run the application"
	@echo "  make test           - Run tests"
	@echo "  make test-cov       - Run tests with coverage report"
	@echo "  make lint           - Run linter"
	@echo "  make format         - Format code"
	@echo "  make clean          - Clean up build artifacts"
	@echo "  make venv           - Create virtual environment"
	@echo "  make activate       - Activate virtual environment (Unix/macOS)"
	@echo "  make activate_windows - Activate virtual environment (Windows)"

# Create virtual environment
venv:
	python3 -m venv venv
	@echo "Virtual environment created. Activate it with:"
	@echo "  make activate       # On Unix/macOS"
	@echo "  make activate_windows # On Windows"

# Activate virtual environment (Unix/macOS)
activate:
	@echo "Activating virtual environment..."
	@echo "Run this command in your shell:"
	@echo "source venv/bin/activate"

# Activate virtual environment (Windows)
activate-windows:
	@echo "Activating virtual environment..."
	@echo "Run this command in your shell:"
	@echo ".\\venv\\Scripts\\activate"

# Install dependencies
install:
	python3 -m pip install --upgrade pip
	pip install -r requirements.txt

# Run the application
run:
	python src/main.py

t:
	python src/t.py

# Run tests
test:
	python3 -m pytest tests/

# Run tests with coverage
test-cov:
	python3 -m pytest --cov=src tests/

# Run linter
lint:
	flake8 src/
	pylint src/

# Format code
format:
	black src/
	isort src/

# Clean up
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete 
