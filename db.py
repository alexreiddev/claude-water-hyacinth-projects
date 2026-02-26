"""SQLite database layer for the personal directory."""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / ".personal_directory.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date_met TEXT NOT NULL,
                where_met TEXT,
                profession TEXT,
                industry TEXT,
                skills TEXT,          -- JSON list
                interests TEXT,       -- JSON list
                resources TEXT,       -- JSON list (money, network, equipment, etc.)
                problems TEXT,        -- JSON list of problems/pain points they mentioned
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER NOT NULL,
                analysis TEXT NOT NULL,
                context TEXT,         -- what context/goal was used for analysis
                created_at TEXT NOT NULL,
                FOREIGN KEY (contact_id) REFERENCES contacts(id)
            )
        """)
        conn.commit()


def add_contact(data: dict) -> int:
    now = datetime.now().isoformat()
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO contacts
                (name, date_met, where_met, profession, industry, skills,
                 interests, resources, problems, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["name"],
            data.get("date_met", datetime.now().strftime("%Y-%m-%d")),
            data.get("where_met", ""),
            data.get("profession", ""),
            data.get("industry", ""),
            json.dumps(data.get("skills", [])),
            json.dumps(data.get("interests", [])),
            json.dumps(data.get("resources", [])),
            json.dumps(data.get("problems", [])),
            data.get("notes", ""),
            now,
            now,
        ))
        conn.commit()
        return cursor.lastrowid


def update_contact(contact_id: int, data: dict):
    now = datetime.now().isoformat()
    fields = []
    values = []
    list_fields = {"skills", "interests", "resources", "problems"}

    for key, val in data.items():
        if key in list_fields:
            fields.append(f"{key} = ?")
            values.append(json.dumps(val))
        elif key not in ("id", "created_at"):
            fields.append(f"{key} = ?")
            values.append(val)

    fields.append("updated_at = ?")
    values.append(now)
    values.append(contact_id)

    with get_connection() as conn:
        conn.execute(
            f"UPDATE contacts SET {', '.join(fields)} WHERE id = ?",
            values,
        )
        conn.commit()


def get_contact(contact_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM contacts WHERE id = ?", (contact_id,)
        ).fetchone()
    if row is None:
        return None
    return _deserialize(dict(row))


def list_contacts(search: str = "") -> list[dict]:
    with get_connection() as conn:
        if search:
            rows = conn.execute(
                """SELECT * FROM contacts
                   WHERE name LIKE ? OR profession LIKE ? OR industry LIKE ?
                      OR notes LIKE ?
                   ORDER BY date_met DESC""",
                (f"%{search}%",) * 4,
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM contacts ORDER BY date_met DESC"
            ).fetchall()
    return [_deserialize(dict(r)) for r in rows]


def save_analysis(contact_id: int, analysis: str, context: str = ""):
    now = datetime.now().isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO analyses (contact_id, analysis, context, created_at) VALUES (?, ?, ?, ?)",
            (contact_id, analysis, context, now),
        )
        conn.commit()


def get_analyses(contact_id: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM analyses WHERE contact_id = ? ORDER BY created_at DESC",
            (contact_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def delete_contact(contact_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM analyses WHERE contact_id = ?", (contact_id,))
        conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        conn.commit()


def _deserialize(row: dict) -> dict:
    for field in ("skills", "interests", "resources", "problems"):
        if row.get(field):
            try:
                row[field] = json.loads(row[field])
            except (json.JSONDecodeError, TypeError):
                row[field] = []
    return row
