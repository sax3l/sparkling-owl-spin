# Deployment Guide

Complete guide for deploying the scraping platform to production environments.

## Deployment Options

### 1. Docker Compose (Recommended for small-medium scale)

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    build: .
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/scraping_platform
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    restart: unless-stopped

  worker:
    build: .
    command: python -m celery worker -A src.scheduler.celery_app
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/scraping_platform
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=scraping_platform
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7
    restart: unless-stopped

volumes:
  postgres_data:
```

### 2. Kubernetes (Recommended for large scale)

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scraping-platform-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: scraping-platform-api
  template:
    metadata:
      labels:
        app: scraping-platform-api
    spec:
      containers:
      - name: api
        image: scrapingplatform/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

### 3. Cloud Providers

#### AWS ECS

```json
{
  "family": "scraping-platform",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "scrapingplatform/api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://..."
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/scraping-platform",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

## Pre-deployment Checklist

### Security

- [ ] Change default passwords and API keys
- [ ] Configure HTTPS/TLS certificates
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure CORS appropriately
- [ ] Set up authentication and authorization
- [ ] Review and update security headers

### Configuration

- [ ] Set production environment variables
- [ ] Configure database connections
- [ ] Set up Redis/caching
- [ ] Configure proxy pools
- [ ] Set up monitoring and logging
- [ ] Configure backup strategies

### Performance

- [ ] Optimize database queries
- [ ] Configure connection pooling
- [ ] Set up horizontal scaling
- [ ] Configure load balancing
- [ ] Optimize Docker images
- [ ] Set resource limits

## Environment Configuration

### Production Environment Variables

```bash
# .env.production
NODE_ENV=production
DATABASE_URL=postgresql://user:password@host:5432/scraping_platform
REDIS_URL=redis://host:6379
SECRET_KEY=your-super-secret-key-here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
LOG_LEVEL=INFO

# Proxy Configuration
PROXY_ENABLED=true
PROXY_ROTATION_ENABLED=true

# Features
ASYNC_PROCESSING=true
BATCH_PROCESSING=true
```

### Database Configuration

```sql
-- Production database setup
CREATE DATABASE scraping_platform;
CREATE USER scraping_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE scraping_platform TO scraping_user;

-- Performance optimizations
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET random_page_cost = 1.1;
SELECT pg_reload_conf();
```

## Load Balancing

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/scraping-platform
upstream api_backend {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    listen 80;
    server_name api.scrapingplatform.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.scrapingplatform.com;
    
    ssl_certificate /etc/ssl/certs/scrapingplatform.crt;
    ssl_certificate_key /etc/ssl/private/scrapingplatform.key;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://api_backend/health;
        access_log off;
    }
}
```

## Monitoring and Observability

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'scraping-platform-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
    
  - job_name: 'scraping-platform-workers'
    static_configs:
      - targets: ['worker1:9090', 'worker2:9090']
```

### Grafana Dashboard

Key metrics to monitor:

- Request rate and latency
- Error rates
- Active scraping jobs
- Queue lengths
- Database connections
- Memory and CPU usage
- Proxy health

## Backup and Recovery

### Database Backups

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump $DATABASE_URL > "$BACKUP_DIR/scraping_platform_$DATE.sql"

# Compress backup
gzip "$BACKUP_DIR/scraping_platform_$DATE.sql"

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

### Automated Backup Schedule

```yaml
# k8s/cronjob-backup.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:14
            command:
            - /bin/bash
            - -c
            - |
              pg_dump $DATABASE_URL | gzip > /backup/db_$(date +%Y%m%d_%H%M%S).sql.gz
              aws s3 cp /backup/ s3://your-backup-bucket/ --recursive
          restartPolicy: OnFailure
```

## Scaling Strategies

### Horizontal Scaling

1. **API Servers**: Scale API pods based on CPU/memory usage
2. **Worker Processes**: Scale workers based on queue length
3. **Database**: Use read replicas for read-heavy workloads

### Vertical Scaling

1. **Increase resources** for existing containers
2. **Optimize queries** and caching
3. **Use connection pooling**

### Auto-scaling Configuration

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: scraping-platform-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: scraping-platform-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Troubleshooting

### Common Issues

1. **High memory usage**: Optimize queries, implement caching
2. **Slow responses**: Check database performance, add indexes
3. **Failed scraping jobs**: Check proxy health, implement retries
4. **Database connection errors**: Configure connection pooling

### Debugging Tools

```bash
# Check application logs
kubectl logs -f deployment/scraping-platform-api

# Monitor resource usage
kubectl top pods

# Database performance
psql $DATABASE_URL -c "SELECT * FROM pg_stat_activity;"

# Redis monitoring
redis-cli monitor
```

## Security Hardening

### Container Security

```dockerfile
# Use non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

USER appuser

# Security scanning
RUN apk add --no-cache ca-certificates
```

### Network Security

- Use private networks
- Configure security groups
- Enable VPC flow logs
- Implement network policies

### Data Protection

- Encrypt data at rest
- Use secure connections (TLS)
- Implement data retention policies
- Regular security audits

## Cost Optimization

### Resource Management

- Use appropriate instance sizes
- Implement auto-scaling
- Use spot instances for workers
- Optimize storage usage

### Monitoring Costs

- Set up billing alerts
- Use cost allocation tags
- Regular cost reviews
- Optimize unused resources
