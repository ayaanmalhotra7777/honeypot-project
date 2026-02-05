"""
SQLite Persistence Module - Stores sessions, messages, and extracted intelligence
"""

import json
import os
import sqlite3
from typing import Dict

DB_PATH = os.getenv("SQLITE_DB_PATH", os.path.join("data", "honeypot.db"))


def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TEXT,
                updated_at TEXT,
                metadata_json TEXT,
                scam_detected INTEGER,
                confidence REAL,
                agent_notes TEXT,
                message_count INTEGER
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                sender TEXT,
                text TEXT,
                timestamp TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS intelligence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                kind TEXT,
                value TEXT,
                UNIQUE(session_id, kind, value)
            )
            """
        )
        conn.commit()


def persist_session(session: Dict) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO sessions (
                session_id,
                created_at,
                updated_at,
                metadata_json,
                scam_detected,
                confidence,
                agent_notes,
                message_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                updated_at=excluded.updated_at,
                metadata_json=excluded.metadata_json,
                scam_detected=excluded.scam_detected,
                confidence=excluded.confidence,
                agent_notes=excluded.agent_notes,
                message_count=excluded.message_count
            """
            ,
            (
                session.get("sessionId"),
                session.get("created_at"),
                session.get("updated_at"),
                json.dumps(session.get("metadata", {}), ensure_ascii=True),
                1 if session.get("scam_detected") else 0,
                session.get("confidence", 0.0),
                session.get("agent_notes", ""),
                session.get("message_count", 0)
            )
        )
        conn.commit()


def persist_message(session_id: str, sender: str, text: str, timestamp: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO messages (session_id, sender, text, timestamp) VALUES (?, ?, ?, ?)",
            (session_id, sender, text, timestamp)
        )
        conn.commit()


def persist_intelligence(session_id: str, intelligence: Dict) -> None:
    items = []
    for key in ["bankAccounts", "upiIds", "phishingLinks", "phoneNumbers", "suspiciousKeywords"]:
        for value in intelligence.get(key, []):
            items.append((session_id, key, str(value)))

    for tactic in intelligence.get("tactics_used", []):
        items.append((session_id, "tactic", json.dumps(tactic, ensure_ascii=True)))

    if not items:
        return

    with _connect() as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO intelligence (session_id, kind, value) VALUES (?, ?, ?)",
            items
        )
        conn.commit()
