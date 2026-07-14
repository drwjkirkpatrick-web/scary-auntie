"""
Deduplication script for scary-auntie plant database.

Merges 8 duplicate plant pairs by consolidating native names, languages, and sources
from the duplicate into the original (lower ID), then removing the duplicate.

Each duplicate has different native names from different language groups —
consolidating them preserves all the knowledge rather than discarding one.
"""
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from database import merge_plant_data, get_connection

# The 8 duplicate pairs — (keep_id, merge_id, additional_native_name,
#                          additional_native_language, additional_source_author,
#                          additional_source_url, description, habitat, etc.)
DUPLICATE_PAIRS = [
    # Rubus chamaemorus — keep ID 1, merge ID 65
    {
        "keep_id": 1,
        "merge_id": 65,
        "additional_native_name": "Néx'w (Tlingit)",
        "additional_native_language": "Tlingit",
        "additional_source_author": "Wikipedia / Telander, Todd (2012) / Yup'ik cuisine",
        "additional_source_url": None,
        "description": None, "habitat": None,
        "traditional_uses": None, "parts_used": None,
        "preparation": None, "cautions": None
    },
    # Vaccinium uliginosum — keep ID 2, merge ID 64
    {
        "keep_id": 2,
        "merge_id": 64,
        "additional_native_name": "Various Yupik and Inupiaq names",
        "additional_native_language": None,  # already has Yupik, Inupiaq
        "additional_source_author": "Wikipedia / Yup'ik cuisine article",
        "additional_source_url": None,
        "description": None, "habitat": None,
        "traditional_uses": None, "parts_used": None,
        "preparation": None, "cautions": None
    },
    # Rubus spectabilis — keep ID 3, merge ID 49
    {
        "keep_id": 3,
        "merge_id": 49,
        "additional_native_name": "Was'x'aan Tléigu (Tlingit)",
        "additional_native_language": "Tlingit",
        "additional_source_author": "Wikipedia / Telander, Todd (2012) / Olson, Wallace M. (1997)",
        "additional_source_url": None,
        "description": None, "habitat": None,
        "traditional_uses": None, "parts_used": None,
        "preparation": None, "cautions": None
    },
    # Vaccinium vitis-idaea — keep ID 5, merge ID 53
    {
        "keep_id": 5,
        "merge_id": 53,
        "additional_native_name": "Dáxw (Tlingit)",
        "additional_native_language": "Tlingit",
        "additional_source_author": "Wikipedia / Telander, Todd (2012)",
        "additional_source_url": None,
        "description": None, "habitat": None,
        "traditional_uses": None, "parts_used": None,
        "preparation": None, "cautions": None
    },
    # Sambucus racemosa — keep ID 10, merge ID 57
    {
        "keep_id": 10,
        "merge_id": 57,
        "additional_native_name": "Yéil' (Tlingit)",
        "additional_native_language": None,  # already has Tlingit
        "additional_source_author": "Wikipedia / Telander, Todd (2012)",
        "additional_source_url": None,
        "description": None, "habitat": None,
        "traditional_uses": None, "parts_used": None,
        "preparation": None, "cautions": None
    },
    # Salix alaxensis — keep ID 15, merge ID 67
    {
        "keep_id": 15,
        "merge_id": 67,
        "additional_native_name": "Various Athabascan and Inupiaq names",
        "additional_native_language": "Athabascan (multiple), Inupiaq",
        "additional_source_author": "Wikipedia / USFS Fire Effects Information System (Uchytil, 1991)",
        "additional_source_url": None,
        "description": None, "habitat": None,
        "traditional_uses": None, "parts_used": None,
        "preparation": None, "cautions": None
    },
    # Picea glauca — keep ID 23, merge ID 70
    {
        "keep_id": 23,
        "merge_id": 70,
        "additional_native_name": "Ts'uu (Dena'ina); various Athabascan names",
        "additional_native_language": "Athabascan (multiple), Inupiaq",
        "additional_source_author": "Wikipedia: Tanana Athabaskans / Garibaldi (1999) / Kari (1987)",
        "additional_source_url": None,
        "description": None, "habitat": None,
        "traditional_uses": None, "parts_used": None,
        "preparation": None, "cautions": None
    },
    # Mertensia maritima — keep ID 38, merge ID 191
    {
        "keep_id": 38,
        "merge_id": 191,
        "additional_native_name": "Various coastal names (Inupiaq, Yupik)",
        "additional_native_language": "Inupiaq, Yupik",
        "additional_source_author": "Wikipedia / Jones (1983)",
        "additional_source_url": None,
        "description": None, "habitat": None,
        "traditional_uses": None, "parts_used": None,
        "preparation": None, "cautions": None
    },
]


def run_dedup():
    """Merge duplicate plants and remove the losers."""
    print("=== Plant Deduplication ===")
    print(f"Processing {len(DUPLICATE_PAIRS)} duplicate pairs...\n")

    for pair in DUPLICATE_PAIRS:
        keep_id = pair["keep_id"]
        merge_id = pair["merge_id"]

        # Verify both exist
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT english_name, latin_binomial FROM plants WHERE id = ?", (keep_id,))
        keep = cursor.fetchone()
        cursor.execute("SELECT english_name, latin_binomial FROM plants WHERE id = ?", (merge_id,))
        merge = cursor.fetchone()
        conn.close()

        if not keep:
            print(f"  SKIP: Keep ID {keep_id} not found")
            continue
        if not merge:
            print(f"  SKIP: Merge ID {merge_id} not found (already deduped?)")
            continue

        print(f"  Merging ID {merge_id} -> {keep_id}: {keep['english_name']} ({keep['latin_binomial']})")

        # Merge data into the kept plant
        merge_plant_data(
            plant_id=keep_id,
            additional_native_name=pair["additional_native_name"],
            additional_native_language=pair["additional_native_language"],
            additional_source_author=pair["additional_source_author"],
            additional_source_url=pair["additional_source_url"],
            description=pair["description"],
            habitat=pair["habitat"],
            traditional_uses=pair["traditional_uses"],
            parts_used=pair["parts_used"],
            preparation=pair["preparation"],
            cautions=pair["cautions"]
        )

        # Re-point any knowledge_entries that reference the merge_id
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE knowledge_entries SET plant_id = ? WHERE plant_id = ?",
                       (keep_id, merge_id))
        moved_entries = cursor.rowcount

        # Re-point any knowledge_records
        cursor.execute("UPDATE knowledge_records SET plant_id = ? WHERE plant_id = ?",
                       (keep_id, merge_id))
        moved_records = cursor.rowcount

        # Delete the duplicate plant
        cursor.execute("DELETE FROM plants WHERE id = ?", (merge_id,))
        conn.commit()
        conn.close()

        print(f"    Merged. Moved {moved_entries} entries, {moved_records} records. Deleted duplicate.")
        print()

    # Verify no duplicates remain
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT latin_binomial, COUNT(*) as cnt
        FROM plants GROUP BY latin_binomial HAVING cnt > 1
    """)
    remaining = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM plants")
    total = cursor.fetchone()[0]
    conn.close()

    print(f"=== Deduplication Complete ===")
    print(f"Total plants: {total}")
    if remaining:
        print(f"WARNING: {len(remaining)} duplicates still remain:")
        for r in remaining:
            print(f"  {r['latin_binomial']} ({r['cnt']}x)")
    else:
        print("No duplicates remaining.")


if __name__ == "__main__":
    run_dedup()