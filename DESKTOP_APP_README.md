# Argus Desktop Application

## 🎉 Installation Complete!

Argus is now installed as a desktop application with a Greek giant icon (Argus Panoptes - the all-seeing).

---

## 🚀 How to Launch

### Method 1: From Application Menu (Easiest)
1. Open your application menu (press Super/Windows key)
2. Search for **"Argus"**
3. Click the Argus icon (Greek giant with multiple eyes)
4. The app will automatically:
   - Start the backend server
   - Start the frontend server
   - Open in your browser

### Method 2: From Terminal
```bash
/home/taimaishu/argus-intelligence-platform/argus-app-launcher.sh
```

### Method 3: From Desktop File
Double-click: `Argus.desktop` in the installation folder

---

## 🛑 How to Stop

### Method 1: From Application Menu
1. Right-click the Argus icon in the application menu
2. Select **"Stop Argus"**

### Method 2: From Terminal
```bash
/home/taimaishu/argus-intelligence-platform/argus-app-stop.sh
```

---

## 📂 Files Installed

```
argus-intelligence-platform/
├── argus-app-launcher.sh    # Main launcher script
├── argus-app-stop.sh         # Stop script
├── argus-icon.svg            # Icon (SVG)
├── argus-icon.png            # Icon (256x256)
├── argus-icon-128.png        # Icon (128x128)
├── argus-icon-64.png         # Icon (64x64)
└── Argus.desktop             # Desktop entry

~/.local/share/applications/
└── Argus.desktop             # Installed desktop entry

~/.argus/
├── logs/                     # Application logs
│   ├── launcher.log
│   ├── backend.log
│   └── frontend.log
└── pids/                     # Process IDs
    ├── backend.pid
    └── frontend.pid
```

---

## 📝 Application Details

**Name:** Argus
**Category:** Office, Development, Network, Security
**Icon:** Greek giant Argus Panoptes with multiple eyes (all-seeing)
**Backend:** http://localhost:8000
**Frontend:** http://localhost:5173

---

## 🔍 Features

- **One-Click Launch:** No terminal needed
- **Automatic Startup:** Both servers start automatically
- **Browser Opens:** Automatically opens in your default browser
- **Clean Shutdown:** Gracefully stops all services
- **Logging:** All logs saved to `~/.argus/logs/`
- **Status Tracking:** PID files prevent duplicate instances

---

## 🐛 Troubleshooting

### App won't start?
1. Check logs: `tail -f ~/.argus/logs/launcher.log`
2. Make sure ports 8000 and 5173 are free
3. Try manual launch to see errors

### Icon not showing?
```bash
update-desktop-database ~/.local/share/applications/
```

### Already running error?
```bash
# Stop existing instance
/home/taimaishu/argus-intelligence-platform/argus-app-stop.sh

# Then launch again
```

---

## 🎨 Icon Design

The icon features **Argus Panoptes**, the all-seeing giant from Greek mythology:
- Golden/bronze body representing the giant
- Multiple blue eyes (13 eyes visible) representing omniscient surveillance
- Greek helmet/crown
- Glowing aura representing divine sight
- Golden border with Greek motifs

---

## 🔄 Updates

To update Argus:
```bash
cd /home/taimaishu/argus-intelligence-platform
git pull  # if using git
# Launcher scripts will use the updated code automatically
```

---

## 🎓 Icon Meaning

**Argus Panoptes** (Ἄργος Πανόπτης):
- "All-seeing" guardian in Greek mythology
- Had 100 eyes that never all closed at once
- Perfect symbol for an intelligence platform
- Represents vigilance, surveillance, and complete awareness

---

**Enjoy your all-seeing intelligence platform! 👁️**
