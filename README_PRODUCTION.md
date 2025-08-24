# 🕷️ Sparkling Owl Spin Production Crawler Platform

**Enterprise-grade web scraping platform with AI-powered data extraction, advanced crawling strategies, and production-ready infrastructure.**

## 🎯 System Overview

Sparkling Owl Spin is a comprehensive web crawling and scraping platform that combines:

- **Advanced Crawling Algorithms** (BFS/DFS/Intelligent Hybrid)
- **AI-Powered Data Extraction** with OpenAI/Claude integration
- **Ultimate Stealth Engine** for anti-detection
- **Production Database Layer** with SQLAlchemy
- **Job Scheduling System** with cron-like functionality
- **Real-time Monitoring** and analytics
- **Compliance Framework** for legal and ethical scraping

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Redis Server** (localhost:6379)
- **PostgreSQL** (optional, SQLite works for testing)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/your-org/sparkling-owl-spin.git
cd sparkling-owl-spin
```

2. **Install dependencies:**
```bash
pip install -r requirements_production.txt
```

3. **Start Redis server:**
```bash
redis-server
```

4. **Verify installation:**
```bash
python verify_implementation.py
```

### Basic Usage

**Run the simple demo:**
```bash
python simple_crawler_demo.py
```

**Or use the components directly:**

```python
import asyncio
import redis.asyncio as redis
from src.crawler.crawl_coordinator import create_crawl_coordinator, CrawlConfiguration

async def crawl_website():
    # Configuration
    config = CrawlConfiguration(
        strategy="intelligent",
        max_pages=1000,
        max_depth=5,
        max_concurrent=10,
        use_ai_extraction=True
    )
    
    # Create coordinator
    redis_client = redis.from_url("redis://localhost:6379/0")
    coordinator = await create_crawl_coordinator(config, redis_client)
    
    # Start crawling
    crawl_id = await coordinator.start_crawl([
        "https://example.com",
        "https://target-site.com"
    ])
    
    # Monitor progress
    while coordinator.is_running:
        status = await coordinator.get_crawl_status()
        print(f"Crawled: {status['stats']['total_crawled']} pages")
        await asyncio.sleep(10)

# Run the crawler
asyncio.run(crawl_website())
```

## 📋 Core Components

### 1. Crawl Coordinator
**File:** `src/crawler/crawl_coordinator.py`

Central orchestration system that manages all crawling operations:

```python
from src.crawler.crawl_coordinator import CrawlCoordinator, CrawlConfiguration

config = CrawlConfiguration(
    strategy="bfs",  # or "dfs", "intelligent", "priority"
    max_pages=10000,
    max_depth=10,
    max_concurrent=20,
    respect_robots_txt=True,
    use_stealth=True
)
```

### 2. URL Queue Management
**File:** `src/crawler/url_queue.py`

Redis-backed persistent URL queue with deduplication:

```python
from src.crawler.url_queue import URLQueue, QueuedURL

queue = URLQueue(redis_client, "my_crawl_queue")

# Add URL to queue
url = QueuedURL(
    url="https://example.com/page",
    priority=1,  # 1 = highest priority
    depth=0
)
await queue.add_url(url)

# Get next URL to crawl
next_url = await queue.get_next_url(domain_delay_seconds=2)
```

### 3. Database Layer
**File:** `src/database/crawl_database.py`

Production-ready database with SQLAlchemy:

```python
from src.database.crawl_database import create_crawl_service

db_service = await create_crawl_service("postgresql://user:pass@localhost/crawldb")

# Create crawl job
job_id = await db_service.create_crawl_job(
    name="My Crawl Job",
    start_urls=["https://example.com"],
    config={"strategy": "bfs", "max_pages": 1000}
)

# Save crawled page
await db_service.save_crawled_page(
    job_id=job_id,
    url="https://example.com/page",
    html_content="<html>...</html>",
    extracted_data={"title": "Page Title", "price": "$99"}
)
```

### 4. Job Scheduler
**File:** `src/scheduler/simple_scheduler.py`

Cron-like job scheduling with Redis persistence:

```python
from src.scheduler.simple_scheduler import SimpleScheduler, ScheduledJob, ScheduleType

scheduler = SimpleScheduler(redis_client, max_concurrent_jobs=5)
await scheduler.start()

# Create scheduled job
job = ScheduledJob(
    id="daily_crawl",
    name="Daily Website Crawl",
    schedule_type=ScheduleType.INTERVAL,
    interval_seconds=86400,  # 24 hours
    start_urls=["https://news-site.com"],
    crawl_config={"strategy": "bfs", "max_pages": 500}
)

await scheduler.schedule_job(job)
```

## 🛠️ Advanced Features

### AI-Powered Data Extraction

```python
# Enable AI extraction in crawl configuration
config = CrawlConfiguration(
    use_ai_extraction=True,
    extract_data=True
)

# The system will automatically use OpenAI/Claude to extract:
# - Product information
# - Article content  
# - Contact details
# - Structured data
```

### Ultimate Stealth Engine

```python
config = CrawlConfiguration(
    use_stealth=True,  # Enables anti-detection features
    delay_between_requests=2.0,  # Polite crawling
    respect_robots_txt=True
)

# Includes:
# - Browser fingerprint spoofing
# - Dynamic User-Agent rotation
# - CAPTCHA solving
# - Proxy rotation
```

### Real-time Monitoring

```python
config = CrawlConfiguration(
    use_real_time_monitoring=True
)

# Provides:
# - Prometheus metrics
# - WebSocket real-time updates
# - Performance dashboards
# - Alert notifications
```

## 📊 Crawling Strategies

### 1. Breadth-First Search (BFS)
Best for: Site-wide coverage, discovering page types
```python
config = CrawlConfiguration(strategy="bfs")
```

### 2. Depth-First Search (DFS)  
Best for: Deep content exploration, following specific paths
```python
config = CrawlConfiguration(strategy="dfs")
```

### 3. Intelligent Hybrid
Best for: Optimal performance, adapts to site structure
```python
config = CrawlConfiguration(strategy="intelligent")
```

### 4. Priority-Based
Best for: Targeted crawling, important pages first
```python
config = CrawlConfiguration(strategy="priority")
```

## 🗄️ Database Schema

The system creates comprehensive database tables:

- **crawl_jobs** - Job configurations and status
- **crawled_pages** - Crawled content and extracted data
- **discovered_links** - Link frontier management
- **extraction_rules** - Data extraction configurations
- **crawl_templates** - Reusable crawl configurations

## ⚙️ Configuration Options

### Environment Variables

```bash
# Redis Configuration
REDIS_URL="redis://localhost:6379/0"

# Database Configuration  
DATABASE_URL="postgresql://user:pass@localhost/crawldb"

# AI Services
OPENAI_API_KEY="your-openai-key"
ANTHROPIC_API_KEY="your-claude-key"

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
```

### Configuration File Example

```yaml
# config/crawler_config.yaml
crawler:
  max_concurrent_jobs: 10
  default_strategy: "intelligent"
  respect_robots_txt: true
  
database:
  connection_pool_size: 20
  query_timeout: 30
  
redis:
  connection_pool_size: 10
  socket_keepalive: true
  
stealth:
  enable_proxy_rotation: true
  captcha_solver: "2captcha"
  browser_profiles: ["chrome", "firefox", "safari"]
```

## 🚀 Production Deployment

### Docker Deployment

```dockerfile
# Use provided Dockerfile
docker build -t sparkling-owl-spin .
docker run -d \
  --name crawler \
  -p 8000:8000 \
  -e REDIS_URL="redis://redis:6379" \
  -e DATABASE_URL="postgresql://postgres:pass@db:5432/crawldb" \
  sparkling-owl-spin
```

### Kubernetes Deployment

```yaml
# See k8s/deployment.yaml for complete configuration
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sparkling-owl-spin
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: crawler
        image: sparkling-owl-spin:latest
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
```

### Scaling Considerations

- **Horizontal Scaling**: Deploy multiple crawler instances
- **Redis Cluster**: For high-availability URL queue
- **Database Sharding**: For large-scale data storage
- **Load Balancing**: Distribute crawl requests

## 📈 Performance Optimization

### Recommended Settings

```python
# High-performance configuration
config = CrawlConfiguration(
    strategy="intelligent",
    max_pages=100000,
    max_concurrent=50,
    delay_between_requests=0.1,  # Fast crawling
    use_stealth=False,  # Disable for speed
    batch_size=100
)
```

### Monitoring Performance

```python
# Get real-time statistics
status = await coordinator.get_crawl_status()
print(f"Pages/second: {status['stats']['pages_per_second']}")
print(f"Queue size: {status['stats']['queue_size']}")
```

## 🛡️ Security and Compliance

### Legal Compliance Features

- **robots.txt** respect and parsing
- **Rate limiting** per domain
- **GDPR-compliant** data collection
- **Terms of Service** checking
- **Data retention** policies

### Security Features

- **Anti-bot detection** bypass
- **Secure credential** management
- **Encrypted data** storage
- **Audit logging** for compliance
- **IP rotation** and proxy support

## 🔧 Troubleshooting

### Common Issues

**Redis Connection Failed:**
```bash
# Start Redis server
redis-server

# Check Redis status
redis-cli ping
```

**Import Errors:**
```bash
# Install all dependencies
pip install -r requirements_production.txt

# Check Python path
python -c "import src; print('OK')"
```

**Database Connection Issues:**
```bash
# Test database connection
python -c "
import asyncio
from src.database.crawl_database import create_crawl_service
asyncio.run(create_crawl_service('sqlite:///test.db'))
print('Database OK')
"
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debug configuration
config = CrawlConfiguration(
    max_pages=10,  # Small test
    max_concurrent=1,  # Single thread
    delay_between_requests=5.0  # Slow and careful
)
```

## 📚 Documentation

- **API Reference**: `docs/api/`
- **Architecture Guide**: `docs/architecture.md`
- **Deployment Guide**: `docs/deployment.md`
- **Performance Tuning**: `docs/performance.md`
- **Legal Compliance**: `docs/compliance.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Update documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: https://sparkling-owl-docs.com
- **Issues**: GitHub Issues
- **Community**: Discord/Slack channel
- **Enterprise**: contact@sparkling-owl.com

---

**🎯 Ready for production use with enterprise-grade reliability and performance!**
