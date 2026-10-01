"""SQLite persistence for calculation history."""

from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def get_database_path() -> Path:
    configured = os.getenv("CALCULATOR_DB_PATH")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parent.parent / "data" / "calculator.db"


def get_connection() -> sqlite3.Connection:
    path = get_database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def init_database() -> None:
    with closing(get_connection()) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS calculation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expression TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_history_created_at "
            "ON calculation_history(created_at DESC)"
        )
        connection.commit()


def add_history(expression: str, result: str) -> dict[str, Any]:
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with closing(get_connection()) as connection:
        cursor = connection.execute(
            "INSERT INTO calculation_history(expression, result, created_at) "
            "VALUES (?, ?, ?)",
            (expression, result, created_at),
        )
        connection.commit()
        history_id = cursor.lastrowid
    return {
        "id": history_id,
        "expression": expression,
        "result": result,
        "created_at": created_at,
    }


def list_history(search: str = "", limit: int = 100) -> list[dict[str, Any]]:
    limit = max(1, min(limit, 200))
    with closing(get_connection()) as connection:
        if search:
            like_value = f"%{search}%"
            rows = connection.execute(
                """
                SELECT id, expression, result, created_at
                FROM calculation_history
                WHERE expression LIKE ? OR result LIKE ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (like_value, like_value, limit),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT id, expression, result, created_at
                FROM calculation_history
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
    return [dict(row) for row in rows]


def delete_history(history_id: int) -> bool:
    with closing(get_connection()) as connection:
        cursor = connection.execute(
            "DELETE FROM calculation_history WHERE id = ?", (history_id,)
        )
        connection.commit()
    return cursor.rowcount > 0


def clear_history() -> int:
    with closing(get_connection()) as connection:
        cursor = connection.execute("DELETE FROM calculation_history")
        connection.commit()
    return cursor.rowcount


def get_statistics() -> dict[str, int]:
    with closing(get_connection()) as connection:
        row = connection.execute(
            "SELECT COUNT(*) AS total FROM calculation_history"
        ).fetchone()
    return {"total": int(row["total"] if row else 0)}
