# Makefile Quick Reference Card

## 🚀 Essential Commands

```bash
make help           # Show all available commands
make quick-start    # Fastest way to get started (Docker only)
make init          # Complete initialization with admin user
make setup         # Setup dev environment (venv + deps)
```

## 📦 Common Workflows

### First Time Setup

```bash
make quick-start    # OR
make init          # Interactive setup with admin user
```

### Daily Development

```bash
make dev           # Start infrastructure
make dev-api       # Run API locally (hot reload)
make test-cov      # Test with coverage
make format        # Format code before commit
```

### Docker Operations

```bash
make up            # Start all services
make down          # Stop all services
make restart       # Restart all services
make logs          # View all logs
make ps            # Show running containers
```

### Testing

```bash
make test          # All tests
make test-cov      # With coverage report
make quick-test    # Fast (unit + API only)
make test-integration  # Integration tests
```

### Code Quality

```bash
make format        # Auto-format (black + isort)
make lint          # Run linter (flake8)
make quality       # All checks (format + lint)
```

### Database

```bash
make migrate       # Run migrations
make migration msg="add field"  # Create migration
make db-shell      # PostgreSQL shell
make create-admin  # Create admin user
```

### Plugins

```bash
make build-plugins     # Build example plugins
make register-plugins  # Register with registry
make list-plugins     # List all plugins
```

### Monitoring

```bash
make health        # Check all services
make status        # Detailed status
make dashboard-ray # Open Ray dashboard
make api-docs      # Open API docs
```

### Utilities

```bash
make clean         # Clean Python cache
make clean-all     # Clean everything
make secret-key    # Generate JWT secret
```

## 📋 Command Patterns

### Specific Service Logs

```bash
make logs-api      # API agent only
make logs-worker   # Ray worker only
make logs-postgres # PostgreSQL only
```

### Development Services

```bash
make dev-api       # API agent locally
make dev-registry  # Plugin registry locally
make dev-worker    # Ray worker locally
```

### Test Variations

```bash
make test-unit     # Unit tests only
make test-api      # API tests only
make test-verbose  # Verbose output
make test-file file=test_api_jobs.py  # Specific file
```

## 🎯 Quick Scenarios

### "I want to start working"

```bash
make dev
make dev-api       # In new terminal
```

### "I made changes, test them"

```bash
make test-cov
make quality
```

### "Fresh start"

```bash
make clean-all
make quick-start
```

### "Something's broken"

```bash
make health
make logs
make restart
```

### "Deploy to production"

See docs/deployment.doc.md

## 💡 Pro Tips

1. **Tab completion works**: `make <TAB><TAB>`
2. **Combine commands**: `make format && make test`
3. **Check help anytime**: `make help`
4. **View detailed guide**: `cat docs/makefile-guide.doc.md`

---

**Quick Links:**

- Full guide: [makefile-guide.doc.md](makefile-guide.doc.md)
- Deployment: [deployment.doc.md](deployment.doc.md)
- API docs: http://localhost:5900/docs (after `make up`)
