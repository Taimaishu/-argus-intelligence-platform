# Deep Web & Dark Web Search Integration

## Overview

Argus Intelligence Platform now includes comprehensive deep web and dark web search capabilities with TAILS-like security features for investigating entities across the entire internet.

## Features

### 🌐 Surface Web Search
- Google Custom Search API
- DuckDuckGo (privacy-focused, no API key required)
- Automatic image and document discovery

### 🕸️ Dark Web Search (.onion sites)
- Tor-routed anonymous searches
- Multiple dark web search engines (Ahmia, Haystak)
- Circuit rotation for enhanced anonymity

### 🔍 Infrastructure Search
- Shodan integration for IP/hostname lookup
- Organization infrastructure discovery
- Geolocation and banner information

### 🔒 TAILS-like Security Features

**Privacy Protection:**
- ✅ Tor circuit rotation (every 5 requests)
- ✅ No logging of visited URLs or .onion addresses
- ✅ Randomized User-Agent headers (prevents fingerprinting)
- ✅ DNS leak protection via SOCKS5h
- ✅ Cookie isolation (no session persistence)
- ✅ Memory-only operations (no disk writes)
- ✅ No JavaScript execution (prevents tracking)
- ✅ Fresh session for each request

**Anonymity Layers:**
1. All traffic encrypted via Tor
2. Circuits rotated automatically
3. No browser fingerprinting
4. Isolated streams per connection
5. Minimal logging (warnings/errors only)

## Installation

### 1. Install Tor (Required for Dark Web Search)

```bash
cd /home/taimaishu/argus-intelligence-platform
sudo bash install-tor-secure.sh
```

The script will:
- Install Tor with secure configuration
- Set up SOCKS proxy on port 9050
- Configure control port on 9051
- Enable circuit rotation
- Apply TAILS-like security settings

### 2. Install Python Dependencies

```bash
cd backend
source venv/bin/activate
pip install stem pysocks requests[socks] beautifulsoup4 shodan
```

### 3. Verify Tor Installation

```bash
# Check Tor status
systemctl status tor

# Test Tor connection
torsocks curl https://check.torproject.org/api/ip
```

Expected output: `"IsTor":true`

## Configuration

### Environment Variables (.env)

```bash
# Required for surface web search
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_CX=your_google_custom_search_engine_id_here

# Required for infrastructure search
SHODAN_API_KEY=your_shodan_api_key_here

# Optional: Tor control password (if configured)
TOR_PASSWORD=your_tor_password_here

# AI providers for analysis
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
```

### Getting API Keys

#### Google Custom Search
1. Visit: https://console.cloud.google.com/
2. Enable "Custom Search API"
3. Create API key → Copy to `GOOGLE_API_KEY`
4. Visit: https://programmablesearchengine.google.com/
5. Create custom search engine → Copy "Search Engine ID" to `GOOGLE_SEARCH_CX`

#### Shodan
1. Visit: https://account.shodan.io/
2. Create account
3. Copy API key from dashboard

## Usage

### Canvas Entity Detail Panel

When you click on any entity in the canvas (person, organization, location, etc.):

1. **Information Tab** - Shows comprehensive entity profile:
   - Who they are (identity/role)
   - Background & past activities
   - Connection to investigation
   - Evidence from documents (with verification links)
   - Key associations
   - Theory & conclusion

2. **Connections Tab** - Shows related entities:
   - Connected people, organizations, locations
   - Relationship types
   - Visual network representation

3. **AI Insights Tab** - AI-powered analysis:
   - Theories about their role
   - Investigation suggestions
   - Warnings and considerations

### Deep Web Search API

Endpoint: `POST /api/canvas/deep-search`

```json
{
  "entity_name": "John Doe",
  "entity_type": "person",
  "include_dark_web": true,
  "include_infrastructure": true
}
```

Response includes:
- `surface_web_results`: Results from Google, DuckDuckGo
- `dark_web_results`: Results from .onion sites (if Tor enabled)
- `infrastructure_results`: Shodan IP/hostname data
- `images_found`: Discovered images
- `documents_found`: Discovered documents
- `tor_enabled`: Whether Tor is running

## Security Considerations

### ⚠️ Important Warnings

1. **Legal Compliance**: Only use for legitimate investigative purposes. Comply with all applicable laws and regulations.

2. **Tor Limitations**:
   - Tor provides anonymity, NOT encryption
   - Always use HTTPS sites when possible
   - Exit node can see unencrypted traffic

3. **Operational Security**:
   - Dark web searches are logged minimally (warnings/errors only)
   - No visited URLs are stored locally
   - Sessions are isolated (no cross-contamination)

4. **Tor Usage**:
   - Client-only mode (not relay/exit node)
   - Circuits rotate automatically
   - Control port secured (localhost only)

### Best Practices

1. **Before Searching**:
   - Ensure Tor is running: `systemctl status tor`
   - Check Tor connection: `torsocks curl https://check.torproject.org/api/ip`

2. **During Investigation**:
   - Use secure AI providers (Anthropic/OpenAI) for analysis
   - Verify findings from multiple sources
   - Document source verification links

3. **After Investigation**:
   - Review logs: `/var/log/tor/notices.log`
   - Clear browser cache (if using web interface)
   - Restart Tor for new identity: `sudo systemctl restart tor`

## Troubleshooting

### Tor Not Working

```bash
# Check Tor status
systemctl status tor

# View logs
journalctl -u tor -n 50

# Restart Tor
sudo systemctl restart tor

# Test connection
torsocks curl https://check.torproject.org/api/ip
```

### No Dark Web Results

1. Verify Tor is running
2. Check Tor connection test passes
3. Ensure `.onion` sites are accessible
4. Check backend logs for errors

### Google Search Not Working

1. Verify `GOOGLE_API_KEY` is set in `.env`
2. Verify `GOOGLE_SEARCH_CX` is set in `.env`
3. Check Google API quotas: https://console.cloud.google.com/
4. Enable "Custom Search API" if disabled

### Images Not Loading

1. Verify `GOOGLE_SEARCH_CX` is configured
2. Check image URLs are accessible
3. Try different entity names
4. Check browser console for CORS errors

## Architecture

### Security Flow

```
User Request
    ↓
Argus Backend (Memory-only)
    ↓
Deep Web Search Service
    ↓
┌─────────────────────────────────────────┐
│  Surface Web          Dark Web          │
│  ↓                    ↓                  │
│  Fresh Session        Tor Circuit       │
│  Random UA            (SOCKS5h)         │
│  No Cookies           ↓                 │
│  ↓                    Circuit Rotation  │
│  HTTPS Request        ↓                 │
│  ↓                    .onion Sites      │
│  Response             ↓                 │
│  ↓                    Response          │
└─────────────────────────────────────────┘
    ↓
Parse & Extract (BeautifulSoup)
    ↓
AI Analysis (Anthropic/OpenAI)
    ↓
Structured Response
    ↓
Frontend Display
```

### Data Flow

1. Entity clicked in canvas
2. Frontend calls `/api/canvas/entity-info`
3. Backend queries document chunks for mentions
4. AI analyzes context and generates profile
5. Frontend displays comprehensive information
6. User can verify via document source links

## Updates & Enhancements

### Completed
- ✅ Entity detail panel with comprehensive information
- ✅ Document source verification links
- ✅ Connected entities from knowledge graph
- ✅ Deep web search service with TAILS-like security
- ✅ Tor integration with circuit rotation
- ✅ Image and document discovery
- ✅ Infrastructure search (Shodan)

### Next Steps
- Add deep web search to entity detail panel UI
- Implement cached results for performance
- Add connection explanation AI analysis
- Integrate OSINT tools (theHarvester, Recon-ng)

## Support

For issues or questions:
1. Check logs: `/var/log/tor/notices.log`
2. Check backend logs: `journalctl -u argus-backend`
3. Test endpoints manually with curl
4. Verify API keys are correctly configured

---

**Remember**: Use responsibly. This tool is for legitimate investigative purposes only.
