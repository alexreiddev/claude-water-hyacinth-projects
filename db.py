#!/usr/bin/env python3
"""
Database layer for TechRec — AI Product Recommendation App.
Tables: sessions, messages, stores, channels, recommendations, admin_config.
"""

import json
import sqlite3
import uuid
from pathlib import Path

DB_PATH = Path("techrec.db")


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA foreign_keys=ON")
    return c


def init_db():
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT UNIQUE NOT NULL,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT NOT NULL,
            role        TEXT NOT NULL,
            content     TEXT NOT NULL,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS stores (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            name                TEXT NOT NULL,
            url                 TEXT NOT NULL,
            logo                TEXT DEFAULT '🛒',
            description         TEXT,
            search_url_template TEXT,
            active              INTEGER DEFAULT 1,
            sort_order          INTEGER DEFAULT 0,
            created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS channels (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            platform    TEXT NOT NULL,
            channel_id  TEXT,
            site_search TEXT,
            categories  TEXT DEFAULT '[]',
            active      INTEGER DEFAULT 1,
            sort_order  INTEGER DEFAULT 0,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS recommendations (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id           TEXT NOT NULL,
            requirements_json    TEXT,
            recommendations_json TEXT,
            created_at           DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS admin_config (
            key     TEXT PRIMARY KEY,
            value   TEXT NOT NULL
        );
        """)
        _seed_default_data(c)


def _seed_default_data(c):
    row = c.execute("SELECT COUNT(*) as cnt FROM stores").fetchone()
    if row["cnt"] > 0:
        return

    default_stores = [
        ("Amazon India",     "https://www.amazon.in",          "🛒", "Wide selection with fast delivery",       "https://www.amazon.in/s?k={query}",               1, 1),
        ("Flipkart",         "https://www.flipkart.com",       "🏪", "Great deals and competitive pricing",      "https://www.flipkart.com/search?q={query}",       1, 2),
        ("Croma",            "https://www.croma.com",          "🔵", "Tata-owned electronics retail chain",      "https://www.croma.com/searchB?q={query}",         1, 3),
        ("Reliance Digital", "https://www.reliancedigital.in", "📱", "Authorised seller with service centers",   "https://www.reliancedigital.in/search?q={query}", 1, 4),
        ("Vijay Sales",      "https://www.vijaysales.com",     "🟠", "Competitive prices with EMI options",      "https://www.vijaysales.com/search/{query}",       1, 5),
    ]
    c.executemany(
        "INSERT INTO stores (name, url, logo, description, search_url_template, active, sort_order) VALUES (?,?,?,?,?,?,?)",
        default_stores,
    )

    default_channels = [
        ("MKBHD",              "youtube", "UCBJycsmduvYEL83R_U4JriQ", None,               '["smartphones","laptops","general"]',       1, 1),
        ("Dave2D",             "youtube", "UCVYamHliCI9rw1tHR1xbkfw", None,               '["laptops","tablets"]',                     1, 2),
        ("Linus Tech Tips",    "youtube", "UCXuqSBlHAE6Xw-yeJA0Tunw", None,               '["laptops","desktops","components"]',        1, 3),
        ("Mr Mobile",          "youtube", "UCSOpcUkE-is7u7c4AkLgqTw", None,               '["smartphones","tablets"]',                 1, 4),
        ("JerryRigEverything", "youtube", "UCWFKCr40YwOZQx8FHU_ZqqQ", None,               '["smartphones"]',                           1, 5),
        ("RTINGS.com",         "google",  None,                        "rtings.com",       '["monitors","tvs","headphones","laptops"]',  1, 6),
        ("Tom\'s Hardware",    "google",  None,                        "tomshardware.com", '["laptops","desktops","components"]',        1, 7),
        ("NotebookCheck",      "google",  None,                        "notebookcheck.net",'["laptops"]',                               1, 8),
        ("GSMArena",           "google",  None,                        "gsmarena.com",     '["smartphones"]',                           1, 9),
        ("The Verge",          "google",  None,                        "theverge.com",     '["general","smartphones","laptops"]',        1, 10),
    ]
    c.executemany(
        "INSERT INTO channels (name, platform, channel_id, site_search, categories, active, sort_order) VALUES (?,?,?,?,?,?,?)",
        default_channels,
    )


# ── Sessions ──────────────────────────────────────────────────────────────────

def create_session() -> str:
    sid = str(uuid.uuid4())
    with _conn() as c:
        c.execute("INSERT INTO sessions (session_id) VALUES (?)", (sid,))
    return sid


def get_session_messages(session_id: str) -> list[dict]:
    with _conn() as c:
        rows = c.execute(
            "SELECT role, content FROM messages WHERE session_id=? ORDER BY id ASC",
            (session_id,),
        ).fetchall()
    return [{"role": r["role"], "content": r["content"]} for r in rows]


def add_message(session_id: str, role: str, content: str):
    with _conn() as c:
        c.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?,?,?)",
            (session_id, role, content),
        )
        c.execute(
            "UPDATE sessions SET updated_at=CURRENT_TIMESTAMP WHERE session_id=?",
            (session_id,),
        )


def clear_session(session_id: str):
    with _conn() as c:
        c.execute("DELETE FROM messages WHERE session_id=?", (session_id,))
        c.execute(
            "UPDATE sessions SET updated_at=CURRENT_TIMESTAMP WHERE session_id=?",
            (session_id,),
        )


# ── Stores ────────────────────────────────────────────────────────────────────

def list_stores(active_only: bool = False) -> list[dict]:
    q = "SELECT * FROM stores"
    if active_only:
        q += " WHERE active=1"
    q += " ORDER BY sort_order ASC, id ASC"
    with _conn() as c:
        rows = c.execute(q).fetchall()
    return [dict(r) for r in rows]


def add_store(data: dict) -> int:
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO stores (name, url, logo, description, search_url_template, active, sort_order) VALUES (?,?,?,?,?,?,?)",
            (data["name"], data["url"], data.get("logo", "🛒"),
             data.get("description", ""), data.get("search_url_template", ""),
             int(data.get("active", 1)), int(data.get("sort_order", 0))),
        )
        return cur.lastrowid


def update_store(store_id: int, data: dict):
    with _conn() as c:
        c.execute(
            "UPDATE stores SET name=?, url=?, logo=?, description=?, search_url_template=?, active=?, sort_order=? WHERE id=?",
            (data["name"], data["url"], data.get("logo", "🛒"),
             data.get("description", ""), data.get("search_url_template", ""),
             int(data.get("active", 1)), int(data.get("sort_order", 0)), store_id),
        )


def delete_store(store_id: int):
    with _conn() as c:
        c.execute("DELETE FROM stores WHERE id=?", (store_id,))


# ── Channels ──────────────────────────────────────────────────────────────────

def list_channels(active_only: bool = False) -> list[dict]:
    q = "SELECT * FROM channels"
    if active_only:
        q += " WHERE active=1"
    q += " ORDER BY sort_order ASC, id ASC"
    with _conn() as c:
        rows = c.execute(q).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["categories"] = json.loads(d.get("categories") or "[]")
        result.append(d)
    return result


def add_channel(data: dict) -> int:
    cats = json.dumps(data.get("categories", []))
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO channels (name, platform, channel_id, site_search, categories, active, sort_order) VALUES (?,?,?,?,?,?,?)",
            (data["name"], data["platform"], data.get("channel_id"),
             data.get("site_search"), cats,
             int(data.get("active", 1)), int(data.get("sort_order", 0))),
        )
        return cur.lastrowid


def update_channel(channel_id: int, data: dict):
    cats = json.dumps(data.get("categories", []))
    with _conn() as c:
        c.execute(
            "UPDATE channels SET name=?, platform=?, channel_id=?, site_search=?, categories=?, active=?, sort_order=? WHERE id=?",
            (data["name"], data["platform"], data.get("channel_id"),
             data.get("site_search"), cats,
             int(data.get("active", 1)), int(data.get("sort_order", 0)), channel_id),
        )


def delete_channel(channel_id: int):
    with _conn() as c:
        c.execute("DELETE FROM channels WHERE id=?", (channel_id,))


# ── Admin Config ──────────────────────────────────────────────────────────────

def get_config(key: str, default: str = "") -> str:
    with _conn() as c:
        row = c.execute("SELECT value FROM admin_config WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def set_config(key: str, value: str):
    with _conn() as c:
        c.execute(
            "INSERT INTO admin_config (key, value) VALUES (?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )


# ── Recommendations ───────────────────────────────────────────────────────────

def save_recommendation(session_id: str, requirements: dict, recommendations: dict):
    with _conn() as c:
        c.execute(
            "INSERT INTO recommendations (session_id, requirements_json, recommendations_json) VALUES (?,?,?)",
            (session_id, json.dumps(requirements), json.dumps(recommendations)),
        )


def get_last_recommendation(session_id: str) -> dict | None:
    with _conn() as c:
        row = c.execute(
            "SELECT * FROM recommendations WHERE session_id=? ORDER BY id DESC LIMIT 1",
            (session_id,),
        ).fetchone()
    if not row:
        return None
    return {
        "requirements":    json.loads(row["requirements_json"]    or "{}"),
        "recommendations": json.loads(row["recommendations_json"] or "{}"),
    }
