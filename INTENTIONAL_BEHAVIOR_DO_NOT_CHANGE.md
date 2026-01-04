# Intentional Behavior - DO NOT CHANGE Without Tests

**Purpose:** This document explicitly marks behavior that is INTENTIONAL and should NOT be refactored, generalized, or "cleaned up" without comprehensive testing.

**Last Updated:** January 3, 2026

---

## 🔒 CRITICAL: Name Mappings

### Location: `image_search_service.py` lines 85-91

```python
name_mappings = {
    "epstein": "Jeffrey Epstein financier",
    "clinton": "Bill Clinton president",
    "andrew": "Prince Andrew Duke of York",
    "trump": "Donald Trump president",
    "maxwell": "Ghislaine Maxwell socialite",
}
```

**Why this exists:** Common surnames return wrong photos without context. These mappings ensure accurate photos.

**DO NOT:**
- ❌ Remove these mappings
- ❌ Generalize to a database or config file
- ❌ Add AI-based name enhancement
- ❌ Remove the hardcoded context words (president, financier, etc.)

**Reason:** This is a curated list based on actual photo accuracy issues. Each mapping was added because generic search failed.

---

### Location: `entity_enrichment_service.py` lines 31-37

```python
self.name_mappings = {
    "epstein": "Jeffrey Epstein",
    "clinton": "Bill Clinton",
    "andrew": "Prince Andrew",
    "trump": "Donald Trump",
    "maxwell": "Ghislaine Maxwell",
}
```

**Why this exists:** Same reason - prevents wrong photos for common surnames.

**Note:** These are slightly different from image_search mappings (no context words). Both are intentional.

---

## 🔒 CRITICAL: Query Enhancement Keywords

### Location: `image_search_service.py` lines 99-107

```python
enhancements = {
    "person": f"{query} mugshot photo official portrait",
    "organization": f"{query} logo headquarters building official",
    "location": f"{query} photo image map aerial view",
    "event": f"{query} photo coverage news image",
    "vehicle": f"{query} photo registration image",
    "financial": f"{query} financial logo company",
}
```

**Why this exists:** Without these keywords, search returns generic stock photos instead of actual entity photos.

**Specific keyword choices:**
- `"mugshot"` - Prioritizes arrest photos for people (investigation context)
- `"official portrait"` - Falls back to formal photos
- `"logo headquarters"` - Finds actual organization, not generic building
- `"aerial view"` - Gets actual location, not tourist photos
- `"registration"` - Finds specific vehicle, not stock car photos

**DO NOT:**
- ❌ Remove any keywords
- ❌ Change keyword order (priority matters)
- ❌ Replace with AI-generated queries
- ❌ Make keywords configurable

**Reason:** Each keyword was added after observing poor search results. Order matters (mugshot before portrait).

---

## 🔒 CRITICAL: Wikipedia Validation Threshold

### Location: `image_search_service.py` lines 215-221

```python
# Check if at least 70% of query words are in title
overlap = len(query_words & title_words) / len(query_words) if query_words else 0
return overlap >= 0.7
```

**Why 70%:** Calibrated through testing. Lower values return wrong people's photos.

**Examples:**
- "Jeffrey Epstein" vs "Epstein–Barr virus" → 50% overlap (rejected ✓)
- "Jeffrey Epstein" vs "Jeffrey Epstein (financier)" → 100% overlap (accepted ✓)
- "Prince Andrew" vs "Prince Andrew, Duke of York" → 100% overlap (accepted ✓)

**DO NOT:**
- ❌ Lower the threshold below 0.7
- ❌ Make it configurable
- ❌ Replace with fuzzy matching
- ❌ Use AI-based similarity

**Reason:** 70% is the minimum threshold that prevents false matches while allowing legitimate variations.

---

## 🔒 CRITICAL: Common Words Filter

### Location: `image_search_service.py` line 207

```python
common_words = {'the', 'a', 'an', 'of', 'in', 'and', 'or', 'for', 'to', 'from', 'jr', 'sr', 'duke', 'prince', 'president'}
```

**Why this exists:** These words don't help distinguish entities. "Prince Andrew" and "Prince William" both have "Prince" - not discriminative.

**DO NOT:**
- ❌ Remove any words from this list
- ❌ Add too many words (might break legitimate matches)
- ❌ Use stopword libraries (those are for NLP, not name matching)

**Reason:** This list is curated for name matching specifically, not general NLP.

---

## 🔒 CRITICAL: Source Priority Order

### Location: `image_search_service.py` line 54

```python
sources = [preferred_source] if preferred_source else ["wikipedia", "google", "pexels", "unsplash"]
```

**Why this order:**
1. **Wikipedia** - Free, accurate for public figures, has validation
2. **Google** - Paid, comprehensive, but requires API key
3. **Pexels** - Free stock photos, good for generic entities
4. **Unsplash** - Free stock photos, good quality

**DO NOT:**
- ❌ Change the order
- ❌ Remove Wikipedia from first position
- ❌ Add random shuffling for "variety"

**Reason:** Wikipedia is most accurate for people/organizations. Stock photos are fallbacks.

---

## 🔒 CRITICAL: Skip Types

### Location: `entity_enrichment_service.py` lines 59-60

```python
skip_types = ['date', 'event', 'phone', 'email', 'address']
skip_names = ['ted', 'the', 'today', '24', 'digital']
```

**Why skip these:**
- **Dates/events** - Don't need photos (already have icons)
- **Phone/email/address** - Not visual entities
- **Generic names** - "ted" might be "TED talk", "the" is article, etc.

**DO NOT:**
- ❌ Remove any skip types
- ❌ Make photo search run for these anyway
- ❌ Add AI decision for skipping

**Reason:** These entity types either don't need photos or cause false matches.

---

## 🔒 CRITICAL: Name Enhancement Patterns

### Location: `entity_enrichment_service.py` lines 239-243

```python
patterns = [
    rf'((?:Prince|President|King|Queen|Duke|Duchess|Lord|Lady|Sir|Dr\.|Professor)\s+{re.escape(entity_name)}(?:\s+\w+)?)',
    rf'({re.escape(entity_name)}\s+(?:Duke|Prince|President|of\s+\w+))',
    rf'({re.escape(entity_name)}\s+\w+(?:\s+\w+)?)',
]
```

**Why these patterns:**
1. Titles before name: "Prince Andrew" → "Prince Andrew Duke of York"
2. Titles after name: "Andrew" → "Andrew Duke of York"
3. Additional names: "Andrew" → "Andrew Windsor"

**Pattern order matters:** Most specific patterns first.

**DO NOT:**
- ❌ Change pattern order
- ❌ Remove any patterns
- ❌ Simplify to single pattern
- ❌ Use NER libraries (too slow, less accurate for titles)

**Reason:** These patterns were tuned for document context extraction. Order prevents overly generic matches.

---

## 🔒 CRITICAL: Placeholder Colors

### Location: `image_search_service.py` lines 301-311

```python
colors = {
    "person": "6366f1",  # Indigo
    "organization": "f97316",  # Orange
    "location": "10b981",  # Green
    "event": "eab308",  # Yellow
    "vehicle": "ef4444",  # Red
    "financial": "059669",  # Emerald
    "phone": "06b6d4",  # Cyan
    "email": "8b5cf6",  # Violet
    "address": "ec4899",  # Pink
}
```

**Why these colors:** Part of UI design system. Users expect consistent colors.

**DO NOT:**
- ❌ Change colors
- ❌ Make them random
- ❌ Use theme colors (these are entity-specific)

**Reason:** Color consistency helps users identify entity types at a glance.

---

## 🔒 CRITICAL: AI Theory Generation Threshold

### Location: `entity_enrichment_service.py` line 171

```python
if entity_type in ['person', 'organization'] and metadata.get('total_mentions', 0) >= 5:
```

**Why 5 mentions:**
- Below 5: Entity is too minor, AI theories not valuable
- At 5+: Entity is significant enough for analysis
- AI generation costs money - threshold prevents waste

**DO NOT:**
- ❌ Lower threshold (wastes API calls)
- ❌ Remove threshold (every entity gets expensive AI call)
- ❌ Make it 0 or 1

**Reason:** 5 mentions is the minimum for statistically significant analysis. Lower values generate noise.

---

## 🔒 CRITICAL: Title Extraction Pattern

### Location: `entity_enrichment_service.py` lines 123-129

```python
title_match = re.match(
    r'^(Prince|President|King|Queen|Duke|Duchess|Lord|Lady|Sir|Dr\.|Professor)',
    enhanced_name,
    re.IGNORECASE
)
```

**Why these titles:** Common formal titles that indicate social status/role.

**DO NOT:**
- ❌ Add more titles without testing
- ❌ Remove any titles
- ❌ Use NER for title extraction (slower, less accurate)

**Reason:** This list is curated for investigation context. Adding more titles causes false matches.

---

## 🔒 CRITICAL: Evidence Excerpt Limits

### Location: `entity_enrichment_service.py` lines 142-156

```python
chunks = db.query(DocumentChunk).filter(
    DocumentChunk.chunk_text.ilike(f'%{entity_name}%')
).limit(5).all()

# Later...
"text": chunk.chunk_text[:300],
```

**Why these limits:**
- **5 chunks** - Enough for context, not too much data
- **300 chars** - Readable excerpt, fits in UI

**DO NOT:**
- ❌ Increase to 10+ chunks (too much data)
- ❌ Increase to 500+ chars (UI breaks)
- ❌ Remove limits (database explosion)

**Reason:** These limits balance comprehensiveness with performance/UI constraints.

---

## 🔒 CRITICAL: Knowledge Field Character Limits

### Location: `entity_enrichment_service.py` lines 195-198

```python
knowledge.description = theories.get('temporal_analysis', '')[:500]
knowledge.background = theories.get('geographic_analysis', '')[:1000]
knowledge.connection_to_investigation = theories.get('network_analysis', '')[:1000]
knowledge.theories = theories.get('theories', '')[:2000]
```

**Why these limits:** Match database schema. Over-limit causes database errors.

**DO NOT:**
- ❌ Remove character limits
- ❌ Increase without changing database schema
- ❌ Let AI generate unlimited text

**Reason:** Database columns have VARCHAR limits. Exceeding them causes INSERT failures.

---

## ⚠️ Summary: What NOT To Do

### NEVER:
1. Remove or generalize hardcoded name mappings
2. Change query enhancement keywords or order
3. Modify Wikipedia validation threshold (70%)
4. Change source priority order
5. Remove skip types or names
6. Alter regex patterns for name extraction
7. Change placeholder color scheme
8. Lower AI theory generation threshold
9. Remove character limits on database fields
10. Add feature flags to make these behaviors configurable
11. Replace with "smarter" AI-based approaches
12. "Clean up" or "modernize" without comprehensive testing

### ALWAYS:
1. Add tests before changing any of these behaviors
2. Document WHY a change is needed
3. Test with real entity data (Epstein, Clinton, etc.)
4. Verify photo accuracy doesn't degrade
5. Check database constraints aren't violated

---

## 📊 Impact of Breaking These Rules

**If name mappings removed:**
- "epstein" → random Epstein photos (doctor, scientist, virus)
- "clinton" → random Clinton (Hillary, George, city)
- **Result:** Wrong photos, user confusion

**If query keywords changed:**
- Remove "mugshot" → get stock photos instead of actual person
- Change order → wrong photo types prioritized
- **Result:** Generic photos, not actual entities

**If Wikipedia threshold lowered:**
- 50% threshold → "Jeffrey Epstein" matches "Epstein–Barr virus"
- **Result:** Wrong people's photos

**If source order changed:**
- Pexels first → stock photos instead of actual people
- **Result:** Generic business person photos

**If skip types removed:**
- Try to find photos for "January 24" or "555-1234"
- **Result:** Random unrelated images, wasted API calls

**If AI threshold removed:**
- Generate theories for every "the", "a", "an"
- **Result:** Massive API costs, useless theories

---

## ✅ What CAN Be Changed

Safe changes that DON'T affect these behaviors:
- Add logging
- Add defensive guards (null checks)
- Add MIME type validation
- Add size limits for images
- Improve error messages
- Add debug metadata (not used in logic)
- Add timeouts
- Add comments

---

**REMEMBER:** This pipeline works correctly. Don't fix what isn't broken.

**Last Review:** January 3, 2026 by Claude (Sonnet 4.5)
**Status:** ✅ All intentional behaviors documented and protected
