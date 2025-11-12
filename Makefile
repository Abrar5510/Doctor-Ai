.PHONY: help install dev-install setup start stop seed test clean docs

help:
	@echo "Medical Symptom Constellation Mapper - Available Commands:"
	@echo ""
	@echo "  make install       - Install production dependencies"
	@echo "  make dev-install   - Install development dependencies"
	@echo "  make setup         - Complete setup (install + docker + seed)"
	@echo "  make start         - Start all services"
	@echo "  make stop          - Stop all services"
	@echo "  make seed          - Seed database with sample data"
	@echo "  make test          - Run tests"
	@echo "  make test-api      - Test API endpoints"
	@echo "  make clean         - Clean up generated files"
	@echo "  make docs          - Open API documentation"
	@echo "  make logs          - View application logs"
	@echo ""

install:
	pip install -r requirements.txt

dev-install: install
	pip install pytest pytest-asyncio pytest-cov black flake8 mypy

setup: install
	@echo "Setting up Doctor AI..."
	docker-compose up -d
	@echo "Waiting for services to start..."
	sleep 10
	@echo "Seeding database..."
	python scripts/seed_data.py
	@echo "Setup complete!"

start:
	@echo "Starting services..."
	docker-compose up -d
	@echo "Starting API server..."
	python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

stop:
	@echo "Stopping services..."
	docker-compose down

seed:
	python scripts/seed_data.py

test:
	pytest tests/ -v --cov=src --cov-report=html

test-api:
	python scripts/test_api.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

docs:
	@echo "Opening API documentation..."
	@echo "Swagger UI: http://localhost:8000/docs"
	@echo "ReDoc: http://localhost:8000/redoc"
	python -c "import webbrowser; webbrowser.open('http://localhost:8000/docs')"

logs:
	tail -f logs/app_*.log
