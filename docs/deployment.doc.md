# Orc Ray Agent - Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Development Deployment](#development-deployment)
4. [Production Deployment](#production-deployment)
5. [Configuration](#configuration)
6. [Database Setup](#database-setup)
7. [Plugin Deployment](#plugin-deployment)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Python** 3.13+
- **Git**
- **PostgreSQL** 17 (included in docker-compose)
- **RabbitMQ** 3.13 (included in docker-compose)

### System Requirements
- **Minimum**: 4GB RAM, 2 CPU cores, 20GB disk
- **Recommended**: 8GB+ RAM, 4+ CPU cores, 50GB+ disk
- **OS**: Linux (Ubuntu 22.04+), macOS, or Windows with WSL2

## Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd orc-ray-agent
```

### 2. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
vim .env
```

### 3. Start All Services
```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Initialize Database
```bash
# Run database migrations
docker-compose exec api-agent alembic upgrade head

# Or run manually
cd api-agent
python -m alembic upgrade head
```

### 5. Create Admin User
```bash
# Access API agent container
docker-compose exec api-agent python

# In Python shell:
from app.core.db import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
admin = User(
    email="admin@example.com",
    hashed_password=get_password_hash("admin123"),
    full_name="Admin User",
    is_active=True
)
db.add(admin)
db.commit()
exit()
```

### 6. Build Example Plugins
```bash
# Build classifier plugin
cd plugins/example-classifier
docker build -t example-classifier:1.0.0 .

# Build processor plugin
cd ../example-processor
docker build -t example-processor:1.0.0 .
```

### 7. Register Plugins
```bash
# Use API to register plugins
curl -X POST http://localhost:5901/api/v1/plugins \
  -H "Content-Type: application/json" \
  -d @plugins/example-classifier/plugin.json

curl -X POST http://localhost:5901/api/v1/plugins \
  -H "Content-Type: application/json" \
  -d @plugins/example-processor/plugin.json
```

### 8. Access Services
- **API Documentation**: http://localhost:5900/docs
- **Admin Dashboard**: http://localhost:5900/dashboard
- **Plugin Registry**: http://localhost:5901/docs
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **Ray Dashboard**: http://localhost:8265

## Development Deployment

### Local Development Setup

#### 1. Install Python Dependencies
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install API agent dependencies
cd api-agent
pip install -r requirements.txt -r requirements-dev.txt

# Install plugin registry dependencies
cd ../plugin-registry
pip install -r requirements.txt

# Install ray worker dependencies
cd ../ray-worker
pip install -r requirements.txt
```

#### 2. Start Infrastructure Only
```bash
# Start only PostgreSQL and RabbitMQ
docker-compose up -d postgres rabbitmq

# Wait for services to be ready
sleep 5
```

#### 3. Run Services Locally

**Terminal 1 - API Agent:**
```bash
cd api-agent
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Plugin Registry:**
```bash
cd plugin-registry
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Terminal 3 - Ray Head:**
```bash
ray start --head --port=6379 --dashboard-host=0.0.0.0 --dashboard-port=8265
```

**Terminal 4 - Ray Worker:**
```bash
cd ray-worker
python main.py
```

#### 4. Run Tests
```bash
cd api-agent

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test suite
pytest app/tests/test_integration.py -v

# View coverage report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

#### 5. Run Code Quality Checks
```bash
cd api-agent

# Format code
black app/

# Check imports
isort app/

# Lint code
flake8 app/

# Or use pre-commit
pre-commit run --all-files
```

## Production Deployment

### 1. Environment Configuration

Create production `.env` file:
```bash
# Database
DATABASE_URL=postgresql://produser:strongpassword@postgres:5432/orc_ray_agent
POSTGRES_USER=produser
POSTGRES_PASSWORD=strongpassword
POSTGRES_DB=orc_ray_agent

# RabbitMQ
RABBITMQ_URL=amqp://produser:strongpassword@rabbitmq:5672/
RABBITMQ_DEFAULT_USER=produser
RABBITMQ_DEFAULT_PASS=strongpassword

# Security
SECRET_KEY=<generate-strong-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# Ray Configuration
RAY_HEAD_ADDRESS=ray-head:10001
PLUGIN_REGISTRY_URL=http://plugin-registry:8000

# Monitoring
LOG_LEVEL=INFO
```

### 2. Generate Secret Key
```bash
# Generate strong secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Production Docker Compose

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:17
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - orc_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  rabbitmq:
    image: rabbitmq:3.13-management
    restart: always
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_DEFAULT_USER}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_DEFAULT_PASS}
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    networks:
      - orc_network
    healthcheck:
      test: rabbitmq-diagnostics -q ping
      interval: 10s
      timeout: 5s
      retries: 5

  api-agent:
    build:
      context: ./api-agent
      dockerfile: Dockerfile
    restart: always
    ports:
      - "5900:8000"
    environment:
      DATABASE_URL: ${DATABASE_URL}
      RABBITMQ_URL: ${RABBITMQ_URL}
      SECRET_KEY: ${SECRET_KEY}
      DEBUG: "False"
    depends_on:
      postgres:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    networks:
      - orc_network

  plugin-registry:
    build:
      context: ./plugin-registry
      dockerfile: Dockerfile
    restart: always
    ports:
      - "5901:8000"
    environment:
      DATABASE_URL: ${DATABASE_URL}
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - orc_network

  ray-head:
    image: rayproject/ray:2.9.1-py310
    restart: always
    command: ray start --head --port=6379 --dashboard-host=0.0.0.0 --dashboard-port=8265 --block
    ports:
      - "10001:10001"
      - "8265:8265"
    shm_size: 2gb
    networks:
      - orc_network

  ray-worker:
    build:
      context: ./ray-worker
      dockerfile: Dockerfile
    restart: always
    environment:
      RAY_HEAD_ADDRESS: ${RAY_HEAD_ADDRESS}
      RABBITMQ_URL: ${RABBITMQ_URL}
      PLUGIN_REGISTRY_URL: ${PLUGIN_REGISTRY_URL}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on:
      - ray-head
      - rabbitmq
      - plugin-registry
    networks:
      - orc_network

volumes:
  postgres_data:
  rabbitmq_data:

networks:
  orc_network:
    driver: bridge
```

### 4. Deploy to Production
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec api-agent alembic upgrade head

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 5. Setup Nginx Reverse Proxy (Optional)

Create `/etc/nginx/sites-available/orc-ray-agent`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:5900;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/v1/plugins {
        proxy_pass http://localhost:5901/api/v1/plugins;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and restart nginx:
```bash
sudo ln -s /etc/nginx/sites-available/orc-ray-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `RABBITMQ_URL` | RabbitMQ connection URL | - | Yes |
| `SECRET_KEY` | JWT signing key | - | Yes |
| `ALGORITHM` | JWT algorithm | HS256 | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | 30 | No |
| `RAY_HEAD_ADDRESS` | Ray head node address | localhost:10001 | Yes |
| `PLUGIN_REGISTRY_URL` | Plugin registry URL | http://localhost:5901 | Yes |
| `DEBUG` | Enable debug mode | False | No |
| `LOG_LEVEL` | Logging level | INFO | No |

### Database Configuration

PostgreSQL connection pool settings in `api-agent/app/core/db.py`:
```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,           # Number of connections in pool
    max_overflow=20,        # Max connections beyond pool_size
    pool_timeout=30,        # Seconds to wait for connection
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_pre_ping=True,     # Test connections before use
)
```

### RabbitMQ Configuration

Queue configuration in `api-agent/app/services/mq_service.py`:
```python
# Durable queues with persistent messages
channel.queue_declare(queue='job_queue', durable=True)
channel.queue_declare(queue='status_queue', durable=True)

# Dead letter exchange for failed messages
channel.exchange_declare(exchange='dlx', exchange_type='fanout')
channel.queue_declare(queue='failed_jobs', durable=True)
channel.queue_bind(exchange='dlx', queue='failed_jobs')
```

## Database Setup

### Initial Migration
```bash
cd api-agent

# Initialize alembic (already done)
# alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### Schema Updates
```bash
# After model changes, create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Backup and Restore
```bash
# Backup database
docker-compose exec postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup.sql

# Restore database
docker-compose exec -T postgres psql -U $POSTGRES_USER $POSTGRES_DB < backup.sql
```

## Plugin Deployment

### Building Custom Plugins

1. **Create Plugin Directory:**
```bash
mkdir -p plugins/my-plugin
cd plugins/my-plugin
```

2. **Create `main.py`:**
```python
import sys
import json

def process(input_data):
    # Your plugin logic here
    result = {"output": "processed"}
    return result

if __name__ == "__main__":
    input_data = json.loads(sys.argv[1]) if len(sys.argv) > 1 else json.load(sys.stdin)
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
    "properties": {
      "data": {"type": "string"}
    }
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "output": {"type": "string"}
    }
  }
}
```

4. **Create `Dockerfile`:**
```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py plugin.json ./

ENTRYPOINT ["python", "main.py"]
```

5. **Build and Register:**
```bash
# Build image
docker build -t my-plugin:1.0.0 .

# Register with plugin registry
curl -X POST http://localhost:5901/api/v1/plugins \
  -H "Content-Type: application/json" \
  -d @plugin.json
```

## Monitoring

### Health Checks
```bash
# API Agent health
curl http://localhost:5900/health

# Plugin Registry health
curl http://localhost:5901/health

# RabbitMQ management
curl -u guest:guest http://localhost:15672/api/overview

# PostgreSQL health
docker-compose exec postgres pg_isready
```

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api-agent

# Last 100 lines
docker-compose logs --tail=100 ray-worker

# Filter by time
docker-compose logs --since 1h
```

### Metrics
Access Ray Dashboard at http://localhost:8265 for:
- Active tasks and actors
- Resource utilization
- Node status
- Task timeline

### Database Monitoring
```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity;

-- Long running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - pg_stat_activity.query_start > interval '1 minute';

-- Table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Troubleshooting

### Common Issues

#### 1. Services Won't Start
```bash
# Check Docker status
docker ps -a

# Check logs for errors
docker-compose logs

# Restart services
docker-compose restart

# Rebuild if needed
docker-compose build --no-cache
docker-compose up -d
```

#### 2. Database Connection Errors
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1"

# Check DATABASE_URL in .env
grep DATABASE_URL .env
```

#### 3. RabbitMQ Connection Errors
```bash
# Check RabbitMQ status
docker-compose exec rabbitmq rabbitmqctl status

# Check queues
docker-compose exec rabbitmq rabbitmqctl list_queues

# Reset RabbitMQ (WARNING: deletes all messages)
docker-compose stop rabbitmq
docker-compose rm -v rabbitmq
docker-compose up -d rabbitmq
```

#### 4. Ray Worker Not Processing Jobs
```bash
# Check Ray cluster status
ray status

# Check Ray worker logs
docker-compose logs ray-worker

# Verify Docker socket mount
docker-compose exec ray-worker ls -la /var/run/docker.sock

# Check plugin images exist
docker images | grep example-
```

#### 5. Plugin Execution Failures
```bash
# Test plugin manually
docker run --rm example-processor:1.0.0 '{"data": [1,2,3], "operation": "sum"}'

# Check plugin logs
docker logs <container-id>

# Verify plugin registration
curl http://localhost:5901/api/v1/plugins
```

### Debug Mode

Enable debug mode in `.env`:
```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

Restart services:
```bash
docker-compose restart
```

### Performance Tuning

#### Database
```ini
# postgresql.conf
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
```

#### Ray Worker
Adjust actor pool size in `ray-worker/mq_consumer.py`:
```python
# Increase for more parallel processing
consumer = JobQueueConsumer(rabbitmq_url, num_actors=10)
```

## Security Best Practices

1. **Change default passwords** in production
2. **Use strong SECRET_KEY** (32+ bytes)
3. **Enable HTTPS** with SSL certificates
4. **Restrict database access** to internal network
5. **Use non-root users** in Docker containers
6. **Keep dependencies updated** regularly
7. **Enable firewall** rules for production
8. **Implement rate limiting** on API endpoints
9. **Regular backups** of database and configurations
10. **Monitor logs** for suspicious activity

## Scaling

### Horizontal Scaling

Add more Ray workers:
```bash
# In docker-compose.yml
  ray-worker-2:
    build: ./ray-worker
    environment:
      RAY_HEAD_ADDRESS: ray-head:10001
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

Scale API agents with load balancer:
```bash
docker-compose up -d --scale api-agent=3
```

### Vertical Scaling

Increase resource limits in `docker-compose.yml`:
```yaml
  api-agent:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

---

**For more information, see:**
- [implementation-status.doc.md](implementation-status.doc.md) - Implementation details
- [../specs/blueprint.specs.md](../specs/blueprint.specs.md) - System architecture
- [agent.doc.md](agent.doc.md) - Development guidelines
