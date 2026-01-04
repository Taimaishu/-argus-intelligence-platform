#!/bin/bash
# One-click startup script for Argus Intelligence Platform

echo "🚀 Starting Argus Intelligence Platform..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down Argus..."
    kill $(jobs -p) 2>/dev/null
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    lsof -ti:5173 | xargs kill -9 2>/dev/null
    exit
}
trap cleanup SIGINT SIGTERM

# Clean up any existing processes on our ports
echo -e "${YELLOW}Cleaning up existing processes...${NC}"
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null
sleep 1

# Start Backend
echo -e "${BLUE}[1/2]${NC} Starting Backend Server..."
cd backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}✗${NC} Virtual environment not found!"
    echo "Run: cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate venv and start
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/argus-backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "Waiting for backend to start..."
sleep 3

# Check if backend started successfully
if kill -0 $BACKEND_PID 2>/dev/null; then
    # Double check by trying to connect
    if curl -s http://localhost:8000/health > /dev/null 2>&1 || [ $? -eq 7 ]; then
        echo -e "${GREEN}✓${NC} Backend running on http://localhost:8000"
    else
        echo -e "${YELLOW}⚠${NC} Backend starting... (checking again)"
        sleep 2
        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo -e "${GREEN}✓${NC} Backend running on http://localhost:8000"
        else
            echo -e "${RED}✗${NC} Backend failed to start. Check /tmp/argus-backend.log"
            echo ""
            echo "Last 10 lines of log:"
            tail -10 /tmp/argus-backend.log
            exit 1
        fi
    fi
else
    echo -e "${RED}✗${NC} Backend failed to start. Check /tmp/argus-backend.log"
    echo ""
    echo "Last 10 lines of log:"
    tail -10 /tmp/argus-backend.log
    exit 1
fi

# Start Frontend
echo -e "${BLUE}[2/2]${NC} Starting Frontend Server..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠${NC} Installing frontend dependencies (this may take a minute)..."
    npm install > /tmp/argus-npm-install.log 2>&1
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗${NC} Failed to install frontend dependencies"
        tail -10 /tmp/argus-npm-install.log
        kill $BACKEND_PID
        exit 1
    fi
fi

npm run dev > /tmp/argus-frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "Waiting for frontend to start..."
sleep 4

# Check if frontend started successfully
if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Frontend running on http://localhost:5173"
else
    echo -e "${RED}✗${NC} Frontend failed to start. Check /tmp/argus-frontend.log"
    echo ""
    echo "Last 10 lines of log:"
    tail -10 /tmp/argus-frontend.log
    kill $BACKEND_PID
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║   🎉 Argus Intelligence Platform Ready!   ║"
echo "╠════════════════════════════════════════════╣"
echo "║  Frontend: http://localhost:5173           ║"
echo "║  Backend:  http://localhost:8000           ║"
echo "║  API Docs: http://localhost:8000/docs      ║"
echo "╠════════════════════════════════════════════╣"
echo "║  Press Ctrl+C to stop all services         ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo -e "${YELLOW}💡 Tip: Open http://localhost:5173 in your browser${NC}"
echo ""

# Keep script running and show simplified status
echo "📋 Services running (logs in /tmp/argus-*.log)"
echo "   Press Ctrl+C to stop"
echo ""

# Wait indefinitely
wait
