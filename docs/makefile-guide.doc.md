# Makefile Usage Guide

Comprehensive guide for using the Orc Ray Agent Makefile commands.

## Quick Reference

```bash
make help           # Show all available commands
make quick-start    # Fastest way to get started
make init          # Complete initialization with admin user
```

## Getting Started

### First Time Setup

**Option 1: With Virtual Environment (Recommended for development)**

```bash
make setup          # Creates venv, installs deps, sets up pre-commit
source venv/bin/activate
make up             # Start all services
make migrate        # Run database migrations
make build-plugins  # Build example plugins
```

**Option 2: Quick Start (Using Docker only)**

```bash
make quick-start    # Sets up and starts everything
```

**Option 3: Complete Initialization (Everything automated)**

```bash
make init           # Full setup + creates admin user interactively
```

## Common Workflows

### Daily Development Workflow

```bash
# Start infrastructure only
make dev

# In separate terminals, run services locally:
make dev-api        # Terminal 1: API Agent
make dev-registry   # Terminal 2: Plugin Registry
make dev-worker     # Terminal 3: Ray Worker

# Run tests before committing
make test-cov
make quality

# Format and commit
make format
git add .
git commit -m "your message"
```

### Docker-based Development

```bash
# Start all services
make up

# View logs
make logs
make logs-api       # Only API agent logs

# Restart after code changes
make restart

# Stop everything
make down
```

### Testing Workflow

```bash
# Quick tests (unit + API)
make quick-test

# All tests
make test

# Tests with coverage
make test-cov

# Open coverage report in browser
make coverage-html

# Specific test file
make test-file file=test_api_jobs.py

# Run only integration tests
make test-integration

# Watch mode (re-run on changes)
make test-watch
```

### Database Management

```bash
# Run migrations
make migrate

# Create new migration
make migration msg="add user roles"

# Rollback last migration
make migrate-down

# Access database shell
make db-shell

# Reset database (DANGER!)
make db-reset

# Create admin user
make create-admin
```

### Plugin Development

```bash
# Build all example plugins
make build-plugins

# Build specific plugin
make build-classifier
make build-processor

# Register plugins with registry
make register-plugins

# List registered plugins
make list-plugins
```

### Code Quality

```bash
# Format code (black + isort)
make format

# Run linter
make lint

# All quality checks
make quality

# Pre-commit hooks
make pre-commit
```

### Monitoring & Debugging

```bash
# Check health of all services
make health

# Show service status
make status

# View specific service logs
make logs-api
make logs-worker
make logs-postgres
make logs-rabbitmq

# Open dashboards in browser
make dashboard-ray        # Ray cluster dashboard
make dashboard-rabbitmq   # RabbitMQ management UI
make dashboard-admin      # Admin web dashboard
make api-docs             # API documentation
```

## Command Categories

### Setup & Installation

| Command                   | Description                       |
| ------------------------- | --------------------------------- |
| `make venv`               | Create Python virtual environment |
| `make install`            | Install production dependencies   |
| `make install-dev`        | Install dev dependencies          |
| `make env`                | Create .env from example          |
| `make pre-commit-install` | Install pre-commit hooks          |
| `make setup`              | Complete initial setup            |
| `make clean-install`      | Clean and reinstall               |

### Docker Operations

| Command                   | Description                 |
| ------------------------- | --------------------------- |
| `make up` / `make start`  | Start all services          |
| `make down` / `make stop` | Stop all services           |
| `make restart`            | Restart all services        |
| `make build`              | Build Docker images         |
| `make rebuild`            | Rebuild without cache       |
| `make logs`               | View all logs               |
| `make logs-api`           | API agent logs only         |
| `make logs-registry`      | Plugin registry logs        |
| `make logs-worker`        | Ray worker logs             |
| `make ps`                 | Show running containers     |
| `make clean-docker`       | Remove containers & volumes |

### Database Operations

| Command                    | Description              |
| -------------------------- | ------------------------ |
| `make migrate`             | Run migrations in Docker |
| `make migrate-local`       | Run migrations locally   |
| `make migration msg="..."` | Create new migration     |
| `make migrate-down`        | Rollback last migration  |
| `make db-shell`            | PostgreSQL shell         |
| `make db-reset`            | Reset database (DANGER)  |
| `make create-admin`        | Create admin user        |

### Development

| Command             | Description                 |
| ------------------- | --------------------------- |
| `make dev`          | Start infrastructure only   |
| `make dev-api`      | Run API agent locally       |
| `make dev-registry` | Run plugin registry locally |
| `make dev-worker`   | Run ray worker locally      |
| `make dev-shell`    | Shell in API container      |

### Testing

| Command                   | Description            |
| ------------------------- | ---------------------- |
| `make test`               | Run all tests          |
| `make test-unit`          | Unit tests only        |
| `make test-api`           | API tests only         |
| `make test-integration`   | Integration tests      |
| `make test-cov`           | Tests with coverage    |
| `make test-verbose`       | Verbose output         |
| `make test-watch`         | Watch mode             |
| `make test-file file=...` | Specific test file     |
| `make coverage-html`      | HTML coverage report   |
| `make coverage-report`    | Terminal coverage      |
| `make quick-test`         | Quick unit + API tests |

### Code Quality

| Command           | Description               |
| ----------------- | ------------------------- |
| `make format`     | Format with black + isort |
| `make lint`       | Run flake8                |
| `make quality`    | All quality checks        |
| `make pre-commit` | Run pre-commit hooks      |

### Plugin Management

| Command                 | Description               |
| ----------------------- | ------------------------- |
| `make build-plugins`    | Build all example plugins |
| `make build-classifier` | Build classifier plugin   |
| `make build-processor`  | Build processor plugin    |
| `make register-plugins` | Register example plugins  |
| `make list-plugins`     | List registered plugins   |

### Monitoring & Health

| Command                   | Description               |
| ------------------------- | ------------------------- |
| `make health`             | Health check all services |
| `make status`             | Detailed service status   |
| `make dashboard-ray`      | Open Ray dashboard        |
| `make dashboard-rabbitmq` | Open RabbitMQ UI          |
| `make dashboard-admin`    | Open admin dashboard      |
| `make api-docs`           | Open API documentation    |

### Utilities

| Command            | Description             |
| ------------------ | ----------------------- |
| `make clean`       | Clean Python cache      |
| `make clean-all`   | Clean everything        |
| `make secret-key`  | Generate JWT secret     |
| `make init`        | Complete initialization |
| `make quick-start` | Quick start             |

## Advanced Usage

### Custom Plugin Development

```bash
# 1. Create plugin directory
mkdir -p plugins/my-plugin
cd plugins/my-plugin

# 2. Create your plugin files
# - main.py
# - plugin.json
# - Dockerfile
# - requirements.txt

# 3. Build plugin
docker build -t my-plugin:1.0.0 .

# 4. Register plugin
curl -X POST http://localhost:5901/api/v1/plugins \
  -H "Content-Type: application/json" \
  -d @plugin.json
```

### Running Specific Tests

```bash
# Run tests matching pattern
cd api-agent && pytest -k "test_job" -v

# Run specific test class
make test-file file=test_integration.py

# Run tests with specific marker
cd api-agent && pytest -m "slow" -v
```

### Database Migrations

```bash
# Create migration after model changes
make migration msg="add user role field"

# Review migration file
cat api-agent/alembic/versions/*.py

# Apply migration
make migrate

# Rollback if needed
make migrate-down
```

### Debugging

```bash
# View logs in real-time
make logs

# Filter logs for errors
make logs-api | grep ERROR

# Access container shell
make dev-shell

# Run Python in container
docker-compose exec api-agent python

# Test database connection
make db-shell
\dt  # List tables
SELECT * FROM users LIMIT 5;
```

### CI/CD Integration

```bash
# Run all quality checks
make quality

# Run full test suite with coverage
make test-cov

# Check if coverage meets threshold
cd api-agent && pytest --cov=app --cov-fail-under=80
```

### Performance Testing

```bash
# Start all services
make up

# In another terminal, run load tests
# (requires locust or similar tool)
locust -f tests/load/locustfile.py --host=http://localhost:5900
```

## Troubleshooting

### Services won't start

```bash
# Check what's running
make ps

# View logs for errors
make logs

# Clean and restart
make clean-docker
make up
```

### Tests failing

```bash
# Clean cache and re-run
make clean
make test

# Run tests with verbose output
make test-verbose

# Check if dependencies are installed
make install-dev
```

### Database issues

```bash
# Check PostgreSQL is running
make health

# Access database shell
make db-shell

# Reset database (CAUTION: destroys data)
make db-reset
```

### Port conflicts

```bash
# Check what's using ports
lsof -i :8000  # API Agent
lsof -i :8001  # Plugin Registry
lsof -i :5432  # PostgreSQL
lsof -i :5672  # RabbitMQ

# Stop conflicting services
make down
```

## Tips & Best Practices

### 1. **Use Tab Completion**

```bash
make <TAB><TAB>  # Shows all available commands
```

### 2. **Combine Commands**

```bash
# Format, lint, and test
make quality && make test
```

### 3. **Check Help Anytime**

```bash
make help  # Shows organized command list
```

### 4. **View Before Destroying**

```bash
# Always check status before clean operations
make ps
make clean-docker  # Prompts for confirmation
```

### 5. **Development Loop**

```bash
# Efficient development cycle
make dev          # Start infrastructure
make dev-api      # Run API locally with hot reload
# Make changes...
make test-cov     # Run tests
make format       # Format code
```

### 6. **Monitor Health**

```bash
# Regular health checks
make health
make status
```

### 7. **Clean Regularly**

```bash
# Clean Python cache weekly
make clean

# Clean Docker monthly (or when running out of space)
make clean-docker
```

## Environment Variables

The Makefile respects these environment variables:

- `PYTHON` - Python executable (default: `python3`)
- `PIP` - Pip executable (default: `pip3`)
- `DOCKER_COMPOSE` - Docker Compose command (default: `docker-compose`)
- `PYTEST` - Pytest executable (default: `pytest`)

Override them as needed:

```bash
PYTHON=python3.13 make test
```

## Integration with IDEs

### VS Code

Add to `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Test with Coverage",
      "type": "shell",
      "command": "make test-cov",
      "problemMatcher": []
    },
    {
      "label": "Start Services",
      "type": "shell",
      "command": "make up",
      "problemMatcher": []
    }
  ]
}
```

### PyCharm

Configure external tools:

- Settings → Tools → External Tools
- Add new tool: Command: `make`, Arguments: `test-cov`

## Aliases (Optional)

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
alias orc-up='make -C ~/path/to/orc-ray-agent up'
alias orc-down='make -C ~/path/to/orc-ray-agent down'
alias orc-test='make -C ~/path/to/orc-ray-agent test'
alias orc-logs='make -C ~/path/to/orc-ray-agent logs'
```

## Getting Help

1. **View all commands**: `make help`
2. **Check this guide**: `cat docs/makefile-guide.doc.md`
3. **View deployment guide**: `cat docs/deployment.doc.md`
4. **Check implementation status**: `cat docs/implementation-status.doc.md`

---

**Quick Start Reminder:**

```bash
make quick-start    # Fastest way to get started
make help          # List all commands
make health        # Check if everything is running
```
