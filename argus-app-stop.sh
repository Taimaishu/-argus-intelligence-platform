#!/bin/bash
###############################################################################
# Argus Intelligence Platform - Stop Script
# Gracefully stops both backend and frontend servers
###############################################################################

set -e

PID_DIR="$HOME/.argus/pids"
LOG_DIR="$HOME/.argus/logs"

# Logging functions
log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $*" | tee -a "$LOG_DIR/launcher.log"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "$LOG_DIR/launcher.log" >&2
}

# Stop backend
stop_backend() {
    if [ -f "$PID_DIR/backend.pid" ]; then
        BACKEND_PID=$(cat "$PID_DIR/backend.pid")
        if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
            log_info "Stopping backend (PID: $BACKEND_PID)..."
            kill -TERM "$BACKEND_PID" 2>/dev/null || kill -9 "$BACKEND_PID" 2>/dev/null
            rm -f "$PID_DIR/backend.pid"
            log_info "Backend stopped"
        else
            log_info "Backend is not running"
            rm -f "$PID_DIR/backend.pid"
        fi
    else
        log_info "Backend PID file not found"
    fi
}

# Stop frontend
stop_frontend() {
    if [ -f "$PID_DIR/frontend.pid" ]; then
        FRONTEND_PID=$(cat "$PID_DIR/frontend.pid")
        if ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
            log_info "Stopping frontend (PID: $FRONTEND_PID)..."
            kill -TERM "$FRONTEND_PID" 2>/dev/null || kill -9 "$FRONTEND_PID" 2>/dev/null
            rm -f "$PID_DIR/frontend.pid"
            log_info "Frontend stopped"
        else
            log_info "Frontend is not running"
            rm -f "$PID_DIR/frontend.pid"
        fi
    else
        log_info "Frontend PID file not found"
    fi

    # Also kill any remaining vite processes
    pkill -f "vite" 2>/dev/null || true
}

# Main execution
main() {
    log_info "========================================="
    log_info "Stopping Argus Intelligence Platform..."
    log_info "========================================="

    stop_backend
    stop_frontend

    log_info "========================================="
    log_info "Argus stopped successfully"
    log_info "========================================="
}

main
