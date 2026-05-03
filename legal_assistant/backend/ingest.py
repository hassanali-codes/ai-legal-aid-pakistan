"""
backend/ingest.py
Loads legal documents from the local CSV file and splits them into chunks.
"""

import os
import csv
from typing import List, Dict


CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "pakistan_laws.csv")


def ingest_documents_from_csv() -> List[Dict]:
    """
    Read all rows from the CSV dataset and return a list of dicts with
    keys: text, title, category, section_number.
    """
    chunks: List[Dict] = []

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            content = row.get("content", "").strip()
            if not content:
                continue

            # Build a rich text chunk that includes the legal metadata
            text = (
                f"Law: {row.get('title', '')}\n"
                f"Category: {row.get('category', '')}\n"
                f"Section: {row.get('section_number', '')}\n\n"
                f"{content}"
            )

            chunks.append(
                {
                    "text": text,
                    "title": row.get("title", ""),
                    "category": row.get("category", ""),
                    "section_number": row.get("section_number", ""),
                }
            )

    return chunks


# Keep the old name as an alias so app.py can import either
ingest_documents_from_db = ingest_documents_from_csv
