# Windows Native Deployment Script for Homepage
# This script deploys using Windows native services

param(
    [switch]$SetupAutostart,
    [switch]$Help
)

# Get the script's directory and the helper scripts directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$helperScriptsDir = Join-Path $scriptDir "helper-scripts\windows-native"

# Function to display help
function Show-Help {
    Write-Host "Windows Native Deployment Script" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor White
    Write-Host "  .\deploy-windows-native.ps1 [options]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor White
    Write-Host "  -SetupAutostart  Setup auto-start on Windows login" -ForegroundColor Yellow
    Write-Host "  -Help            Show this help message" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor White
    Write-Host "  .\deploy-windows-native.ps1              # Deploy native services" -ForegroundColor Green
    Write-Host "  .\deploy-windows-native.ps1 -SetupAutostart  # Deploy + setup auto-start" -ForegroundColor Green
    Write-Host "  .\deploy-windows-native.ps1 -Help         # Show this help" -ForegroundColor Green
    Write-Host ""
    Write-Host "This script deploys your homepage using Windows native services." -ForegroundColor Gray
}

# Function to check if a script exists
function Test-ScriptExists {
    param([string]$ScriptName)
    $scriptPath = Join-Path $helperScriptsDir $ScriptName
    return Test-Path $scriptPath
}

# Function to run a script with error handling
function Invoke-Script {
    param([string]$ScriptName, [string]$Arguments = "")
    
    $scriptPath = Join-Path $helperScriptsDir $ScriptName
    if (-not (Test-Path $scriptPath)) {
        Write-Error "Required script not found: $ScriptName"
        return $false
    }
    
    try {
        Write-Host "Running: $ScriptName" -ForegroundColor Cyan
        if ($Arguments) {
            & $scriptPath $Arguments
        }
        else {
            & $scriptPath
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ $ScriptName completed successfully" -ForegroundColor Green
            return $true
        }
        else {
            Write-Error "✗ $ScriptName failed with exit code: $LASTEXITCODE"
            return $false
        }
    }
    catch {
        Write-Error "✗ Error running $ScriptName : $_"
        return $false
    }
}

# Main execution
try {
    # Show help if requested
    if ($Help) {
        Show-Help
        exit 0
    }
    
    Write-Host "🖥️  Windows Native Deployment Script" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "🖥️  Deploying with Windows native services..." -ForegroundColor Blue
    
    # Check if required scripts exist
    $requiredScripts = @("start-homepage.ps1", "deploy-homepage.ps1")
    foreach ($script in $requiredScripts) {
        if (-not (Test-ScriptExists $script)) {
            Write-Error "Required script not found: $script"
            Write-Host "Please ensure all deployment scripts are present." -ForegroundColor Red
            exit 1
        }
    }
    
    # Run native deployment
    if (Invoke-Script "deploy-homepage.ps1") {
        Write-Host "✅ Native deployment completed successfully!" -ForegroundColor Green
    }
    else {
        Write-Error "❌ Native deployment failed!"
        exit 1
    }
    
    # Setup auto-start if requested
    if ($SetupAutostart) {
        Write-Host ""
        Write-Host "🔧 Setting up auto-start on Windows login..." -ForegroundColor Blue
        
        if (Invoke-Script "setup-autostart.ps1") {
            Write-Host "✅ Auto-start setup completed successfully!" -ForegroundColor Green
            Write-Host "Your services will now start automatically on Windows login." -ForegroundColor Cyan
        }
        else {
            Write-Error "❌ Auto-start setup failed!"
            Write-Host "You can manually run: .\setup-autostart.ps1" -ForegroundColor Yellow
        }
    }
    
    # Final status
    Write-Host ""
    Write-Host "🎉 Deployment Summary:" -ForegroundColor Green
    Write-Host "  • Native services deployed" -ForegroundColor White
    
    if ($SetupAutostart) {
        Write-Host "  • Auto-start configured" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "🌐 Access your application:" -ForegroundColor Cyan
    Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
    Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
    
    Write-Host ""
    Write-Host "For more options, run: .\deploy-windows-native.ps1 -Help" -ForegroundColor Gray
    
}
catch {
    Write-Error "Deployment failed with error: $_"
    exit 1
}
