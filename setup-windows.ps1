# Argus Intelligence Platform - Windows Setup Script
# Run this script in PowerShell to set up the development environment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Argus Intelligence Platform - Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green

    # Extract version number
    if ($pythonVersion -match "(\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 13)) {
            Write-Host "⚠ Warning: Python 3.13+ recommended. Current version may have compatibility issues." -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check Node.js
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Found Node.js: $nodeVersion" -ForegroundColor Green

    $npmVersion = npm --version 2>&1
    Write-Host "✓ Found npm: v$npmVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found!" -ForegroundColor Red
    Write-Host "  Download from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check Ollama
Write-Host "Checking Ollama installation..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✓ Found: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Ollama not found!" -ForegroundColor Red
    Write-Host "  Download from: https://ollama.com/download/windows" -ForegroundColor Yellow
    Write-Host "  The application will continue, but AI features won't work without Ollama." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setting up Backend..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Backend setup
Set-Location backend

Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
python -m venv venv

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "✓ Backend setup complete!" -ForegroundColor Green

# Check if .env exists
if (!(Test-Path ".env")) {
    Write-Host ""
    Write-Host "Creating default .env file..." -ForegroundColor Yellow

    $envContent = @"
# Application
APP_NAME=Argus Intelligence Platform
DEBUG=True
ENVIRONMENT=development

# Database
DATABASE_URL=sqlite:///./storage/database/research_tool.db

# AI Providers
DEFAULT_EMBEDDING_PROVIDER=local
DEFAULT_LLM_PROVIDER=ollama

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_LLM_MODEL=gurubot/llama3-guru-uncensored:latest

# Optional API Keys (only if using cloud AI)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# OSINT APIs (Optional)
SHODAN_API_KEY=
VT_API_KEY=
HIBP_API_KEY=

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
"@

    $envContent | Out-File -FilePath ".env" -Encoding utf8
    Write-Host "✓ Created .env file with default settings" -ForegroundColor Green
    Write-Host "  Edit backend/.env to add your API keys if needed" -ForegroundColor Yellow
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setting up Frontend..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Set-Location frontend

Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
npm install

Write-Host "✓ Frontend setup complete!" -ForegroundColor Green

Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Ollama Model Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (Get-Command ollama -ErrorAction SilentlyContinue) {
    Write-Host "Pulling required Ollama models..." -ForegroundColor Yellow
    Write-Host "This may take a while (models are several GB)..." -ForegroundColor Yellow
    Write-Host ""

    Write-Host "Pulling embedding model (nomic-embed-text)..." -ForegroundColor Yellow
    ollama pull nomic-embed-text

    Write-Host ""
    Write-Host "Pulling LLM model (gurubot/llama3-guru-uncensored:latest)..." -ForegroundColor Yellow
    ollama pull gurubot/llama3-guru-uncensored:latest

    Write-Host "✓ Models downloaded successfully!" -ForegroundColor Green
} else {
    Write-Host "⚠ Skipping model download (Ollama not found)" -ForegroundColor Yellow
    Write-Host "  Install Ollama and run these commands manually:" -ForegroundColor Yellow
    Write-Host "  ollama pull nomic-embed-text" -ForegroundColor Cyan
    Write-Host "  ollama pull gurubot/llama3-guru-uncensored:latest" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start the backend (in PowerShell):" -ForegroundColor Yellow
Write-Host "   cd backend" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host ""
Write-Host "2. Start the frontend (in a new PowerShell window):" -ForegroundColor Yellow
Write-Host "   cd frontend" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "3. Or use the convenience scripts:" -ForegroundColor Yellow
Write-Host "   .\start-backend.bat  (in one terminal)" -ForegroundColor White
Write-Host "   .\start-frontend.bat (in another terminal)" -ForegroundColor White
Write-Host ""
Write-Host "Then open: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
