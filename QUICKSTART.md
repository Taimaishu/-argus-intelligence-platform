# Argus Intelligence Platform - Quick Start

## 🚀 One-Click Launch

```bash
./START_ARGUS.sh
```

That's it! Wait 5 seconds for both services to start.

## 🌐 Access the Platform

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎨 Canvas Auto-Generation

1. Navigate to **Canvas** page
2. Click **"Auto-Generate"** button
3. System extracts entities from Epstein documents
4. Creates visual knowledge graph with connections
5. Click **"Show Chat"** to interact with AI assistant

## 💬 Canvas AI Commands

Try asking:
- "Show me all connections to Maxwell"
- "Add Epstein as a person"
- "Connect Maxwell and Clinton"
- "Highlight all financial entities"
- "Reorganize the canvas"

## 🛑 Stop Services

Press **Ctrl+C** in the terminal running START_ARGUS.sh

## 📋 View Logs

- Backend: `/tmp/argus-backend.log`
- Frontend: `/tmp/argus-frontend.log`

## 🔧 Manual Start (if needed)

**Backend:**
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```
