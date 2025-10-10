<div align="center">
  <img src="ray-orc-agent-logo.png" alt="Ray Orc Agent Logo" width="200"/>

  # Orc Ray Agent

  **Ray-based Distributed ML Plugin Agent System**

  [![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
  [![Ray](https://img.shields.io/badge/Ray-2.9.1-00ADD8.svg)](https://www.ray.io/)
  [![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

  A scalable MLOps platform for executing containerized ML plugins in a distributed Ray cluster with FastAPI, RabbitMQ, and PostgreSQL.
</div>

---

## 🚀 Overview

Orc Ray Agent is a distributed machine learning plugin agent system that enables dynamic execution of containerized ML models and data processing logic across a distributed computing cluster. The system provides:

- **Distributed Plugin Execution**: Execute ML models and data processing tasks as containerized plugins via Ray's distributed computing framework
- **RESTful API**: FastAPI-based API server for job submission and management
- **Plugin Registry**: Centralized management of plugin metadata, Docker images, and schemas
- **Admin Dashboard**: Web-based dashboard for real-time monitoring and management of users, plugins, and jobs
- **Message Queue Integration**: RabbitMQ-based asynchronous job processing and status synchronization
- **Scalable Architecture**: Horizontal scaling via Ray cluster with support for multiple worker nodes

## 📋 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.13+
- Git
- Make (optional, but recommended)

### Fastest Start (Using Makefile)

```bash
# Clone repository
git clone <repository-url>
cd orc-ray-agent

# Quick start - sets up and starts everything
make quick-start

# Or for complete initialization with admin user
make init

# View all available commands
make help
```

**That's it!** Access the services:

- **API Documentation**: http://localhost:5900/docs
- **Admin Dashboard**: http://localhost:5900/dashboard
- **Plugin Registry**: http://localhost:5901/docs
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **Ray Dashboard**: http://localhost:8265

### Manual Installation (Without Make)

<details>
<summary>Click to expand manual installation steps</summary>

1. **Clone repository:**
```bash
git clone <repository-url>
cd orc-ray-agent
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Start services:**
```bash
docker-compose up -d
```

4. **Initialize database:**
```bash
docker-compose exec api-agent alembic upgrade head
```

5. **Build example plugins:**
```bash
cd plugins/example-classifier
docker build -t example-classifier:1.0.0 .

cd ../example-processor
docker build -t example-processor:1.0.0 .
```

</details>

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User / Client                        │
└─────────────────┬───────────────────────────┬───────────────┘
                  │                           │
                  ▼                           ▼
        ┌─────────────────┐        ┌─────────────────┐
        │   API Agent     │        │Admin Dashboard  │
        │   (FastAPI)     │◄───────┤  (Jinja2 UI)   │
        │   Port 5900     │        └─────────────────┘
        └────────┬────────┘
                 │
        ┌────────┼────────────────────────┐
        ▼        ▼                        ▼
 ┌──────────┐ ┌──────────┐      ┌───────────────┐
 │PostgreSQL│ │RabbitMQ  │      │Plugin Registry│
 │    17    │ │   3.13   │      │  (FastAPI)    │
 └──────────┘ └────┬─────┘      │  Port 5901    │
                   │             └───────────────┘
                   │ job_queue
                   │
                   ▼
        ┌────────────────────┐
        │   Ray Cluster      │
        │  ┌──────────────┐  │
        │  │  Ray Head    │  │
        │  │  Port 8265   │  │
        │  └──────────────┘  │
        │  ┌──────────────┐  │
        │  │ Ray Worker   │  │
        │  │ (PluginActor)│  │
        │  └──────┬───────┘  │
        └─────────┼──────────┘
                  │
                  ▼
        ┌─────────────────┐
        │Plugin Containers│
        │  (Docker)       │
        └─────────────────┘
```

## 📦 Components

| Component           | Purpose                                           | Technology         |
| ------------------- | ------------------------------------------------- | ------------------ |
| **API Agent**       | REST API server, user authentication, job management | FastAPI, SQLAlchemy |
| **Plugin Registry** | Plugin metadata management service                | FastAPI, PostgreSQL |
| **Ray Worker**      | Distributed job execution engine                  | Ray, Docker SDK    |
| **Admin Dashboard** | Web-based management interface                    | Jinja2, Tailwind, Alpine.js |
| **Database**        | Data persistence (users, jobs, plugins)           | PostgreSQL 17      |
| **Message Queue**   | Asynchronous job distribution & status updates    | RabbitMQ 3.13      |

## 🛠️ Technology Stack

| Layer                | Technology                          |
| -------------------- | ----------------------------------- |
| **Backend**          | Python 3.13, FastAPI, Pydantic      |
| **Database**         | PostgreSQL 17, SQLAlchemy 2.0       |
| **Message Queue**    | RabbitMQ 3.13                       |
| **Distributed Computing** | Ray 2.9.1                      |
| **Frontend**         | Jinja2, Tailwind CSS, Alpine.js     |
| **Containerization** | Docker, Docker Compose              |
| **Migrations**       | Alembic                             |
| **Testing**          | Pytest, pytest-cov                  |
| **Code Quality**     | Ruff (linting & formatting)         |
| **Package Manager**  | uv                                  |

## 🔧 Development

### Setup Development Environment

```bash
# Complete setup (creates venv, installs deps, sets up hooks)
make setup
source venv/bin/activate

# Start only infrastructure (postgres, rabbitmq, ray-head)
make dev

# In separate terminals, run services locally:
make dev-api        # Terminal 1: API Agent with hot reload
make dev-registry   # Terminal 2: Plugin Registry
make dev-worker     # Terminal 3: Ray Worker

# Run tests
make test           # All tests
make test-cov       # With coverage
make quick-test     # Quick (unit + API only)

# Code quality
make format         # Format code
make lint           # Run linter
make quality        # All quality checks
```

See [docs/makefile-guide.doc.md](docs/makefile-guide.doc.md) for complete command reference.

### Creating Custom Plugins

<details>
<summary>Click to expand plugin development guide</summary>

1. **Create plugin structure:**
```bash
mkdir -p plugins/my-plugin
cd plugins/my-plugin
```

2. **Create `main.py`:**
```python
import sys
import json

def process(input_data):
    # Your logic here
    result = {"output": "processed"}
    return result

if __name__ == "__main__":
    input_data = json.loads(sys.argv[1])
    result = process(input_data)
    print(json.dumps(result))
```

3. **Create `plugin.json`:**
```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "My custom plugin",
  "docker_image": "my-plugin:1.0.0",
  "input_schema": {
    "type": "object",
    "properties": {"data": {"type": "string"}}
  },
  "output_schema": {
    "type": "object",
    "properties": {"output": {"type": "string"}}
  }
}
```

4. **Create `Dockerfile`:**
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install -e .
COPY main.py plugin.json ./
ENTRYPOINT ["python", "main.py"]
```

5. **Build and register:**
```bash
docker build -t my-plugin:1.0.0 .
curl -X POST http://localhost:5901/api/v1/plugins \
  -H "Content-Type: application/json" \
  -d @plugin.json
```

</details>

## 📚 API Examples

### Authentication

```bash
# Login
curl -X POST http://localhost:5900/api/v1/auth/token \
  -d "username=admin@example.com&password=admin123"

# Get current user
curl -X GET http://localhost:5900/api/v1/auth/me \
  -H "Authorization: Bearer <token>"
```

### Job Management

```bash
# Create job
curl -X POST http://localhost:5900/api/v1/jobs \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "plugin_name": "example-processor",
    "input_data": {"data": [1,2,3,4,5], "operation": "sum"}
  }'

# List jobs
curl -X GET http://localhost:5900/api/v1/jobs \
  -H "Authorization: Bearer <token>"

# Get job details
curl -X GET http://localhost:5900/api/v1/jobs/1 \
  -H "Authorization: Bearer <token>"
```

### Plugin Management

```bash
# Register plugin
curl -X POST http://localhost:5901/api/v1/plugins \
  -H "Content-Type: application/json" \
  -d @plugin.json

# List plugins
curl -X GET http://localhost:5901/api/v1/plugins

# Get plugin details
curl -X GET http://localhost:5901/api/v1/plugins/1
```

## 🧪 Testing

The project includes 50+ tests covering:
- Unit tests for models
- Security functions tests
- API endpoint tests
- Integration tests for E2E workflows

```bash
# Run all tests
pytest

# Run specific test file
pytest api-agent/app/tests/test_integration.py -v

# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html
```

**Test Coverage Target:** 80%

**Test Statistics:**
- Total: 50+ tests
- User model: 5 tests
- Job model: 7 tests
- Plugin model: 3 tests
- Security: 9 tests
- Authentication API: 7 tests
- User Management API: 9 tests
- Job Management API: 11 tests
- Integration tests: E2E workflows

## 📊 Monitoring

### Health Checks

```bash
# API Agent
curl http://localhost:5900/health

# Plugin Registry
curl http://localhost:5901/health

# RabbitMQ
curl -u guest:guest http://localhost:15672/api/overview
```

### Dashboards

- **Ray Dashboard**: http://localhost:8265 - Task execution, resource usage
- **RabbitMQ Management**: http://localhost:15672 - Queue statistics, connections
- **Admin Dashboard**: http://localhost:5900/dashboard - Jobs, users, plugins

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f api-agent
docker-compose logs -f ray-worker

# Last 100 lines
docker-compose logs --tail=100
```

## 📖 Documentation

### Specifications

- **[specs/blueprint.specs.md](specs/blueprint.specs.md)** - System architecture and design (Korean, ~1800 lines)
- **[specs/structure.specs.md](specs/structure.specs.md)** - Complete project structure guide (~625 lines)

### Documentation

- **[docs/agent.doc.md](docs/agent.doc.md)** - Development guidelines and TDD principles
- **[docs/deployment.doc.md](docs/deployment.doc.md)** - Comprehensive deployment guide (~780 lines)
- **[docs/implementation-status.doc.md](docs/implementation-status.doc.md)** - Implementation progress and test statistics (~345 lines)
- **[docs/makefile-guide.doc.md](docs/makefile-guide.doc.md)** - Complete Makefile command reference (~560 lines)
- **[docs/makefile-quickref.doc.md](docs/makefile-quickref.doc.md)** - Quick reference card (~148 lines)
- **[docs/claude.doc.md](docs/claude.doc.md)** - AI assistant instructions

## 📈 Project Status

- **Implementation**: 95% complete (9 of 10 phases)
- **Total Tests**: 50+ unit, API, and integration tests
- **Code Coverage**: Pending verification (Target: 80%)
- **TDD Compliance**: 100%

### Completed Phases

1. ✅ Project Foundation
2. ✅ Database Models with TDD
3. ✅ Core Services & Schemas
4. ✅ Authentication & User Management API
5. ✅ Job Management API with RabbitMQ
6. ✅ Plugin Registry Service
7. ✅ Ray Worker Implementation
8. ✅ Example Plugins
9. ✅ Admin Dashboard
10. 🔄 Integration Tests & Documentation (In Progress)

## 🤝 Contributing

This project follows TDD (Test-Driven Development) and Tidy First principles:

1. **Write tests first** (RED phase)
2. **Implement minimum code** to pass tests (GREEN phase)
3. **Refactor** while keeping tests green
4. **Separate** structural and behavioral changes
5. **Use clear commit messages**

See [docs/agent.doc.md](docs/agent.doc.md) for detailed development guidelines.

## 📝 License

See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with FastAPI, Ray, RabbitMQ, and PostgreSQL.

---

**Last Updated:** 2025-10-10
**Version:** 1.0.0
**Implementation Progress:** 95% complete (9 of 10 phases)
