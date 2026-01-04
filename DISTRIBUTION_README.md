# Argus Intelligence Platform - USB Portable Edition

**Version:** 1.0
**Release Date:** January 3, 2026
**Package:** argus-usb-portable.zip (373 KB)

---

## 📦 What's Included

This portable USB deployment includes:

- ✅ **Complete Backend** - Python FastAPI application with all AI features
- ✅ **Production Frontend** - Pre-built React application (675 KB)
- ✅ **Cross-Platform Launchers** - Windows (.bat) and Linux (.sh) scripts
- ✅ **Ollama Support** - Auto-download llama3.2:1b (small, fast local AI model)
- ✅ **Setup Wizard** - First-run experience for API key configuration
- ✅ **Complete Documentation** - USB_README.txt + CREATE_USB_DEPLOYMENT.md

---

## 🚀 Quick Start

### **Windows 10/11:**
1. Extract `argus-usb-portable.zip` to your USB drive
2. Double-click `START_ARGUS_USB.bat`
3. Follow the on-screen prompts
4. Browser opens automatically with Setup Wizard

### **Linux (Ubuntu/Debian/Fedora/Arch):**
1. Extract `argus-usb-portable.zip` to your USB drive
2. Open terminal in the extracted folder
3. Run: `bash START_ARGUS_USB.sh`
4. Follow the on-screen prompts
5. Browser opens automatically

---

## 💾 Storage Options

When you launch Argus, you'll be prompted to choose where to store data:

| Option | Description | Best For |
|--------|-------------|----------|
| **USB Drive** | Same location as app | Small datasets, simple setup |
| **External HDD** | Separate external drive | Large document collections |
| **System Temp** | Cleared on restart | Sensitive data, temporary analysis |
| **Custom Path** | Your own location | Advanced users |

---

## 🔑 API Key Setup

On first launch, the Setup Wizard will guide you through configuring API keys:

### **Option 1: Cloud AI (Recommended)**
- **OpenAI** - Best performance, $0.50/million tokens
  - Get key: https://platform.openai.com/api-keys
- **Anthropic Claude** - High quality, good for analysis
  - Get key: https://console.anthropic.com/account/keys

### **Option 2: Local AI (Free)**
- **Ollama** - Free, offline, privacy-focused
  - Install: https://ollama.ai
  - Launcher auto-downloads llama3.2:1b model (1.3 GB)
  - No API key needed!

### **Option 3: Skip Setup**
- Configure later via Settings page
- Can use Ollama without any API keys

---

## 📋 System Requirements

### **Minimum:**
- **OS:** Windows 10/11 or Linux (any modern distro)
- **Python:** 3.10 or higher
- **RAM:** 2 GB
- **Storage:** 500 MB (more for documents)
- **Internet:** Required for initial setup and API-based AI

### **Recommended:**
- **RAM:** 8 GB (for large document analysis)
- **Storage:** 5 GB+ (for Ollama + document storage)
- **CPU:** Multi-core for faster processing

---

## 🎯 Features

### **Document Analysis**
- Upload and analyze PDF, DOCX, XLSX, PPTX, TXT, Markdown, code files
- Automatic entity extraction (people, organizations, locations, dates)
- Metadata tracking and knowledge graph generation

### **AI-Powered Chat**
- Multi-provider support (OpenAI, Anthropic, Google, Ollama)
- Document-aware conversations
- System prompt customization
- Text-to-speech with adjustable speed

### **Knowledge Canvas**
- Visual relationship mapping
- Entity clustering and analysis
- Timeline generation
- Interactive graph exploration

### **OSINT Tools**
- Web scraping and content extraction
- Email intelligence gathering
- IP and hash lookups
- Artifact detection

### **Metadata Analysis**
- Cross-document entity tracking
- Co-occurrence analysis
- Timeline reconstruction
- Pattern detection

---

## 📂 Package Structure

```
argus-usb-portable/
├── START_ARGUS_USB.bat          # Windows launcher
├── START_ARGUS_USB.sh           # Linux launcher
├── USB_README.txt               # Quick start guide
├── CREATE_USB_DEPLOYMENT.md     # Detailed documentation
├── README.md                    # Project overview
├── backend/                     # Python backend application
│   ├── requirements.txt         # Python dependencies
│   ├── .env.template           # Configuration template
│   └── app/                    # FastAPI application
│       ├── main.py
│       ├── api/                # API routes
│       ├── core/               # Core services
│       ├── models/             # Data models
│       └── utils/              # Utilities
└── frontend-dist/              # Pre-built React app
    ├── index.html
    └── assets/
        ├── index-*.js          # JavaScript bundle (675 KB)
        └── index-*.css         # Styles (104 KB)
```

---

## 🔧 First Launch Process

The launcher will automatically:

1. **[1/7] Check Python** - Verify Python 3.10+ is installed
2. **[2/7] Check Ollama** - Detect Ollama and download llama3.2:1b if available
3. **[3/7] Configure Storage** - Prompt for storage location
4. **[4/7] Install Dependencies** - Create virtual environment and install packages (~5-10 minutes first time)
5. **[5/7] Start Backend** - Launch FastAPI server on http://localhost:8000
6. **[6/7] Start Frontend** - Launch frontend server on http://localhost:5173
7. **[7/7] Open Browser** - Automatically open Argus with Setup Wizard

---

## ⚙️ Configuration

### **API Keys (via Setup Wizard or Settings Page)**
Keys are stored locally in browser localStorage:
- `api_key_openai` - OpenAI API key
- `api_key_anthropic` - Anthropic API key
- `api_key_google` - Google AI API key
- `setup_completed` - Setup wizard flag

### **Backend Configuration (.env.template)**
```bash
# Environment
DEBUG=False
ENVIRONMENT=production

# Ollama (auto-configured by launcher)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b

# Storage (set by launcher based on user choice)
STORAGE_PATH=./storage_external
DATABASE_PATH=./storage/database/research_tool.db
UPLOAD_DIR=./storage/uploads

# Security (change in production)
API_KEY=change-this-to-a-random-string
SECRET_KEY=change-this-to-another-random-string

# CORS
CORS_ORIGINS=["http://localhost:5173"]

# Features
FEATURE_EPSTEIN_MODE=True
FEATURE_URL_EXTRACTION=False
```

---

## 🛠️ Troubleshooting

### **Python Not Found**
- **Windows:** Install from https://www.python.org/downloads/ (check "Add Python to PATH")
- **Linux:** `sudo apt install python3 python3-pip` (Ubuntu/Debian)

### **Backend Fails to Start**
- Check `backend/backend.log` for errors
- Ensure port 8000 is not in use: `lsof -ti:8000` (Linux) or `netstat -ano | findstr :8000` (Windows)
- Try re-running the launcher (dependencies may have failed to install)

### **Frontend Not Loading**
- Ensure port 5173 is not in use
- Check browser console for errors (F12)
- Verify `frontend-dist/index.html` exists

### **Ollama Model Download Slow**
- llama3.2:1b is 1.3 GB - first download takes 1-3 minutes depending on connection
- Subsequent launches skip download (model is cached)

### **Permission Errors on USB**
- Virtual environment is created in system temp (/tmp on Linux, %TEMP% on Windows)
- This bypasses USB filesystem limitations (no symlink support)

---

## 🔒 Security Notes

### **API Key Storage**
- Keys stored in browser localStorage (local-only, not sent to server)
- For USB deployments, keys are cleared when browser cache is cleared
- Never commit .env files with real API keys to version control

### **Data Privacy**
- All document processing happens locally
- AI providers (OpenAI, Anthropic) receive only the specific prompts you send
- Ollama runs completely offline - no data leaves your machine

### **Network Security**
- Backend runs on localhost only (not accessible from network)
- CORS configured to only allow frontend access
- No external connections except to AI provider APIs (if configured)

---

## 📈 Performance Tips

### **Faster Startup**
- After first launch, dependencies are cached (subsequent starts take ~10 seconds)
- Keep virtual environment in /tmp or %TEMP% (automatic)
- Use Ollama for instant responses (no API latency)

### **Large Document Collections**
- Use External HDD storage option (not USB)
- Consider cloud AI for faster processing (OpenAI GPT-4 Turbo)
- Enable batch processing for multiple documents

### **Memory Optimization**
- Close unused browser tabs
- Restart backend if memory grows (Stop → Start launcher)
- Use Ollama llama3.2:1b for low-memory environments (only 1.3 GB)

---

## 🆘 Support

### **Documentation**
- USB_README.txt - Quick start
- CREATE_USB_DEPLOYMENT.md - Detailed setup guide
- README.md - Project overview

### **Issues & Feedback**
- GitHub: https://github.com/anthropics/argus/issues
- Email: support@argusai.example.com (if available)

### **Community**
- Discord: https://discord.gg/argusai (if available)
- Forum: https://community.argusai.example.com (if available)

---

## 📜 License

[Include your license information here]

---

## 🙏 Credits

- Built with FastAPI, React, TypeScript, Python
- AI powered by OpenAI, Anthropic, Google, and Ollama
- Icons by Lucide React
- PDF parsing with PyMuPDF
- Entity extraction with spaCy

---

## 📝 Version History

### **v1.0 (January 3, 2026)**
- ✅ Initial USB portable release
- ✅ Cross-platform launchers (Windows + Linux)
- ✅ Setup wizard for first-run experience
- ✅ Ollama integration with llama3.2:1b
- ✅ External storage configuration
- ✅ API key management via Settings page
- ✅ Complete document analysis pipeline
- ✅ Knowledge canvas and metadata tracking

---

**Made with ❤️ for investigators, researchers, and analysts**

*For questions or support, see USB_README.txt or CREATE_USB_DEPLOYMENT.md*
