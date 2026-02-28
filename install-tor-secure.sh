#!/bin/bash
#
# Tor Installation and Configuration Script
# Sets up Tor with TAILS-like security features for deep web searches
#

echo "========================================="
echo "Tor Installation for Argus Platform"
echo "TAILS-like Security Configuration"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  This script should be run with sudo"
    echo "Run: sudo bash install-tor-secure.sh"
    exit 1
fi

echo "📦 Installing Tor..."

# Detect OS
if [ -f /etc/debian_version ]; then
    # Debian/Ubuntu
    apt-get update
    apt-get install -y tor tor-geoipdb torsocks
elif [ -f /etc/redhat-release ]; then
    # RedHat/CentOS/Fedora
    yum install -y tor torsocks
elif [ -f /etc/arch-release ]; then
    # Arch Linux
    pacman -S --noconfirm tor torsocks
else
    echo "❌ Unsupported OS. Please install Tor manually."
    exit 1
fi

echo "✅ Tor installed"
echo ""

# Install Python dependencies for Tor control
echo "📦 Installing Python Tor control dependencies..."
pip3 install stem pysocks requests[socks] || pip install stem pysocks requests[socks]
echo "✅ Python dependencies installed"
echo ""

# Configure Tor for enhanced security (TAILS-like)
echo "🔒 Configuring Tor for enhanced security..."

TOR_CONFIG="/etc/tor/torrc"
BACKUP_CONFIG="/etc/tor/torrc.backup.$(date +%Y%m%d_%H%M%S)"

# Backup original config
cp "$TOR_CONFIG" "$BACKUP_CONFIG"
echo "   Backup created: $BACKUP_CONFIG"

# Create secure Tor configuration
cat > "$TOR_CONFIG" << 'EOF'
# Argus Intelligence Platform - Secure Tor Configuration
# TAILS-like security settings

# SOCKS proxy
SOCKSPort 9050
SOCKSPolicy accept 127.0.0.1
SOCKSPolicy reject *

# Control port for circuit management
ControlPort 9051
# ControlPortWriteToFile /var/lib/tor/control_port

# Enhanced security settings
DataDirectory /var/lib/tor

# Prevent DNS leaks
DNSPort 0

# Circuit settings for anonymity
NewCircuitPeriod 60
MaxCircuitDirtiness 600
CircuitBuildTimeout 60

# Security: Isolate streams
IsolateDestAddr 1
IsolateDestPort 1

# Disable directory cache to reduce fingerprinting
DirCache 0

# Enhanced anonymity
EnforceDistinctSubnets 1

# Exclude bad exit nodes
ExcludeExitNodes {??}
StrictNodes 0

# Logging (minimal for security)
Log notice file /var/log/tor/notices.log

# No relay/exit node (client only)
ORPort 0
DirPort 0

# Security hardening
ClientOnly 1
SafeLogging 1

# Prevent leaks
DisableDebuggerAttachment 1

# Connection limits
ConnLimit 100

# Timeout settings
CircuitStreamTimeout 60
LearnCircuitBuildTimeout 1

# Enhanced path selection
PathBiasCircThreshold 150
PathBiasNoticeRate 0.7
PathBiasWarnRate 0.85
PathBiasExtremeRate 0.95
EOF

echo "✅ Tor configuration complete"
echo ""

# Set proper permissions
chmod 644 "$TOR_CONFIG"
chown root:root "$TOR_CONFIG"

# Create log directory
mkdir -p /var/log/tor
chown debian-tor:debian-tor /var/log/tor 2>/dev/null || chown tor:tor /var/log/tor 2>/dev/null

# Start/restart Tor service
echo "🚀 Starting Tor service..."
systemctl enable tor
systemctl restart tor

# Wait for Tor to start
echo "⏳ Waiting for Tor to initialize..."
sleep 5

# Check Tor status
if systemctl is-active --quiet tor; then
    echo "✅ Tor service is running"
else
    echo "❌ Tor service failed to start"
    echo "Check logs: journalctl -u tor -n 50"
    exit 1
fi

# Test Tor connection
echo ""
echo "🔍 Testing Tor connection..."
if command -v torsocks &> /dev/null; then
    IP=$(torsocks curl -s https://check.torproject.org/api/ip 2>/dev/null | grep -o '"IsTor":[^,]*' | grep -o '[^:]*$')
    if [ "$IP" = "true" ]; then
        echo "✅ Tor is working correctly!"
        echo "   You are successfully routing through Tor"
    else
        echo "⚠️  Tor connection test failed"
        echo "   The service is running but connection test failed"
    fi
else
    echo "⚠️  torsocks not installed, skipping connection test"
fi

echo ""
echo "========================================="
echo "Tor Installation Complete!"
echo "========================================="
echo ""
echo "📝 Configuration details:"
echo "   SOCKS proxy: 127.0.0.1:9050"
echo "   Control port: 127.0.0.1:9051"
echo "   Config file: $TOR_CONFIG"
echo "   Log file: /var/log/tor/notices.log"
echo ""
echo "🔒 Security features enabled:"
echo "   ✓ DNS leak protection"
echo "   ✓ Circuit isolation"
echo "   ✓ Stream isolation"
echo "   ✓ Automatic circuit rotation"
echo "   ✓ Client-only mode (no relay/exit)"
echo "   ✓ Minimal logging"
echo ""
echo "🎯 Usage:"
echo "   The Argus platform will automatically use Tor"
echo "   when searching the dark web for entity information."
echo ""
echo "   To manually test Tor:"
echo "   torsocks curl https://check.torproject.org/api/ip"
echo ""
echo "⚠️  Security reminders:"
echo "   - Tor provides anonymity, not encryption"
echo "   - Use HTTPS sites when possible"
echo "   - Dark web searches are for investigative purposes only"
echo "   - Comply with all applicable laws and regulations"
echo ""
