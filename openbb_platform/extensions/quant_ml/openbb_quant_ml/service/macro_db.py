"""SQLite storage helpers for Macro services."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

from openbb_quant_ml.service.macro_constants import MACRO_DB_PATH, MACRO_ROOT
from openbb_quant_ml.service.storage import utc_now_iso


def _ensure_db_parent(path: Path) -> None:
    MACRO_ROOT.mkdir(parents=True, exist_ok=True)
    path.parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_connection() -> Iterable[sqlite3.Connection]:
    """Yield SQLite connection with standard pragmas."""
    _ensure_db_parent(MACRO_DB_PATH)
    conn = sqlite3.connect(MACRO_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    try:
        yield conn
    finally:
        conn.close()


def init_macro_db() -> None:
    """Initialize macro DB schema."""
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS macro_series (
              id TEXT PRIMARY KEY,
              source TEXT NOT NULL,
              series_id TEXT NOT NULL,
              title TEXT,
              frequency TEXT,
              units TEXT,
              domain TEXT,
              default_transform TEXT,
              publish_lag INTEGER,
              notes TEXT,
              active INTEGER DEFAULT 1,
              updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS macro_obs (
              source TEXT NOT NULL,
              series_id TEXT NOT NULL,
              date TEXT NOT NULL,
              value REAL,
              realtime_start TEXT,
              realtime_end TEXT,
              fetched_at TEXT NOT NULL,
              UNIQUE(source, series_id, date, realtime_start, realtime_end) ON CONFLICT REPLACE
            );

            CREATE INDEX IF NOT EXISTS idx_macro_obs_key_date
              ON macro_obs(source, series_id, date);

            CREATE TABLE IF NOT EXISTS macro_derived (
              derived_id TEXT PRIMARY KEY,
              expression TEXT NOT NULL,
              dependencies TEXT NOT NULL,
              default_transform TEXT,
              created_at TEXT,
              updated_at TEXT,
              is_favorite INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS macro_alert_events (
              event_id TEXT PRIMARY KEY,
              rule_id TEXT NOT NULL,
              severity TEXT NOT NULL,
              triggered_at TEXT NOT NULL,
              message TEXT NOT NULL,
              value REAL,
              threshold REAL,
              context TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_macro_alert_events_ts
              ON macro_alert_events(triggered_at DESC);
            """
        )
        conn.commit()


def upsert_catalog_item(item: dict[str, Any]) -> None:
    """Upsert catalog row."""
    init_macro_db()
    payload = {
        "id": item.get("id"),
        "source": item.get("source", "FRED"),
        "series_id": item.get("series_id"),
        "title": item.get("title"),
        "frequency": item.get("frequency"),
        "units": item.get("units"),
        "domain": item.get("domain"),
        "default_transform": item.get("default_transform", "level"),
        "publish_lag": int(item.get("publish_lag", 1)),
        "notes": item.get("notes"),
        "active": 1 if item.get("active", True) else 0,
        "updated_at": utc_now_iso(),
    }
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO macro_series(
              id, source, series_id, title, frequency, units, domain, default_transform,
              publish_lag, notes, active, updated_at
            )
            VALUES(
              :id, :source, :series_id, :title, :frequency, :units, :domain, :default_transform,
              :publish_lag, :notes, :active, :updated_at
            )
            ON CONFLICT(id) DO UPDATE SET
              source=excluded.source,
              series_id=excluded.series_id,
              title=excluded.title,
              frequency=excluded.frequency,
              units=excluded.units,
              domain=excluded.domain,
              default_transform=excluded.default_transform,
              publish_lag=excluded.publish_lag,
              notes=excluded.notes,
              active=excluded.active,
              updated_at=excluded.updated_at
            """,
            payload,
        )
        conn.commit()


def get_catalog_item(key: str) -> dict[str, Any] | None:
    """Find catalog row by id or series_id."""
    init_macro_db()
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM macro_series
            WHERE id = ? OR series_id = ?
            ORDER BY CASE WHEN id = ? THEN 0 ELSE 1 END
            LIMIT 1
            """,
            (key, key, key),
        ).fetchone()
    return dict(row) if row else None


def list_catalog(domain: str | None = None, active_only: bool = True) -> list[dict[str, Any]]:
    """List catalog rows."""
    init_macro_db()
    where: list[str] = []
    params: list[Any] = []
    if domain:
        where.append("domain = ?")
        params.append(domain)
    if active_only:
        where.append("active = 1")
    query = "SELECT * FROM macro_series"
    if where:
        query += " WHERE " + " AND ".join(where)
    query += " ORDER BY domain, id"
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def upsert_observations(source: str, series_id: str, rows: list[dict[str, Any]]) -> int:
    """Upsert observations for a series."""
    init_macro_db()
    if not rows:
        return 0
    payload = [
        (
            source,
            series_id,
            str(item.get("date")),
            float(item.get("value")) if item.get("value") is not None else None,
            item.get("realtime_start"),
            item.get("realtime_end"),
            item.get("fetched_at", utc_now_iso()),
        )
        for item in rows
    ]
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO macro_obs(
              source, series_id, date, value, realtime_start, realtime_end, fetched_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            payload,
        )
        conn.commit()
    return len(payload)


def load_observations(
    source: str,
    series_id: str,
    start: str | None = None,
    end: str | None = None,
) -> list[dict[str, Any]]:
    """Load latest-vintage observations by date."""
    init_macro_db()
    start_safe = start or "1900-01-01"
    end_safe = end or "9999-12-31"
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT date, value, realtime_start, realtime_end, fetched_at
            FROM (
              SELECT
                date,
                value,
                realtime_start,
                realtime_end,
                fetched_at,
                ROW_NUMBER() OVER (
                  PARTITION BY date
                  ORDER BY COALESCE(realtime_end, '') DESC, fetched_at DESC
                ) AS rn
              FROM macro_obs
              WHERE source = ? AND series_id = ? AND date >= ? AND date <= ?
            ) x
            WHERE rn = 1
            ORDER BY date
            """,
            (source, series_id, start_safe, end_safe),
        ).fetchall()
    return [dict(row) for row in rows]


def get_obs_date_bounds(source: str, series_id: str) -> tuple[str | None, str | None]:
    """Return min/max date for stored observations."""
    init_macro_db()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT MIN(date) AS min_date, MAX(date) AS max_date FROM macro_obs WHERE source = ? AND series_id = ?",
            (source, series_id),
        ).fetchone()
    if not row:
        return None, None
    return row["min_date"], row["max_date"]


def save_derived_expression(
    derived_id: str,
    expression: str,
    dependencies: list[str],
    default_transform: str = "level",
    is_favorite: bool = True,
) -> None:
    """Save derived expression as favorite row."""
    init_macro_db()
    now = utc_now_iso()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO macro_derived(
              derived_id, expression, dependencies, default_transform, created_at, updated_at, is_favorite
            )
            VALUES(?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(derived_id) DO UPDATE SET
              expression=excluded.expression,
              dependencies=excluded.dependencies,
              default_transform=excluded.default_transform,
              updated_at=excluded.updated_at,
              is_favorite=excluded.is_favorite
            """,
            (
                derived_id,
                expression,
                json.dumps(dependencies),
                default_transform,
                now,
                now,
                1 if is_favorite else 0,
            ),
        )
        conn.commit()


def list_derived_expressions() -> list[dict[str, Any]]:
    """List saved derived expressions."""
    init_macro_db()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM macro_derived ORDER BY updated_at DESC, derived_id"
        ).fetchall()
    out: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        raw_deps = item.get("dependencies")
        if isinstance(raw_deps, str):
            try:
                item["dependencies"] = json.loads(raw_deps)
            except json.JSONDecodeError:
                item["dependencies"] = []
        out.append(item)
    return out


def save_alert_events(events: list[dict[str, Any]]) -> int:
    """Persist alert events, skipping empty payloads."""
    init_macro_db()
    if not events:
        return 0
    rows = []
    for event in events:
        event_id = event.get("event_id") or uuid4().hex
        rows.append(
            (
                event_id,
                event.get("rule_id", ""),
                event.get("severity", "info"),
                event.get("triggered_at", utc_now_iso()),
                event.get("message", ""),
                float(event.get("value", 0.0)),
                float(event.get("threshold", 0.0)),
                json.dumps(event.get("context", {}), ensure_ascii=False),
            )
        )
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO macro_alert_events(
              event_id, rule_id, severity, triggered_at, message, value, threshold, context
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()
    return len(rows)


def list_alert_events(limit: int = 200) -> list[dict[str, Any]]:
    """List alert events history."""
    init_macro_db()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM macro_alert_events ORDER BY triggered_at DESC LIMIT ?",
            (max(1, int(limit)),),
        ).fetchall()
    out: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        raw_ctx = item.get("context")
        if isinstance(raw_ctx, str):
            try:
                item["context"] = json.loads(raw_ctx)
            except json.JSONDecodeError:
                item["context"] = {}
        out.append(item)
    return out
