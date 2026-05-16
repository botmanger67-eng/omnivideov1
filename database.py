import sqlite3
import json
from typing import List, Dict, Any

DB_PATH = "user_sessions.db"

def init_db():
    """Create the user_sessions table if it doesn't exist."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                user_id INTEGER PRIMARY KEY,
                conversation_history TEXT NOT NULL
            )
        """)

def get_conversation_history(user_id: int) -> List[Dict[str, str]]:
    """
    Retrieve the stored conversation history for a given user.
    Returns a list of messages in the format [{"role": "user", "content": "..."}, ...]
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT conversation_history FROM user_sessions WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        if row and row[0]:
            return json.loads(row[0])
        return []

def update_conversation_history(user_id: int, new_messages: List[Dict[str, str]]):
    """
    Replace the entire conversation history for a user.
    new_messages must be a JSON‑serializable list.
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO user_sessions (user_id, conversation_history) VALUES (?, ?)",
            (user_id, json.dumps(new_messages))
        )

def append_to_history(user_id: int, role: str, content: str):
    """Append a single message to the user's conversation history."""
    history = get_conversation_history(user_id)
    history.append({"role": role, "content": content})
    # Keep last 20 messages to avoid unbounded growth
    if len(history) > 20:
        history = history[-20:]
    update_conversation_history(user_id, history)