# Homepage Startup Launcher
# This script starts the frontend and backend services if they are not already running

param(
    [string]$ProjectRoot = "",
    [string]$FrontendDir = "",
    [string]$BackendDir = "",
    [string]$LogFile = ""
)

# Set default values if not provided
if (-not $ProjectRoot) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}

if (-not $FrontendDir) {
    $FrontendDir = Join-Path $ProjectRoot "frontend"
}

if (-not $BackendDir) {
    $BackendDir = Join-Path $ProjectRoot "backend"
}

if (-not $LogFile) {
    $LogFile = Join-Path $ProjectRoot "startup.log"
}

# Function to write log messages
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-Host $logMessage
    Add-Content -Path $LogFile -Value $logMessage
}

# Function to check if a process is running
function Test-ProcessRunning {
    param(
        [string]$ProcessName,
        [string]$CommandLinePattern,
        [string]$WorkingDirectory
    )
    
    try {
        $processes = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue
        foreach ($proc in $processes) {
            try {
                $cmdline = (Get-WmiObject Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
                $cwd = (Get-WmiObject Win32_Process -Filter "ProcessId = $($proc.Id)").ExecutablePath
                
                if ($cmdline -and $cmdline -like "*$CommandLinePattern*") {
                    if ($WorkingDirectory -and $cwd -and $cwd.StartsWith($WorkingDirectory)) {
                        return $true
                    }
                    elseif (-not $WorkingDirectory) {
                        return $true
                    }
                }
            }
            catch {
                # Skip processes we can't access
                continue
            }
        }
        return $false
    }
    catch {
        return $false
    }
}

# Function to start frontend
function Start-Frontend {
    param([string]$FrontendPath)
    
    Write-Log "Checking if frontend is already running..."
    
    if (Test-ProcessRunning -ProcessName "node" -CommandLinePattern "npm run dev" -WorkingDirectory $FrontendPath) {
        Write-Log "Frontend is already running, skipping startup"
        return $true
    }
    
    Write-Log "Starting frontend development server..."
    
    try {
        # Check if package.json exists
        $packageJson = Join-Path $FrontendPath "package.json"
        if (-not (Test-Path $packageJson)) {
            Write-Log "ERROR: package.json not found in frontend directory: $packageJson"
            return $false
        }
        
        # Check if node_modules exists
        $nodeModules = Join-Path $FrontendPath "node_modules"
        if (-not (Test-Path $nodeModules)) {
            Write-Log "WARNING: node_modules not found, running npm install first..."
            $installResult = Start-Process -FilePath "npm" -ArgumentList "install" -WorkingDirectory $FrontendPath -Wait -PassThru
            if ($installResult.ExitCode -ne 0) {
                Write-Log "ERROR: npm install failed with exit code $($installResult.ExitCode)"
                return $false
            }
        }
        
        # Start the frontend process
        $frontendProcess = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory $FrontendPath -PassThru -WindowStyle Hidden
        Start-Sleep -Seconds 3
        
        if (-not $frontendProcess.HasExited) {
            Write-Log "Frontend started successfully (PID: $($frontendProcess.Id))"
            return $true
        }
        else {
            Write-Log "ERROR: Frontend process exited immediately with code $($frontendProcess.ExitCode)"
            return $false
        }
    }
    catch {
        Write-Log "ERROR: Failed to start frontend: $($_.Exception.Message)"
        return $false
    }
}

# Function to start backend
function Start-Backend {
    param([string]$BackendPath)
    
    Write-Log "Checking if backend is already running..."
    
    if (Test-ProcessRunning -ProcessName "python" -CommandLinePattern "__main__.py" -WorkingDirectory $BackendPath) {
        Write-Log "Backend is already running, skipping startup"
        return $true
    }
    
    Write-Log "Starting backend server..."
    
    try {
        # Check if __main__.py exists
        $mainPy = Join-Path $BackendPath "__main__.py"
        if (-not (Test-Path $mainPy)) {
            Write-Log "ERROR: __main__.py not found in backend directory: $mainPy"
            return $false
        }
        
        # Check if virtual environment exists
        $venvPython = Join-Path $BackendPath "venv\Scripts\python.exe"
        $pythonCmd = "python"
        
        if (Test-Path $venvPython) {
            $pythonCmd = $venvPython
            Write-Log "Using virtual environment Python: $pythonCmd"
        }
        else {
            Write-Log "Using system Python: $pythonCmd"
        }
        
        # Start the backend process
        $backendProcess = Start-Process -FilePath $pythonCmd -ArgumentList "__main__.py" -WorkingDirectory $BackendPath -PassThru -WindowStyle Hidden
        Start-Sleep -Seconds 3
        
        if (-not $backendProcess.HasExited) {
            Write-Log "Backend started successfully (PID: $($backendProcess.Id))"
            return $true
        }
        else {
            Write-Log "ERROR: Backend process exited immediately with code $($backendProcess.ExitCode)"
            return $false
        }
    }
    catch {
        Write-Log "ERROR: Failed to start backend: $($_.Exception.Message)"
        return $false
    }
}

# Main execution
Write-Log "=== Homepage Startup Launcher Started ==="
Write-Log "Project Root: $ProjectRoot"
Write-Log "Frontend Directory: $FrontendDir"
Write-Log "Backend Directory: $BackendDir"
Write-Log "Log File: $LogFile"

# Validate directories
if (-not (Test-Path $ProjectRoot)) {
    Write-Log "ERROR: Project root directory not found: $ProjectRoot"
    exit 1
}

if (-not (Test-Path $FrontendDir)) {
    Write-Log "ERROR: Frontend directory not found: $FrontendDir"
    exit 1
}

if (-not (Test-Path $BackendDir)) {
    Write-Log "ERROR: Backend directory not found: $BackendDir"
    exit 1
}

# Start services
$frontendSuccess = Start-Frontend -FrontendPath $FrontendDir
$backendSuccess = Start-Backend -BackendPath $BackendDir

if ($frontendSuccess -and $backendSuccess) {
    Write-Log "=== All services started successfully ==="
    exit 0
}
else {
    Write-Log "=== Some services failed to start ==="
    if (-not $frontendSuccess) {
        Write-Log "Frontend startup failed"
    }
    if (-not $backendSuccess) {
        Write-Log "Backend startup failed"
    }
    exit 1
}
