from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

import psycopg2
import psycopg2.extras

from src.core.config import get_settings


@contextmanager
def _get_conn() -> Iterator["psycopg2.extensions.connection"]:
    settings = get_settings()
    conn = psycopg2.connect(settings.database_url)
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def _get_cursor() -> Iterator["psycopg2.extensions.cursor"]:
    with _get_conn() as conn:
        # RealDictCursor returns dict rows (nice for JSON)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()


# PUBLIC_INTERFACE
def fetch_one(query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    """Execute a query and return one row as a dict, or None."""
    with _get_cursor() as cur:
        cur.execute(query, params)
        row = cur.fetchone()
        return dict(row) if row else None


# PUBLIC_INTERFACE
def fetch_all(query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    """Execute a query and return all rows as a list of dicts."""
    with _get_cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]


# PUBLIC_INTERFACE
def execute(query: str, params: tuple[Any, ...] = ()) -> None:
    """Execute a statement that returns no rows."""
    with _get_cursor() as cur:
        cur.execute(query, params)
