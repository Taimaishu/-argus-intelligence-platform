# AI-Powered Image Search for Canvas Entities

## Overview
The platform now automatically finds and displays relevant photos for each entity on the canvas - actual photos of people, places, organizations, and things!

## How It Works
When you auto-generate a canvas or add entities, the AI searches for matching images using:
1. **Google Custom Search** - Finds actual photos from across the web
2. **Pexels** - Free stock photos
3. **Unsplash** - High-quality stock photos
4. **Placeholder** - Generated avatars as fallback

## Setup Instructions

### 1. Google Custom Search API (Recommended for Best Results)

#### Step 1: Get Google API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project or select existing
3. Click "Create Credentials" → "API Key"
4. Copy your API key

#### Step 2: Enable Custom Search API
1. Go to [API Library](https://console.cloud.google.com/apis/library)
2. Search for "Custom Search API"
3. Click "Enable"

#### Step 3: Create Custom Search Engine
1. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Click "Add" or "Create"
3. **Search Settings:**
   - **Sites to search:** Leave empty or add `*` to search entire web
   - **Name:** "Argus Image Search"
   - **Language:** English
4. After creation, click "Control Panel"
5. Enable "Image search" option
6. Enable "Search the entire web"
7. Copy your "Search engine ID" (looks like: `0123456789abcdef:xyz`)

#### Step 4: Add to .env
Edit `/home/taimaishu/argus-intelligence-platform/backend/.env`:
```bash
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_CX=your_search_engine_id_here
```

### 2. Alternative APIs (Optional)

#### Unsplash (Stock Photos)
1. Create account at [Unsplash Developers](https://unsplash.com/developers)
2. Create new application
3. Copy your "Access Key"
4. Add to .env:
```bash
UNSPLASH_ACCESS_KEY=your_unsplash_key
```

#### Pexels (Stock Photos)
1. Create account at [Pexels API](https://www.pexels.com/api/)
2. Copy your API key
3. Add to .env:
```bash
PEXELS_API_KEY=your_pexels_key
```

## Current Status
✅ Google API Key: **Configured**
❌ Google Search Engine ID: **NOT configured** (required for web image search)
❌ Unsplash: Not configured (optional)
❌ Pexels: Not configured (optional)

## Testing Image Search

### Test via API:
```bash
curl -X POST http://localhost:8000/api/canvas/search-image \
  -H "Content-Type: application/json" \
  -d '{
    "entity_name": "Jeffrey Epstein",
    "entity_type": "person",
    "count": 3
  }'
```

### Test on Canvas:
1. Go to Canvas page
2. Click "Auto-Generate" to create entities from documents
3. Entities will automatically have relevant images

## Features

### Automatic Image Assignment
- ✅ **Person entities** → Actual photos/headshots of the person
- ✅ **Organization entities** → Logos, buildings, headquarters
- ✅ **Location entities** → Actual photos of the place
- ✅ **Vehicle entities** → Photos of the actual vehicle
- ✅ **Event entities** → Coverage photos from the event

### Smart Search Queries
The AI enhances search queries based on entity type:
- Person: "Jeffrey Epstein photo portrait headshot"
- Organization: "Acme Corp logo headquarters building"
- Location: "Little St. James Island photo image"

### Image Display
- Images appear as thumbnails at the top of each canvas node
- Hover over nodes to see full entity details
- Images auto-hide if they fail to load
- Placeholder avatars shown as fallback

## Priority Order
1. **Google Custom Search** (best - finds actual specific photos)
2. Pexels (good - high-quality stock photos)
3. Unsplash (good - high-quality stock photos)
4. Placeholder (fallback - generated avatars with initials)

## Privacy & Legal Notes
- All image searches use legitimate APIs with proper attribution
- Images are sourced from public web results or licensed stock photo sites
- No unauthorized scraping or copyright violation
- For sensitive investigations, consider disabling automatic image search

## Troubleshooting

### "No images found" / Placeholder images only
- Check that GOOGLE_SEARCH_CX is set in .env
- Verify Google Custom Search API is enabled
- Restart backend: `bash backend/start_backend.sh`

### Images not displaying
- Check browser console for CORS errors
- Verify image URLs are accessible
- Some images may be blocked by content security policies

### Rate Limits
- Google: 100 queries/day (free tier)
- Unsplash: 50 requests/hour (free tier)
- Pexels: 200 requests/hour (free tier)

For higher limits, upgrade to paid tiers or use multiple API keys.
