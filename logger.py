"""
CSV Logger - Structured event logging for analytics
"""

import csv
import json
import os
from datetime import datetime
from typing import Dict

LOG_PATH = os.getenv("CSV_LOG_PATH", os.path.join("logs", "honeypot_events.csv"))


def _ensure_log_dir() -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)


def log_event(
    session_id: str,
    sender_text: str,
    agent_reply: str,
    scam_detected: bool,
    confidence: float,
    message_count: int,
    callback_sent: bool,
    intelligence: Dict,
    metadata: Dict
) -> None:
    _ensure_log_dir()
    file_exists = os.path.exists(LOG_PATH)

    row = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "sender_text": sender_text,
        "agent_reply": agent_reply,
        "scam_detected": int(bool(scam_detected)),
        "confidence": confidence,
        "message_count": message_count,
        "callback_sent": int(bool(callback_sent)),
        "intelligence_json": json.dumps(intelligence, ensure_ascii=True),
        "metadata_json": json.dumps(metadata, ensure_ascii=True)
    }

    with open(LOG_PATH, "a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
