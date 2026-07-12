"""
scary-auntie: Alaskan Native Ecological Knowledge Database
Database layer with blockchain-like integrity (hash chains for tamper evidence).
Author: scary-auntie project
"""

import sqlite3
import hashlib
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "data", "scary_auntie.db")


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database():
    """Initialize the database schema with blockchain-like integrity."""
    conn = get_connection()
    cursor = conn.cursor()

    # --- BLOCKCHAIN INTEGRITY TABLE ---
    # Each record gets a hash based on its content + previous hash.
    # This creates a tamper-evident chain of ecological knowledge entries.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS block_chain (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT NOT NULL,
            record_id INTEGER NOT NULL,
            operation TEXT NOT NULL,  -- INSERT, UPDATE, DELETE
            timestamp TEXT NOT NULL,
            data_json TEXT NOT NULL,
            previous_hash TEXT NOT NULL,
            block_hash TEXT NOT NULL UNIQUE,
            recorder_name TEXT,
            signature TEXT
        )
    """)

    # --- PLANTS TABLE ---
    # Verified botanical information from authoritative sources.
    # Sources are tracked for attribution.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latin_binomial TEXT NOT NULL,
            english_name TEXT NOT NULL,
            native_alaskan_name TEXT,  -- Native language name (Yupik, Inupiaq, Tlingit, etc.)
            native_language TEXT,        -- Which Alaska Native language
            family TEXT,
            description TEXT,
            habitat TEXT,
            traditional_uses TEXT,       -- Medicinal, food, tool, spiritual
            parts_used TEXT,
            preparation TEXT,            -- How the plant is prepared
            cautions TEXT,
            image_url TEXT,
            verified INTEGER DEFAULT 0,  -- 1 = verified by expert, 0 = community-contributed
            source_author TEXT,          -- Attribution for scraped/cited info
            source_url TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            block_hash TEXT              -- Links to blockchain entry
        )
    """)

    # --- KNOWLEDGE_ENTRIES TABLE ---
    # Children and adolescents contribute observations here.
    # Each entry is hashed into the blockchain for integrity.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id INTEGER,
            recorder_name TEXT NOT NULL,       -- Name of child/adolescent
            recorder_age INTEGER,               -- Optional age
            location_description TEXT,          -- Where they found it
            latitude REAL,
            longitude REAL,
            observation TEXT,                   -- What they observed
            native_name_used TEXT,             -- Which native name they used
            photo_path TEXT,
            entry_date TEXT NOT NULL,
            reviewed INTEGER DEFAULT 0,         -- 0 = pending, 1 = approved, 2 = flagged
            reviewed_by TEXT,
            reviewed_at TEXT,
            review_notes TEXT,
            block_hash TEXT,                    -- Links to blockchain entry
            FOREIGN KEY (plant_id) REFERENCES plants(id)
        )
    """)

    # --- USERS TABLE ---
    # Teachers and admins
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'teacher',  -- teacher, admin, student
            active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
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

    conn.commit()
    conn.close()


def compute_hash(data: dict, previous_hash: str) -> str:
    """
    Compute a SHA-256 hash of record data + previous hash.
    This creates a blockchain-like tamper-evident chain.
    """
    # Sort keys for deterministic hashing
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
    # Genesis block hash
    return "0" * 64


def add_block(table_name: str, record_id: int, operation: str,
              data: dict, recorder_name: Optional[str] = None) -> str:
    """
    Add a block to the blockchain for tamper-evident record keeping.
    Returns the block hash.
    """
    conn = get_connection()
    cursor = conn.cursor()

    previous_hash = get_last_hash()
    timestamp = datetime.utcnow().isoformat() + "Z"
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
        previous_hash = row["block_hash"]

    return tampered


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
    """Add a verified plant to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat() + "Z"

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
    conn.commit()
    conn.close()

    # Add to blockchain
    data = {
        "table": "plants", "id": plant_id,
        "latin_binomial": latin_binomial,
        "english_name": english_name,
        "native_alaskan_name": native_alaskan_name,
        "source_author": source_author
    }
    block_hash = add_block("plants", plant_id, "INSERT", data)

    # Update plant with block hash
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE plants SET block_hash = ? WHERE id = ?",
                   (block_hash, plant_id))
    conn.commit()
    conn.close()

    return plant_id


def add_knowledge_entry(plant_id: Optional[int],
                        recorder_name: str,
                        recorder_age: Optional[int] = None,
                        location_description: Optional[str] = None,
                        latitude: Optional[float] = None,
                        longitude: Optional[float] = None,
                        observation: Optional[str] = None,
                        native_name_used: Optional[str] = None,
                        photo_path: Optional[str] = None) -> int:
    """Add a community knowledge entry (child/adolescent observation)."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat() + "Z"

    cursor.execute("""
        INSERT INTO knowledge_entries
        (plant_id, recorder_name, recorder_age, location_description,
         latitude, longitude, observation, native_name_used,
         photo_path, entry_date, reviewed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (plant_id, recorder_name, recorder_age, location_description,
          latitude, longitude, observation, native_name_used,
          photo_path, now, 0))

    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Add to blockchain
    data = {
        "table": "knowledge_entries",
        "id": entry_id,
        "recorder_name": recorder_name,
        "plant_id": plant_id,
        "observation": observation,
        "location": location_description
    }
    block_hash = add_block("knowledge_entries", entry_id, "INSERT",
                           data, recorder_name)

    # Update entry with block hash
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE knowledge_entries SET block_hash = ? WHERE id = ?",
                   (block_hash, entry_id))
    conn.commit()
    conn.close()

    return entry_id


def create_user(username: str, display_name: str,
                password_hash: str, role: str = "teacher") -> int:
    """Create a teacher/admin user."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat() + "Z"

    try:
        cursor.execute("""
            INSERT INTO users (username, display_name, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (username, display_name, password_hash, role, now))
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


def get_all_plants(search: Optional[str] = None,
                   verified_only: bool = False) -> List[Dict[str, Any]]:
    """Get all plants, optionally filtered."""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM plants WHERE 1=1"
    params = []

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

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_plant_by_id(plant_id: int) -> Optional[Dict[str, Any]]:
    """Get a single plant by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plants WHERE id = ?", (plant_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_entries(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all knowledge entries, optionally filtered by review status."""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT ke.*, p.english_name as plant_english_name,
               p.latin_binomial, p.native_alaskan_name
        FROM knowledge_entries ke
        LEFT JOIN plants p ON ke.plant_id = p.id
        WHERE 1=1
    """
    params = []

    if status == "pending":
        query += " AND ke.reviewed = 0"
    elif status == "approved":
        query += " AND ke.reviewed = 1"
    elif status == "flagged":
        query += " AND ke.reviewed = 2"

    query += " ORDER BY ke.entry_date DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def review_entry(entry_id: int, reviewer_name: str,
                 decision: int, notes: Optional[str] = None):
    """
    Review a knowledge entry.
    decision: 1 = approve, 2 = flag
    """
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat() + "Z"

    cursor.execute("""
        UPDATE knowledge_entries
        SET reviewed = ?, reviewed_by = ?, reviewed_at = ?, review_notes = ?
        WHERE id = ?
    """, (decision, reviewer_name, now, notes, entry_id))

    conn.commit()
    conn.close()

    # Add to blockchain
    data = {
        "table": "knowledge_entries",
        "id": entry_id,
        "action": "review",
        "decision": decision,
        "reviewer": reviewer_name,
        "notes": notes
    }
    add_block("knowledge_entries", entry_id, "UPDATE", data, reviewer_name)


def get_stats() -> Dict[str, int]:
    """Get dashboard statistics."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM plants")
    total_plants = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM plants WHERE verified = 1")
    verified_plants = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM knowledge_entries")
    total_entries = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM knowledge_entries WHERE reviewed = 0")
    pending_entries = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM knowledge_entries WHERE reviewed = 1")
    approved_entries = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM knowledge_entries WHERE reviewed = 2")
    flagged_entries = cursor.fetchone()[0]

    conn.close()
    return {
        "total_plants": total_plants,
        "verified_plants": verified_plants,
        "total_entries": total_entries,
        "pending_entries": pending_entries,
        "approved_entries": approved_entries,
        "flagged_entries": flagged_entries
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
