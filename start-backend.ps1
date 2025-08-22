# PowerShell script for starting Lovable Backend with Database Setup
# This script builds and starts the backend services with database

Write-Host "🚀 Starting Lovable Backend with Database Setup..." -ForegroundColor Green

# Create necessary directories
$directories = @(
    "docker\postgres\init",
    "data\postgres", 
    "data\redis",
    "data\pgadmin"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker is not running. Please start Docker first." -ForegroundColor Red
    exit 1
}

# Build backend image
Write-Host "🔨 Building backend Docker image..." -ForegroundColor Yellow
docker-compose -f docker-compose.backend.yml build backend

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build backend image" -ForegroundColor Red
    exit 1
}

# Start services
Write-Host "🐘 Starting PostgreSQL database..." -ForegroundColor Yellow
docker-compose -f docker-compose.backend.yml up -d postgres

# Wait for PostgreSQL to be ready
Write-Host "⏳ Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0

do {
    Start-Sleep -Seconds 2
    $attempt++
    $ready = docker-compose -f docker-compose.backend.yml exec postgres pg_isready -U lovable -d lovable_db 2>$null
    
    if ($ready -match "accepting connections") {
        break
    }
    
    Write-Host "PostgreSQL is not ready yet. Waiting... (Attempt $attempt of $maxAttempts)"
    
} while ($attempt -lt $maxAttempts)

if ($attempt -ge $maxAttempts) {
    Write-Host "❌ PostgreSQL failed to start within timeout" -ForegroundColor Red
    exit 1
}

Write-Host "✅ PostgreSQL is ready!" -ForegroundColor Green

# Start Redis
Write-Host "🔴 Starting Redis cache..." -ForegroundColor Yellow
docker-compose -f docker-compose.backend.yml up -d redis

# Start PGAdmin
Write-Host "🔧 Starting PGAdmin..." -ForegroundColor Yellow
docker-compose -f docker-compose.backend.yml up -d pgadmin

# Start backend service
Write-Host "🚀 Starting backend API..." -ForegroundColor Yellow
docker-compose -f docker-compose.backend.yml up -d backend

# Show status
Write-Host ""
Write-Host "📊 Service Status:" -ForegroundColor Cyan
docker-compose -f docker-compose.backend.yml ps

Write-Host ""
Write-Host "🎉 Lovable Backend is now running!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Available Services:" -ForegroundColor Cyan
Write-Host "   • Backend API:       http://localhost:8000" -ForegroundColor White
Write-Host "   • API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   • PostgreSQL:        localhost:5432" -ForegroundColor White
Write-Host "   • Redis:             localhost:6379" -ForegroundColor White
Write-Host "   • PGAdmin:           http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "🔑 Default Credentials:" -ForegroundColor Cyan
Write-Host "   • Database: lovable / lovable123" -ForegroundColor White
Write-Host "   • PGAdmin:  admin@lovable.com / admin123" -ForegroundColor White
Write-Host "   • Admin User: admin / admin123" -ForegroundColor White
Write-Host ""
Write-Host "🛠️  Useful Commands:" -ForegroundColor Cyan
Write-Host "   • Stop all services:  docker-compose -f docker-compose.backend.yml down" -ForegroundColor White
Write-Host "   • View logs:          docker-compose -f docker-compose.backend.yml logs -f" -ForegroundColor White
Write-Host "   • Restart backend:    docker-compose -f docker-compose.backend.yml restart backend" -ForegroundColor White
Write-Host ""
