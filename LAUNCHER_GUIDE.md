# 🚀 Argus Intelligence Platform - Launch Guide

## ✅ Three Ways to Launch

### 1. Desktop Icon (Recommended)
- **Location**: Your Desktop
- **Icon Name**: "Argus Intelligence Platform"
- **Action**: Double-click the icon
- A terminal will open showing startup progress

### 2. Application Menu
- **Location**: Application Menu → Development or Education
- **Search**: Type "Argus" in your application launcher
- **Action**: Click to launch

### 3. Command Line
```bash
cd ~/argus-intelligence-platform
./START_ARGUS.sh
```

## 📍 What Happens When You Launch

1. Terminal window opens showing startup progress
2. Backend starts on port 8000 (takes 3 seconds)
3. Frontend starts on port 5173 (takes 4 seconds)
4. Browser opens automatically at http://localhost:5173

## 🌐 Access Points

- **Main App**: http://localhost:5173
- **API Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🛑 How to Stop

In the terminal window that opened, press **Ctrl+C**

All services will shut down automatically.

## 🎨 Using the Canvas Auto-Generation

1. Click on "Canvas" in the navigation menu
2. Click the **"Auto-Generate"** button
3. System will:
   - Extract entities from Epstein documents
   - Create visual nodes (people, organizations, locations, etc.)
   - Draw connections between related entities
   - Apply force-directed layout
4. Click **"Show Chat"** to interact with the AI assistant
5. Try commands like:
   - "Show me all connections to Maxwell"
   - "Add Epstein as a person"
   - "Highlight all financial entities"
   - "Reorganize the canvas"

## 📂 Important Files

- **Launcher Script**: `~/argus-intelligence-platform/START_ARGUS.sh`
- **Desktop Icon**: `~/Desktop/argus-intelligence.desktop`
- **Menu Entry**: `~/.local/share/applications/argus-intelligence.desktop`
- **Icon Image**: `~/argus-intelligence-platform/argus-icon.png`
- **Backend Log**: `/tmp/argus-backend.log`
- **Frontend Log**: `/tmp/argus-frontend.log`

## 🔧 Troubleshooting

**Icon doesn't appear on desktop?**
- Right-click desktop → Refresh
- Or log out and log back in

**Icon shows "Untrusted Application"?**
- Right-click icon → "Allow Launching"

**Port already in use?**
- The START_ARGUS.sh script automatically cleans up old processes
- Just run it again

**Need to reset everything?**
```bash
cd ~/argus-intelligence-platform
lsof -ti:8000 | xargs kill -9
lsof -ti:5173 | xargs kill -9
./START_ARGUS.sh
```

## 💡 Tips

- Keep the terminal window open - it shows live status
- If you close the terminal, services will stop automatically
- You can check logs anytime: `tail -f /tmp/argus-backend.log`
- The platform auto-saves canvas changes
