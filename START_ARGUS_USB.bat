@echo off
REM Argus Intelligence Platform - Windows USB Launcher
REM Portable deployment for Windows 10+

title Argus Intelligence Platform

echo ============================================
echo   Argus Intelligence Platform
echo   USB Portable Edition
echo ============================================
echo.

REM Get USB drive letter
set USB_DRIVE=%~d0
set USB_PATH=%~dp0
cd /d "%USB_PATH%"

REM Check Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.10 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)
python --version
echo OK!
echo.

REM Storage configuration
echo [2/6] Configuring storage location...
echo.
echo Where should Argus store documents and data?
echo.
echo   1. USB Drive (same as app) - Limited by USB size
echo   2. External Hard Drive - Recommended for large datasets
echo   3. System Temp Folder - Cleared on restart, good for sensitive data
echo   4. Custom Location - Specify your own path
echo.
set /p STORAGE_CHOICE="Enter choice (1-4) [default: 1]: " || set STORAGE_CHOICE=1

if "%STORAGE_CHOICE%"=="2" (
    echo.
    set /p CUSTOM_STORAGE="Enter external drive path (e.g., E:\argus-data): "
    set STORAGE_PATH=%CUSTOM_STORAGE%
) else if "%STORAGE_CHOICE%"=="3" (
    set STORAGE_PATH=%TEMP%\argus-storage
) else if "%STORAGE_CHOICE%"=="4" (
    echo.
    set /p CUSTOM_STORAGE="Enter custom path: "
    set STORAGE_PATH=%CUSTOM_STORAGE%
) else (
    set STORAGE_PATH=%USB_PATH%storage_external
)

echo.
echo Storage location: %STORAGE_PATH%
if not exist "%STORAGE_PATH%" mkdir "%STORAGE_PATH%"
if not exist "%STORAGE_PATH%\database" mkdir "%STORAGE_PATH%\database"
if not exist "%STORAGE_PATH%\uploads" mkdir "%STORAGE_PATH%\uploads"
echo OK!
echo.

REM Set environment variables
set DATABASE_PATH=%STORAGE_PATH%\database\research_tool.db
set UPLOAD_DIR=%STORAGE_PATH%\uploads

REM Install backend dependencies
echo [3/6] Installing backend dependencies...
cd backend
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install backend dependencies
    echo Check backend.log for details
    pause
    exit /b 1
)
echo OK!
echo.

REM Start backend server
echo [4/6] Starting backend server...
start /B cmd /c "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1"
echo Backend server starting on http://localhost:8000
timeout /t 5 /nobreak >nul

REM Check if backend is running
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Backend may not have started properly
    echo Check backend.log for errors
    timeout /t 3 /nobreak >nul
)
echo OK!
echo.

REM Start frontend server
echo [5/6] Starting frontend server...
cd ..\frontend-dist
if not exist index.html (
    echo.
    echo ERROR: Frontend files not found!
    echo Please build the frontend first:
    echo   cd frontend
    echo   npm run build
    echo   xcopy /E /I dist ..\frontend-dist
    pause
    exit /b 1
)

start /B cmd /c "python -m http.server 5173 > frontend.log 2>&1"
echo Frontend server starting on http://localhost:5173
timeout /t 3 /nobreak >nul
echo OK!
echo.

REM Display success message
echo [6/6] Opening Argus in browser...
echo.
echo ============================================
echo   Argus is now running!
echo ============================================
echo.
echo   Frontend:  http://localhost:5173
echo   Backend:   http://localhost:8000
echo   Storage:   %STORAGE_PATH%
echo.
echo First time? The setup wizard will guide you through API key configuration.
echo.
echo To stop Argus:
echo   1. Close this window, OR
echo   2. Press Ctrl+C
echo.
echo ============================================
echo.

REM Open browser
start http://localhost:5173

REM Keep window open
echo Argus is running. Press any key to stop...
pause >nul

REM Cleanup
echo.
echo Stopping Argus...
taskkill /F /FI "WINDOWTITLE eq *uvicorn*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq *http.server*" >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do taskkill /F /PID %%a >nul 2>&1

echo Stopped.
timeout /t 2 /nobreak >nul
