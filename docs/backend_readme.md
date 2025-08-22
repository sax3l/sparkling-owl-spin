# Lovable Backend

A modern, production-ready FastAPI backend for the Lovable platform.

## Features

- **FastAPI Framework**: Modern, fast, and async Python web framework
- **JWT Authentication**: Secure user authentication and authorization
- **SQLAlchemy ORM**: Robust database abstraction and migrations
- **Pydantic Models**: Type-safe data validation and serialization
- **RESTful API**: Clean, consistent API design
- **Rate Limiting**: Built-in protection against abuse
- **Security Headers**: Production-ready security configurations
- **Request Logging**: Comprehensive request/response logging
- **Error Handling**: Centralized error handling and responses
- **Database Migrations**: Alembic-based schema versioning
- **CLI Tools**: Command-line interface for management tasks

## Architecture

```
backend/
├── __init__.py              # Package initialization
├── main.py                  # FastAPI application entry point
├── app.py                   # Application factory
├── settings.py              # Configuration management
├── config.py                # Advanced configuration
├── api.py                   # Main API router
├── auth.py                  # Authentication system
├── routers.py               # API route handlers
├── models.py                # Pydantic models
├── db_models.py             # SQLAlchemy database models
├── database.py              # Database connection
├── services.py              # Business logic services
├── dependencies.py          # FastAPI dependencies
├── middleware.py            # Custom middleware
├── exceptions.py            # Error handling
├── utils.py                 # Utility functions
├── cli.py                   # Command-line interface
├── requirements.txt         # Python dependencies
├── alembic.ini             # Alembic configuration
└── migrations/             # Database migrations
    ├── env.py
    └── versions/
        └── 001_initial.py
```

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL (optional, SQLite by default)
- Redis (optional, for caching)

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Initialize database:**
   ```bash
   python cli.py db init
   ```

4. **Create admin user:**
   ```bash
   python cli.py user create --admin
   ```

5. **Start the server:**
   ```bash
   python cli.py serve --reload
   ```

The API will be available at `http://localhost:8000`

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Application environment |
| `DEBUG` | `False` | Debug mode |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `DATABASE_URL` | `sqlite:///./lovable.db` | Database connection URL |
| `JWT_SECRET_KEY` | `your-secret-key-here` | JWT signing key |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiration |
| `CORS_ALLOW_ORIGINS` | `http://localhost:3000` | Allowed CORS origins |

### Database Configuration

**SQLite (Development):**
```env
DATABASE_URL=sqlite:///./lovable.db
```

**PostgreSQL (Production):**
```env
DATABASE_URL=postgresql://user:password@localhost/lovable
```

**Redis (Optional):**
```env
REDIS_URL=redis://localhost:6379/0
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/token` - OAuth2 token endpoint
- `POST /api/v1/auth/refresh` - Refresh access token

### Users
- `GET /api/v1/users/me` - Current user info
- `PUT /api/v1/users/me` - Update current user
- `GET /api/v1/users/{id}` - Get user by ID (admin)

### Projects
- `GET /api/v1/projects` - List user projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{id}` - Get project
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Templates
- `GET /api/v1/templates` - List templates
- `POST /api/v1/templates` - Create template
- `GET /api/v1/templates/{id}` - Get template

### Jobs
- `GET /api/v1/jobs` - List user jobs
- `POST /api/v1/jobs` - Create job
- `GET /api/v1/jobs/{id}` - Get job
- `PATCH /api/v1/jobs/{id}/status` - Update job status

### Health
- `GET /api/v1/health` - Health check
- `GET /api/v1/health/db` - Database health

## CLI Commands

### Server Management
```bash
python cli.py serve                    # Start server
python cli.py serve --reload           # Start with auto-reload
python cli.py serve --host 0.0.0.0     # Specify host
python cli.py serve --port 8080        # Specify port
```

### Database Management
```bash
python cli.py db init                  # Initialize database
python cli.py db reset                 # Reset database
python cli.py db drop                  # Drop all tables
```

### User Management
```bash
python cli.py user create              # Create user (interactive)
python cli.py user info <username>     # Get user info
```

### Configuration
```bash
python cli.py config show              # Show configuration
python cli.py config validate          # Validate configuration
```

### Health & Info
```bash
python cli.py health                   # Check health
python cli.py version                  # Show version
```

## Development

### Code Style
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

### Pre-commit Hooks
```bash
pre-commit install
pre-commit run --all-files
```

### Testing
```bash
pytest                                 # Run tests
pytest --cov                          # Run with coverage
pytest -v                             # Verbose output
```

### Database Migrations
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
alembic downgrade -1
```

## Security

### Authentication
- JWT-based authentication
- Secure password hashing with bcrypt
- Token expiration and refresh
- API key support

### Security Headers
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection
- Strict-Transport-Security
- Referrer-Policy

### Rate Limiting
- Per-IP request limits
- Configurable thresholds
- Different limits for different endpoints

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "cli.py", "serve", "--host", "0.0.0.0"]
```

### Production Settings
```env
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=your-secure-secret-key
CORS_ALLOW_ORIGINS=https://yourdomain.com
```

### Systemd Service
```ini
[Unit]
Description=Lovable Backend
After=network.target

[Service]
Type=simple
User=lovable
WorkingDirectory=/opt/lovable/backend
ExecStart=/opt/lovable/venv/bin/python cli.py serve
Restart=always

[Install]
WantedBy=multi-user.target
```

## Monitoring

### Health Checks
- `/api/v1/health` - Application health
- `/api/v1/health/db` - Database connectivity

### Metrics
- Request count and response times
- Status code distribution
- Error rates
- Database connection pool status

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking
- Audit logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
