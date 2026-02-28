#!/bin/bash
###############################################################################
# Argus Intelligence Platform - Application Launcher
# Starts both backend and frontend servers automatically
###############################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$HOME/.argus/logs"
PID_DIR="$HOME/.argus/pids"

# Create directories if they don't exist
mkdir -p "$LOG_DIR" "$PID_DIR"

# Logging functions
log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $*" | tee -a "$LOG_DIR/launcher.log"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "$LOG_DIR/launcher.log" >&2
}

# Check if already running
check_if_running() {
    if [ -f "$PID_DIR/backend.pid" ]; then
        BACKEND_PID=$(cat "$PID_DIR/backend.pid")
        if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
            log_info "Backend already running (PID: $BACKEND_PID)"
            BACKEND_RUNNING=true
        else
            rm -f "$PID_DIR/backend.pid"
            BACKEND_RUNNING=false
        fi
    else
        BACKEND_RUNNING=false
    fi

    if [ -f "$PID_DIR/frontend.pid" ]; then
        FRONTEND_PID=$(cat "$PID_DIR/frontend.pid")
        if ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
            log_info "Frontend already running (PID: $FRONTEND_PID)"
            FRONTEND_RUNNING=true
        else
            rm -f "$PID_DIR/frontend.pid"
            FRONTEND_RUNNING=false
        fi
    else
        FRONTEND_RUNNING=false
    fi
}

# Start backend
start_backend() {
    if [ "$BACKEND_RUNNING" = true ]; then
        log_info "Backend already running, skipping..."
        return 0
    fi

    log_info "Starting Argus backend server..."
    cd "$SCRIPT_DIR/backend"

    # Activate virtual environment and start uvicorn in background
    source venv/bin/activate
    nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 \
        > "$LOG_DIR/backend.log" 2>&1 &

    BACKEND_PID=$!
    echo $BACKEND_PID > "$PID_DIR/backend.pid"
    log_info "Backend started (PID: $BACKEND_PID)"

    # Wait for backend to be ready
    log_info "Waiting for backend to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            log_info "Backend is ready!"
            return 0
        fi
        sleep 1
    done

    log_error "Backend failed to start properly"
    return 1
}

# Start frontend
start_frontend() {
    if [ "$FRONTEND_RUNNING" = true ]; then
        log_info "Frontend already running, skipping..."
        return 0
    fi

    log_info "Starting Argus frontend server..."
    cd "$SCRIPT_DIR/frontend"

    nohup npm run dev > "$LOG_DIR/frontend.log" 2>&1 &

    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$PID_DIR/frontend.pid"
    log_info "Frontend started (PID: $FRONTEND_PID)"

    # Wait for frontend to be ready
    log_info "Waiting for frontend to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:5173 > /dev/null 2>&1; then
            log_info "Frontend is ready!"
            return 0
        fi
        sleep 1
    done

    log_error "Frontend failed to start properly"
    return 1
}

# Open browser
open_browser() {
    log_info "Opening Argus in browser..."
    sleep 2

    # Try different browser commands
    if command -v xdg-open > /dev/null 2>&1; then
        xdg-open "http://localhost:5173" > /dev/null 2>&1
    elif command -v gnome-open > /dev/null 2>&1; then
        gnome-open "http://localhost:5173" > /dev/null 2>&1
    elif command -v firefox > /dev/null 2>&1; then
        firefox "http://localhost:5173" > /dev/null 2>&1 &
    elif command -v google-chrome > /dev/null 2>&1; then
        google-chrome "http://localhost:5173" > /dev/null 2>&1 &
    else
        log_info "Please open http://localhost:5173 in your browser"
    fi
}

# Main execution
main() {
    log_info "========================================="
    log_info "Argus Intelligence Platform Starting..."
    log_info "========================================="

    check_if_running

    if start_backend && start_frontend; then
        log_info "========================================="
        log_info "Argus is running!"
        log_info "Frontend: http://localhost:5173"
        log_info "Backend:  http://localhost:8000"
        log_info "========================================="
        log_info ""
        log_info "Logs are available at: $LOG_DIR"
        log_info "To stop Argus, run: $SCRIPT_DIR/argus-app-stop.sh"

        open_browser

        exit 0
    else
        log_error "Failed to start Argus"
        log_error "Check logs at: $LOG_DIR"
        exit 1
    fi
}

main
