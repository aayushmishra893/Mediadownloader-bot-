# ============================================================
#   Database Handler - SQLite3
# ============================================================

import sqlite3
from config import DB_PATH, FREE_CREDITS_NEW_USER


def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    """Create tables if not exist."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id   INTEGER PRIMARY KEY,
            username  TEXT,
            credits   INTEGER DEFAULT 2,
            status    TEXT DEFAULT 'Active',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tokens (
            token     TEXT PRIMARY KEY,
            user_id   INTEGER,
            used      INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def add_or_get_user(user_id: int, username: str = None):
    """Add new user or return existing user data."""
    conn = get_connection()
    c = conn.cursor()
    
    # Check if user exists
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    
    if not user:
        # New user - add with free credits
        c.execute(
            "INSERT INTO users (user_id, username, credits, status) VALUES (?, ?, ?, 'Active')",
            (user_id, username, FREE_CREDITS_NEW_USER)
        )
        conn.commit()
        conn.close()
        return {"is_new": True, "credits": FREE_CREDITS_NEW_USER, "status": "Active"}
    
    conn.close()
    return {
        "is_new": False,
        "credits": user[2],
        "status":  user[3]
    }


def get_credits(user_id: int) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT credits FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0


def deduct_credit(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET credits = credits - 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def add_credits(user_id: int, amount: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()


def get_user_status(user_id: int) -> str:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT status FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def ban_user(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET status = 'Banned' WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def unban_user(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET status = 'Active' WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def save_token(token: str, user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO tokens (token, user_id, used) VALUES (?, ?, 0)",
        (token, user_id)
    )
    conn.commit()
    conn.close()


def verify_token(token: str, user_id: int) -> bool:
    """Returns True if token is valid and unused."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM tokens WHERE token = ? AND user_id = ? AND used = 0",
        (token, user_id)
    )
    row = c.fetchone()
    if row:
        c.execute("UPDATE tokens SET used = 1 WHERE token = ?", (token,))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False


def get_all_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE status = 'Active'")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]


def get_stats():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE status = 'Banned'")
    banned = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE status = 'Active'")
    active = c.fetchone()[0]
    conn.close()
    return {"total": total, "active": active, "banned": banned}
