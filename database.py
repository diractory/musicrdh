import sqlite3
import threading
import config

_lock = threading.Lock()
_conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
_conn.execute(
    "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, first_name TEXT, username TEXT)"
)
_conn.execute(
    "CREATE TABLE IF NOT EXISTS chats (chat_id INTEGER PRIMARY KEY, title TEXT)"
)
_conn.commit()


def add_user(user_id: int, first_name: str = "", username: str = ""):
    with _lock:
        _conn.execute(
            "INSERT OR REPLACE INTO users (user_id, first_name, username) VALUES (?, ?, ?)",
            (user_id, first_name, username or ""),
        )
        _conn.commit()


def add_chat(chat_id: int, title: str = ""):
    with _lock:
        _conn.execute(
            "INSERT OR REPLACE INTO chats (chat_id, title) VALUES (?, ?)",
            (chat_id, title or ""),
        )
        _conn.commit()


def all_users():
    with _lock:
        cur = _conn.execute("SELECT user_id FROM users")
        return [row[0] for row in cur.fetchall()]


def all_chats():
    with _lock:
        cur = _conn.execute("SELECT chat_id FROM chats")
        return [row[0] for row in cur.fetchall()]


def users_count():
    with _lock:
        cur = _conn.execute("SELECT COUNT(*) FROM users")
        return cur.fetchone()[0]


def chats_count():
    with _lock:
        cur = _conn.execute("SELECT COUNT(*) FROM chats")
        return cur.fetchone()[0]
