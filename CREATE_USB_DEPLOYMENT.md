# Create Argus USB Deployment

This guide will help you create a portable USB deployment of Argus that works on both Windows 10 and Linux.

## Requirements

- USB drive (8GB minimum for app, documents stored separately)
- Python 3.10+ installed on target systems
- Node.js 18+ installed on target systems (optional if pre-building frontend)

## Quick Setup

### 1. Prepare USB Drive

Format your USB drive with exFAT (works on both Windows and Linux):
- **Windows**: Right-click drive → Format → exFAT
- **Linux**: `sudo mkfs.exfat /dev/sdX1` (replace sdX1 with your USB device)

### 2. Copy Deployment Files

Run the deployment script:

```bash
# From the argus-intelligence-platform directory
python3 create_usb_deployment.py /path/to/usb
```

Or manually copy:
```bash
USB_PATH="/media/usb"  # Change to your USB mount point

# Copy backend
cp -r backend $USB_PATH/
cp requirements.txt $USB_PATH/

# Copy frontend (built version)
cd frontend
npm run build
cp -r dist $USB_PATH/frontend-dist/

# Copy launcher scripts
cp usb-launcher-*.sh $USB_PATH/
cp usb-launcher-*.bat $USB_PATH/
```

### 3. Configure External Storage

Edit `backend/.env` on the USB:

```env
# Store data on external drive (not USB)
STORAGE_PATH=./storage_external

# Or use system temp directory
# STORAGE_PATH=/tmp/argus-storage

# Database (lightweight, can stay on USB)
DATABASE_PATH=./storage/database/research_tool.db
```

## Launch Scripts

### Windows (`START_ARGUS.bat`)

Double-click to start Argus on Windows:

```batch
@echo off
echo Starting Argus Intelligence Platform...

REM Get USB drive letter
set USB_DRIVE=%~d0
cd /d "%USB_DRIVE%"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

REM Ask for storage location
echo.
echo Where do you want to store documents and data?
echo 1. Same drive as USB (may fill up)
echo 2. External hard drive (recommended)
echo 3. System temp folder
echo.
set /p STORAGE_CHOICE="Enter choice (1-3): "

if "%STORAGE_CHOICE%"=="2" (
    set /p STORAGE_PATH="Enter full path to external drive (e.g., E:\argus-data): "
) else if "%STORAGE_CHOICE%"=="3" (
    set STORAGE_PATH=%TEMP%\argus-storage
) else (
    set STORAGE_PATH=%USB_DRIVE%\storage_external
)

echo.
echo Using storage location: %STORAGE_PATH%
mkdir "%STORAGE_PATH%" 2>nul

REM Start backend
cd backend
echo Installing Python dependencies...
python -m pip install -q -r requirements.txt

echo Starting backend server...
start /B cmd /c "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1"

REM Wait for backend
timeout /t 5 /nobreak

REM Start frontend
cd ..\frontend-dist
echo Starting frontend server...
start /B cmd /c "python -m http.server 5173 > frontend.log 2>&1"

REM Wait for frontend
timeout /t 3 /nobreak

REM Open browser
echo.
echo ============================================
echo Argus Intelligence Platform is now running!
echo ============================================
echo.
echo Frontend: http://localhost:5173
echo Backend API: http://localhost:8000
echo.
echo Press Ctrl+C in this window to stop Argus
echo.

start http://localhost:5173

REM Keep window open
pause
```

### Linux (`START_ARGUS.sh`)

Make executable and run:

```bash
#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Argus Intelligence Platform...${NC}"

# Get USB mount point
USB_PATH="$(dirname "$(readlink -f "$0")")"
cd "$USB_PATH"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    echo "Please install Python 3.10+ using your package manager"
    exit 1
fi

# Ask for storage location
echo ""
echo "Where do you want to store documents and data?"
echo "1. Same drive as USB (may fill up)"
echo "2. External hard drive (recommended)"
echo "3. System temp folder"
echo ""
read -p "Enter choice (1-3): " STORAGE_CHOICE

case $STORAGE_CHOICE in
    2)
        read -p "Enter full path to external drive (e.g., /mnt/external/argus-data): " STORAGE_PATH
        ;;
    3)
        STORAGE_PATH="/tmp/argus-storage"
        ;;
    *)
        STORAGE_PATH="$USB_PATH/storage_external"
        ;;
esac

echo ""
echo -e "${GREEN}Using storage location: $STORAGE_PATH${NC}"
mkdir -p "$STORAGE_PATH"

# Export for backend
export STORAGE_PATH="$STORAGE_PATH"

# Start backend
cd backend
echo "Installing Python dependencies..."
pip3 install -q -r requirements.txt

echo "Starting backend server..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend
sleep 5

# Start frontend
cd ../frontend-dist
echo "Starting frontend server..."
python3 -m http.server 5173 > frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend
sleep 3

# Display info
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Argus Intelligence Platform is now running!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:8000"
echo ""
echo "Opening browser..."
xdg-open http://localhost:5173 2>/dev/null || echo "Please open http://localhost:5173 in your browser"

echo ""
echo -e "${YELLOW}Press Enter to stop Argus${NC}"
read

# Cleanup
echo "Stopping Argus..."
kill $BACKEND_PID 2>/dev/null
kill $FRONTEND_PID 2>/dev/null
echo "Stopped."
```

## Testing Setup Wizard

1. Open browser to http://localhost:5173
2. Clear localStorage: Press F12 → Console → Type: `localStorage.clear()` → Enter
3. Refresh page - Setup wizard should appear
4. Follow wizard to enter API keys
5. Verify keys are saved: Check Settings page

## Storage Options

### Option 1: USB Only (Simple but limited)
- All data on USB drive
- Limited by USB capacity
- Slower performance

### Option 2: External Drive (Recommended)
- App on USB, data on external HDD/SSD
- Unlimited capacity
- Better performance
- Configure via launcher or .env

### Option 3: System Temp (Temporary)
- Data cleared on system restart
- Good for sensitive investigations
- No persistent storage needed

## Configuration

Edit `backend/.env` on USB:

```env
# App settings
DEBUG=False
ENVIRONMENT=production

# Storage paths
STORAGE_PATH=/mnt/external/argus-data  # External drive
DATABASE_PATH=./storage/database/research_tool.db  # Keep DB on USB (small)

# API Keys (leave empty - users enter via UI)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=

# Security
API_KEY=your-random-key-here
CORS_ORIGINS=["http://localhost:5173"]
```

## Distribution

To distribute to others:

1. **Build portable package**:
   ```bash
   cd argus-intelligence-platform
   npm run build  # Build frontend
   zip -r argus-usb.zip backend/ frontend-dist/ *.sh *.bat README.md
   ```

2. **User extracts to USB**:
   - Extract zip to USB root
   - Run appropriate launcher script
   - Enter API keys in setup wizard

3. **First-time setup** (2-3 minutes):
   - Launcher installs Python dependencies
   - Opens browser with setup wizard
   - User enters API keys
   - Ready to use!

## Troubleshooting

### Windows Issues

**Python not found**:
```batch
# Add Python to PATH or use full path
C:\Python310\python.exe -m uvicorn ...
```

**Port already in use**:
```batch
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <pid> /F
```

### Linux Issues

**Permission denied**:
```bash
chmod +x START_ARGUS.sh
```

**Python module not found**:
```bash
pip3 install --user -r requirements.txt
```

**Port already in use**:
```bash
lsof -ti:8000 | xargs kill -9
```

## Security Notes

- **API Keys**: Stored only in browser localStorage (session only)
- **Data**: Encrypted at rest if using disk encryption
- **Network**: Runs on localhost only (no external access)
- **Cleanup**: Clear localStorage when done: `localStorage.clear()`

## Advanced: Pre-built Deployment

For systems without Node.js, pre-build the frontend:

```bash
cd frontend
npm install
npm run build
# Dist files in frontend/dist/
```

Then copy `dist/` to USB as `frontend-dist/` and serve with Python HTTP server (no Node.js needed on target system).
