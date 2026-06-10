# IBKR Analytics - Makefile
# Usage: make <target>

.PHONY: help install test test-cov lint format clean serve-backend serve-frontend serve-all typecheck pre-commit

# Default target
help:
	@echo "IBKR Analytics - Available Commands:"
	@echo ""
	@echo "  make install         Install dependencies"
	@echo "  make test           Run tests"
	@echo "  make test-cov       Run tests with coverage"
	@echo "  make lint           Run linters (flake8, black check)"
	@echo "  make format         Format code (black, isort)"
	@echo "  make typecheck      Run type checker (mypy)"
	@echo "  make clean          Clean cache files"
	@echo "  make serve-backend  Start backend server (port 8000)"
	@echo "  make serve-frontend Start frontend server (port 8050)"
	@echo "  make serve-all      Start both servers"
	@echo "  make pre-commit     Run pre-commit hooks"

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	python -m pytest tests/ -v

# Run tests with coverage
test-cov:
	python -m pytest tests/unit/ --cov=core --cov=dashboard.backend --cov=alpha_research.portfolio --cov=alpha_research.backtests --cov=alpha_research.execution --cov-report=term-missing

# Run linters
lint:
	@echo "Running flake8..."
	flake8 core/ dashboard/ alpha_research/ --max-line-length=120 --ignore=E501,W503,E203
	@echo ""
	@echo "Running black check..."
	black --check core/ dashboard/ alpha_research/ --diff

# Format code
format:
	@echo "Running black..."
	black core/ dashboard/ alpha_research/
	@echo "Running isort..."
	isort core/ dashboard/ alpha_research/ --profile black

# Type checking
typecheck:
	mypy core/ dashboard/backend/ --ignore-missing-imports

# Clean cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "coverage.json" -delete 2>/dev/null || true

# Start backend server (run from repo root so absolute imports resolve)
serve-backend:
	python -m uvicorn dashboard.backend.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend server (PYTHONPATH=. so `import dashboard...` resolves)
serve-frontend:
	PYTHONPATH=. python dashboard/frontend/app.py

# Start both servers (in background)
serve-all:
	@echo "Starting backend on port 8000..."
	python -m uvicorn dashboard.backend.main:app --reload --host 0.0.0.0 --port 8000 &
	@echo "Starting frontend on port 8050..."
	PYTHONPATH=. python dashboard/frontend/app.py &

# Run pre-commit hooks
pre-commit:
	pre-commit run --all-files
