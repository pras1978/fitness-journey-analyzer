.PHONY: help env-pip env-setup install-dev test lint format run-api run-frontend run-all clean

help:
	@echo "Fitness Journey Analyzer - Available Commands"
	@echo ""
	@echo "Environment Setup:"
	@echo "  make env-pip         Create pip venv environment"
	@echo "  make env-setup       Set up .env configuration file"
	@echo ""
	@echo "Installation:"
	@echo "  make install-dev     Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make test            Run tests with pytest"
	@echo "  make lint            Run code linters (black, flake8, mypy)"
	@echo "  make format          Format code with black and isort"
	@echo ""
	@echo "Running Application:"
	@echo "  make run-api         Start FastAPI backend server"
	@echo "  make run-frontend    Start Streamlit frontend"
	@echo "  make run-all         Start both API and frontend"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean           Remove cache files and build artifacts"
	@echo ""

# Environment Setup
env-pip:
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip setuptools wheel
	@echo ""
	@echo "✓ Virtual environment created!"
	@echo "✓ Activate with: source venv/bin/activate"

env-setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✓ Created .env file - edit with your settings"; \
	else \
		echo "ℹ .env already exists"; \
	fi

# Installation
install-dev:
	pip install -r requirements-dev.txt
	@echo "✓ Development dependencies installed"

# Code Quality
test:
	pytest -v --tb=short

test-cov:
	pytest --cov=backend --cov-report=html --cov-report=term

lint:
	@echo "Running code quality checks..."
	black --check .
	flake8 backend/ frontend/ ml/
	mypy backend/
	@echo "✓ All checks passed!"

format:
	@echo "Formatting code..."
	black .
	isort .
	@echo "✓ Code formatted!"

# Running Application
run-api:
	uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	streamlit run frontend/streamlit_app.py

run-all:
	@echo "Starting both API and frontend..."
	@echo "API: http://localhost:8000 (docs: http://localhost:8000/docs)"
	@echo "Frontend: http://localhost:8501"
	@echo ""
	@echo "Run these commands in separate terminals:"
	@echo "  Terminal 1: make run-api"
	@echo "  Terminal 2: make run-frontend"

# Cleanup
clean:
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name 'htmlcov' -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleaned up cache and build artifacts"

.DEFAULT_GOAL := help