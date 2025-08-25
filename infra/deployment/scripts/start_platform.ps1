# Startup script for Advanced Web Scraping Platform (Windows)
Write-Host "🚀 Starting Advanced Web Scraping Platform..." -ForegroundColor Green

# Check if Python backend dependencies are installed
if (!(Test-Path "backend_venv")) {
    Write-Host "📦 Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv backend_venv
}

# Activate virtual environment
& ".\backend_venv\Scripts\Activate.ps1"

# Install Python dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements_backend.txt

# Start Redis (assuming Redis is installed)
Write-Host "🔄 Starting Redis server..." -ForegroundColor Yellow
Start-Process "redis-server" -WindowStyle Hidden

# Start Celery worker
Write-Host "👷 Starting Celery worker..." -ForegroundColor Yellow
Set-Location backend
Start-Process "celery" -ArgumentList "-A main.celery worker --loglevel=info" -WindowStyle Hidden

# Start FastAPI backend
Write-Host "🖥️ Starting FastAPI backend server..." -ForegroundColor Yellow
Start-Process "python" -ArgumentList "-m uvicorn main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Hidden

Set-Location ..

# Install Node.js dependencies if needed
if (!(Test-Path "node_modules")) {
    Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Yellow
    npm install
}

# Start Next.js frontend
Write-Host "🌐 Starting Next.js frontend..." -ForegroundColor Yellow
npm run dev

Write-Host "✅ Platform started successfully!" -ForegroundColor Green
Write-Host "🖥️ Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "📊 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
