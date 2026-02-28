"""Extract more entities from documents and add to canvas."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.entity_extraction_service import EntityExtractionService, EntityType
from app.models.database_models import DocumentChunk, CanvasNode, EntityKnowledge
from app.database import SessionLocal
from sqlalchemy import func
import uuid
import re

def extract_and_add_entities():
    """Extract entities from documents and add to canvas."""
    db = SessionLocal()
    try:
        entity_service = EntityExtractionService()

        # Get all document chunks
        chunks = db.query(DocumentChunk).all()
        print(f"Processing {len(chunks)} document chunks...")

        # Combine all text
        all_text = "\n\n".join([chunk.chunk_text for chunk in chunks])

        # Extract entities
        print("Extracting entities...")
        entities = entity_service.extract_entities(all_text)

        # Group by name to count mentions
        entity_counts = {}
        for entity in entities:
            name = entity.name
            if name not in entity_counts:
                entity_counts[name] = {
                    'type': entity.entity_type,
                    'count': 0,
                    'confidence': entity.confidence
                }
            entity_counts[name]['count'] += 1

        # Filter out entities with only 1 mention (likely noise)
        significant_entities = {
            name: data for name, data in entity_counts.items()
            if data['count'] >= 2 or data['confidence'] >= 0.8
        }

        print(f"Found {len(significant_entities)} significant entities")

        # Get existing canvas nodes
        existing_nodes = db.query(CanvasNode).all()
        existing_labels = {node.data.get('label', '').lower() for node in existing_nodes}

        print(f"Existing nodes: {len(existing_labels)}")

        # Add new entities to canvas
        added = 0
        skipped = 0

        # Calculate grid positions
        row_size = 10
        x_spacing = 300
        y_spacing = 200
        start_x = 100
        start_y = 500

        idx = len(existing_nodes)

        for name, data in significant_entities.items():
            if name.lower() in existing_labels:
                skipped += 1
                continue

            # Skip very short names or common words
            if len(name) <= 2 or name.lower() in ['the', 'a', 'an', 'of', 'in', 'to', 'for', 'and', 'or', 'but', 'mr', 'ms', 'mrs', 'dr']:
                skipped += 1
                continue

            # Map entity type to node type
            entity_type_map = {
                'PERSON': 'PERSON',
                'ORG': 'ORGANIZATION',
                'GPE': 'LOCATION',  # Geopolitical entity
                'LOC': 'LOCATION',
                'DATE': 'DATE',
                'EVENT': 'EVENT',
                'MONEY': 'FINANCIAL',
                'CARDINAL': 'DATE',  # Numbers can be dates or amounts
            }

            node_type = entity_type_map.get(data['type'].name, 'PERSON')

            # Calculate position in grid
            row = idx // row_size
            col = idx % row_size
            x = start_x + (col * x_spacing)
            y = start_y + (row * y_spacing)

            # Create node
            node_id = f"{node_type.lower()}-{uuid.uuid4().hex[:8]}"
            node = CanvasNode(
                id=node_id,
                type=node_type,
                position_x=x,
                position_y=y,
                data={
                    'label': name,
                    'mentions': data['count'],
                    'confidence': data['confidence']
                }
            )

            db.add(node)
            added += 1
            idx += 1

            print(f"  Added: {name} ({node_type}) - {data['count']} mentions")

        db.commit()

        print(f"\nSummary:")
        print(f"  Added: {added} new entities")
        print(f"  Skipped: {skipped} (already exist or too generic)")
        print(f"  Total canvas nodes: {len(existing_nodes) + added}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    extract_and_add_entities()
