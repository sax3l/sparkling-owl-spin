#!/bin/bash

# Application entrypoint script
set -e

# Default to web if no command specified
COMMAND=${1:-web}

echo "Starting application with command: $COMMAND"

# Wait for required services
echo "Waiting for services to be ready..."
python scripts/wait_for_services.py

# Run database migrations if needed
if [ "$COMMAND" = "web" ] || [ "$COMMAND" = "migrate" ]; then
    echo "Running database migrations..."
    python scripts/init_db.py
fi

# Start appropriate service
case $COMMAND in
    "web")
        echo "Starting web application..."
        exec gunicorn src.webapp.app:create_app() \
            --bind 0.0.0.0:8000 \
            --workers 4 \
            --worker-class uvicorn.workers.UvicornWorker \
            --access-logfile - \
            --error-logfile - \
            --log-level info
        ;;
    "api")
        echo "Starting API server..."
        exec uvicorn src.webapp.api:app \
            --host 0.0.0.0 \
            --port 8000 \
            --workers 4 \
            --access-log
        ;;
    "graphql")
        echo "Starting GraphQL server..."
        exec python -m src.graphql.server \
            --host 0.0.0.0 \
            --port 8000
        ;;
    "migrate")
        echo "Running migrations only..."
        python scripts/init_db.py
        echo "Migrations completed"
        ;;
    "shell")
        echo "Starting interactive shell..."
        exec python -i -c "
from src.database.connection import get_db_connection
from src.services import *
from src.utils import *
print('Application shell ready. Database and services imported.')
"
        ;;
    "test")
        echo "Running tests..."
        exec python -m pytest tests/ -v
        ;;
    "dev")
        echo "Starting development server..."
        export FLASK_ENV=development
        export FLASK_DEBUG=1
        exec flask --app src.webapp.app run \
            --host 0.0.0.0 \
            --port 8000 \
            --debug
        ;;
    *)
        echo "Executing custom command: $*"
        exec "$@"
        ;;
esac