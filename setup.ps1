# PowerShell Setup Script for Crawler Platform
# Run this script to setup the development environment on Windows

Write-Host "🚀 Setting up Crawler Platform..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Found Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Node.js not found. Frontend features will be limited." -ForegroundColor Yellow
}

# Create virtual environment
if (Test-Path "venv") {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment and install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
& venv\Scripts\pip install --upgrade pip
& venv\Scripts\pip install -r requirements.txt

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env file created. Please update with your configuration." -ForegroundColor Green
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Create necessary directories
$directories = @(
    "data\raw",
    "data\processed", 
    "data\exports\csv",
    "data\exports\json",
    "data\exports\excel",
    "data\redis_backups",
    "logs",
    "templates\html"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✅ Created directory: $dir" -ForegroundColor Green
    }
}

# Setup frontend if Node.js is available
if (Get-Command node -ErrorAction SilentlyContinue) {
    if (Test-Path "frontend") {
        Write-Host "Setting up frontend..." -ForegroundColor Yellow
        Set-Location frontend
        npm install
        npm run build
        Set-Location ..
        Write-Host "✅ Frontend setup completed" -ForegroundColor Green
    }
}

# Run basic tests
Write-Host "Running basic tests..." -ForegroundColor Yellow
try {
    & venv\Scripts\python -c "import yaml; print('✅ YAML configuration working')"
    & venv\Scripts\python -c "from src.utils.logger import get_logger; print('✅ Core imports working')"
    Write-Host "✅ Basic tests passed" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Some tests failed. Please check the setup." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Update .env file with your configuration" -ForegroundColor White
Write-Host "2. Setup PostgreSQL database" -ForegroundColor White  
Write-Host "3. Activate virtual environment: venv\Scripts\activate" -ForegroundColor White
Write-Host "4. Run the application: python main.py" -ForegroundColor White
Write-Host ""
Write-Host "For development:" -ForegroundColor Cyan
Write-Host "  Activate venv: venv\Scripts\activate" -ForegroundColor White
Write-Host "  Run tests: pytest" -ForegroundColor White
Write-Host "  Start dev server: uvicorn main:create_app --factory --reload" -ForegroundColor White
