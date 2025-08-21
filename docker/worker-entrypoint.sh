#!/bin/bash

# Worker entrypoint script for different worker types
set -e

WORKER_TYPE=${1:-crawler}
WORKER_CONCURRENCY=${WORKER_CONCURRENCY:-4}
WORKER_LOG_LEVEL=${WORKER_LOG_LEVEL:-INFO}

echo "Starting worker type: $WORKER_TYPE with concurrency: $WORKER_CONCURRENCY"

# Wait for database and redis to be ready
python scripts/wait_for_services.py

# Initialize database if needed
if [ "$WORKER_TYPE" = "scheduler" ]; then
    echo "Initializing database..."
    python scripts/init_db.py
fi

# Start appropriate worker type
case $WORKER_TYPE in
    "crawler")
        echo "Starting crawler worker..."
        exec python -m celery -A src.crawler.tasks worker \
            --loglevel=$WORKER_LOG_LEVEL \
            --concurrency=$WORKER_CONCURRENCY \
            --queues=crawler,high_priority \
            --hostname=crawler@%h
        ;;
    "scraper")
        echo "Starting scraper worker..."
        exec python -m celery -A src.scraper.tasks worker \
            --loglevel=$WORKER_LOG_LEVEL \
            --concurrency=$WORKER_CONCURRENCY \
            --queues=scraper,extraction \
            --hostname=scraper@%h
        ;;
    "scheduler")
        echo "Starting scheduler worker..."
        exec python -m celery -A src.scheduler.tasks worker \
            --loglevel=$WORKER_LOG_LEVEL \
            --concurrency=1 \
            --queues=scheduler \
            --hostname=scheduler@%h &
        
        # Also start beat scheduler
        exec python -m celery -A src.scheduler.tasks beat \
            --loglevel=$WORKER_LOG_LEVEL \
            --schedule=/app/data/celerybeat-schedule
        ;;
    "analysis")
        echo "Starting analysis worker..."
        exec python -m celery -A src.analysis.tasks worker \
            --loglevel=$WORKER_LOG_LEVEL \
            --concurrency=$WORKER_CONCURRENCY \
            --queues=analysis,ml_training \
            --hostname=analysis@%h
        ;;
    "flower")
        echo "Starting Flower monitoring..."
        exec python -m celery -A src.crawler.tasks flower \
            --port=5555 \
            --broker_api=http://guest:guest@rabbitmq:15672/api/
        ;;
    "rq")
        echo "Starting RQ worker..."
        exec python -m rq worker \
            --url redis://redis:6379/0 \
            --verbose
        ;;
    *)
        echo "Unknown worker type: $WORKER_TYPE"
        echo "Available types: crawler, scraper, scheduler, analysis, flower, rq"
        exit 1
        ;;
esac
