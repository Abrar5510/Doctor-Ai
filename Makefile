.PHONY: help install dev-install setup start stop seed test clean docs docker-up docker-down docker-restart docker-logs docker-ps docker-clean

help:
	@echo "Medical Symptom Constellation Mapper - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install       - Install production dependencies"
	@echo "  make dev-install   - Install development dependencies"
	@echo "  make setup         - Complete setup (install + docker + seed)"
	@echo ""
	@echo "Service Management:"
	@echo "  make start         - Start all services"
	@echo "  make stop          - Stop all services"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-up     - Start Docker services (Qdrant, Postgres, Redis)"
	@echo "  make docker-up-all - Start all Docker services including API"
	@echo "  make docker-down   - Stop Docker services"
	@echo "  make docker-restart- Restart Docker services"
	@echo "  make docker-logs   - View Docker container logs"
	@echo "  make docker-ps     - Show running Docker containers"
	@echo "  make docker-clean  - Remove all containers, volumes, and images"
	@echo "  make docker-health - Check health status of all containers"
	@echo ""
	@echo "Database:"
	@echo "  make seed          - Seed database with sample data"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test          - Run tests"
	@echo "  make test-api      - Test API endpoints"
	@echo "  make clean         - Clean up generated files"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs          - Open API documentation"
	@echo "  make logs          - View application logs"
	@echo ""

install:
	pip install -r requirements.txt

dev-install: install
	pip install pytest pytest-asyncio pytest-cov black flake8 mypy

setup: install
	@echo "Setting up Doctor AI..."
	@command -v docker >/dev/null 2>&1 || { echo "Error: Docker is not installed. Please install Docker first."; exit 1; }
	@command -v docker compose >/dev/null 2>&1 || command -v docker-compose >/dev/null 2>&1 || { echo "Error: Docker Compose is not installed."; exit 1; }
	@if command -v docker compose >/dev/null 2>&1; then \
		docker compose up -d; \
	else \
		docker-compose up -d; \
	fi
	@echo "Waiting for services to become healthy..."
	@sleep 15
	@echo "Seeding database..."
	python scripts/seed_data.py
	@echo "Setup complete!"

start:
	@echo "Starting services..."
	@if command -v docker compose >/dev/null 2>&1; then \
		docker compose up -d; \
	else \
		docker-compose up -d; \
	fi
	@echo "Waiting for services to become healthy..."
	@sleep 5
	@echo "Starting API server..."
	python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

stop:
	@echo "Stopping services..."
	@if command -v docker compose >/dev/null 2>&1; then \
		docker compose down; \
	else \
		docker-compose down; \
	fi

# Docker-specific commands
docker-up:
	@echo "Starting Docker services (databases only)..."
	@if command -v docker compose >/dev/null 2>&1; then \
		docker compose up -d qdrant postgres redis; \
	else \
		docker-compose up -d qdrant postgres redis; \
	fi
	@echo "Waiting for services to become healthy..."
	@sleep 10
	@echo "Services started! Use 'make docker-health' to check status."

docker-up-all:
	@echo "Starting all Docker services (including API)..."
	@if command -v docker compose >/dev/null 2>&1; then \
		docker compose --profile full up -d; \
	else \
		docker-compose --profile full up -d; \
	fi
	@echo "Waiting for services to become healthy..."
	@sleep 15
	@echo "All services started! Use 'make docker-health' to check status."

docker-down:
	@echo "Stopping Docker services..."
	@if command -v docker compose >/dev/null 2>&1; then \
		docker compose down; \
	else \
		docker-compose down; \
	fi
	@echo "Docker services stopped."

docker-restart:
	@echo "Restarting Docker services..."
	@if command -v docker compose >/dev/null 2>&1; then \
		docker compose restart; \
	else \
		docker-compose restart; \
	fi
	@echo "Docker services restarted."

docker-logs:
	@echo "Showing Docker container logs (press Ctrl+C to exit)..."
	@if command -v docker compose >/dev/null 2>&1; then \
		docker compose logs -f; \
	else \
		docker-compose logs -f; \
	fi

docker-ps:
	@echo "Running Docker containers:"
	@docker ps --filter "name=doctor-ai" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

docker-health:
	@echo "Health status of Docker services:"
	@echo "=================================="
	@docker ps --filter "name=doctor-ai" --format "table {{.Names}}\t{{.Status}}" || echo "No containers running"
	@echo ""
	@echo "Checking connectivity:"
	@echo "  Qdrant:    curl -s http://localhost:6333/ > /dev/null && echo '✓ Connected' || echo '✗ Not available'"
	@echo "  Postgres:  pg_isready -h localhost -U doctor_ai 2>/dev/null && echo '✓ Connected' || echo '✗ Not available'"
	@echo "  Redis:     redis-cli -h localhost ping 2>/dev/null | grep -q PONG && echo '✓ Connected' || echo '✗ Not available'"

docker-clean:
	@echo "WARNING: This will remove all Doctor AI containers, volumes, and images!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		if command -v docker compose >/dev/null 2>&1; then \
			docker compose down -v --rmi all; \
		else \
			docker-compose down -v --rmi all; \
		fi; \
		echo "Docker resources cleaned."; \
	else \
		echo "Cancelled."; \
	fi

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
