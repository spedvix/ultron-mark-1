# Quick Start Script for Ultron
# This script helps you get started quickly

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "        Ultron - AI Academic Assistant" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env file created!" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  Please edit the .env file and add your credentials:" -ForegroundColor Yellow
    Write-Host "   - University login details" -ForegroundColor Yellow
    Write-Host "   - Notion API key and database IDs" -ForegroundColor Yellow
    Write-Host "   - Telegram bot token and chat ID" -ForegroundColor Yellow
    Write-Host "   - OpenAI API key" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "See SETUP.md for detailed instructions." -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter after configuring .env to continue"
}

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Cyan
$pythonVersion = python --version 2>&1
Write-Host "Found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Ask if user wants to create virtual environment
$createVenv = Read-Host "Do you want to create a virtual environment? (recommended) [Y/n]"
if ($createVenv -eq "" -or $createVenv -eq "Y" -or $createVenv -eq "y") {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    Write-Host "✅ Virtual environment created!" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment activated!" -ForegroundColor Green
    Write-Host ""
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt
Write-Host "✅ Dependencies installed!" -ForegroundColor Green
Write-Host ""

# Run setup check
Write-Host "Running setup check..." -ForegroundColor Cyan
python setup_check.py
Write-Host ""

# Ask if user wants to start Ultron
$startUltron = Read-Host "Do you want to start Ultron now? [Y/n]"
if ($startUltron -eq "" -or $startUltron -eq "Y" -or $startUltron -eq "y") {
    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "Starting Ultron..." -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Dashboard will be available at: http://localhost:8080" -ForegroundColor Green
    Write-Host "Telegram bot will start automatically" -ForegroundColor Green
    Write-Host ""
    Write-Host "Press Ctrl+C to stop Ultron" -ForegroundColor Yellow
    Write-Host ""
    python main.py
} else {
    Write-Host ""
    Write-Host "To start Ultron manually, run:" -ForegroundColor Cyan
    Write-Host "  python main.py" -ForegroundColor Yellow
    Write-Host ""
}
