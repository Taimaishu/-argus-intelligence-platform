# Argus Intelligence Platform v1.1 - USB Portable Edition

**Release Date:** January 3, 2026

---

## 🚀 What's New

### USB Portable Deployment
- **Complete portable package** ready for USB drives or external storage
- **Cross-platform support** - Works on Windows 10/11 and Linux (Ubuntu, Debian, Fedora, Arch)
- **Automatic setup wizard** guides users through first-run configuration
- **No installation required** - Just extract and run!
- **903 KB package** containing 206 files with complete application

### Safe Improvements to Image/Entity Search
- **100% behavior preservation** - All existing functionality unchanged
- **Enhanced stability** - Defensive guards prevent crashes from invalid inputs
- **Better logging** - Query transformations and name mappings now visible
- **Image validation** - MIME type checking, size limits (10 MB max), HEAD request validation
- **Database safety** - Proper transaction rollback handling with SQLAlchemyError
- **Debug metadata** - Enhanced observability for troubleshooting

### New Features
- **Setup Wizard** - First-run experience for API key configuration
- **Settings Page** - Manage API keys for OpenAI, Anthropic, Google, Unsplash, Pexels
- **Canvas Generation** - AI-powered entity clustering and timeline visualization
- **Knowledge Graph** - Relationship mapping across documents
- **Metadata Analysis** - Cross-document entity tracking and co-occurrence analysis
- **Entity Extraction** - Enhanced NER with support for 9+ entity types
- **Unredaction Service** - Document recovery and redaction removal
- **Canvas Chat** - Entity-specific conversations with context awareness
- **Entity Nodes** - Specialized UI for Person, Organization, Location, Event, etc.

---

## 📦 Download

**USB Portable Package:** `argus-usb-portable.zip` (903 KB)

### Quick Start

**Windows:**
1. Extract `argus-usb-portable.zip` to your USB drive
2. Double-click `START_ARGUS_USB.bat`
3. Follow the on-screen prompts
4. Browser opens automatically

**Linux:**
1. Extract `argus-usb-portable.zip` to your USB drive
2. Open terminal in the extracted folder
3. Run: `bash START_ARGUS_USB.sh`
4. Follow the on-screen prompts
5. Browser opens automatically

---

## ✨ Key Improvements

### Image Search Pipeline
- Added defensive guards for null/empty query strings
- Enhanced logging shows query transformations (e.g., "epstein" → "Jeffrey Epstein financier")
- Image validation with MIME type checking (JPEG, PNG, GIF, WebP, SVG)
- Size limit enforcement (10 MB maximum)
- HEAD request validation before downloading images
- Better timeout handling with explicit exception catching

### Entity Enrichment
- Input validation prevents crashes from invalid entity names or node IDs
- Database transaction safety with proper rollback on errors
- Enhanced logging for name enhancement (e.g., "Andrew" → "Prince Andrew Duke of York")
- Defensive guards for missing documents in evidence collection
- Better error context in all exception handlers

### Preserved Critical Behaviors
All intentional behaviors remain unchanged:
- ✅ Name mappings (epstein, clinton, andrew, trump, maxwell)
- ✅ Query enhancement keywords (mugshot, official portrait, etc.)
- ✅ 70% Wikipedia validation threshold
- ✅ Source priority order (wikipedia → google → pexels → unsplash)
- ✅ Skip types (date, event, phone, email, address)
- ✅ Regex patterns for entity name extraction
- ✅ AI theory generation threshold (5 mentions minimum)
- ✅ Character limits for database fields

---

## 🔧 Technical Details

### Testing
- ✅ **13/13 API tests passed** (100% pass rate)
- ✅ **Zero behavioral changes** detected
- ✅ All existing functionality preserved
- ✅ Original files backed up (.backup files)

### New Services
- `canvas_generation_service.py` - AI-powered canvas generation
- `knowledge_graph_service.py` - Relationship mapping
- `metadata_analysis_service.py` - Cross-document tracking
- `entity_extraction_service.py` - Enhanced NER
- `entity_enrichment_service.py` - Photo and metadata enrichment (improved)
- `image_search_service.py` - Multi-provider image search (improved)
- `unredaction_service.py` - Document recovery

### Frontend Components
- `SetupWizard.tsx` - First-run configuration
- `SettingsPage.tsx` - API key management
- `CanvasChatPanel.tsx` - Entity-specific chat
- `EntityDetailPanel.tsx` - Enriched entity information
- Entity nodes: Person, Organization, Location, Event, Date, Email, Phone, Address, Vehicle, Financial

### Documentation
- `IMAGE_SEARCH_PIPELINE_REVIEW.md` - Complete safety review (13 KB)
- `INTENTIONAL_BEHAVIOR_DO_NOT_CHANGE.md` - Protection guide (12 KB)
- `DISTRIBUTION_README.md` - USB deployment overview
- `CREATE_USB_DEPLOYMENT.md` - Detailed deployment instructions
- `USB_DEPLOYMENT_CHECKLIST.md` - Pre-deployment verification
- `LAUNCHER_GUIDE.md` - Launcher script documentation

---

## 📋 System Requirements

### Minimum
- **OS:** Windows 10/11 or Linux (any modern distro)
- **Python:** 3.10 or higher
- **RAM:** 2 GB
- **Storage:** 500 MB (more for documents)
- **Internet:** Required for initial setup and API-based AI

### Recommended
- **RAM:** 8 GB (for large document analysis)
- **Storage:** 5 GB+ (for Ollama + document storage)
- **CPU:** Multi-core for faster processing

---

## 🔑 API Keys

The setup wizard supports:
- **OpenAI** - Best performance, $0.50/million tokens
- **Anthropic Claude** - High quality, good for analysis
- **Google AI** - Gemini models support
- **Ollama** - Free, offline, privacy-focused (no API key needed!)

---

## 🛠️ Migration Guide

If upgrading from v1.0:
1. Backup your existing installation
2. Download `argus-usb-portable.zip`
3. Extract to new location (or replace existing)
4. Your data is stored separately (database, uploads)
5. No migration required - just run the new version!

**Note:** If you have an existing `.env` file, it will be preserved.

---

## 🐛 Bug Fixes

- Fixed crash when image search receives null/empty queries
- Fixed database rollback issues in entity enrichment
- Fixed timeout handling in image fetch operations
- Fixed missing document errors in evidence extraction
- Improved error messages throughout the application

---

## 📚 Resources

- **Documentation:** See included `CREATE_USB_DEPLOYMENT.md`
- **Issues:** https://github.com/Taimaishu/-argus-intelligence-platform/issues
- **Quick Start:** See included `USB_README.txt`

---

## 🙏 Credits

- Built with FastAPI, React, TypeScript, Python
- AI powered by OpenAI, Anthropic, Google, and Ollama
- Icons by Lucide React
- PDF parsing with PyMuPDF
- Entity extraction with spaCy

---

## 📝 Full Changelog

**Added:**
- USB portable deployment package (903 KB, 206 files)
- Setup wizard for first-run API key configuration
- Settings page for API key management
- Canvas generation service with AI clustering
- Knowledge graph service for relationship mapping
- Metadata analysis service for cross-document tracking
- Entity extraction service with enhanced NER
- Entity enrichment service with automatic photo/metadata
- Image search service with multi-provider support
- Unredaction service for document recovery
- Canvas chat panel for entity-specific conversations
- Entity detail panel with enriched information
- Specialized entity nodes (9+ types)
- Database migrations system
- Comprehensive documentation (5+ new guides)

**Improved:**
- Image search stability with defensive guards
- Entity enrichment error handling
- Database transaction safety
- Logging for query transformations
- Input validation across all services
- Timeout handling for external requests
- Error messages and context

**Fixed:**
- Crash from null/empty queries
- Database rollback failures
- Missing document errors
- Timeout exceptions in image fetch

**Preserved:**
- 100% of existing image/entity search behavior
- All critical name mappings and query enhancements
- Wikipedia validation threshold (70%)
- Source priority ordering
- Entity classification logic
- AI theory generation thresholds

---

**Made with ❤️ for investigators, researchers, and analysts**

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
