#!/bin/bash

# Argus Intelligence Platform - Linux USB Launcher
# Portable deployment for Linux distributions

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Argus Intelligence Platform${NC}"
echo -e "${BLUE}  USB Portable Edition${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Get USB path
USB_PATH="$(dirname "$(readlink -f "$0")")"
cd "$USB_PATH" || exit 1

# Check Python
echo -e "${YELLOW}[1/6] Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    echo ""
    echo "Please install Python 3.10+ using your package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  Fedora:        sudo dnf install python3 python3-pip"
    echo "  Arch:          sudo pacman -S python python-pip"
    echo ""
    exit 1
fi
python3 --version
echo -e "${GREEN}OK!${NC}"
echo ""

# Storage configuration
echo -e "${YELLOW}[2/6] Configuring storage location...${NC}"
echo ""
echo "Where should Argus store documents and data?"
echo ""
echo "  1. USB Drive (same as app) - Limited by USB size"
echo "  2. External Hard Drive - Recommended for large datasets"
echo "  3. System Temp Folder - Cleared on restart, good for sensitive data"
echo "  4. Custom Location - Specify your own path"
echo ""
read -p "Enter choice (1-4) [default: 1]: " STORAGE_CHOICE
STORAGE_CHOICE=${STORAGE_CHOICE:-1}

case $STORAGE_CHOICE in
    2)
        echo ""
        read -p "Enter external drive path (e.g., /mnt/external/argus-data): " CUSTOM_STORAGE
        STORAGE_PATH="$CUSTOM_STORAGE"
        ;;
    3)
        STORAGE_PATH="/tmp/argus-storage"
        ;;
    4)
        echo ""
        read -p "Enter custom path: " CUSTOM_STORAGE
        STORAGE_PATH="$CUSTOM_STORAGE"
        ;;
    *)
        STORAGE_PATH="$USB_PATH/storage_external"
        ;;
esac

echo ""
echo -e "Storage location: ${GREEN}$STORAGE_PATH${NC}"
mkdir -p "$STORAGE_PATH/database"
mkdir -p "$STORAGE_PATH/uploads"
echo -e "${GREEN}OK!${NC}"
echo ""

# Set environment variables
export DATABASE_PATH="$STORAGE_PATH/database/research_tool.db"
export UPLOAD_DIR="$STORAGE_PATH/uploads"

# Install backend dependencies
echo -e "${YELLOW}[3/6] Installing backend dependencies...${NC}"
cd backend || exit 1

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}ERROR: pip3 is not installed${NC}"
    echo "Please install pip3 using your package manager"
    exit 1
fi

pip3 install --quiet --upgrade pip
pip3 install --quiet -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to install backend dependencies${NC}"
    echo "Check backend.log for details"
    exit 1
fi
echo -e "${GREEN}OK!${NC}"
echo ""

# Start backend server
echo -e "${YELLOW}[4/6] Starting backend server...${NC}"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend server starting on http://localhost:8000 (PID: $BACKEND_PID)"
sleep 5

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${YELLOW}WARNING: Backend may not have started properly${NC}"
    echo "Check backend.log for errors"
    sleep 3
fi
echo -e "${GREEN}OK!${NC}"
echo ""

# Start frontend server
echo -e "${YELLOW}[5/6] Starting frontend server...${NC}"
cd ../frontend-dist || exit 1

if [ ! -f "index.html" ]; then
    echo -e "${RED}ERROR: Frontend files not found!${NC}"
    echo ""
    echo "Please build the frontend first:"
    echo "  cd frontend"
    echo "  npm run build"
    echo "  cp -r dist ../frontend-dist"
    echo ""
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

python3 -m http.server 5173 > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend server starting on http://localhost:5173 (PID: $FRONTEND_PID)"
sleep 3
echo -e "${GREEN}OK!${NC}"
echo ""

# Display success message
echo -e "${YELLOW}[6/6] Opening Argus in browser...${NC}"
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Argus is now running!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "  Frontend:  ${BLUE}http://localhost:5173${NC}"
echo -e "  Backend:   ${BLUE}http://localhost:8000${NC}"
echo -e "  Storage:   ${BLUE}$STORAGE_PATH${NC}"
echo ""
echo "First time? The setup wizard will guide you through API key configuration."
echo ""
echo "To stop Argus, press ${YELLOW}Enter${NC} in this terminal"
echo ""
echo -e "${GREEN}============================================${NC}"
echo ""

# Open browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5173 &
elif command -v gnome-open &> /dev/null; then
    gnome-open http://localhost:5173 &
elif command -v kde-open &> /dev/null; then
    kde-open http://localhost:5173 &
else
    echo "Please open http://localhost:5173 in your browser"
fi

# Wait for user to stop
echo -e "${YELLOW}Argus is running. Press Enter to stop...${NC}"
read

# Cleanup
echo ""
echo "Stopping Argus..."
kill $BACKEND_PID 2>/dev/null
kill $FRONTEND_PID 2>/dev/null

# Also kill any remaining processes on those ports
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

echo -e "${GREEN}Stopped.${NC}"
sleep 2
