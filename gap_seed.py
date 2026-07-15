"""
scary-auntie: Gap Analysis Seed Script (Record)

Adds 42 missing Alaskan Native botanicals identified by comparing
the Garibaldi (1999) "Medicinal Flora of the Alaska Natives" PDF
against the existing 250-plant database.

Sources:
- Garibaldi, Ann. "Medicinal Flora of the Alaska Natives." 1999.
  https://accs.uaa.alaska.edu/wp-content/uploads/Medicinal_Flora_Alaska_Natives.pdf
- UAF Museum of the North Ethnobotany Film Series
  https://www.uaf.edu/museum/collections/herb/ethnobotany/
- State of Alaska Ethnobotany Project
  https://plants.alaska.gov/pdf/StateAlaskaEthnobotanyProject.pdf

The full plant data (descriptions, traditional uses, preparations, cautions,
native names, source attribution) was inserted directly via database.add_plant()
on July 14, 2026. Plant IDs 259–300.

Usage:
    cd ~/projects/scary-auntie
    source venv/bin/activate
    python3 gap_seed.py    # verifies the 42 plants are present

Date: July 2026
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import init_database, add_plant
import sqlite3

init_database()

db_path = os.path.join(os.path.dirname(__file__), "data", "scary_auntie.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT latin_binomial FROM plants")
existing = {row[0] for row in cursor.fetchall()}
conn.close()

GARIBALDI_URL = "https://accs.uaa.alaska.edu/wp-content/uploads/Medicinal_Flora_Alaska_Natives.pdf"
GARIBALDI = "Garibaldi, Ann"
UAF_URL = "https://www.uaf.edu/museum/collections/herb/ethnobotany/"
STATE_URL = "https://plants.alaska.gov/pdf/StateAlaskaEthnobotanyProject.pdf"

# ── 42 NEW PLANTS FROM GAP ANALYSIS ──
# Categories: Trees/Shrubs (4), Herbs (22), Grasses/Sedges (2),
# Ferns (3), Mosses/Lichens (5), Fungi (2), Seaweeds/Algae (4)

new_plants = [
    # Trees & Shrubs
    ("Populus tremuloides", "Quaking Aspen / Trembling Aspen"),
    ("Cornus suecica", "Swedish Dwarf Dogwood / Bunchberry"),
    ("Myrica gale var. tomentosa", "Sweet Gale / Bog Myrtle"),
    ("Ribes triste", "Wild Red Currant / Northern Red Currant"),
    # Herbs
    ("Artemisia unalaskensis var. aleutica", "Aleutian Wormwood / Sisikax"),
    ("Aster subspicatus", "Purple Daisy / Purple Aster"),
    ("Caltha palustris ssp. arctica", "Marsh Marigold / Yellow Marsh Marigold"),
    ("Capsella bursa-pastoris", "Shepherd's Purse"),
    ("Coptis aspleniifolia", "Goldthread (Fern-leaved)"),
    ("Geum calthifolium", "Ross Avens / Caltha-leaved Avens"),
    ("Heuchera glabra", "Alpine Heuchera / Alum Root"),
    ("Leptarrhena pyrolifolia", "Leatherleaved Saxifrage"),
    ("Mimulus guttatus", "Yellow Monkey Flower / Common Monkey Flower"),
    ("Nuphar polysepalum", "Yellow Pond Lily / Cow Lily"),
    ("Oxytropis maydelliana", "Yellow Oxytrope / Maydell's Oxytropis"),
    ("Petasites hyperboreus", "Northern Coltsfoot"),
    ("Plantago macrocarpa", "Narrowleaf Plantain / Seashore Plantain"),
    ("Rumex acetosella", "Sheep Sorrel / Common Sorrel"),
    ("Rumex arcticus", "Arctic Dock / Sourdock / Wild Rhubarb"),
    ("Rumex fenestratus", "Indian Rhubarb / Windowed Dock"),
    ("Senecio pseudo-arnica", "Beach Fleabane / Ragwort"),
    ("Smilacina racemosa", "False Solomon's Seal"),
    ("Thalictrum sparsiflorum", "Meadow Rue / Few-flowered Meadow Rue"),
    ("Valeriana capitata", "Capitate Valerian"),
    ("Viola epipsila", "Marsh Violet"),
    ("Viola glabella", "Yellow Violet / Pioneer Violet"),
    # Grasses & Sedges
    ("Eriophorum russeolum", "Red Cottongrass / Chestnut Cottongrass"),
    ("Eriophorum scheuchzeri", "White Cottongrass / Scheuchzer's Cottongrass"),
    # Ferns
    ("Adiantum pedatum var. aleuticum", "Maidenhair Fern / Aleutian Maidenhair"),
    ("Asplenium trichomanes", "Spleenwort / Maidenhair Spleenwort"),
    ("Asplenium viride", "Green Spleenwort"),
    # Mosses & Lichens
    ("Bryoria trichodes ssp. americana", "Old Man's Beard / Black Tree Lichen"),
    ("Cladonia bellidiflora", "Cup Lichen / Bellflower Cladonia"),
    ("Hylocomium splendens", "Splendid Feather Moss / Step Moss"),
    ("Nephroma arcticum", "Arctic Kidney Lichen"),
    ("Peltigera aphthosa", "Peltigera Lichen / Scaly Pelt Lichen"),
    # Fungi
    ("Fomes igniarius", "Ink Polypore / False Tinder Fungus / Birch Conk"),
    ("Lycoperdon", "Puffball"),
    # Seaweeds & Algae
    ("Agarum cribrosum", "Agarum / Brown Seaweed / Perforated Kelp"),
    ("Alaria marginata", "Winged Kelp / Ribbon Kelp"),
    ("Nereocystis luetkeana", "Bull Kelp / Bullwhip Kelp / Giant Kelp"),
    ("Rhodoglossum latissimum", "Red Seaweed / Broad Red Algae"),
]

missing_from_db = []
already_present = []
for latin, english in new_plants:
    if latin in existing:
        already_present.append((latin, english))
    else:
        missing_from_db.append((latin, english))

print("Gap Analysis Seed Script (Verification)")
print(f"  Total new plants expected: {len(new_plants)}")
print(f"  Already in DB: {len(already_present)}")
print(f"  Missing (to add): {len(missing_from_db)}")

if missing_from_db:
    print("\nMissing plants:")
    for latin, english in missing_from_db:
        print(f"  - {latin:45s} | {english}")
else:
    print("\n✅ All 42 gap analysis plants are present in the database.")
    print(f"   Total plants: {len(existing)}")