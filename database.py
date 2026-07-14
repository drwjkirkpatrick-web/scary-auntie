"""
scary-auntie: Alaskan Native Ecological Knowledge Database
Database layer with blockchain-like integrity (hash chains for tamper evidence).

Architecture — "Hub of the Wheel":
  - Plants (botanicals) are the HUB — the primary, prepopulated reference database.
  - Knowledge Categories are SPOKES — extensible topics (animals, weather, stories,
    place names, crafts, etc.) that connect back to the botanical hub.
  - Knowledge Records are observations/entries within any category, contributed by
    community members (children, youth, elders) and reviewed by teachers/admins.
  - Groups (clans, tribes, communities) customize the wheel: their name, languages,
    territory, map center, and which categories they activate.

Author: scary-auntie project
"""

import sqlite3
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "data", "scary_auntie.db")


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys so ON DELETE CASCADE works
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _now() -> str:
    """UTC timestamp in ISO-8601 with 'Z' suffix (replaces deprecated utcnow())."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# ═══════════════════════════════════════════════════════════════
# DATABASE INITIALIZATION
# ═══════════════════════════════════════════════════════════════

def init_database():
    """Initialize the full database schema with blockchain integrity.

    Tables created (if they don't exist):
      block_chain       — tamper-evident hash chain for all operations
      plants            — verified botanical reference (THE HUB)
      knowledge_categories — extensible knowledge spokes (animals, weather, etc.)
      knowledge_records — community observations within any category
      knowledge_entries — legacy botanical observations (backward-compat)
      groups            — community/clan/tribe customization
      users             — teacher/admin/student accounts
      audit_log         — activity logging
    """
    conn = get_connection()
    cursor = conn.cursor()

    # --- BLOCKCHAIN INTEGRITY TABLE ---
    # Each record gets a hash based on its content + the previous block's hash.
    # This creates a tamper-evident chain: change any record and every subsequent
    # block's hash becomes invalid.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS block_chain (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT NOT NULL,
            record_id INTEGER NOT NULL,
            operation TEXT NOT NULL,          -- INSERT, UPDATE, DELETE
            timestamp TEXT NOT NULL,
            data_json TEXT NOT NULL,
            previous_hash TEXT NOT NULL,
            block_hash TEXT NOT NULL UNIQUE,
            recorder_name TEXT,
            signature TEXT
        )
    """)

    # --- PLANTS TABLE (THE HUB) ---
    # Verified botanical information from authoritative sources.
    # Source attribution is tracked for every entry.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latin_binomial TEXT NOT NULL,
            english_name TEXT NOT NULL,
            native_alaskan_name TEXT,        -- Native language name(s)
            native_language TEXT,            -- Which Alaska Native language(s)
            family TEXT,
            description TEXT,
            habitat TEXT,
            traditional_uses TEXT,           -- Medicinal, food, tool, spiritual
            parts_used TEXT,
            preparation TEXT,                -- How the plant is prepared
            cautions TEXT,
            image_url TEXT,
            verified INTEGER DEFAULT 0,     -- 1 = verified by expert
            source_author TEXT,              -- Attribution for scraped/cited info
            source_url TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            block_hash TEXT                  -- Links to blockchain entry
        )
    """)

    # --- KNOWLEDGE CATEGORIES TABLE (THE SPOKES) ---
    # Each category is a knowledge domain: botanicals (the hub), animals, weather,
    # stories/oral-history, place names, crafts, etc. Categories are extensible —
    # each group can activate the ones relevant to their community.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT NOT NULL UNIQUE,       -- URL-safe identifier: 'animals', 'weather'
            display_name TEXT NOT NULL,      -- Human-readable: 'Animal Knowledge'
            icon TEXT,                      -- Emoji or symbol: '🐺', '🌧️'
            description TEXT,
            is_hub INTEGER DEFAULT 0,       -- 1 = this is the botanical hub (plants)
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            block_hash TEXT
        )
    """)

    # --- KNOWLEDGE RECORDS TABLE (GENERIC OBSERVATIONS) ---
    # Community observations within any knowledge category.
    # Each record links to a category and optionally to a specific plant (the hub).
    # This lets an animal sighting reference a plant the animal was near, or a
    # weather observation note which plants are blooming.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            plant_id INTEGER,                -- Optional link to hub (botanical)
            title TEXT,                      -- Short title for the observation
            recorder_name TEXT NOT NULL,    -- Name of contributor (child/youth/elder)
            recorder_age INTEGER,           -- Optional age
            location_description TEXT,
            latitude REAL,
            longitude REAL,
            observation TEXT,               -- The main content / story / description
            native_name_used TEXT,          -- Native language term used
            tags TEXT,                      -- Comma-separated free-form tags
            photo_path TEXT,
            entry_date TEXT NOT NULL,
            reviewed INTEGER DEFAULT 0,     -- 0 = pending, 1 = approved, 2 = flagged
            reviewed_by TEXT,
            reviewed_at TEXT,
            review_notes TEXT,
            block_hash TEXT,
            FOREIGN KEY (category_id) REFERENCES knowledge_categories(id),
            FOREIGN KEY (plant_id) REFERENCES plants(id) ON DELETE SET NULL
        )
    """)

    # --- KNOWLEDGE ENTRIES TABLE (LEGACY — botanical observations) ---
    # Kept for backward compatibility with existing seeded data.
    # New observations should go through knowledge_records with the botanical category.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id INTEGER,
            recorder_name TEXT NOT NULL,
            recorder_age INTEGER,
            location_description TEXT,
            latitude REAL,
            longitude REAL,
            observation TEXT,
            native_name_used TEXT,
            photo_path TEXT,
            entry_date TEXT NOT NULL,
            reviewed INTEGER DEFAULT 0,
            reviewed_by TEXT,
            reviewed_at TEXT,
            review_notes TEXT,
            block_hash TEXT,
            FOREIGN KEY (plant_id) REFERENCES plants(id) ON DELETE SET NULL
        )
    """)

    # --- GROUPS TABLE (COMMUNITY / CLAN CUSTOMIZATION) ---
    # Each group customizes the knowledge wheel for their community:
    #   - Their name and self-identification (clan, tribe, village, etc.)
    #   - Their Native language(s)
    #   - Their geographic territory (map center + zoom)
    #   - Which knowledge categories they activate
    #   - Branding colors for the UI
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,              -- 'Yupik Communities of the Yukon'
            group_type TEXT,                 -- 'clan', 'tribe', 'village', 'school'
            description TEXT,
            native_language TEXT,            -- Primary language(s) of the group
            region TEXT,                     -- Geographic region: 'Yukon-Kuskokwim Delta'
            map_center_lat REAL DEFAULT 64.5,
            map_center_lng REAL DEFAULT -150.0,
            map_zoom INTEGER DEFAULT 4,
            primary_color TEXT DEFAULT '#2d5a3d',
            accent_color TEXT DEFAULT '#c4a35a',
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            block_hash TEXT
        )
    """)

    # --- GROUP CATEGORY ACTIVATIONS ---
    # Many-to-many: which categories each group has activated.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_category_activations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            display_order INTEGER DEFAULT 0,
            is_visible INTEGER DEFAULT 1,
            FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES knowledge_categories(id) ON DELETE CASCADE,
            UNIQUE(group_id, category_id)
        )
    """)

    # --- USERS TABLE ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'teacher',  -- teacher, admin, student
            group_id INTEGER,                      -- which group this user belongs to
            active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE SET NULL
        )
    """)

    # --- AUDIT_LOG TABLE ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            table_name TEXT,
            record_id INTEGER,
            user_name TEXT,
            details TEXT,
            timestamp TEXT NOT NULL
        )
    """)

    # ── MIGRATIONS: add columns to existing tables ──
    # CREATE TABLE IF NOT EXISTS won't add columns to tables that already exist.
    # We check each column and ALTER TABLE if missing. SQLite doesn't support
    # IF NOT EXISTS on ALTER TABLE ADD COLUMN, so we check first.
    cursor.execute("PRAGMA table_info(users)")
    user_cols = {r[1] for r in cursor.fetchall()}
    if "group_id" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL")
        print("Migration: added group_id column to users table")

    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════
# BLOCKCHAIN LAYER
# ═══════════════════════════════════════════════════════════════

def compute_hash(data: dict, previous_hash: str) -> str:
    """
    Compute a SHA-256 hash of record data + previous hash.
    Creates a blockchain-like tamper-evident chain.
    """
    # Sort keys for deterministic hashing — same data always produces same hash
    data_string = json.dumps(data, sort_keys=True, default=str)
    combined = data_string + previous_hash
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def get_last_hash() -> str:
    """Get the hash of the most recent block in the chain."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT block_hash FROM block_chain ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return row["block_hash"]
    # Genesis block hash — all zeros, the starting point of the chain
    return "0" * 64


def add_block(table_name: str, record_id: int, operation: str,
              data: dict, recorder_name: Optional[str] = None) -> str:
    """
    Add a block to the blockchain for tamper-evident record keeping.
    Returns the block hash.

    Note: This opens its own connection. Callers that have already committed
    should use this, but be aware the block add is a separate transaction.
    For truly atomic operations, use add_block_within_conn instead.
    """
    conn = get_connection()
    cursor = conn.cursor()

    previous_hash = get_last_hash()
    timestamp = _now()
    data_json = json.dumps(data, sort_keys=True, default=str)
    block_hash = compute_hash(data, previous_hash)

    cursor.execute("""
        INSERT INTO block_chain
        (table_name, record_id, operation, timestamp, data_json,
         previous_hash, block_hash, recorder_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (table_name, record_id, operation, timestamp, data_json,
          previous_hash, block_hash, recorder_name))

    conn.commit()
    conn.close()
    return block_hash


def add_block_within_conn(conn: sqlite3.Connection, table_name: str,
                          record_id: int, operation: str,
                          data: dict, recorder_name: Optional[str] = None) -> str:
    """
    Add a block using an existing connection — for atomic transactions.
    The caller is responsible for committing.
    """
    cursor = conn.cursor()

    # Get last hash within this connection
    cursor.execute("SELECT block_hash FROM block_chain ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    previous_hash = row["block_hash"] if row else "0" * 64

    timestamp = _now()
    data_json = json.dumps(data, sort_keys=True, default=str)
    block_hash = compute_hash(data, previous_hash)

    cursor.execute("""
        INSERT INTO block_chain
        (table_name, record_id, operation, timestamp, data_json,
         previous_hash, block_hash, recorder_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (table_name, record_id, operation, timestamp, data_json,
          previous_hash, block_hash, recorder_name))

    return block_hash


def verify_chain() -> List[Dict[str, Any]]:
    """
    Verify the integrity of the blockchain.
    Returns a list of any tampered blocks found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, table_name, record_id, operation, timestamp,
               data_json, previous_hash, block_hash
        FROM block_chain ORDER BY id ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    tampered = []
    previous_hash = "0" * 64

    for row in rows:
        data = json.loads(row["data_json"])
        expected_hash = compute_hash(data, previous_hash)
        if expected_hash != row["block_hash"]:
            tampered.append({
                "block_id": row["id"],
                "expected_hash": expected_hash,
                "actual_hash": row["block_hash"],
                "table": row["table_name"],
                "record_id": row["record_id"]
            })
        # Walk the chain: next block's previous_hash should be this block's hash
        previous_hash = row["block_hash"]

    return tampered


# ═══════════════════════════════════════════════════════════════
# PLANT CRUD (THE HUB)
# ═══════════════════════════════════════════════════════════════

def add_plant(latin_binomial: str, english_name: str,
              native_alaskan_name: Optional[str] = None,
              native_language: Optional[str] = None,
              family: Optional[str] = None,
              description: Optional[str] = None,
              habitat: Optional[str] = None,
              traditional_uses: Optional[str] = None,
              parts_used: Optional[str] = None,
              preparation: Optional[str] = None,
              cautions: Optional[str] = None,
              image_url: Optional[str] = None,
              verified: bool = False,
              source_author: Optional[str] = None,
              source_url: Optional[str] = None) -> int:
    """Add a verified plant to the database. Atomic — plant + block in one transaction."""
    conn = get_connection()
    cursor = conn.cursor()
    now = _now()

    cursor.execute("""
        INSERT INTO plants
        (latin_binomial, english_name, native_alaskan_name, native_language,
         family, description, habitat, traditional_uses, parts_used,
         preparation, cautions, image_url, verified, source_author,
         source_url, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (latin_binomial, english_name, native_alaskan_name, native_language,
          family, description, habitat, traditional_uses, parts_used,
          preparation, cautions, image_url, 1 if verified else 0,
          source_author, source_url, now, now))

    plant_id = cursor.lastrowid

    # Add to blockchain within the SAME transaction — atomic integrity
    data = {
        "table": "plants", "id": plant_id,
        "latin_binomial": latin_binomial,
        "english_name": english_name,
        "native_alaskan_name": native_alaskan_name,
        "source_author": source_author
    }
    block_hash = add_block_within_conn(conn, "plants", plant_id, "INSERT", data)

    # Update plant with block hash
    cursor.execute("UPDATE plants SET block_hash = ? WHERE id = ?",
                   (block_hash, plant_id))

    conn.commit()
    conn.close()
    return plant_id


def merge_plant_data(plant_id: int, additional_native_name: Optional[str] = None,
                     additional_native_language: Optional[str] = None,
                     additional_source_author: Optional[str] = None,
                     additional_source_url: Optional[str] = None,
                     description: Optional[str] = None,
                     habitat: Optional[str] = None,
                     traditional_uses: Optional[str] = None,
                     parts_used: Optional[str] = None,
                     preparation: Optional[str] = None,
                     cautions: Optional[str] = None):
    """
    Merge additional data into an existing plant — used for deduplication.
    Native names and languages are appended (semicolon-separated).
    Sources are appended. Other fields are filled only if currently NULL.
    """
    conn = get_connection()
    cursor = conn.cursor()
    now = _now()

    # Fetch current values
    cursor.execute("SELECT * FROM plants WHERE id = ?", (plant_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError(f"Plant {plant_id} not found")
    plant = dict(row)

    updates = {}

    # Append native names (avoid duplicates)
    if additional_native_name:
        existing = plant["native_alaskan_name"] or ""
        # Check if this name fragment is already present
        if additional_native_name not in existing:
            if existing:
                updates["native_alaskan_name"] = f"{existing}; {additional_native_name}"
            else:
                updates["native_alaskan_name"] = additional_native_name

    # Append native languages
    if additional_native_language:
        existing = plant["native_language"] or ""
        if additional_native_language not in existing:
            if existing:
                updates["native_language"] = f"{existing}, {additional_native_language}"
            else:
                updates["native_language"] = additional_native_language

    # Append source authors
    if additional_source_author:
        existing = plant["source_author"] or ""
        if additional_source_author not in existing:
            if existing:
                updates["source_author"] = f"{existing}; {additional_source_author}"
            else:
                updates["source_author"] = additional_source_author

    # Append source URLs
    if additional_source_url:
        existing = plant["source_url"] or ""
        if additional_source_url not in existing:
            if existing:
                updates["source_url"] = f"{existing}; {additional_source_url}"
            else:
                updates["source_url"] = additional_source_url

    # Fill in NULL fields with new data if provided
    for field in ["description", "habitat", "traditional_uses",
                  "parts_used", "preparation", "cautions"]:
        val = locals().get(field)
        if val and not plant.get(field):
            updates[field] = val

    updates["updated_at"] = now

    if updates:
        set_clauses = ", ".join(f"{k} = ?" for k in updates)
        params = list(updates.values()) + [plant_id]
        cursor.execute(f"UPDATE plants SET {set_clauses} WHERE id = ?", params)

        # Add blockchain block for the merge
        data = {
            "table": "plants", "id": plant_id,
            "action": "merge",
            "merged_native_name": additional_native_name,
            "merged_source": additional_source_author
        }
        block_hash = add_block_within_conn(conn, "plants", plant_id, "UPDATE", data)
        cursor.execute("UPDATE plants SET block_hash = ? WHERE id = ?",
                       (block_hash, plant_id))

        conn.commit()

    conn.close()
    return plant_id


def get_all_plants(search: Optional[str] = None,
                   verified_only: bool = False,
                   limit: Optional[int] = None,
                   offset: int = 0) -> List[Dict[str, Any]]:
    """Get all plants, optionally filtered by search and verification status."""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM plants WHERE 1=1"
    params: list = []

    if search:
        query += """ AND (
            latin_binomial LIKE ? OR english_name LIKE ?
            OR native_alaskan_name LIKE ? OR COALESCE(traditional_uses,'') LIKE ?
        )"""
        like = f"%{search}%"
        params.extend([like, like, like, like])

    if verified_only:
        query += " AND verified = 1"

    query += " ORDER BY english_name ASC"

    if limit:
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_plant_count() -> int:
    """Get total plant count (for pagination)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM plants")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_plant_by_id(plant_id: int) -> Optional[Dict[str, Any]]:
    """Get a single plant by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plants WHERE id = ?", (plant_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_plant_categories() -> List[Dict[str, Any]]:
    """Get plant counts grouped by family — for the browse page sidebar."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT family, COUNT(*) as count
        FROM plants
        WHERE family IS NOT NULL AND family != ''
        GROUP BY family
        ORDER BY count DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════════
# KNOWLEDGE CATEGORIES (THE SPOKES)
# ═══════════════════════════════════════════════════════════════

def add_category(slug: str, display_name: str,
                 icon: Optional[str] = None,
                 description: Optional[str] = None,
                 is_hub: bool = False) -> int:
    """Create a new knowledge category (spoke of the wheel)."""
    conn = get_connection()
    cursor = conn.cursor()
    now = _now()

    cursor.execute("""
        INSERT INTO knowledge_categories
        (slug, display_name, icon, description, is_hub, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (slug, display_name, icon, description, 1 if is_hub else 0, now, now))

    cat_id = cursor.lastrowid

    data = {
        "table": "knowledge_categories", "id": cat_id,
        "slug": slug, "display_name": display_name, "is_hub": is_hub
    }
    block_hash = add_block_within_conn(conn, "knowledge_categories", cat_id, "INSERT", data)
    cursor.execute("UPDATE knowledge_categories SET block_hash = ? WHERE id = ?",
                   (block_hash, cat_id))

    conn.commit()
    conn.close()
    return cat_id


def get_all_categories() -> List[Dict[str, Any]]:
    """Get all knowledge categories."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM knowledge_categories ORDER BY is_hub DESC, display_name ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_category_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    """Get a category by its slug."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM knowledge_categories WHERE slug = ?", (slug,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_category_by_id(category_id: int) -> Optional[Dict[str, Any]]:
    """Get a category by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM knowledge_categories WHERE id = ?", (category_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_category_counts() -> Dict[str, int]:
    """Get observation counts per category — for the wheel view."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT kc.slug, COUNT(kr.id) as count
        FROM knowledge_categories kc
        LEFT JOIN knowledge_records kr ON kc.id = kr.category_id
        GROUP BY kc.id, kc.slug
    """)
    rows = cursor.fetchall()
    conn.close()
    return {r["slug"]: r["count"] for r in rows}


# ═══════════════════════════════════════════════════════════════
# KNOWLEDGE RECORDS (GENERIC OBSERVATIONS)
# ═══════════════════════════════════════════════════════════════

def add_knowledge_record(category_id: int,
                         recorder_name: str,
                         title: Optional[str] = None,
                         plant_id: Optional[int] = None,
                         recorder_age: Optional[int] = None,
                         location_description: Optional[str] = None,
                         latitude: Optional[float] = None,
                         longitude: Optional[float] = None,
                         observation: Optional[str] = None,
                         native_name_used: Optional[str] = None,
                         tags: Optional[str] = None,
                         photo_path: Optional[str] = None) -> int:
    """Add a community knowledge observation within a category. Atomic."""
    conn = get_connection()
    cursor = conn.cursor()
    now = _now()

    cursor.execute("""
        INSERT INTO knowledge_records
        (category_id, plant_id, title, recorder_name, recorder_age,
         location_description, latitude, longitude, observation,
         native_name_used, tags, photo_path, entry_date, reviewed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (category_id, plant_id, title, recorder_name, recorder_age,
          location_description, latitude, longitude, observation,
          native_name_used, tags, photo_path, now))

    record_id = cursor.lastrowid

    data = {
        "table": "knowledge_records", "id": record_id,
        "category_id": category_id, "recorder_name": recorder_name,
        "plant_id": plant_id, "observation": observation,
        "location": location_description
    }
    block_hash = add_block_within_conn(conn, "knowledge_records", record_id, "INSERT",
                                        data, recorder_name)
    cursor.execute("UPDATE knowledge_records SET block_hash = ? WHERE id = ?",
                   (block_hash, record_id))

    conn.commit()
    conn.close()
    return record_id


def get_records_by_category(category_id: int,
                            status: Optional[str] = None,
                            limit: Optional[int] = None,
                            offset: int = 0) -> List[Dict[str, Any]]:
    """Get knowledge records for a category, optionally filtered by review status."""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT kr.*, kc.display_name as category_name, kc.icon as category_icon,
               p.english_name as plant_english_name,
               p.latin_binomial, p.native_alaskan_name as plant_native_name
        FROM knowledge_records kr
        LEFT JOIN knowledge_categories kc ON kr.category_id = kc.id
        LEFT JOIN plants p ON kr.plant_id = p.id
        WHERE kr.category_id = ?
    """
    params: list = [category_id]

    if status == "pending":
        query += " AND kr.reviewed = 0"
    elif status == "approved":
        query += " AND kr.reviewed = 1"
    elif status == "flagged":
        query += " AND kr.reviewed = 2"

    query += " ORDER BY kr.entry_date DESC"

    if limit:
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_record_by_id(record_id: int) -> Optional[Dict[str, Any]]:
    """Get a single knowledge record by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT kr.*, kc.display_name as category_name, kc.slug as category_slug,
               p.english_name as plant_english_name,
               p.latin_binomial, p.native_alaskan_name as plant_native_name
        FROM knowledge_records kr
        LEFT JOIN knowledge_categories kc ON kr.category_id = kc.id
        LEFT JOIN plants p ON kr.plant_id = p.id
        WHERE kr.id = ?
    """, (record_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def review_record(record_id: int, reviewer_name: str,
                  decision: int, notes: Optional[str] = None):
    """Review a knowledge record. decision: 1 = approve, 2 = flag. Atomic."""
    conn = get_connection()
    cursor = conn.cursor()
    now = _now()

    cursor.execute("""
        UPDATE knowledge_records
        SET reviewed = ?, reviewed_by = ?, reviewed_at = ?, review_notes = ?
        WHERE id = ?
    """, (decision, reviewer_name, now, notes, record_id))

    data = {
        "table": "knowledge_records", "id": record_id,
        "action": "review", "decision": decision,
        "reviewer": reviewer_name, "notes": notes
    }
    block_hash = add_block_within_conn(conn, "knowledge_records", record_id, "UPDATE",
                                        data, reviewer_name)

    conn.commit()
    conn.close()


def get_all_records(status: Optional[str] = None,
                    limit: Optional[int] = None,
                    offset: int = 0) -> List[Dict[str, Any]]:
    """Get all knowledge records across all categories."""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT kr.*, kc.display_name as category_name, kc.slug as category_slug,
               kc.icon as category_icon,
               p.english_name as plant_english_name
        FROM knowledge_records kr
        LEFT JOIN knowledge_categories kc ON kr.category_id = kc.id
        LEFT JOIN plants p ON kr.plant_id = p.id
        WHERE 1=1
    """
    params: list = []

    if status == "pending":
        query += " AND kr.reviewed = 0"
    elif status == "approved":
        query += " AND kr.reviewed = 1"
    elif status == "flagged":
        query += " AND kr.reviewed = 2"

    query += " ORDER BY kr.entry_date DESC"

    if limit:
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_record_count(status: Optional[str] = None) -> int:
    """Get total knowledge record count (for pagination)."""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT COUNT(*) FROM knowledge_records WHERE 1=1"
    params: list = []

    if status == "pending":
        query += " AND reviewed = 0"
    elif status == "approved":
        query += " AND reviewed = 1"
    elif status == "flagged":
        query += " AND reviewed = 2"

    cursor.execute(query, params)
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_approved_records_with_coords() -> List[Dict[str, Any]]:
    """Get approved records that have GPS coordinates — for the map."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT kr.id, kr.recorder_name, kr.title, kr.location_description,
               kr.latitude, kr.longitude, kr.observation,
               kr.native_name_used, kr.entry_date,
               kc.display_name as category_name, kc.icon as category_icon,
               p.english_name as plant_name
        FROM knowledge_records kr
        LEFT JOIN knowledge_categories kc ON kr.category_id = kc.id
        LEFT JOIN plants p ON kr.plant_id = p.id
        WHERE kr.reviewed = 1
          AND kr.latitude IS NOT NULL
          AND kr.longitude IS NOT NULL
        ORDER BY kr.entry_date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ═══════════════════════════════════════════════════════════════
# LEGACY KNOWLEDGE ENTRIES (backward compatibility)
# ═══════════════════════════════════════════════════════════════

def add_knowledge_entry(plant_id: Optional[int],
                        recorder_name: str,
                        recorder_age: Optional[int] = None,
                        location_description: Optional[str] = None,
                        latitude: Optional[float] = None,
                        longitude: Optional[float] = None,
                        observation: Optional[str] = None,
                        native_name_used: Optional[str] = None,
                        photo_path: Optional[str] = None) -> int:
    """Add a botanical knowledge entry (legacy — backward compatible with original schema)."""
    conn = get_connection()
    cursor = conn.cursor()
    now = _now()

    cursor.execute("""
        INSERT INTO knowledge_entries
        (plant_id, recorder_name, recorder_age, location_description,
         latitude, longitude, observation, native_name_used,
         photo_path, entry_date, reviewed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (plant_id, recorder_name, recorder_age, location_description,
          latitude, longitude, observation, native_name_used,
          photo_path, now))

    entry_id = cursor.lastrowid

    data = {
        "table": "knowledge_entries", "id": entry_id,
        "recorder_name": recorder_name, "plant_id": plant_id,
        "observation": observation, "location": location_description
    }
    block_hash = add_block_within_conn(conn, "knowledge_entries", entry_id, "INSERT",
                                        data, recorder_name)
    cursor.execute("UPDATE knowledge_entries SET block_hash = ? WHERE id = ?",
                   (block_hash, entry_id))

    conn.commit()
    conn.close()
    return entry_id


def get_all_entries(status: Optional[str] = None,
                    limit: Optional[int] = None,
                    offset: int = 0) -> List[Dict[str, Any]]:
    """Get all legacy knowledge entries, optionally filtered by review status."""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT ke.*, p.english_name as plant_english_name,
               p.latin_binomial, p.native_alaskan_name
        FROM knowledge_entries ke
        LEFT JOIN plants p ON ke.plant_id = p.id
        WHERE 1=1
    """
    params: list = []

    if status == "pending":
        query += " AND ke.reviewed = 0"
    elif status == "approved":
        query += " AND ke.reviewed = 1"
    elif status == "flagged":
        query += " AND ke.reviewed = 2"

    query += " ORDER BY ke.entry_date DESC"

    if limit:
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def review_entry(entry_id: int, reviewer_name: str,
                 decision: int, notes: Optional[str] = None):
    """Review a legacy knowledge entry. decision: 1 = approve, 2 = flag. Atomic."""
    conn = get_connection()
    cursor = conn.cursor()
    now = _now()

    cursor.execute("""
        UPDATE knowledge_entries
        SET reviewed = ?, reviewed_by = ?, reviewed_at = ?, review_notes = ?
        WHERE id = ?
    """, (decision, reviewer_name, now, notes, entry_id))

    data = {
        "table": "knowledge_entries", "id": entry_id,
        "action": "review", "decision": decision,
        "reviewer": reviewer_name, "notes": notes
    }
    add_block_within_conn(conn, "knowledge_entries", entry_id, "UPDATE",
                           data, reviewer_name)

    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════
# GROUPS (COMMUNITY / CLAN CUSTOMIZATION)
# ═══════════════════════════════════════════════════════════════

def add_group(name: str, group_type: Optional[str] = None,
              description: Optional[str] = None,
              native_language: Optional[str] = None,
              region: Optional[str] = None,
              map_center_lat: float = 64.5,
              map_center_lng: float = -150.0,
              map_zoom: int = 4,
              primary_color: str = "#2d5a3d",
              accent_color: str = "#c4a35a") -> int:
    """Create a new community group (clan, tribe, village, school)."""
    conn = get_connection()
    cursor = conn.cursor()
    now = _now()

    cursor.execute("""
        INSERT INTO groups
        (name, group_type, description, native_language, region,
         map_center_lat, map_center_lng, map_zoom,
         primary_color, accent_color, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
    """, (name, group_type, description, native_language, region,
          map_center_lat, map_center_lng, map_zoom,
          primary_color, accent_color, now, now))

    group_id = cursor.lastrowid

    data = {
        "table": "groups", "id": group_id,
        "name": name, "group_type": group_type,
        "native_language": native_language
    }
    block_hash = add_block_within_conn(conn, "groups", group_id, "INSERT", data)
    cursor.execute("UPDATE groups SET block_hash = ? WHERE id = ?",
                   (block_hash, group_id))

    conn.commit()
    conn.close()
    return group_id


def get_all_groups() -> List[Dict[str, Any]]:
    """Get all groups."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM groups ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_group_by_id(group_id: int) -> Optional[Dict[str, Any]]:
    """Get a group by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM groups WHERE id = ?", (group_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_group(group_id: int, **kwargs):
    """Update a group's fields. Pass column names as keyword arguments."""
    conn = get_connection()
    cursor = conn.cursor()
    now = _now()

    # Always update updated_at
    kwargs["updated_at"] = now

    set_clauses = ", ".join(f"{k} = ?" for k in kwargs)
    params = list(kwargs.values()) + [group_id]
    cursor.execute(f"UPDATE groups SET {set_clauses} WHERE id = ?", params)

    conn.commit()
    conn.close()


def activate_group_category(group_id: int, category_id: int,
                            display_order: int = 0):
    """Activate a knowledge category for a group."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO group_category_activations
        (group_id, category_id, display_order, is_visible)
        VALUES (?, ?, ?, 1)
    """, (group_id, category_id, display_order))
    conn.commit()
    conn.close()


def get_group_categories(group_id: int) -> List[Dict[str, Any]]:
    """Get categories activated for a specific group."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT kc.*, gca.display_order, gca.is_visible
        FROM knowledge_categories kc
        JOIN group_category_activations gca ON kc.id = gca.category_id
        WHERE gca.group_id = ? AND gca.is_visible = 1
        ORDER BY gca.display_order ASC, kc.display_name ASC
    """, (group_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════════
# USERS
# ═══════════════════════════════════════════════════════════════

def create_user(username: str, display_name: str,
                password_hash: str, role: str = "teacher",
                group_id: Optional[int] = None) -> int:
    """Create a teacher/admin/user."""
    conn = get_connection()
    cursor = conn.cursor()
    now = _now()

    try:
        cursor.execute("""
            INSERT INTO users (username, display_name, password_hash, role, group_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, display_name, password_hash, role, group_id, now))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError(f"Username '{username}' already exists")


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Get user by username."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND active = 1",
                   (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_users() -> List[Dict[str, Any]]:
    """Get all users for admin management."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.username, u.display_name, u.role, u.active,
               u.created_at, u.group_id, g.name as group_name
        FROM users u
        LEFT JOIN groups g ON u.group_id = g.id
        ORDER BY u.id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════════
# STATISTICS
# ═══════════════════════════════════════════════════════════════

def get_stats() -> Dict[str, int]:
    """Get dashboard statistics across both legacy entries and new records."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM plants")
    total_plants = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM plants WHERE verified = 1")
    verified_plants = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM knowledge_entries")
    legacy_entries = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM knowledge_records")
    new_records = cursor.fetchone()[0]

    total_entries = legacy_entries + new_records

    cursor.execute("SELECT COUNT(*) FROM knowledge_entries WHERE reviewed = 0")
    legacy_pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM knowledge_records WHERE reviewed = 0")
    new_pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM knowledge_entries WHERE reviewed = 1")
    legacy_approved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM knowledge_records WHERE reviewed = 1")
    new_approved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM knowledge_entries WHERE reviewed = 2")
    legacy_flagged = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM knowledge_records WHERE reviewed = 2")
    new_flagged = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM knowledge_categories")
    total_categories = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM groups")
    total_groups = cursor.fetchone()[0]

    conn.close()
    return {
        "total_plants": total_plants,
        "verified_plants": verified_plants,
        "total_entries": total_entries,
        "pending_entries": legacy_pending + new_pending,
        "approved_entries": legacy_approved + new_approved,
        "flagged_entries": legacy_flagged + new_flagged,
        "total_categories": total_categories,
        "total_groups": total_groups
    }


def get_blockchain_summary() -> Dict[str, Any]:
    """Get summary of the blockchain."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM block_chain")
    total_blocks = cursor.fetchone()[0]

    cursor.execute("SELECT block_hash FROM block_chain ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    latest_hash = row["block_hash"] if row else None

    cursor.execute("""
        SELECT table_name, COUNT(*) as count
        FROM block_chain GROUP BY table_name
    """)
    table_counts = {r["table_name"]: r["count"] for r in cursor.fetchall()}

    conn.close()

    tampered = verify_chain()

    return {
        "total_blocks": total_blocks,
        "latest_hash": latest_hash,
        "table_counts": table_counts,
        "integrity_ok": len(tampered) == 0,
        "tampered_blocks": tampered
    }


# ═══════════════════════════════════════════════════════════════
# DEFAULT DATA SEEDING
# ═══════════════════════════════════════════════════════════════

def seed_default_categories():
    """Create the default knowledge categories (spokes of the wheel).

    The botanical category is the HUB — it always exists because the plants
    table is the central reference. Other categories are spokes that groups
    can activate as needed.
    """
    default_categories = [
        {"slug": "botanicals", "display_name": "Botanical Knowledge",
         "icon": "🌿", "description": "Plants, their uses, and traditional ecological knowledge. THE HUB — all other categories connect here.",
         "is_hub": True},
        {"slug": "animals", "display_name": "Animal Knowledge",
         "icon": "🐺", "description": "Wildlife observations, animal behavior, tracking, and hunting knowledge.", "is_hub": False},
        {"slug": "weather", "display_name": "Weather & Seasons",
         "icon": "🌧️", "description": "Weather patterns, seasonal changes, ice conditions, and climate observations.", "is_hub": False},
        {"slug": "stories", "display_name": "Stories & Oral History",
         "icon": "🗣️", "description": "Oral traditions, stories, legends, and cultural knowledge from elders.", "is_hub": False},
        {"slug": "places", "display_name": "Place Names & Geography",
         "icon": "🗺️", "description": "Traditional place names, geographic features, and land-use knowledge.", "is_hub": False},
        {"slug": "crafts", "display_name": "Crafts & Material Culture",
         "icon": "🪢", "description": "Basket making, tool crafting, textile work, and traditional material knowledge.", "is_hub": False},
    ]

    for cat in default_categories:
        # Check if category already exists
        existing = get_category_by_slug(cat["slug"])
        if not existing:
            add_category(
                slug=cat["slug"],
                display_name=cat["display_name"],
                icon=cat["icon"],
                description=cat["description"],
                is_hub=cat["is_hub"]
            )


def seed_default_group():
    """Create a default group if none exists."""
    groups = get_all_groups()
    if not groups:
        add_group(
            name="Alaska Native Communities",
            group_type="network",
            description="Default community group — customize this for your clan, tribe, village, or school.",
            native_language="Yupik, Inupiaq, Dena'ina, Tlingit, Haida, Alutiiq, Athabascan",
            region="Statewide Alaska",
            map_center_lat=64.5,
            map_center_lng=-150.0,
            map_zoom=4
        )
        print("Default group created: 'Alaska Native Communities'")
        print("Customize this in the admin panel for your specific community.")