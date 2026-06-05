from __future__ import annotations

import json
import sqlite3
from pathlib import Path

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = frozenset({"en", "ru"})


def _db_path(base_dir: Path) -> Path:
    return base_dir / "data" / "projects.db"


def _json_settings_path(base_dir: Path) -> Path:
    return base_dir / "data" / "user_settings.json"


def _connect(base_dir: Path) -> sqlite3.Connection:
    path = _db_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    return conn


def _get_setting(conn: sqlite3.Connection, key: str) -> str | None:
    row = conn.execute(
        "SELECT value FROM app_settings WHERE key = ?", (key,)
    ).fetchone()
    return row[0] if row else None


def _set_setting(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        """
        INSERT INTO app_settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (key, value),
    )
    conn.commit()


def _migrate_json_settings(base_dir: Path, conn: sqlite3.Connection) -> None:
    if _get_setting(conn, "language_chosen"):
        return
    path = _json_settings_path(base_dir)
    if not path.is_file():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return
    if data.get("language"):
        _set_setting(conn, "language", str(data["language"]))
    if data.get("language_chosen"):
        _set_setting(conn, "language_chosen", "1")


def get_language(base_dir: Path) -> str:
    conn = _connect(base_dir)
    try:
        _migrate_json_settings(base_dir, conn)
        lang = _get_setting(conn, "language") or DEFAULT_LANGUAGE
        lang = lang.lower()
        return lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
    finally:
        conn.close()


def is_language_chosen(base_dir: Path) -> bool:
    conn = _connect(base_dir)
    try:
        _migrate_json_settings(base_dir, conn)
        return _get_setting(conn, "language_chosen") == "1"
    finally:
        conn.close()


def needs_language_selection(base_dir: Path) -> bool:
    if is_language_chosen(base_dir):
        return False
    from app.setup_state import is_setup_complete

    return not is_setup_complete(base_dir)


def set_language(base_dir: Path, language: str) -> str:
    lang = language.lower()
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    conn = _connect(base_dir)
    try:
        _set_setting(conn, "language", lang)
        _set_setting(conn, "language_chosen", "1")
    finally:
        conn.close()
    return lang
