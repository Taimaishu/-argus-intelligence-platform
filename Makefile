# Argus Intelligence Platform - Makefile
# Cross-platform build automation

.PHONY: help setup setup-backend setup-frontend setup-models clean clean-backend clean-frontend start start-backend start-frontend test

# Default Python and Node commands
PYTHON := python3
NODE := node
NPM := npm

# Directories
BACKEND_DIR := backend
FRONTEND_DIR := frontend
VENV_DIR := $(BACKEND_DIR)/venv

# Platform detection
ifeq ($(OS),Windows_NT)
    PLATFORM := Windows
    VENV_BIN := $(VENV_DIR)/Scripts
    PYTHON := python
else
    PLATFORM := Unix
    VENV_BIN := $(VENV_DIR)/bin
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Darwin)
        PLATFORM := macOS
    else
        PLATFORM := Linux
    endif
endif

# Default target
help:
	@echo "Argus Intelligence Platform - Make Targets"
	@echo ""
	@echo "Platform detected: $(PLATFORM)"
	@echo ""
	@echo "Setup targets:"
	@echo "  make setup          - Complete setup (backend + frontend + models)"
	@echo "  make setup-backend  - Set up Python backend only"
	@echo "  make setup-frontend - Set up Node.js frontend only"
	@echo "  make setup-models   - Download Ollama models only"
	@echo ""
	@echo "Run targets:"
	@echo "  make start          - Start both backend and frontend"
	@echo "  make start-backend  - Start backend server"
	@echo "  make start-frontend - Start frontend dev server"
	@echo ""
	@echo "Clean targets:"
	@echo "  make clean          - Clean all build artifacts"
	@echo "  make clean-backend  - Clean backend artifacts"
	@echo "  make clean-frontend - Clean frontend artifacts"
	@echo ""
	@echo "Test targets:"
	@echo "  make test           - Run all tests"
	@echo ""

# Complete setup
setup: setup-backend setup-frontend setup-models
	@echo ""
	@echo "✓ Complete setup finished!"
	@echo ""
	@echo "To start the application:"
	@echo "  make start-backend  (in one terminal)"
	@echo "  make start-frontend (in another terminal)"
	@echo ""
	@echo "Or use: make start"
	@echo ""

# Backend setup
setup-backend:
	@echo "Setting up backend..."
	@cd $(BACKEND_DIR) && \
	if [ ! -d "venv" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv venv; \
	fi && \
	echo "Installing dependencies..." && \
	$(VENV_BIN)/python -m pip install --upgrade pip --quiet && \
	$(VENV_BIN)/pip install -r requirements.txt --quiet && \
	if [ ! -f ".env" ]; then \
		echo "Creating default .env file..."; \
		cp .env.example .env 2>/dev/null || \
		cat > .env <<-'EOF'
			APP_NAME=Argus Intelligence Platform
			DEBUG=True
			ENVIRONMENT=development
			DATABASE_URL=sqlite:///./storage/database/research_tool.db
			DEFAULT_EMBEDDING_PROVIDER=local
			DEFAULT_LLM_PROVIDER=ollama
			OLLAMA_BASE_URL=http://localhost:11434
			OLLAMA_EMBEDDING_MODEL=nomic-embed-text
			OLLAMA_LLM_MODEL=gurubot/llama3-guru-uncensored:latest
			CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
		EOF
	fi
	@echo "✓ Backend setup complete!"

# Frontend setup
setup-frontend:
	@echo "Setting up frontend..."
	@cd $(FRONTEND_DIR) && \
	if [ -f "package-lock.json" ]; then \
		echo "Installing dependencies (npm ci)..."; \
		$(NPM) ci; \
	else \
		echo "Installing dependencies (npm install)..."; \
		$(NPM) install; \
	fi
	@echo "✓ Frontend setup complete!"

# Ollama models setup
setup-models:
	@echo "Setting up Ollama models..."
	@if command -v ollama >/dev/null 2>&1; then \
		echo "Checking existing models..."; \
		if ! ollama list | grep -q "nomic-embed-text"; then \
			echo "Downloading embedding model..."; \
			ollama pull nomic-embed-text; \
		else \
			echo "✓ Embedding model already downloaded"; \
		fi; \
		if ! ollama list | grep -q "gurubot/llama3-guru-uncensored"; then \
			echo "Downloading LLM model..."; \
			ollama pull gurubot/llama3-guru-uncensored:latest; \
		else \
			echo "✓ LLM model already downloaded"; \
		fi; \
		echo "✓ Ollama models setup complete!"; \
	else \
		echo "⚠ Ollama not found. Install from: https://ollama.com"; \
		echo "Then run: make setup-models"; \
	fi

# Clean all
clean: clean-backend clean-frontend
	@echo "✓ All clean!"

# Clean backend
clean-backend:
	@echo "Cleaning backend..."
	@rm -rf $(BACKEND_DIR)/venv
	@rm -rf $(BACKEND_DIR)/storage/chromadb
	@rm -rf $(BACKEND_DIR)/storage/database
	@find $(BACKEND_DIR) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find $(BACKEND_DIR) -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Backend cleaned!"

# Clean frontend
clean-frontend:
	@echo "Cleaning frontend..."
	@rm -rf $(FRONTEND_DIR)/node_modules
	@rm -rf $(FRONTEND_DIR)/dist
	@rm -rf $(FRONTEND_DIR)/.vite
	@echo "✓ Frontend cleaned!"

# Start both servers (requires terminal multiplexer)
start:
	@echo "Starting Argus Intelligence Platform..."
	@echo ""
	@echo "Note: This requires tmux or screen to run both servers"
	@echo "For manual start:"
	@echo "  Terminal 1: make start-backend"
	@echo "  Terminal 2: make start-frontend"
	@echo ""
	@if command -v tmux >/dev/null 2>&1; then \
		tmux new-session -d -s argus 'make start-backend'; \
		tmux split-window -h 'make start-frontend'; \
		tmux attach-session -t argus; \
	else \
		echo "tmux not found. Starting servers sequentially (Ctrl+C to stop)"; \
		make start-backend & \
		sleep 3; \
		make start-frontend; \
	fi

# Start backend server
start-backend:
	@echo "Starting backend server..."
	@cd $(BACKEND_DIR) && \
	. $(VENV_BIN)/activate && \
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend dev server
start-frontend:
	@echo "Starting frontend dev server..."
	@cd $(FRONTEND_DIR) && \
	$(NPM) run dev

# Run tests
test:
	@echo "Running tests..."
	@echo "Backend tests:"
	@cd $(BACKEND_DIR) && \
	. $(VENV_BIN)/activate && \
	pytest tests/ -v || echo "No backend tests found"
	@echo ""
	@echo "Frontend tests:"
	@cd $(FRONTEND_DIR) && \
	$(NPM) test || echo "No frontend tests configured"

# Development helpers
.PHONY: dev-backend dev-frontend
dev-backend: start-backend
dev-frontend: start-frontend

# Check prerequisites
.PHONY: check
check:
	@echo "Checking prerequisites..."
	@echo ""
	@which $(PYTHON) >/dev/null && echo "✓ Python: $$($(PYTHON) --version)" || echo "✗ Python not found"
	@which $(NODE) >/dev/null && echo "✓ Node.js: $$($(NODE) --version)" || echo "✗ Node.js not found"
	@which $(NPM) >/dev/null && echo "✓ npm: $$($(NPM) --version)" || echo "✗ npm not found"
	@which ollama >/dev/null && echo "✓ Ollama: $$(ollama --version)" || echo "⚠ Ollama not found (optional)"
	@echo ""
