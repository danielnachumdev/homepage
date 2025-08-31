# Homepage Startup Script for Windows
# This script starts both backend and frontend services

param(
    [switch]$StopOnly,
    [switch]$Restart
)

# Function to stop existing processes
function Stop-HomepageServices {
    Write-Host "Stopping existing Homepage services..." -ForegroundColor Yellow
    
    # Stop backend processes
    $backendProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*__main__.py*" }
    if ($backendProcesses) {
        $backendProcesses | Stop-Process -Force
        Write-Host "Backend processes stopped." -ForegroundColor Green
    }
    
    # Stop frontend processes (Vite dev server)
    $frontendProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*vite*" }
    if ($frontendProcesses) {
        $frontendProcesses | Stop-Process -Force
        Write-Host "Frontend processes stopped." -ForegroundColor Green
    }
    
    # Wait a moment for processes to fully terminate
    Start-Sleep -Seconds 2
}

# Function to start services
function Start-HomepageServices {
    Write-Host "Starting Homepage services..." -ForegroundColor Green
    
    # Get the project root (two levels up from helper-scripts/windows-native)
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $projectRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
    Write-Host "Project root: $projectRoot" -ForegroundColor Gray
    
    # Set working directory to project root
    Set-Location $projectRoot
    
    # Start backend
    Write-Host "Starting backend service..." -ForegroundColor Cyan
    Start-Process -FilePath "python" -ArgumentList "-m", "backend" -WorkingDirectory "backend" -WindowStyle Minimized -PassThru | Out-Null
    
    # Wait for backend to start
    Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Start frontend
    Write-Host "Starting frontend service..." -ForegroundColor Cyan
    Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory "frontend" -WindowStyle Minimized -PassThru | Out-Null
    
    Write-Host "All services started!" -ForegroundColor Green
    Write-Host "Backend: http://localhost:8000" -ForegroundColor White
    Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "Backend API Docs: http://localhost:8000/docs" -ForegroundColor White
}

# Main execution
try {
    if ($StopOnly) {
        Stop-HomepageServices
        Write-Host "Services stopped successfully." -ForegroundColor Green
        exit 0
    }
    
    if ($Restart) {
        Write-Host "Restarting Homepage services..." -ForegroundColor Yellow
        Stop-HomepageServices
        Start-Sleep -Seconds 2
        Start-HomepageServices
        exit 0
    }
    
    # Default behavior: start services
    Start-HomepageServices
    
}
catch {
    Write-Error "Error: $_"
    exit 1
}
