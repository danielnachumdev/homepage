@echo off
echo Homepage Service Manager
echo ======================
echo.
echo 1. Start services
echo 2. Stop services
echo 3. Restart services
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo Starting services...
    powershell -ExecutionPolicy Bypass -File "%~dp0start-homepage.ps1"
) else if "%choice%"=="2" (
    echo Stopping services...
    powershell -ExecutionPolicy Bypass -File "%~dp0start-homepage.ps1" -StopOnly
) else if "%choice%"=="3" (
    echo Restarting services...
    powershell -ExecutionPolicy Bypass -File "%~dp0start-homepage.ps1" -Restart
) else if "%choice%"=="4" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice. Please run the script again.
    pause
    exit /b 1
)

echo.
echo Operation completed. Press any key to exit...
pause >nul
