#!/usr/bin/env python3
"""
Analyze all Epstein PDF files for redactions
"""
import os
import sys
import json
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, '/home/taimaishu/argus-intelligence-platform/backend')

from app.core.unredaction_service import UnredactionService

async def analyze_all_files():
    files_dir = Path("/home/taimaishu/argus-intelligence-platform/Epstien_Files")

    # Get all PDF files
    pdf_files = [
        "2025.07 DOJ FBI Memorandum.pdf",
        "A. Evidence List from US v. Maxwell, 1.20-cr-00330 (SDNY 2020).pdf",
        "Attorney_General_Letter_Feb_2025.pdf",
        "B. Flight Log Released in US v. Maxwell, 1.20-cr-00330 (SDNY 2020).pdf",
        "C. Contact Book (Redacted).pdf",
        "D. Masseuse List (Redacted).pdf",
        "FBI_Victim_Impact_Statement.pdf",
        "Grand_Jury_Documents_001.pdf",
        "Interview Transcript - Maxwell 2025.07.24-cft (Redacted).pdf",
        "Maxwell_Case_Document_809.pdf",
        "Maxwell_Proffer_Agreement.pdf",
    ]

    service = UnredactionService()
    results = {}

    print("=" * 80)
    print("EPSTEIN FILES REDACTION ANALYSIS")
    print("=" * 80)
    print()

    for pdf_file in pdf_files:
        file_path = files_dir / pdf_file

        if not file_path.exists():
            print(f"⚠️  SKIPPED: {pdf_file} (not found)")
            continue

        print(f"\n📄 Analyzing: {pdf_file}")
        print(f"   Size: {file_path.stat().st_size / 1024:.1f} KB")

        try:
            # Analyze the document
            result = await service.analyze_document(str(file_path), use_ai=False, use_ocr=False)

            summary = result.get("summary", {})
            total_redactions = summary.get("total_redactions", 0)
            total_pages = result.get("total_pages", 0)
            predictions = summary.get("predictions_made", 0)

            results[pdf_file] = {
                "total_redactions": total_redactions,
                "total_pages": total_pages,
                "total_predictions": predictions,
                "avg_per_page": round(total_redactions / total_pages, 2) if total_pages > 0 else 0
            }

            print(f"   ✓ Pages: {total_pages}")
            print(f"   ✓ Redactions: {total_redactions}")
            print(f"   ✓ Predictions: {predictions}")
            print(f"   ✓ Avg per page: {results[pdf_file]['avg_per_page']}")

        except Exception as e:
            print(f"   ✗ ERROR: {str(e)}")
            results[pdf_file] = {"error": str(e)}

    # Generate summary
    print("\n" + "=" * 80)
    print("SUMMARY - ALL EPSTEIN FILES")
    print("=" * 80)

    total_docs = len([r for r in results.values() if "error" not in r])
    total_redactions_all = sum(r.get("total_redactions", 0) for r in results.values() if "error" not in r)
    total_pages_all = sum(r.get("total_pages", 0) for r in results.values() if "error" not in r)
    total_predictions_all = sum(r.get("total_predictions", 0) for r in results.values() if "error" not in r)

    print(f"\n📊 Total Documents Analyzed: {total_docs}")
    print(f"📄 Total Pages: {total_pages_all}")
    print(f"🔒 Total Redactions: {total_redactions_all}")
    print(f"🔍 Total Predictions: {total_predictions_all}")
    if total_pages_all > 0:
        print(f"📈 Average Redactions per Page: {total_redactions_all / total_pages_all:.2f}")
    if total_redactions_all > 0:
        print(f"💡 Prediction Success Rate: {100 * total_predictions_all / total_redactions_all:.2f}%")

    # Top 5 most redacted documents
    print("\n🔝 TOP 5 MOST REDACTED DOCUMENTS:")
    sorted_docs = sorted(
        [(k, v.get("total_redactions", 0)) for k, v in results.items() if "error" not in v],
        key=lambda x: x[1],
        reverse=True
    )[:5]

    for i, (doc, redactions) in enumerate(sorted_docs, 1):
        print(f"   {i}. {doc}: {redactions} redactions")

    # Save detailed results
    output_file = "/tmp/epstein_all_files_analysis.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Detailed results saved to: {output_file}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(analyze_all_files())
