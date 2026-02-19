# Ultron Dashboard Restart Script
# This script stops any running Ultron processes and starts the dashboard

Write-Host "=" -ForegroundColor Cyan -NoNewline; Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "  ULTRON - Restart Dashboard" -ForegroundColor Cyan
Write-Host "=" -ForegroundColor Cyan -NoNewline; Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# Stop existing Python processes running Ultron
Write-Host "Stopping existing Ultron processes..." -ForegroundColor Yellow
$pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    foreach ($proc in $pythonProcesses) {
        try {
            Stop-Process -Id $proc.Id -Force
            Write-Host "  ✓ Stopped process ID: $($proc.Id)" -ForegroundColor Green
        } catch {
            Write-Host "  ✗ Could not stop process ID: $($proc.Id)" -ForegroundColor Red
        }
    }
    Start-Sleep -Seconds 2
} else {
    Write-Host "  No running processes found" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Starting Ultron Dashboard..." -ForegroundColor Yellow
Write-Host ""

# Start the dashboard
python main.py
