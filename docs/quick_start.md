# Quick Start Guide

Get up and running with the Scraping Platform in just a few minutes.

## Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- Docker and Docker Compose (optional but recommended)
- PostgreSQL 14+ (or use Docker)

## Installation

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/scraping-platform.git
cd scraping-platform

# Start all services
docker-compose up -d

# The API will be available at http://localhost:8000
# The frontend will be available at http://localhost:3000
```

### Option 2: Local Development

```bash
# Clone the repository
git clone https://github.com/your-org/scraping-platform.git
cd scraping-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
python scripts/init_db.py

# Start the API server
python -m uvicorn src.webapp.main:app --reload

# In another terminal, start the frontend
cd frontend
npm run dev
```

## First Steps

### 1. Get an API Key

```bash
# Create an API key
curl -X POST http://localhost:8000/api/v1/auth/api-keys \
  -H "Content-Type: application/json" \
  -d '{"name": "my-first-key", "scopes": ["scraping:read", "scraping:write"]}'
```

### 2. Start Your First Scraping Job

```bash
# Start a simple scraping job
curl -X POST http://localhost:8000/api/v1/scraping/jobs \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "template": "company_profile_v1",
    "export_format": "json"
  }'
```

### 3. Check Job Status

```bash
# Get job status
curl http://localhost:8000/api/v1/jobs/{job_id} \
  -H "Authorization: Bearer your-api-key"
```

### 4. Download Results

Once the job is complete, download your results:

```bash
# Download results
curl http://localhost:8000/api/v1/exports/{export_id}/download \
  -H "Authorization: Bearer your-api-key" \
  -o results.json
```

## Templates

The platform comes with several pre-built templates:

- `company_profile_v1` - Extract company information
- `person_profile_v1` - Extract person/contact details
- `product_detail_v1` - Extract product information
- `article_content_v1` - Extract article text and metadata

### Using Custom Templates

Create a custom template file:

```yaml
# templates/my_template.yaml
name: "my_custom_template"
version: "1.0"
selectors:
  title: "h1"
  description: ".description"
  price: ".price"
  images: "img[src]::attr(src)"
transformations:
  price: "currency"
  images: "list"
```

## Configuration

Key configuration files:

- `config/app_config.yml` - Main application settings
- `config/rate_limits.yml` - Rate limiting configuration
- `config/proxies.yml` - Proxy pool settings
- `.env` - Environment variables

## Next Steps

- Read the [API Documentation](api_documentation.md)
- Explore [Template Development](template_development.md)
- Set up [Monitoring and Observability](observability_setup.md)
- Configure [Proxy Pools](proxy_configuration.md)

## Getting Help

- 📚 [Full Documentation](README.md)
- 💬 [Community Forum](https://forum.scrapingplatform.com)
- 🐛 [Issue Tracker](https://github.com/your-org/scraping-platform/issues)
- 📧 [Support Email](mailto:support@scrapingplatform.com)
