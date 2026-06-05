from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class ProjectStorage:
    """Хранит проекты (ключ source:id), чтобы не слать повторные уведомления."""

    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS seen_projects (
                project_id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                title TEXT,
                first_seen_at TEXT DEFAULT (datetime('now')),
                notified_at TEXT
            )
            """
        )
        self._migrate()
        self._conn.commit()

    def _migrate(self) -> None:
        columns = {
            row[1]
            for row in self._conn.execute("PRAGMA table_info(seen_projects)")
        }
        if "notified_at" not in columns:
            self._conn.execute(
                "ALTER TABLE seen_projects ADD COLUMN notified_at TEXT"
            )
        # Старые записи FL.ru без префикса источника
        self._conn.execute(
            """
            UPDATE seen_projects
            SET project_id = 'fl_ru:' || project_id
            WHERE project_id NOT LIKE '%:%'
            """
        )

    def is_seen(self, storage_key: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM seen_projects WHERE project_id = ?",
            (storage_key,),
        ).fetchone()
        return row is not None

    def mark_seen(self, storage_key: str, url: str, title: str) -> None:
        """Запомнить проект без отправки (первичное заполнение базы)."""
        self._conn.execute(
            """
            INSERT OR IGNORE INTO seen_projects (project_id, url, title, notified_at)
            VALUES (?, ?, ?, NULL)
            """,
            (storage_key, url, title),
        )
        self._conn.commit()

    def mark_notified(self, storage_key: str, url: str, title: str) -> None:
        """Запомнить проект после успешной отправки в Telegram."""
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        self._conn.execute(
            """
            INSERT INTO seen_projects (project_id, url, title, notified_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(project_id) DO UPDATE SET
                url = excluded.url,
                title = excluded.title,
                notified_at = excluded.notified_at
            """,
            (storage_key, url, title, now),
        )
        self._conn.commit()

    def count(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) FROM seen_projects").fetchone()
        return int(row[0]) if row else 0

    def count_notified(self) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) FROM seen_projects WHERE notified_at IS NOT NULL"
        ).fetchone()
        return int(row[0]) if row else 0

    def close(self) -> None:
        self._conn.close()
