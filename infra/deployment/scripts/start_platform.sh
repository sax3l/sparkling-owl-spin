#!/bin/bash

# Startup script for Advanced Web Scraping Platform
echo "🚀 Starting Advanced Web Scraping Platform..."

# Check if Python backend dependencies are installed
if [ ! -d "backend_venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python -m venv backend_venv
fi

# Activate virtual environment
source backend_venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements_backend.txt

# Start Redis (for Celery)
echo "🔄 Starting Redis server..."
redis-server --daemonize yes

# Start Celery worker
echo "👷 Starting Celery worker..."
cd backend
celery -A main.celery worker --loglevel=info --detach

# Start FastAPI backend
echo "🖥️ Starting FastAPI backend server..."
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &

cd ..

# Install Node.js dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Start Next.js frontend
echo "🌐 Starting Next.js frontend..."
npm run dev

echo "✅ Platform started successfully!"
echo "🖥️ Backend API: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "📊 API Docs: http://localhost:8000/docs"
