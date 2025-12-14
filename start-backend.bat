@echo off
REM Argus Intelligence Platform - Start Backend
REM Run this script to start the FastAPI backend server

echo ========================================
echo Argus Intelligence Platform - Backend
echo ========================================
echo.

cd backend

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting FastAPI server...
echo Backend will be available at: http://localhost:8000
echo API documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
