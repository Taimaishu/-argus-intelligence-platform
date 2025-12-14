# Quick Start Guide - Argus Intelligence Platform

Get up and running with Argus in under 5 minutes!

## 🚀 Fast Track with Docker

**Easiest way to run Argus:**

```bash
# Clone the repository
git clone https://github.com/Taimaishu/-argus-intelligence-platform.git
cd -argus-intelligence-platform

# Start everything with Docker Compose
docker-compose up -d

# Access the platform
open http://localhost:3000
```

That's it! Argus is now running with:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📋 Manual Setup (Development)

### Step 1: Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure Environment (Optional)
```bash
# Copy example .env
cp .env.example .env

# Edit .env to add your API keys (optional)
# - OPENAI_API_KEY=your_key_here
# - ANTHROPIC_API_KEY=your_key_here
# - SHODAN_API_KEY=your_key_here
# - VT_API_KEY=your_key_here
```

### Step 3: Start Backend
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Frontend Setup (New Terminal)
```bash
cd frontend
npm install
npm run dev
```

### Step 5: Access the Platform
Open http://localhost:3000 in your browser

## 🔧 Install Ollama (For Local AI)

Argus works best with Ollama for privacy-focused local AI:

```bash
# Install Ollama from https://ollama.ai
curl -fsSL https://ollama.com/install.sh | sh

# Pull recommended models
ollama pull llama3.1:8b        # Best for chat
ollama pull nomic-embed-text   # For embeddings

# Verify it's running
ollama list
```

## 🎯 Example Investigation Workflow

### 1. Upload Documents
- Navigate to **Documents** page
- Drag & drop your research files (PDFs, DOCX, etc.)
- Wait for AI processing to complete

### 2. Semantic Search
- Go to **Search** page
- Ask natural language questions:
  - "What are the main security vulnerabilities?"
  - "Show me all references to cryptocurrency"
  - "Find connections between these organizations"

### 3. OSINT Analysis
- Visit **OSINT** page
- **Artifact Analysis** tab:
  - Paste IP addresses, domains, hashes, or URLs
  - Get instant threat intelligence from Shodan/VirusTotal
- **Web Scraper** tab:
  - Scrape websites for intelligence gathering
  - Extract emails, phones, social media links

### 4. Build Investigation Map
- Open **Canvas** page
- Click "Add Node" → Create document/insight/note nodes
- Draw connections between related items
- Visualize your investigation timeline

### 5. Discover Patterns
- Check **Patterns** page
- View AI-discovered document clusters
- See network analysis showing central documents
- Find suggested connections you might have missed

### 6. Chat with AI Assistant
- Go to **Chat** page
- Switch between providers (Ollama/OpenAI/Anthropic)
- Select models from dropdown
- Brainstorm theories and get insights from your documents

## 🔐 Privacy & Security

**Local-First Mode (Default):**
- No API keys needed
- Everything runs on your machine
- Ollama for AI (100% local)
- Zero data collection

**API-Enhanced Mode (Optional):**
- Add API keys in `.env` for enhanced capabilities
- Switch providers in Chat interface
- Still processes documents locally
- Only chat queries sent to APIs

## 📊 System Requirements

**Minimum:**
- 8GB RAM
- 4 CPU cores
- 10GB disk space

**Recommended:**
- 16GB+ RAM
- 8 CPU cores
- 50GB disk space (for models)
- GPU (optional, speeds up Ollama)

## 🧪 Testing the Installation

```bash
# Check backend
curl http://localhost:8000/health

# Expected: {"status":"healthy","version":"1.0.0"}

# Check frontend
curl http://localhost:3000

# Expected: HTML content
```

## 🆘 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Need 3.13+

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Frontend build errors
```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Ollama connection failed
```bash
# Check if Ollama is running
ollama list

# Start Ollama (if not running)
ollama serve

# Verify models are installed
ollama pull llama3.1:8b
```

### Docker issues
```bash
# Clean Docker and rebuild
docker-compose down -v
docker system prune -a
docker-compose up --build
```

## 🎓 Next Steps

1. **Read the full README** for detailed features
2. **Check CONTRIBUTING.md** to contribute
3. **Explore API docs** at http://localhost:8000/docs
4. **Join discussions** on GitHub for questions

## 💡 Pro Tips

- **Model Management**: Use Chat page settings to pull Ollama models directly from UI
- **Batch Upload**: Select multiple documents at once for processing
- **Keyboard Shortcuts**: Cmd/Ctrl + K for quick search (coming soon)
- **Auto-save**: Canvas auto-saves every 2 seconds
- **Dark Mode**: Toggle in header (persists across sessions)

## 📚 Example Use Cases

**Cybersecurity Investigation:**
```
1. Upload: Threat reports, IOC lists, vulnerability databases
2. Search: "Find all references to this IP address"
3. OSINT: Analyze IPs/domains with Shodan/VirusTotal
4. Canvas: Map attack infrastructure
5. Patterns: Discover connections between incidents
```

**Research Project:**
```
1. Upload: Academic papers, articles, notes
2. Search: "What are the key findings about X?"
3. Chat: "Summarize the main theories"
4. Canvas: Build concept map
5. Patterns: Find thematic clusters
```

**Investigative Journalism:**
```
1. Upload: Documents, leaks, court records
2. Search: "Show all mentions of this person"
3. OSINT: Track web presence, emails
4. Canvas: Timeline of events
5. Patterns: Discover hidden connections
```

---

**Ready to investigate? Start uploading documents and discover insights! 🔍**
