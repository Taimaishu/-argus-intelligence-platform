@echo off
REM Argus Intelligence Platform - Start Frontend
REM Run this script to start the React frontend development server

echo ========================================
echo Argus Intelligence Platform - Frontend
echo ========================================
echo.

cd frontend

echo Starting Vite development server...
echo Frontend will be available at: http://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev

pause
