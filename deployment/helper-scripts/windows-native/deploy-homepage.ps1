# Homepage Deployment Script for Windows
# This script stops existing services and restarts them with updated code

Write-Host "Deploying Homepage Services..." -ForegroundColor Green
Write-Host "This will stop existing services and restart them with updated code." -ForegroundColor Yellow
Write-Host ""

# Check if the main startup script exists
$startupScript = Join-Path $PSScriptRoot "start-homepage.ps1"
if (-not (Test-Path $startupScript)) {
    Write-Error "start-homepage.ps1 not found in the current directory."
    exit 1
}

# Get the project root (two levels up from helper-scripts/windows-native)
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Write-Host "Project root: $projectRoot" -ForegroundColor Gray

# Execute the restart functionality
try {
    & $startupScript -Restart
    Write-Host ""
    Write-Host "Deployment completed successfully!" -ForegroundColor Green
    Write-Host "Services are now running with updated code." -ForegroundColor White
    Write-Host ""
    Write-Host "Access your application at:" -ForegroundColor Cyan
    Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
    Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
    
} catch {
    Write-Error "Deployment failed: $_"
    exit 1
}
