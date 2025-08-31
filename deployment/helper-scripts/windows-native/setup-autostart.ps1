# Setup Auto-Start for Homepage Services
# This script creates a shortcut in the Windows startup folder

param(
    [switch]$Remove
)

# Get the current script directory and the startup script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$startupScript = Join-Path $scriptDir "start-homepage.ps1"

# Get the project root for the working directory
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)

# Get the Windows startup folder path
$startupFolder = [Environment]::GetFolderPath("Startup")
$shortcutPath = Join-Path $startupFolder "Homepage Services.lnk"

if ($Remove) {
    # Remove auto-start
    if (Test-Path $shortcutPath) {
        Remove-Item $shortcutPath -Force
        Write-Host "Auto-start shortcut removed successfully." -ForegroundColor Green
    } else {
        Write-Host "No auto-start shortcut found." -ForegroundColor Yellow
    }
    exit 0
}

# Create the shortcut
try {
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($shortcutPath)
    
    # Set the target to PowerShell with our script
    $Shortcut.TargetPath = "powershell.exe"
    $Shortcut.Arguments = "-ExecutionPolicy Bypass -WindowStyle Minimized -File `"$startupScript`""
    $Shortcut.WorkingDirectory = $projectRoot
    $Shortcut.Description = "Start Homepage Services on Windows Login"
    $Shortcut.IconLocation = "powershell.exe,0"
    
    # Save the shortcut
    $Shortcut.Save()
    
    Write-Host "Auto-start shortcut created successfully!" -ForegroundColor Green
    Write-Host "Location: $shortcutPath" -ForegroundColor White
    Write-Host "Your homepage services will now start automatically on Windows login." -ForegroundColor Cyan
    Write-Host "To remove auto-start, run: .\setup-autostart.ps1 -Remove" -ForegroundColor Yellow
    
} catch {
    Write-Error "Failed to create auto-start shortcut: $_"
    exit 1
}
