"""SQLite storage helpers for Macro services."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from contextlib import contextmanager
from pathlib import Path
from typing import Any
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
    conn = sqlite3.connect(MACRO_DB_PATH, timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=15000;")
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

            CREATE TABLE IF NOT EXISTS macro_features (
              source TEXT NOT NULL,
              series_id TEXT NOT NULL,
              date TEXT NOT NULL,
              feat_name TEXT NOT NULL,
              feat_value REAL,
              updated_at TEXT NOT NULL,
              PRIMARY KEY (source, series_id, date, feat_name) ON CONFLICT REPLACE
            );

            CREATE INDEX IF NOT EXISTS idx_macro_features_key_date
              ON macro_features(source, series_id, date, feat_name);

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

            CREATE TABLE IF NOT EXISTS macro_studies (
              id TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              objective TEXT,
              conclusion_json TEXT,
              linked_assets_json TEXT,
              linked_feature_set_id TEXT,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS macro_study_series (
              study_id TEXT NOT NULL,
              position INTEGER NOT NULL,
              key TEXT NOT NULL,
              alias TEXT,
              transform_chain_json TEXT,
              freq TEXT,
              fill TEXT,
              axis TEXT,
              normalize_mode TEXT,
              lag_mode TEXT,
              display_style TEXT,
              updated_at TEXT NOT NULL,
              PRIMARY KEY (study_id, position) ON CONFLICT REPLACE
            );

            CREATE INDEX IF NOT EXISTS idx_macro_study_series_key
              ON macro_study_series(study_id, key);

            CREATE TABLE IF NOT EXISTS macro_study_views (
              study_id TEXT NOT NULL,
              view_id TEXT NOT NULL,
              mode TEXT NOT NULL,
              title TEXT,
              layout_json TEXT,
              updated_at TEXT NOT NULL,
              PRIMARY KEY (study_id, view_id) ON CONFLICT REPLACE
            );

            CREATE TABLE IF NOT EXISTS macro_study_notes (
              study_id TEXT NOT NULL,
              note_type TEXT NOT NULL,
              body TEXT,
              updated_at TEXT NOT NULL,
              PRIMARY KEY (study_id, note_type) ON CONFLICT REPLACE
            );

            CREATE TABLE IF NOT EXISTS macro_study_reports (
              study_id TEXT NOT NULL,
              report_id INTEGER,
              title TEXT,
              report_path TEXT NOT NULL,
              created_at TEXT,
              source_run_id TEXT,
              symbols_json TEXT,
              PRIMARY KEY (study_id, report_path) ON CONFLICT REPLACE
            );

            CREATE INDEX IF NOT EXISTS idx_macro_study_reports_study
              ON macro_study_reports(study_id, created_at DESC);
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


def load_observations_asof(
    source: str,
    series_id: str,
    as_of_date: str,
    start: str | None = None,
    end: str | None = None,
) -> list[dict[str, Any]]:
    """Load observations as they were known at a given as-of date."""
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
                  ORDER BY COALESCE(realtime_start, '1900-01-01') DESC, fetched_at DESC
                ) AS rn
              FROM macro_obs
              WHERE source = ? AND series_id = ? AND date >= ? AND date <= ?
                AND (realtime_start IS NULL OR realtime_start <= ?)
            ) x
            WHERE rn = 1
            ORDER BY date
            """,
            (source, series_id, start_safe, end_safe, as_of_date),
        ).fetchall()
    return [dict(row) for row in rows]


def load_observation_vintages(
    source: str,
    series_id: str,
    obs_date: str,
) -> list[dict[str, Any]]:
    """Return all stored vintages for one observation date."""
    init_macro_db()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT date, value, realtime_start, realtime_end, fetched_at
            FROM macro_obs
            WHERE source = ? AND series_id = ? AND date = ?
            ORDER BY COALESCE(realtime_start, '') ASC, fetched_at ASC
            """,
            (source, series_id, obs_date),
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


def get_obs_summary(source: str, series_id: str) -> dict[str, Any]:
    """Return freshness and vintage coverage summary for a series."""
    init_macro_db()
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
              MIN(date) AS first_obs,
              MAX(date) AS last_obs,
              MAX(fetched_at) AS last_fetched_at,
              COUNT(*) AS total_rows,
              COUNT(DISTINCT date) AS distinct_dates,
              CASE WHEN COUNT(*) > COUNT(DISTINCT date) THEN 1 ELSE 0 END AS vintage_available
            FROM macro_obs
            WHERE source = ? AND series_id = ?
            """,
            (source, series_id),
        ).fetchone()
    return dict(row) if row else {}


def get_obs_summaries(
    series_pairs: list[tuple[str, str]],
) -> dict[tuple[str, str], dict[str, Any]]:
    """Return freshness/vintage summaries for multiple series in one query."""
    normalized_pairs: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for source, series_id in series_pairs:
        key = (str(source or "").strip(), str(series_id or "").strip())
        if not key[0] or not key[1] or key in seen:
            continue
        normalized_pairs.append(key)
        seen.add(key)

    if not normalized_pairs:
        return {}

    init_macro_db()
    values_sql = ",".join("(?, ?)" for _ in normalized_pairs)
    params: list[str] = [item for pair in normalized_pairs for item in pair]
    query = f"""
        WITH requested(source, series_id) AS (
          VALUES {values_sql}
        )
        SELECT
          requested.source AS source,
          requested.series_id AS series_id,
          MIN(mo.date) AS first_obs,
          MAX(mo.date) AS last_obs,
          MAX(mo.fetched_at) AS last_fetched_at,
          COUNT(mo.date) AS total_rows,
          COUNT(DISTINCT mo.date) AS distinct_dates,
          CASE
            WHEN COUNT(mo.date) > COUNT(DISTINCT mo.date) THEN 1
            ELSE 0
          END AS vintage_available
        FROM requested
        LEFT JOIN macro_obs mo
          ON mo.source = requested.source
         AND mo.series_id = requested.series_id
        GROUP BY requested.source, requested.series_id
    """
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return {
        (str(row["source"]), str(row["series_id"])): dict(row)
        for row in rows
    }


def upsert_macro_features(
    source: str,
    series_id: str,
    rows: list[dict[str, Any]],
) -> int:
    """Upsert feature rows for one macro series."""
    init_macro_db()
    if not rows:
        return 0
    payload = [
        (
            source,
            series_id,
            str(item.get("date")),
            str(item.get("feat_name")),
            float(item.get("feat_value")) if item.get("feat_value") is not None else None,
            str(item.get("updated_at") or utc_now_iso()),
        )
        for item in rows
        if item.get("date") is not None and item.get("feat_name")
    ]
    if not payload:
        return 0
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO macro_features(
              source, series_id, date, feat_name, feat_value, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            payload,
        )
        conn.commit()
    return len(payload)


def load_macro_features(
    source: str = "FRED",
    series_ids: list[str] | None = None,
    feat_names: list[str] | None = None,
    start: str | None = None,
    end: str | None = None,
) -> list[dict[str, Any]]:
    """Load macro feature rows."""
    init_macro_db()
    where = ["source = ?"]
    params: list[Any] = [source]
    if series_ids:
        placeholders = ",".join("?" for _ in series_ids)
        where.append(f"series_id IN ({placeholders})")
        params.extend(series_ids)
    if feat_names:
        placeholders = ",".join("?" for _ in feat_names)
        where.append(f"feat_name IN ({placeholders})")
        params.extend(feat_names)
    if start:
        where.append("date >= ?")
        params.append(start)
    if end:
        where.append("date <= ?")
        params.append(end)
    query = "SELECT source, series_id, date, feat_name, feat_value, updated_at FROM macro_features"
    if where:
        query += " WHERE " + " AND ".join(where)
    query += " ORDER BY date, series_id, feat_name"
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def get_macro_obs_health_stats() -> dict[str, Any]:
    """Return aggregate observation stats for macro health endpoint."""
    init_macro_db()
    with get_connection() as conn:
        catalog_total = conn.execute("SELECT COUNT(*) AS cnt FROM macro_series WHERE active = 1").fetchone()
        with_obs = conn.execute(
            "SELECT COUNT(*) AS cnt FROM (SELECT DISTINCT source, series_id FROM macro_obs)"
        ).fetchone()
        obs_tail = conn.execute(
            "SELECT MAX(date) AS last_obs_date_global, MAX(fetched_at) AS last_fetched_at_global FROM macro_obs"
        ).fetchone()
    return {
        "total_series_in_catalog": int(catalog_total["cnt"]) if catalog_total else 0,
        "total_series_with_obs": int(with_obs["cnt"]) if with_obs else 0,
        "last_obs_date_global": obs_tail["last_obs_date_global"] if obs_tail else None,
        "last_fetched_at_global": obs_tail["last_fetched_at_global"] if obs_tail else None,
    }


def get_macro_feature_health_stats(top_n: int = 10) -> dict[str, Any]:
    """Return aggregate feature stats for macro health endpoint."""
    init_macro_db()
    top_n_safe = max(1, int(top_n))
    with get_connection() as conn:
        base = conn.execute(
            "SELECT COUNT(*) AS cnt, MAX(date) AS last_feature_date FROM macro_features"
        ).fetchone()
        names = conn.execute(
            """
            SELECT feat_name, COUNT(*) AS cnt
            FROM macro_features
            GROUP BY feat_name
            ORDER BY cnt DESC, feat_name ASC
            LIMIT ?
            """,
            (top_n_safe,),
        ).fetchall()
    return {
        "total_feature_rows": int(base["cnt"]) if base else 0,
        "last_feature_date": base["last_feature_date"] if base else None,
        "feature_names_present": [str(row["feat_name"]) for row in names],
    }


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


def _json_default(value: Any, fallback: Any) -> Any:
    if value is None:
        return fallback
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return fallback
    return value


def save_macro_study(study: dict[str, Any]) -> dict[str, Any]:
    """Persist a macro study payload."""
    init_macro_db()
    study_id = str(study.get("id") or uuid4().hex)
    now = utc_now_iso()
    created_at = str(study.get("created_at") or now)
    series_specs = study.get("series_specs") or []
    view_specs = study.get("view_specs") or []
    notes = str(study.get("notes") or "")
    linked_reports = study.get("linked_reports")

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO macro_studies(
              id, name, objective, conclusion_json, linked_assets_json, linked_feature_set_id, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              name=excluded.name,
              objective=excluded.objective,
              conclusion_json=excluded.conclusion_json,
              linked_assets_json=excluded.linked_assets_json,
              linked_feature_set_id=excluded.linked_feature_set_id,
              updated_at=excluded.updated_at
            """,
            (
                study_id,
                str(study.get("name") or "Untitled Study"),
                str(study.get("objective") or ""),
                json.dumps(study.get("conclusion") or {}, ensure_ascii=False),
                json.dumps(study.get("linked_assets") or [], ensure_ascii=False),
                study.get("linked_feature_set_id"),
                created_at,
                now,
            ),
        )
        conn.execute("DELETE FROM macro_study_series WHERE study_id = ?", (study_id,))
        for position, spec in enumerate(series_specs):
            item = dict(spec)
            conn.execute(
                """
                INSERT OR REPLACE INTO macro_study_series(
                  study_id, position, key, alias, transform_chain_json, freq, fill, axis,
                  normalize_mode, lag_mode, display_style, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    study_id,
                    position,
                    str(item.get("key") or ""),
                    item.get("alias"),
                    json.dumps(item.get("transform_chain") or [], ensure_ascii=False),
                    item.get("freq"),
                    item.get("fill"),
                    item.get("axis"),
                    item.get("normalize_mode"),
                    item.get("lag_mode"),
                    item.get("display_style"),
                    now,
                ),
            )

        conn.execute("DELETE FROM macro_study_views WHERE study_id = ?", (study_id,))
        for view in view_specs:
            item = dict(view)
            view_id = str(item.get("view_id") or uuid4().hex)
            conn.execute(
                """
                INSERT OR REPLACE INTO macro_study_views(
                  study_id, view_id, mode, title, layout_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    study_id,
                    view_id,
                    str(item.get("mode") or "explorer"),
                    item.get("title"),
                    json.dumps(item.get("layout") or {}, ensure_ascii=False),
                    now,
                ),
            )

        conn.execute(
            """
            INSERT OR REPLACE INTO macro_study_notes(study_id, note_type, body, updated_at)
            VALUES (?, 'draft', ?, ?)
            """,
            (study_id, notes, now),
        )
        if linked_reports is not None:
            conn.execute("DELETE FROM macro_study_reports WHERE study_id = ?", (study_id,))
            for attachment in linked_reports:
                item = dict(attachment)
                report_path = str(item.get("report_path") or "").strip()
                if not report_path:
                    continue
                conn.execute(
                    """
                    INSERT OR REPLACE INTO macro_study_reports(
                      study_id, report_id, title, report_path, created_at, source_run_id, symbols_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        study_id,
                        item.get("report_id"),
                        item.get("title"),
                        report_path,
                        item.get("created_at"),
                        item.get("source_run_id"),
                        json.dumps(item.get("symbols") or [], ensure_ascii=False),
                    ),
                )
        conn.commit()

    saved = get_macro_study(study_id)
    if saved is None:
        raise RuntimeError(f"Failed to load saved study: {study_id}")
    return saved


def get_macro_study(study_id: str) -> dict[str, Any] | None:
    """Load one macro study object."""
    init_macro_db()
    with get_connection() as conn:
        head = conn.execute("SELECT * FROM macro_studies WHERE id = ?", (study_id,)).fetchone()
        if not head:
            return None
        series_rows = conn.execute(
            "SELECT * FROM macro_study_series WHERE study_id = ? ORDER BY position ASC",
            (study_id,),
        ).fetchall()
        view_rows = conn.execute(
            "SELECT * FROM macro_study_views WHERE study_id = ? ORDER BY view_id ASC",
            (study_id,),
        ).fetchall()
        note_row = conn.execute(
            "SELECT body FROM macro_study_notes WHERE study_id = ? AND note_type = 'draft'",
            (study_id,),
        ).fetchone()
        report_rows = conn.execute(
            "SELECT * FROM macro_study_reports WHERE study_id = ? ORDER BY created_at DESC, report_path ASC",
            (study_id,),
        ).fetchall()

    item = dict(head)
    return {
        "id": item["id"],
        "name": item.get("name") or "Untitled Study",
        "objective": item.get("objective") or "",
        "series_specs": [
            {
                "key": row["key"],
                "alias": row["alias"],
                "transform_chain": _json_default(row["transform_chain_json"], []),
                "freq": row["freq"] or "native",
                "fill": row["fill"] or "ffill",
                "axis": row["axis"] or "left",
                "normalize_mode": row["normalize_mode"] or "raw",
                "lag_mode": row["lag_mode"],
                "display_style": row["display_style"] or "line",
            }
            for row in series_rows
        ],
        "view_specs": [
            {
                "view_id": row["view_id"],
                "mode": row["mode"],
                "title": row["title"],
                "layout": _json_default(row["layout_json"], {}),
            }
            for row in view_rows
        ],
        "notes": note_row["body"] if note_row else "",
        "conclusion": _json_default(item.get("conclusion_json"), {}),
        "linked_assets": _json_default(item.get("linked_assets_json"), []),
        "linked_reports": [
            {
                "report_id": row["report_id"],
                "title": row["title"],
                "report_path": row["report_path"],
                "created_at": row["created_at"],
                "source_run_id": row["source_run_id"],
                "symbols": _json_default(row["symbols_json"], []),
            }
            for row in report_rows
        ],
        "linked_feature_set_id": item.get("linked_feature_set_id"),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
    }


def list_macro_studies() -> list[dict[str, Any]]:
    """List macro studies ordered by latest update."""
    init_macro_db()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id FROM macro_studies ORDER BY updated_at DESC, name ASC"
        ).fetchall()
    out: list[dict[str, Any]] = []
    for row in rows:
        item = get_macro_study(str(row["id"]))
        if item is not None:
            out.append(item)
    return out


def attach_report_to_macro_study(
    study_id: str,
    *,
    report_id: int | None,
    title: str | None,
    report_path: str,
    created_at: str | None,
    source_run_id: str | None = None,
    symbols: list[str] | None = None,
) -> dict[str, Any] | None:
    """Attach one report artifact to a study."""
    init_macro_db()
    if not get_macro_study(study_id):
        return None
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO macro_study_reports(
              study_id, report_id, title, report_path, created_at, source_run_id, symbols_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                study_id,
                report_id,
                title,
                str(report_path),
                created_at or utc_now_iso(),
                source_run_id,
                json.dumps(symbols or [], ensure_ascii=False),
            ),
        )
        conn.execute(
            "UPDATE macro_studies SET updated_at = ? WHERE id = ?",
            (utc_now_iso(), study_id),
        )
        conn.commit()
    return get_macro_study(study_id)
