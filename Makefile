# Makefile for AI Learning Platform

# Variables
DOCKER_COMPOSE = docker-compose -f docker-compose.yml -f docker-compose.dev.yml
DOCKER_COMPOSE_PROD = docker-compose -f docker-compose.yml

# Default target
all: help

# Help target
help:
	@echo "Available commands:"
	@echo "  make dev           - Start development environment"
	@echo "  make prod          - Start production environment"
	@echo "  make stop          - Stop all containers"
	@echo "  make down          - Stop and remove all containers"
	@echo "  make logs          - View logs from all services"
	@echo "  make logs-backend  - View backend logs"
	@echo "  make logs-frontend - View frontend logs"
	@echo "  make logs-db       - View database logs"
	@echo "  make shell-backend - Open shell in backend container"
	@echo "  make shell-db      - Open shell in database container"
	@echo "  make migrate       - Run database migrations"
	@echo "  make migrate-gen   - Generate new migration"
	@echo "  make test          - Run tests"
	@echo "  make clean         - Remove temporary files"

# Development
.PHONY: dev
dev:
	${DOCKER_COMPOSE} up --build

# Production
.PHONY: prod
prod:
	${DOCKER_COMPOSE_PROD} up --build -d

# Stop containers
.PHONY: stop
stop:
	${DOCKER_COMPOSE} down

# Remove containers and volumes
.PHONY: down
down:
	${DOCKER_COMPOSE} down -v

# View logs
.PHONY: logs
logs:
	${DOCKER_COMPOSE} logs -f

.PHONY: logs-backend
logs-backend:
	${DOCKER_COMPOSE} logs -f backend

.PHONY: logs-frontend
logs-frontend:
	${DOCKER_COMPOSE} logs -f frontend

.PHONY: logs-db
logs-db:
	${DOCKER_COMPOSE} logs -f db

# Shell access
.PHONY: shell-backend
shell-backend:
	${DOCKER_COMPOSE} exec backend bash

.PHONY: shell-db
shell-db:
	${DOCKER_COMPOSE} exec db psql -U postgres

# Database
.PHONY: migrate
migrate:
	${DOCKER_COMPOSE} exec backend alembic upgrade head

.PHONY: migrate-gen
migrate-gen:
	@read -p "Enter migration message: " msg; \
	${DOCKER_COMPOSE} exec backend alembic revision --autogenerate -m "$$msg"

# Testing
.PHONY: test
test:
	${DOCKER_COMPOSE} exec backend pytest tests/ -v --cov=app

# Clean up
.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	rm -rf .coverage htmlcov/

# Format code
.PHONY: format
format:
	${DOCKER_COMPOSE} exec backend black .
	${DOCKER_COMPOSE} exec backend isort .

# Lint code
.PHONY: lint
lint:
	${DOCKER_COMPOSE} exec backend black --check .
	${DOCKER_COMPOSE} exec backend isort --check-only .
	${DOCKER_COMPOSE} exec backend flake8 .
	${DOCKER_COMPOSE} exec backend mypy .
