"""SQLite helpers for trading runtime state."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from typing import Any

from openbb_quant_ml.service.constants import RUN_REGISTRY_DB_PATH

_LOCK = RLock()


@contextmanager
def _connect(path: Path | None = None) -> Iterable[sqlite3.Connection]:
    db_path = path or RUN_REGISTRY_DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def ensure_trading_registry() -> None:
    """Create trading runtime tables when missing."""
    with _LOCK, _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trading_runs (
                cycle_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                mode TEXT NOT NULL,
                universe_id TEXT,
                started_at_utc TEXT NOT NULL,
                finished_at_utc TEXT,
                signal_count INTEGER DEFAULT 0,
                order_count INTEGER DEFAULT 0,
                fill_count INTEGER DEFAULT 0,
                error TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trading_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_id TEXT,
                event_type TEXT NOT NULL,
                ticker TEXT,
                strategy_name TEXT,
                status TEXT,
                message TEXT,
                metadata_json TEXT,
                created_at_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trading_signal_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_id TEXT NOT NULL,
                signal_id TEXT NOT NULL,
                ticker TEXT NOT NULL,
                strategy_name TEXT NOT NULL,
                signal_type TEXT,
                side TEXT,
                strength REAL,
                confidence REAL,
                risk_status TEXT,
                created_at_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trading_orders (
                order_id TEXT PRIMARY KEY,
                cycle_id TEXT,
                ticker TEXT NOT NULL,
                strategy_name TEXT NOT NULL,
                side TEXT NOT NULL,
                status TEXT NOT NULL,
                quantity REAL NOT NULL,
                requested_price REAL,
                filled_price REAL,
                notional REAL,
                reason TEXT,
                metadata_json TEXT,
                created_at_utc TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trading_fills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                cycle_id TEXT,
                ticker TEXT NOT NULL,
                strategy_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                notional REAL NOT NULL,
                fee REAL NOT NULL,
                slippage_bps REAL,
                metadata_json TEXT,
                filled_at_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trading_positions (
                ticker TEXT NOT NULL,
                strategy_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                avg_entry_price REAL NOT NULL,
                market_price REAL,
                stop_loss REAL,
                take_profit REAL,
                trailing_stop REAL,
                updated_at_utc TEXT NOT NULL,
                PRIMARY KEY(ticker, strategy_name)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trading_daily_performance (
                as_of_date TEXT PRIMARY KEY,
                equity REAL NOT NULL,
                cash REAL NOT NULL,
                used_capital REAL NOT NULL,
                realized_pnl REAL NOT NULL,
                unrealized_pnl REAL NOT NULL,
                total_pnl REAL NOT NULL,
                return_pct REAL NOT NULL,
                drawdown REAL NOT NULL,
                turnover REAL NOT NULL,
                metadata_json TEXT,
                created_at_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trading_risk_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_id TEXT,
                ticker TEXT,
                strategy_name TEXT,
                rule_id TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT NOT NULL,
                metadata_json TEXT,
                created_at_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS algorithm_registry (
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                status TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 0,
                sandbox_mode INTEGER NOT NULL DEFAULT 1,
                signal_only INTEGER NOT NULL DEFAULT 1,
                description TEXT,
                parameters_json TEXT,
                required_columns_json TEXT,
                validation_result_json TEXT,
                recent_run_result_json TEXT,
                recent_error TEXT,
                performance_summary_json TEXT,
                last_run_at_utc TEXT,
                created_at_utc TEXT NOT NULL,
                modified_at_utc TEXT NOT NULL,
                PRIMARY KEY(name, version)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS algorithm_validation_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                status TEXT NOT NULL,
                passed INTEGER NOT NULL,
                report_path TEXT,
                summary_json TEXT,
                created_at_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS algorithm_run_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                as_of_date TEXT NOT NULL,
                signal_count INTEGER NOT NULL DEFAULT 0,
                order_count INTEGER NOT NULL DEFAULT 0,
                fill_count INTEGER NOT NULL DEFAULT 0,
                win_rate REAL NOT NULL DEFAULT 0,
                avg_pnl REAL NOT NULL DEFAULT 0,
                max_drawdown REAL NOT NULL DEFAULT 0,
                sharpe REAL NOT NULL DEFAULT 0,
                turnover REAL NOT NULL DEFAULT 0,
                hold_duration REAL NOT NULL DEFAULT 0,
                rejected_order_rate REAL NOT NULL DEFAULT 0,
                risk_block_rate REAL NOT NULL DEFAULT 0,
                created_at_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS execution_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_mode TEXT NOT NULL,
                broker_name TEXT,
                live_adapter_enabled INTEGER NOT NULL DEFAULT 0,
                broker_ready INTEGER NOT NULL DEFAULT 0,
                created_at_utc TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL
            )
            """
        )


def upsert_trading_run(row: dict[str, Any]) -> None:
    ensure_trading_registry()
    with _LOCK, _connect() as conn:
        conn.execute(
            """
            INSERT INTO trading_runs(
                cycle_id, status, mode, universe_id, started_at_utc, finished_at_utc,
                signal_count, order_count, fill_count, error
            ) VALUES (
                :cycle_id, :status, :mode, :universe_id, :started_at_utc, :finished_at_utc,
                :signal_count, :order_count, :fill_count, :error
            )
            ON CONFLICT(cycle_id) DO UPDATE SET
                status=excluded.status,
                mode=excluded.mode,
                universe_id=excluded.universe_id,
                finished_at_utc=excluded.finished_at_utc,
                signal_count=excluded.signal_count,
                order_count=excluded.order_count,
                fill_count=excluded.fill_count,
                error=excluded.error
            """,
            {
                "cycle_id": row.get("cycle_id"),
                "status": row.get("status", "unknown"),
                "mode": row.get("mode", "paper"),
                "universe_id": row.get("universe_id"),
                "started_at_utc": row.get("started_at_utc"),
                "finished_at_utc": row.get("finished_at_utc"),
                "signal_count": int(row.get("signal_count", 0) or 0),
                "order_count": int(row.get("order_count", 0) or 0),
                "fill_count": int(row.get("fill_count", 0) or 0),
                "error": row.get("error"),
            },
        )


def insert_trading_event(
    *,
    cycle_id: str | None,
    event_type: str,
    ticker: str | None,
    strategy_name: str | None,
    status: str | None,
    message: str,
    metadata: dict[str, Any] | None,
    created_at_utc: str,
) -> None:
    ensure_trading_registry()
    with _LOCK, _connect() as conn:
        conn.execute(
            """
            INSERT INTO trading_events(
                cycle_id, event_type, ticker, strategy_name, status, message, metadata_json, created_at_utc
            ) VALUES (
                :cycle_id, :event_type, :ticker, :strategy_name, :status, :message, :metadata_json, :created_at_utc
            )
            """,
            {
                "cycle_id": cycle_id,
                "event_type": event_type,
                "ticker": ticker,
                "strategy_name": strategy_name,
                "status": status,
                "message": message,
                "metadata_json": json.dumps(metadata or {}, ensure_ascii=False),
                "created_at_utc": created_at_utc,
            },
        )


def list_trading_events(*, limit: int = 250) -> list[dict[str, Any]]:
    ensure_trading_registry()
    with _LOCK, _connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM trading_events ORDER BY id DESC LIMIT :limit
            """,
            {"limit": max(1, int(limit))},
        ).fetchall()
    out: list[dict[str, Any]] = []
    for row in rows:
        try:
            metadata = json.loads(str(row["metadata_json"] or "{}"))
        except Exception:
            metadata = {}
        out.append(
            {
                "timestamp": str(row["created_at_utc"]),
                "event_type": str(row["event_type"]),
                "ticker": str(row["ticker"] or ""),
                "strategy": str(row["strategy_name"] or ""),
                "status": str(row["status"] or ""),
                "message": str(row["message"] or ""),
                "metadata": metadata if isinstance(metadata, dict) else {},
            }
        )
    out.reverse()
    return out


def upsert_algorithm_record(row: dict[str, Any]) -> None:
    ensure_trading_registry()
    with _LOCK, _connect() as conn:
        conn.execute(
            """
            INSERT INTO algorithm_registry(
                name, version, status, active, sandbox_mode, signal_only, description,
                parameters_json, required_columns_json, validation_result_json,
                recent_run_result_json, recent_error, performance_summary_json,
                last_run_at_utc, created_at_utc, modified_at_utc
            ) VALUES (
                :name, :version, :status, :active, :sandbox_mode, :signal_only, :description,
                :parameters_json, :required_columns_json, :validation_result_json,
                :recent_run_result_json, :recent_error, :performance_summary_json,
                :last_run_at_utc, :created_at_utc, :modified_at_utc
            )
            ON CONFLICT(name, version) DO UPDATE SET
                status=excluded.status,
                active=excluded.active,
                sandbox_mode=excluded.sandbox_mode,
                signal_only=excluded.signal_only,
                description=excluded.description,
                parameters_json=excluded.parameters_json,
                required_columns_json=excluded.required_columns_json,
                validation_result_json=excluded.validation_result_json,
                recent_run_result_json=excluded.recent_run_result_json,
                recent_error=excluded.recent_error,
                performance_summary_json=excluded.performance_summary_json,
                last_run_at_utc=excluded.last_run_at_utc,
                modified_at_utc=excluded.modified_at_utc
            """,
            {
                "name": row.get("name"),
                "version": row.get("version"),
                "status": row.get("status", "draft"),
                "active": 1 if bool(row.get("active", False)) else 0,
                "sandbox_mode": 1 if bool(row.get("sandbox_mode", True)) else 0,
                "signal_only": 1 if bool(row.get("signal_only", True)) else 0,
                "description": row.get("description"),
                "parameters_json": json.dumps(row.get("parameters", {}), ensure_ascii=False),
                "required_columns_json": json.dumps(row.get("required_columns", []), ensure_ascii=False),
                "validation_result_json": json.dumps(row.get("validation_result", {}), ensure_ascii=False),
                "recent_run_result_json": json.dumps(row.get("recent_run_result", {}), ensure_ascii=False),
                "recent_error": row.get("recent_error"),
                "performance_summary_json": json.dumps(row.get("performance_summary", {}), ensure_ascii=False),
                "last_run_at_utc": row.get("last_run_at"),
                "created_at_utc": row.get("created_at"),
                "modified_at_utc": row.get("modified_at"),
            },
        )


def list_algorithm_records() -> list[dict[str, Any]]:
    ensure_trading_registry()
    with _LOCK, _connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM algorithm_registry ORDER BY name ASC, version DESC
            """
        ).fetchall()
    out: list[dict[str, Any]] = []
    for row in rows:
        out.append(
            {
                "name": str(row["name"]),
                "version": str(row["version"]),
                "status": str(row["status"]),
                "active": bool(row["active"]),
                "sandbox_mode": bool(row["sandbox_mode"]),
                "signal_only": bool(row["signal_only"]),
                "description": str(row["description"] or ""),
                "parameters": json.loads(str(row["parameters_json"] or "{}")),
                "required_columns": json.loads(str(row["required_columns_json"] or "[]")),
                "validation_result": json.loads(str(row["validation_result_json"] or "{}")),
                "recent_run_result": json.loads(str(row["recent_run_result_json"] or "{}")),
                "recent_error": str(row["recent_error"] or "") or None,
                "performance_summary": json.loads(str(row["performance_summary_json"] or "{}")),
                "last_run_at": str(row["last_run_at_utc"] or "") or None,
                "created_at": str(row["created_at_utc"] or "") or None,
                "modified_at": str(row["modified_at_utc"] or "") or None,
            }
        )
    return out


def insert_validation_run(row: dict[str, Any]) -> None:
    ensure_trading_registry()
    with _LOCK, _connect() as conn:
        conn.execute(
            """
            INSERT INTO algorithm_validation_runs(
                name, version, status, passed, report_path, summary_json, created_at_utc
            ) VALUES (
                :name, :version, :status, :passed, :report_path, :summary_json, :created_at_utc
            )
            """,
            {
                "name": row.get("name"),
                "version": row.get("version"),
                "status": row.get("status", "failed"),
                "passed": 1 if bool(row.get("passed", False)) else 0,
                "report_path": row.get("report_path"),
                "summary_json": json.dumps(row.get("summary", {}), ensure_ascii=False),
                "created_at_utc": row.get("created_at"),
            },
        )

