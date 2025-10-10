# Orc Ray Agent - Makefile
# Comprehensive commands for development, testing, and deployment

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Project paths
API_AGENT := api-agent
PLUGIN_REGISTRY := plugin-registry
RAY_WORKER := ray-worker
PLUGINS := plugins

# Python
PYTHON := python3
PIP := pip3
VENV := .venv
PYTEST := pytest

# Docker
DOCKER_COMPOSE := docker-compose
DOCKER := docker

.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)Orc Ray Agent - Available Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Setup & Installation:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E 'install|setup|venv|env' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Docker Operations:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E 'up|down|start|stop|restart|build|logs|ps|docker' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Database Operations:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E 'migrate|db-|create-admin' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E 'dev-' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E 'test|coverage' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Code Quality:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E 'format|lint|quality|pre-commit' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Plugin Management:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E 'plugin' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Monitoring & Health:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E 'health|status|dashboard' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Utilities:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E 'clean|secret' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ============================================================================
# Setup & Installation
# ============================================================================

.PHONY: venv
venv: ## Create Python virtual environment
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)✓ Virtual environment created$(NC)"
	@echo "Activate with: source $(VENV)/bin/activate"

.PHONY: install
install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	$(PIP) install uv
	cd $(API_AGENT) && uv pip install .
	cd $(PLUGIN_REGISTRY) && uv pip install .
	cd $(RAY_WORKER) && uv pip install .
	@echo "$(GREEN)✓ Production dependencies installed$(NC)"

.PHONY: install-dev
install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(PIP) install uv
	cd $(API_AGENT) && uv pip install -e ".[dev]"
	cd $(PLUGIN_REGISTRY) && uv pip install -e ".[dev]"
	cd $(RAY_WORKER) && uv pip install -e ".[dev]"
	@echo "$(GREEN)✓ Development dependencies installed$(NC)"

.PHONY: env
env: ## Create .env file from example
	@if [ ! -f .env ]; then \
		echo "$(BLUE)Creating .env file...$(NC)"; \
		cp .env.example .env; \
		echo "$(GREEN)✓ .env file created$(NC)"; \
		echo "$(YELLOW)⚠ Please update .env with your settings$(NC)"; \
	else \
		echo "$(YELLOW).env file already exists$(NC)"; \
	fi

.PHONY: pre-commit-install
pre-commit-install: ## Install pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	pre-commit install
	@echo "$(GREEN)✓ Pre-commit hooks installed$(NC)"

.PHONY: setup
setup: env venv install-dev pre-commit-install ## Complete initial setup
	@echo "$(GREEN)✓ Setup complete!$(NC)"
	@echo "Next steps:"
	@echo "  1. Activate venv: source $(VENV)/bin/activate"
	@echo "  2. Update .env with your settings"
	@echo "  3. Run: make up"

.PHONY: clean-install
clean-install: clean install-dev ## Clean and reinstall all dependencies
	@echo "$(GREEN)✓ Clean install complete$(NC)"

# ============================================================================
# Docker Operations
# ============================================================================

.PHONY: up start
up: ## Start all services with docker-compose
	@echo "$(BLUE)Starting all services...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✓ All services started$(NC)"
	@echo "API Docs: http://localhost:5900/docs"
	@echo "Dashboard: http://localhost:5900/dashboard"

start: up ## Alias for 'up'

.PHONY: down stop
down: ## Stop all services
	@echo "$(BLUE)Stopping all services...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ All services stopped$(NC)"

stop: down ## Alias for 'down'

.PHONY: restart
restart: down up ## Restart all services
	@echo "$(GREEN)✓ All services restarted$(NC)"

.PHONY: build
build: ## Build all Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	$(DOCKER_COMPOSE) build
	@echo "$(GREEN)✓ Docker images built$(NC)"

.PHONY: rebuild
rebuild: ## Rebuild all Docker images without cache
	@echo "$(BLUE)Rebuilding Docker images...$(NC)"
	$(DOCKER_COMPOSE) build --no-cache
	@echo "$(GREEN)✓ Docker images rebuilt$(NC)"

.PHONY: logs
logs: ## View logs from all services
	$(DOCKER_COMPOSE) logs -f

.PHONY: logs-api
logs-api: ## View API agent logs
	$(DOCKER_COMPOSE) logs -f api-agent

.PHONY: logs-registry
logs-registry: ## View plugin registry logs
	$(DOCKER_COMPOSE) logs -f plugin-registry

.PHONY: logs-worker
logs-worker: ## View ray worker logs
	$(DOCKER_COMPOSE) logs -f ray-worker

.PHONY: logs-postgres
logs-postgres: ## View postgres logs
	$(DOCKER_COMPOSE) logs -f postgres

.PHONY: logs-rabbitmq
logs-rabbitmq: ## View rabbitmq logs
	$(DOCKER_COMPOSE) logs -f rabbitmq

.PHONY: ps
ps: ## Show running containers
	$(DOCKER_COMPOSE) ps

.PHONY: clean-docker
clean-docker: ## Remove all containers and volumes
	@echo "$(RED)Warning: This will remove all containers and volumes$(NC)"
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	$(DOCKER_COMPOSE) down -v
	@echo "$(GREEN)✓ Containers and volumes removed$(NC)"

# ============================================================================
# Database Operations
# ============================================================================

.PHONY: migrate
migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	$(DOCKER_COMPOSE) exec api-agent alembic upgrade head
	@echo "$(GREEN)✓ Migrations complete$(NC)"

.PHONY: migrate-local
migrate-local: ## Run migrations locally (not in Docker)
	@echo "$(BLUE)Running database migrations locally...$(NC)"
	cd $(API_AGENT) && alembic upgrade head
	@echo "$(GREEN)✓ Migrations complete$(NC)"

.PHONY: migration
migration: ## Create new database migration (usage: make migration msg="description")
	@if [ -z "$(msg)" ]; then \
		echo "$(RED)Error: Please provide migration message$(NC)"; \
		echo "Usage: make migration msg=\"your message\""; \
		exit 1; \
	fi
	@echo "$(BLUE)Creating migration: $(msg)$(NC)"
	cd $(API_AGENT) && alembic revision --autogenerate -m "$(msg)"
	@echo "$(GREEN)✓ Migration created$(NC)"

.PHONY: migrate-down
migrate-down: ## Rollback last migration
	@echo "$(BLUE)Rolling back last migration...$(NC)"
	$(DOCKER_COMPOSE) exec api-agent alembic downgrade -1
	@echo "$(GREEN)✓ Rollback complete$(NC)"

.PHONY: db-shell
db-shell: ## Open PostgreSQL shell
	$(DOCKER_COMPOSE) exec postgres psql -U user -d plugindb

.PHONY: db-reset
db-reset: ## Reset database (WARNING: destroys all data)
	@echo "$(RED)Warning: This will destroy all database data$(NC)"
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	$(DOCKER_COMPOSE) down -v postgres
	$(DOCKER_COMPOSE) up -d postgres
	@sleep 5
	@$(MAKE) migrate
	@echo "$(GREEN)✓ Database reset complete$(NC)"

.PHONY: create-admin
create-admin: ## Create admin user (interactive)
	@echo "$(BLUE)Creating admin user...$(NC)"
	$(DOCKER_COMPOSE) exec api-agent python -c "from app.core.db import SessionLocal; from app.models.user import User; from app.core.security import get_password_hash; db = SessionLocal(); admin = User(email=input('Email: '), hashed_password=get_password_hash(input('Password: ')), full_name=input('Full name: '), is_active=True); db.add(admin); db.commit(); print('✓ Admin user created')"

# ============================================================================
# Development
# ============================================================================

.PHONY: dev
dev: ## Start only infrastructure (postgres, rabbitmq, ray-head)
	@echo "$(BLUE)Starting development infrastructure...$(NC)"
	$(DOCKER_COMPOSE) up -d postgres rabbitmq ray-head
	@echo "$(GREEN)✓ Infrastructure started$(NC)"
	@echo "$(YELLOW)Run services locally:$(NC)"
	@echo "  make dev-api"
	@echo "  make dev-registry"
	@echo "  make dev-worker"

.PHONY: dev-api
dev-api: ## Run API agent locally with hot reload
	@echo "$(BLUE)Starting API agent locally...$(NC)"
	cd $(API_AGENT) && uvicorn app.main:app --reload --host 0.0.0.0 --port 5900

.PHONY: dev-registry
dev-registry: ## Run plugin registry locally with hot reload
	@echo "$(BLUE)Starting plugin registry locally...$(NC)"
	cd $(PLUGIN_REGISTRY) && uvicorn app.main:app --reload --host 0.0.0.0 --port 5901

.PHONY: dev-worker
dev-worker: ## Run ray worker locally
	@echo "$(BLUE)Starting ray worker locally...$(NC)"
	cd $(RAY_WORKER) && python main.py

.PHONY: dev-shell
dev-shell: ## Open shell in API agent container
	$(DOCKER_COMPOSE) exec api-agent /bin/bash

# ============================================================================
# Testing
# ============================================================================

.PHONY: test
test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	cd $(API_AGENT) && $(PYTEST) -v
	@echo "$(GREEN)✓ All tests passed$(NC)"

.PHONY: test-unit
test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	cd $(API_AGENT) && $(PYTEST) app/tests/test_models_*.py app/tests/test_core_*.py -v

.PHONY: test-api
test-api: ## Run API tests only
	@echo "$(BLUE)Running API tests...$(NC)"
	cd $(API_AGENT) && $(PYTEST) app/tests/test_api_*.py -v

.PHONY: test-integration
test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	cd $(API_AGENT) && $(PYTEST) app/tests/test_integration.py -v

.PHONY: test-cov
test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	cd $(API_AGENT) && $(PYTEST) --cov=app --cov-report=term --cov-report=html
	@echo "$(GREEN)✓ Coverage report generated$(NC)"
	@echo "HTML report: $(API_AGENT)/htmlcov/index.html"

.PHONY: test-verbose
test-verbose: ## Run tests with verbose output
	@echo "$(BLUE)Running tests (verbose)...$(NC)"
	cd $(API_AGENT) && $(PYTEST) -vv -s

.PHONY: test-watch
test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	cd $(API_AGENT) && $(PYTEST) -f

.PHONY: test-file
test-file: ## Run specific test file (usage: make test-file file=test_api_jobs.py)
	@if [ -z "$(file)" ]; then \
		echo "$(RED)Error: Please provide test file$(NC)"; \
		echo "Usage: make test-file file=test_api_jobs.py"; \
		exit 1; \
	fi
	@echo "$(BLUE)Running $(file)...$(NC)"
	cd $(API_AGENT) && $(PYTEST) app/tests/$(file) -v

.PHONY: coverage-html
coverage-html: test-cov ## Generate HTML coverage report
	@echo "$(GREEN)Opening coverage report...$(NC)"
	@if command -v open > /dev/null; then \
		open $(API_AGENT)/htmlcov/index.html; \
	elif command -v xdg-open > /dev/null; then \
		xdg-open $(API_AGENT)/htmlcov/index.html; \
	else \
		echo "Please open $(API_AGENT)/htmlcov/index.html manually"; \
	fi

.PHONY: coverage-report
coverage-report: ## Show coverage report in terminal
	cd $(API_AGENT) && $(PYTEST) --cov=app --cov-report=term-missing

# ============================================================================
# Code Quality
# ============================================================================

.PHONY: format
format: ## Format code with ruff
	@echo "$(BLUE)Formatting code...$(NC)"
	cd $(API_AGENT) && ruff format app/
	cd $(PLUGIN_REGISTRY) && ruff format app/
	cd $(RAY_WORKER) && ruff format .
	@echo "$(GREEN)✓ Code formatted$(NC)"

.PHONY: lint
lint: ## Run ruff linter
	@echo "$(BLUE)Running linter...$(NC)"
	cd $(API_AGENT) && ruff check app/
	cd $(PLUGIN_REGISTRY) && ruff check app/
	cd $(RAY_WORKER) && ruff check .
	@echo "$(GREEN)✓ Linting passed$(NC)"

.PHONY: quality
quality: format lint ## Run all code quality checks
	@echo "$(GREEN)✓ All quality checks passed$(NC)"

.PHONY: pre-commit
pre-commit: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	cd $(API_AGENT) && pre-commit run --all-files
	@echo "$(GREEN)✓ Pre-commit checks passed$(NC)"

# ============================================================================
# Plugin Management
# ============================================================================

.PHONY: build-plugins
build-plugins: build-classifier build-processor ## Build all example plugins
	@echo "$(GREEN)✓ All plugins built$(NC)"

.PHONY: build-classifier
build-classifier: ## Build example classifier plugin
	@echo "$(BLUE)Building classifier plugin...$(NC)"
	cd $(PLUGINS)/example-classifier && $(DOCKER) build -t example-classifier:1.0.0 .
	@echo "$(GREEN)✓ Classifier plugin built$(NC)"

.PHONY: build-processor
build-processor: ## Build example processor plugin
	@echo "$(BLUE)Building processor plugin...$(NC)"
	cd $(PLUGINS)/example-processor && $(DOCKER) build -t example-processor:1.0.0 .
	@echo "$(GREEN)✓ Processor plugin built$(NC)"

.PHONY: register-plugins
register-plugins: ## Register example plugins with registry
	@echo "$(BLUE)Registering plugins...$(NC)"
	@echo "Registering classifier..."
	@curl -s -X POST http://localhost:5901/api/v1/plugins \
		-H "Content-Type: application/json" \
		-d @$(PLUGINS)/example-classifier/plugin.json || echo "$(YELLOW)Plugin may already be registered$(NC)"
	@echo ""
	@echo "Registering processor..."
	@curl -s -X POST http://localhost:5901/api/v1/plugins \
		-H "Content-Type: application/json" \
		-d @$(PLUGINS)/example-processor/plugin.json || echo "$(YELLOW)Plugin may already be registered$(NC)"
	@echo ""
	@echo "$(GREEN)✓ Plugins registered$(NC)"

.PHONY: list-plugins
list-plugins: ## List all registered plugins
	@echo "$(BLUE)Registered plugins:$(NC)"
	@curl -s http://localhost:5901/api/v1/plugins | python -m json.tool

# ============================================================================
# Monitoring & Health
# ============================================================================

.PHONY: health
health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@echo -n "API Agent:        "
	@curl -s http://localhost:5900/health > /dev/null && echo "$(GREEN)✓ Healthy$(NC)" || echo "$(RED)✗ Unhealthy$(NC)"
	@echo -n "Plugin Registry:  "
	@curl -s http://localhost:5901/health > /dev/null && echo "$(GREEN)✓ Healthy$(NC)" || echo "$(RED)✗ Unhealthy$(NC)"
	@echo -n "RabbitMQ:         "
	@curl -s -u guest:guest http://localhost:15672/api/overview > /dev/null && echo "$(GREEN)✓ Healthy$(NC)" || echo "$(RED)✗ Unhealthy$(NC)"
	@echo -n "PostgreSQL:       "
	@$(DOCKER_COMPOSE) exec -T postgres pg_isready -U user -d plugindb > /dev/null && echo "$(GREEN)✓ Healthy$(NC)" || echo "$(RED)✗ Unhealthy$(NC)"

.PHONY: status
status: ps health ## Show detailed status of all services

.PHONY: dashboard-ray
dashboard-ray: ## Open Ray dashboard in browser
	@echo "$(BLUE)Opening Ray dashboard...$(NC)"
	@if command -v open > /dev/null; then \
		open http://localhost:8265; \
	elif command -v xdg-open > /dev/null; then \
		xdg-open http://localhost:8265; \
	else \
		echo "Ray Dashboard: http://localhost:8265"; \
	fi

.PHONY: dashboard-rabbitmq
dashboard-rabbitmq: ## Open RabbitMQ management UI in browser
	@echo "$(BLUE)Opening RabbitMQ dashboard...$(NC)"
	@if command -v open > /dev/null; then \
		open http://localhost:15672; \
	elif command -v xdg-open > /dev/null; then \
		xdg-open http://localhost:15672; \
	else \
		echo "RabbitMQ Dashboard: http://localhost:15672"; \
	fi

.PHONY: dashboard-admin
dashboard-admin: ## Open admin dashboard in browser
	@echo "$(BLUE)Opening admin dashboard...$(NC)"
	@if command -v open > /dev/null; then \
		open http://localhost:5900/dashboard; \
	elif command -v xdg-open > /dev/null; then \
		xdg-open http://localhost:5900/dashboard; \
	else \
		echo "Admin Dashboard: http://localhost:5900/dashboard"; \
	fi

.PHONY: api-docs
api-docs: ## Open API documentation in browser
	@echo "$(BLUE)Opening API docs...$(NC)"
	@if command -v open > /dev/null; then \
		open http://localhost:5900/docs; \
	elif command -v xdg-open > /dev/null; then \
		xdg-open http://localhost:5900/docs; \
	else \
		echo "API Docs: http://localhost:5900/docs"; \
	fi

# ============================================================================
# Utilities
# ============================================================================

.PHONY: clean
clean: ## Clean Python cache and build artifacts
	@echo "$(BLUE)Cleaning Python cache and artifacts...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleaned$(NC)"

.PHONY: clean-all
clean-all: clean clean-docker ## Clean everything (docker + python + cache)
	@echo "$(GREEN)✓ All cleaned$(NC)"

.PHONY: secret-key
secret-key: ## Generate new secret key for JWT
	@echo "$(BLUE)Generating new secret key...$(NC)"
	@python -c "import secrets; print(secrets.token_urlsafe(32))"

.PHONY: init
init: setup build-plugins up migrate create-admin register-plugins ## Complete initialization (setup + build + migrate + admin)
	@echo "$(GREEN)✓ Initialization complete!$(NC)"
	@echo ""
	@echo "$(BLUE)Access points:$(NC)"
	@echo "  API Docs:     http://localhost:5900/docs"
	@echo "  Dashboard:    http://localhost:5900/dashboard"
	@echo "  Ray:          http://localhost:8265"
	@echo "  RabbitMQ:     http://localhost:15672"

# ============================================================================
# Quick Commands
# ============================================================================

.PHONY: quick-start
quick-start: env up migrate build-plugins ## Quick start for first time (no venv)
	@echo "$(GREEN)✓ Quick start complete!$(NC)"
	@echo "Access API docs: http://localhost:5900/docs"

.PHONY: quick-test
quick-test: test-unit test-api ## Quick test (unit + API tests)
	@echo "$(GREEN)✓ Quick tests passed$(NC)"

# Default target
.DEFAULT_GOAL := help
