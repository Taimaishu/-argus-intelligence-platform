"""Simple entity extraction using regex patterns."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.models.database_models import DocumentChunk, CanvasNode, EntityKnowledge
from app.database import SessionLocal
import uuid
import re
from collections import Counter

def extract_entities_simple():
    """Extract entities using simple regex patterns."""
    db = SessionLocal()
    try:
        # Get all document chunks
        chunks = db.query(DocumentChunk).all()
        print(f"Processing {len(chunks)} document chunks...")

        # Combine all text
        all_text = "\n\n".join([chunk.chunk_text for chunk in chunks])

        # Entity patterns
        # Names: Capitalized words (2-3 words)
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'

        # Locations: Common location patterns
        location_pattern = r'\b(New York|Los Angeles|Miami|Palm Beach|London|Paris|Washington|Bradford|Manhattan|Florida)\b'

        # Organizations: Corp, Inc, LLC, FBI, CIA, etc.
        org_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Corp|Inc|LLC|Ltd|Organization|Agency|Bureau|Foundation|Institute|University|College)))\b|'
        org_pattern += r'\b(FBI|CIA|DOJ|NSA|NYPD|SEC|IRS)\b'

        # Dates and years
        date_pattern = r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b|\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b|\b((?:19|20)\d{2})\b'

        # Phone numbers
        phone_pattern = r'\b(\d{3}[-.]?\d{3}[-.]?\d{4})\b'

        # Email addresses
        email_pattern = r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'

        # Extract all matches
        names = re.findall(name_pattern, all_text)
        locations = re.findall(location_pattern, all_text)
        orgs = re.findall(org_pattern, all_text)
        orgs = [o for sublist in orgs for o in sublist if o]  # Flatten and filter empty
        dates = re.findall(date_pattern, all_text)
        dates = [d for sublist in dates for d in sublist if d]  # Flatten and filter empty
        phones = re.findall(phone_pattern, all_text)
        emails = re.findall(email_pattern, all_text)

        print(f"Found {len(names)} names, {len(locations)} locations, {len(orgs)} organizations, {len(dates)} dates")

        # Count occurrences
        name_counts = Counter(names)
        location_counts = Counter(locations)
        org_counts = Counter(orgs)
        date_counts = Counter(dates)
        phone_counts = Counter(phones)
        email_counts = Counter(emails)

        # Get existing canvas nodes
        existing_nodes = db.query(CanvasNode).all()
        existing_labels = {node.data.get('label', '').lower() for node in existing_nodes}
        print(f"Existing nodes: {len(existing_labels)}")

        # Common words to skip
        common_words = {'The', 'This', 'That', 'These', 'Those', 'What', 'When', 'Where', 'Why', 'How',
                       'Could', 'Would', 'Should', 'Must', 'Can', 'Will', 'May', 'Might',
                       'United States', 'New Year', 'Palm Beach County'}

        added = 0
        row_size = 10
        x_spacing = 300
        y_spacing = 200
        start_x = 100
        start_y = 500
        idx = len(existing_nodes)

        # Add entities in order of mention count
        entities_to_add = []

        # Process names (persons)
        for name, count in name_counts.most_common(30):
            if count >= 2 and name not in common_words and name.lower() not in existing_labels:
                entities_to_add.append(('PERSON', name, count))

        # Process locations
        for location, count in location_counts.most_common(20):
            if count >= 2 and location.lower() not in existing_labels:
                entities_to_add.append(('LOCATION', location, count))

        # Process organizations
        for org, count in org_counts.most_common(15):
            if count >= 2 and org.lower() not in existing_labels:
                entities_to_add.append(('ORGANIZATION', org, count))

        # Process dates (top ones only)
        for date, count in date_counts.most_common(10):
            if count >= 3 and date.lower() not in existing_labels:
                entities_to_add.append(('DATE', date, count))

        # Process phones
        for phone, count in phone_counts.most_common(5):
            if count >= 2 and phone.lower() not in existing_labels:
                entities_to_add.append(('PHONE', phone, count))

        # Process emails
        for email, count in email_counts.most_common(5):
            if count >= 2 and email.lower() not in existing_labels:
                entities_to_add.append(('EMAIL', email, count))

        # Add to canvas
        for entity_type, name, count in entities_to_add:
            row = idx // row_size
            col = idx % row_size
            x = start_x + (col * x_spacing)
            y = start_y + (row * y_spacing)

            node_id = f"{entity_type.lower()}-{uuid.uuid4().hex[:8]}"
            node = CanvasNode(
                id=node_id,
                type=entity_type,
                position_x=x,
                position_y=y,
                data={
                    'label': name,
                    'mentions': count
                }
            )

            db.add(node)
            added += 1
            idx += 1
            print(f"  Added: {name} ({entity_type}) - {count} mentions")

        db.commit()

        print(f"\nSummary:")
        print(f"  Added: {added} new entities")
        print(f"  Total canvas nodes: {len(existing_nodes) + added}")

        return added

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return 0
    finally:
        db.close()

if __name__ == "__main__":
    extract_entities_simple()
