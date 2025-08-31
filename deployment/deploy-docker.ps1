# Docker Deployment Script for Homepage
# This script automatically finds docker-compose.yml relative to its own location
#
# ⚠️  WARNING: Docker deployment is NOT RECOMMENDED for Windows
#     Some Windows native functionality may not be supported or may work differently
#     Consider using native deployment instead: .\deploy-homepage.ps1
#
# Get the script's directory and navigate to the project root (parent of deployment folder)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$composeFile = Join-Path $projectRoot "docker-compose.yml"

# Check if docker-compose.yml exists
if (-not (Test-Path $composeFile)) {
    Write-Error "docker-compose.yml not found at: $composeFile"
    exit 1
}

# Display warning about Docker deployment on Windows
Write-Host "⚠️  WARNING: Docker deployment is NOT RECOMMENDED for Windows" -ForegroundColor Yellow
Write-Host "   Some Windows native functionality may not be supported or may work differently" -ForegroundColor Yellow
Write-Host "   Consider using native deployment instead: .\deploy-homepage.ps1" -ForegroundColor Yellow
Write-Host ""

# Ask for confirmation before proceeding
$confirmation = Read-Host "Do you want to continue with Docker deployment? (y/N)"
if ($confirmation -ne "y" -and $confirmation -ne "Y") {
    Write-Host "Docker deployment cancelled. Use native deployment instead." -ForegroundColor Green
    exit 0
}

Write-Host "Proceeding with Docker deployment..." -ForegroundColor Green
docker compose -f $composeFile up -d --build