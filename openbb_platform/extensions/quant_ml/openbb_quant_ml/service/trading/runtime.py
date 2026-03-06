"""Trading runtime orchestration service."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pandas as pd

from openbb_quant_ml.service.reporting import write_report
from openbb_quant_ml.service.trading.config_manager import (
    get_trading_config,
    save_trading_settings,
)
from openbb_quant_ml.service.trading.custom_algorithm_adapter import (
    CustomAlgorithmAdapter,
)
from openbb_quant_ml.service.trading.custom_algorithm_registry import (
    discover_custom_algorithms,
    sync_custom_algorithm_registry,
    update_algorithm_toggle,
)
from openbb_quant_ml.service.trading.dashboard_adapter import (
    build_trading_status_payload,
)
from openbb_quant_ml.service.trading.event_logger import log_trading_event
from openbb_quant_ml.service.trading.execution.paper import PaperExecutionEngine
from openbb_quant_ml.service.trading.market_data_service import (
    load_trading_market_data,
)
from openbb_quant_ml.service.trading.order_manager import build_order_intent
from openbb_quant_ml.service.trading.performance_tracker import (
    build_performance_snapshot,
    persist_performance_snapshot,
    update_positions_market_values,
)
from openbb_quant_ml.service.trading.portfolio_state_manager import (
    append_closed_position,
    apply_fill_to_portfolio,
    load_account_state,
    load_open_positions,
    save_account_state,
    save_open_positions,
)
from openbb_quant_ml.service.trading.registry import (
    ensure_trading_registry,
    list_algorithm_records,
    list_trading_events,
    upsert_algorithm_record,
    upsert_trading_run,
)
from openbb_quant_ml.service.trading.risk_engine import evaluate_signal_risk
from openbb_quant_ml.service.trading.storage import (
    append_frame,
    closed_positions_path,
    fill_history_path,
    latest_performance_path,
    latest_risk_path,
    latest_scan_meta_path,
    latest_signals_path,
    load_frame,
    load_runtime_json,
    order_history_path,
    performance_history_path,
    risk_events_path,
    save_frame,
    save_runtime_json,
    signal_history_path,
)
from openbb_quant_ml.service.trading.strategy_registry import (
    get_builtin_strategy_registry,
)
from openbb_quant_ml.service.trading.universe_service import (
    load_symbol_metadata,
    load_trading_universe,
)
from openbb_quant_ml.service.trading.validation_pipeline import (
    validate_custom_algorithm,
)


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _today_key() -> str:
    return _now_iso()[:10]


def _cycle_id() -> str:
    return f"trading-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}"


def _load_latest_signals() -> list[dict[str, Any]]:
    frame = load_frame(latest_signals_path())
    if frame.empty:
        return []
    return frame.to_dict(orient="records")


def _load_orders() -> list[dict[str, Any]]:
    frame = load_frame(order_history_path())
    if frame.empty:
        return []
    return frame.sort_values("created_at").to_dict(orient="records")


def _load_fills() -> pd.DataFrame:
    return load_frame(fill_history_path())


def _load_closed_positions() -> pd.DataFrame:
    return load_frame(closed_positions_path())


def _load_risk_events() -> list[dict[str, Any]]:
    frame = load_frame(risk_events_path())
    if frame.empty:
        return []
    return frame.to_dict(orient="records")


def _latest_symbol_price(frame: pd.DataFrame) -> float:
    if frame.empty:
        return 0.0
    return float(frame.iloc[-1].get("close", 0.0) or 0.0)


def _build_signal_row(
    signal: dict[str, Any],
    *,
    symbol_meta: dict[str, Any],
    risk_result: dict[str, Any],
    has_position: bool,
) -> dict[str, Any]:
    metadata = signal.get("metadata", {}) if isinstance(signal.get("metadata"), dict) else {}
    return {
        **signal,
        "ticker": str(signal.get("ticker", "")).upper(),
        "name": str(symbol_meta.get("name", signal.get("ticker", "")) or signal.get("ticker", "")),
        "current_price": float(metadata.get("price", signal.get("entry_price_hint", 0.0)) or 0.0),
        "signal_type": str(signal.get("signal_type", signal.get("signal", "entry"))),
        "strategy_name": str(signal.get("strategy_name", "")),
        "signal_strength": float(signal.get("strength", 0.0) or 0.0),
        "entry_score": float(signal.get("strength", 0.0) or 0.0) * 100.0,
        "priority": float(signal.get("strength", 0.0) or 0.0) * float(signal.get("confidence", 0.0) or 0.0),
        "rsi": float(metadata.get("rsi", 0.0) or 0.0),
        "macd_hist": float(metadata.get("macd_hist", 0.0) or 0.0),
        "ma_relation": float(metadata.get("ma_relation", 0.0) or 0.0),
        "volume_change_pct": float(metadata.get("volume_change_pct", 0.0) or 0.0),
        "atr": float(metadata.get("atr", 0.0) or 0.0),
        "recent_return": float(metadata.get("recent_return", 0.0) or 0.0),
        "recommended_action": str(metadata.get("recommended_action", "Hold")),
        "position_held": has_position,
        "risk_check_status": "PASS" if risk_result.get("passed", False) else "BLOCKED",
        "risk_reason_codes": list(risk_result.get("reason_codes", [])),
        "sector": str(symbol_meta.get("sector_l1", symbol_meta.get("category", "other")) or "other"),
    }


def _reset_runtime_counters(account_state: dict[str, Any]) -> dict[str, Any]:
    if str(account_state.get("counter_date", "") or "") == _today_key():
        return account_state
    account_state = dict(account_state)
    account_state["counter_date"] = _today_key()
    account_state["today_realized_pnl"] = 0.0
    account_state["today_signal_count"] = 0
    account_state["today_order_count"] = 0
    account_state["today_fill_count"] = 0
    return account_state


def _sync_algorithm_stats(
    *,
    rows: list[dict[str, Any]],
    signals: list[dict[str, Any]],
    orders: list[dict[str, Any]],
    fills: list[dict[str, Any]],
    performance: dict[str, Any],
    last_error_map: dict[tuple[str, str], str | None],
) -> None:
    counts_by_algo: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        key = (row["name"], row["version"])
        counts_by_algo[key] = {"signal_count": 0, "order_count": 0, "fill_count": 0}
    for signal in signals:
        key = (str(signal.get("strategy_name", "")), str(signal.get("algorithm_version", "")))
        if key in counts_by_algo:
            counts_by_algo[key]["signal_count"] += 1
    for order in orders:
        key = (str(order.get("strategy_name", "")), str(order.get("algorithm_version", "")))
        if key in counts_by_algo:
            counts_by_algo[key]["order_count"] += 1
    for fill in fills:
        key = (str(fill.get("strategy_name", "")), str(fill.get("algorithm_version", "")))
        if key in counts_by_algo:
            counts_by_algo[key]["fill_count"] += 1
    for row in rows:
        key = (row["name"], row["version"])
        stats = counts_by_algo.get(key, {})
        summary = dict(row.get("performance_summary", {}) or {})
        summary.update(
            {
                "signal_count": int(stats.get("signal_count", 0)),
                "order_count": int(stats.get("order_count", 0)),
                "fill_count": int(stats.get("fill_count", 0)),
                "win_rate": float(performance.get("win_rate", 0.0) or 0.0),
                "avg_pnl": float(performance.get("total_pnl", 0.0) or 0.0),
                "max_drawdown": float(performance.get("max_drawdown", 0.0) or 0.0),
                "sharpe": float(performance.get("sharpe", 0.0) or 0.0),
                "turnover": float(performance.get("turnover", 0.0) or 0.0),
                "hold_duration": float(performance.get("avg_holding_period", 0.0) or 0.0),
            }
        )
        new_row = dict(row)
        new_row["performance_summary"] = summary
        new_row["recent_run_result"] = {
            "signal_count": int(stats.get("signal_count", 0)),
            "order_count": int(stats.get("order_count", 0)),
            "fill_count": int(stats.get("fill_count", 0)),
        }
        new_row["recent_error"] = last_error_map.get(key)
        new_row["last_run_at"] = _now_iso()
        new_row["modified_at"] = _now_iso()
        upsert_algorithm_record(new_row)


def get_trading_settings_payload() -> dict[str, Any]:
    """Return current trading settings plus strategy and algorithm registry rows."""
    config = get_trading_config(refresh=True)
    strategies = []
    for name, strategy in get_builtin_strategy_registry().items():
        cfg = config.get("strategies", {}).get(name, {})
        strategies.append(
            {
                "name": name,
                "version": strategy.version,
                "description": strategy.description,
                "enabled": bool(cfg.get("enabled", False)),
                "parameters": dict(cfg.get("params", {}) or {}),
            }
        )
    algorithms = sync_custom_algorithm_registry()
    return {
        **config,
        "built_in_strategies": strategies,
        "custom_algorithm_records": algorithms,
    }


def update_trading_settings_payload(update: dict[str, Any]) -> dict[str, Any]:
    """Persist one trading settings update."""
    settings = save_trading_settings(update)
    return {
        **settings,
        "built_in_strategies": get_trading_settings_payload()["built_in_strategies"],
        "custom_algorithm_records": sync_custom_algorithm_registry(),
    }


def get_trading_status_payload() -> dict[str, Any]:
    """Return the latest high-level trading status payload."""
    settings = get_trading_config(refresh=True)
    account_state = _reset_runtime_counters(load_account_state(float(settings.get("account", {}).get("initial_cash", 1_000_000.0) or 1_000_000.0)))
    positions = update_positions_market_values(
        load_open_positions(),
        {str(item.get("ticker", "")).upper(): float(item.get("current_price", item.get("entry_price", 0.0)) or 0.0) for item in load_open_positions()},
    )
    latest_signals = _load_latest_signals()
    latest_orders = _load_orders()[-250:]
    performance = load_runtime_json(latest_performance_path(), default={})
    if not isinstance(performance, dict):
        performance = {}
    status = build_trading_status_payload(
        settings=settings,
        account_state=account_state,
        positions=positions,
        latest_signals=latest_signals,
        latest_orders=latest_orders,
        performance=performance,
    )
    return {
        **status,
        "execution_mode": str(settings.get("execution", {}).get("mode", "paper") or "paper"),
        "model_version": "trading-runtime-v1",
    }


def run_trading_cycle(*, auto_execute: bool | None = None) -> dict[str, Any]:
    """Run one EOD trading cycle: scan universe, generate signals, risk check, and optionally paper execute."""
    ensure_trading_registry()
    cycle_id = _cycle_id()
    started_at = _now_iso()
    settings = get_trading_config(refresh=True)
    settings_execution = dict(settings.get("execution", {}) or {})
    if auto_execute is not None:
        settings_execution["auto_order"] = bool(auto_execute)
    settings["execution"] = settings_execution
    account_state = _reset_runtime_counters(
        load_account_state(
            float(settings.get("account", {}).get("initial_cash", 1_000_000.0) or 1_000_000.0)
        )
    )
    account_state["runtime_status"] = "running"
    account_state["last_cycle_id"] = cycle_id
    save_account_state(account_state)

    try:
        symbols = load_trading_universe(str(settings.get("universe_id", "default") or "default"))
        metadata_map = load_symbol_metadata()
        account_state["watchlist_size"] = len(symbols)
        datasets, skipped = load_trading_market_data(
            symbols=symbols,
            lookback_days=int(settings.get("scan", {}).get("lookback_days", 320) or 320),
            provider=str(settings.get("scan", {}).get("provider", "yfinance") or "yfinance"),
            max_workers=int(settings.get("scan", {}).get("max_workers", 8) or 8),
        )
        positions = load_open_positions()
        existing_orders = _load_orders()
        pending_orders = [
            row
            for row in existing_orders
            if str(row.get("status", "")).lower() in {"pending", "submitted"}
        ]
        builtin_registry = get_builtin_strategy_registry()
        algorithm_records = sync_custom_algorithm_registry()
        custom_algorithm_map = {
            (row["name"], row["version"]): row for row in algorithm_records
        }
        discovered_algorithms = {
            (algo.name, algo.version): algo for algo in discover_custom_algorithms()
        }

        normalized_signals: list[dict[str, Any]] = []
        latest_prices: dict[str, float] = {}
        last_error_map: dict[tuple[str, str], str | None] = {}

        for symbol, frame in datasets.items():
            symbol_meta = metadata_map.get(symbol, {"symbol": symbol, "name": symbol})
            latest_prices[symbol] = _latest_symbol_price(frame)
            has_position = any(
                str(row.get("ticker", "")).upper() == symbol for row in positions
            )
            for name, strategy in builtin_registry.items():
                strategy_cfg = settings.get("strategies", {}).get(name, {})
                if not isinstance(strategy_cfg, dict) or not bool(strategy_cfg.get("enabled", False)):
                    continue
                generated = strategy.generate_signal(
                    frame,
                    params=dict(strategy_cfg.get("params", {}) or {}),
                    symbol=symbol,
                )
                if generated is None:
                    continue
                risk_result = evaluate_signal_risk(
                    signal=generated,
                    settings=settings,
                    account_state=account_state,
                    positions=positions,
                    existing_orders=pending_orders,
                    symbol_frame=frame,
                    symbol_meta=symbol_meta,
                    strategy_enabled=True,
                    allow_auto_order=True,
                )
                normalized_signals.append(
                    _build_signal_row(
                        generated,
                        symbol_meta=symbol_meta,
                        risk_result=risk_result,
                        has_position=has_position,
                    )
                )
            for key, algo in discovered_algorithms.items():
                record = custom_algorithm_map.get(key)
                if record is None:
                    continue
                if str(record.get("status", "")).lower() in {"paused", "deprecated"}:
                    continue
                adapter = CustomAlgorithmAdapter(algo)
                output, issues, error = adapter.execute(frame, symbol=symbol)
                last_error_map[key] = error
                if error:
                    log_trading_event(
                        cycle_id=cycle_id,
                        event_type="system_error",
                        ticker=symbol,
                        strategy=algo.name,
                        status="error",
                        message=f"{algo.name} execution failed: {error}",
                        metadata={"issues": issues},
                        notify=True,
                        severity="critical",
                    )
                    continue
                if output.empty:
                    continue
                for _, row in output.tail(1).iterrows():
                    generated = row.to_dict()
                    risk_result = evaluate_signal_risk(
                        signal=generated,
                        settings=settings,
                        account_state=account_state,
                        positions=positions,
                        existing_orders=pending_orders,
                        symbol_frame=frame,
                        symbol_meta=symbol_meta,
                        strategy_enabled=bool(
                            record.get("active", False)
                            or record.get("status") in {"sandbox", "validated", "active"}
                        ),
                        algorithm_status=str(record.get("status", "sandbox")),
                        allow_auto_order=True,
                    )
                    normalized_signals.append(
                        _build_signal_row(
                            generated,
                            symbol_meta=symbol_meta,
                            risk_result=risk_result,
                            has_position=has_position,
                        )
                    )

        normalized_signals.sort(
            key=lambda item: float(item.get("priority", 0.0) or 0.0),
            reverse=True,
        )
        signals_frame = pd.DataFrame(normalized_signals)
        if signals_frame.empty:
            signals_frame = pd.DataFrame(
                columns=[
                    "signal_id",
                    "timestamp",
                    "ticker",
                    "name",
                    "current_price",
                    "signal_type",
                    "side",
                    "strategy_name",
                    "algorithm_version",
                    "signal_strength",
                    "entry_score",
                    "priority",
                    "rsi",
                    "macd_hist",
                    "ma_relation",
                    "volume_change_pct",
                    "atr",
                    "recent_return",
                    "recommended_action",
                    "position_held",
                    "risk_check_status",
                    "risk_reason_codes",
                    "reason",
                    "sector",
                ]
            )

        paper_engine = PaperExecutionEngine(
            slippage_bps=float(settings_execution.get("slippage_bps", 2.0) or 2.0),
            commission_bps=float(settings_execution.get("commission_bps", 1.0) or 1.0),
            fill_policy=str(settings_execution.get("fill_policy", "close") or "close"),
        )
        new_orders: list[dict[str, Any]] = []
        new_fills: list[dict[str, Any]] = []
        risk_events: list[dict[str, Any]] = []

        for signal in normalized_signals:
            ticker = str(signal.get("ticker", "")).upper()
            current_frame = datasets.get(ticker, pd.DataFrame())
            latest_bar = current_frame.iloc[-1].to_dict() if not current_frame.empty else {}
            existing_position = next(
                (row for row in positions if str(row.get("ticker", "")).upper() == ticker),
                None,
            )
            risk_result = {
                "passed": str(signal.get("risk_check_status", "")).upper() == "PASS",
                "reason_codes": list(signal.get("risk_reason_codes", [])),
            }
            if not risk_result["passed"]:
                for code in risk_result["reason_codes"]:
                    risk_event = {
                        "timestamp": _now_iso(),
                        "ticker": ticker,
                        "strategy_name": signal.get("strategy_name"),
                        "rule_id": code,
                        "severity": "warning",
                        "status": "blocked",
                        "message": code.replace("_", " "),
                        "metadata": {"signal_id": signal.get("signal_id")},
                    }
                    risk_events.append(risk_event)
                    log_trading_event(
                        cycle_id=cycle_id,
                        event_type="risk_check_failed",
                        ticker=ticker,
                        strategy=str(signal.get("strategy_name", "")),
                        status="blocked",
                        message=f"{ticker}: {risk_event['message']}",
                        metadata=risk_event,
                    )
                continue
            order = build_order_intent(
                signal=signal,
                settings=settings,
                account_state=account_state,
                existing_position=existing_position,
                price=float(latest_bar.get("close", signal.get("current_price", 0.0)) or 0.0),
            )
            if order is None:
                continue
            order["cycle_id"] = cycle_id
            order["algorithm_version"] = signal.get("algorithm_version")
            if not bool(settings_execution.get("auto_order", False)) or bool(
                settings_execution.get("manual_approval", False)
            ):
                order["status"] = "pending"
                new_orders.append(order)
                log_trading_event(
                    cycle_id=cycle_id,
                    event_type="order_created",
                    ticker=ticker,
                    strategy=str(order.get("strategy_name", "")),
                    status="pending",
                    message=f"Pending paper order created for {ticker}.",
                    metadata={"order_id": order["order_id"]},
                )
                continue
            submitted = paper_engine.submit_order(order, latest_bar)
            updated_order = submitted["order"]
            new_orders.append(updated_order)
            fill = submitted.get("fill")
            if isinstance(fill, dict):
                fill["cycle_id"] = cycle_id
                fill["algorithm_version"] = signal.get("algorithm_version")
                new_fills.append(fill)
                account_state, positions, closed_row = apply_fill_to_portfolio(
                    fill=fill,
                    account_state=account_state,
                    positions=positions,
                    symbol_meta=metadata_map.get(ticker, {"symbol": ticker}),
                )
                if closed_row is not None:
                    append_closed_position(closed_row)
                log_trading_event(
                    cycle_id=cycle_id,
                    event_type="order_filled",
                    ticker=ticker,
                    strategy=str(updated_order.get("strategy_name", "")),
                    status="filled",
                    message=f"Paper fill simulated for {ticker}.",
                    metadata={"order_id": updated_order["order_id"], "fill_id": fill["fill_id"]},
                )

        if not signals_frame.empty:
            save_frame(latest_signals_path(), signals_frame)
            append_frame(signal_history_path(), signals_frame.assign(cycle_id=cycle_id))
        meta_payload = {
            "cycle_id": cycle_id,
            "generated_at": _now_iso(),
            "signal_count": int(len(normalized_signals)),
            "skipped_symbols": skipped,
            "universe_id": settings.get("universe_id", "default"),
        }
        save_runtime_json(latest_scan_meta_path(), meta_payload)

        if new_orders:
            append_frame(order_history_path(), pd.DataFrame(new_orders))
            account_state["last_order_at"] = _now_iso()
        if new_fills:
            append_frame(fill_history_path(), pd.DataFrame(new_fills))
            account_state["last_fill_at"] = _now_iso()
        if risk_events:
            append_frame(risk_events_path(), pd.DataFrame(risk_events))
            save_runtime_json(
                latest_risk_path(),
                {
                    "generated_at": _now_iso(),
                    "limits": settings.get("risk", {}),
                    "events": risk_events[-100:],
                },
            )
        else:
            save_runtime_json(
                latest_risk_path(),
                {
                    "generated_at": _now_iso(),
                    "limits": settings.get("risk", {}),
                    "events": [],
                },
            )
        positions = update_positions_market_values(positions, latest_prices)
        save_open_positions(positions)

        fills_frame = _load_fills()
        closed_positions = _load_closed_positions()
        performance = build_performance_snapshot(
            settings=settings,
            account_state=account_state,
            open_positions=positions,
            fills=fills_frame,
            closed_positions=closed_positions,
        )
        persist_performance_snapshot(performance)
        account_state["cash"] = performance["cash"]
        account_state["used_capital"] = performance["used_capital"]
        account_state["equity"] = performance["equity"]
        account_state["unrealized_pnl"] = performance["unrealized_pnl"]
        account_state["total_pnl"] = performance["total_pnl"]
        account_state["equity_peak"] = max(
            float(account_state.get("equity_peak", performance["equity"]) or performance["equity"]),
            float(performance["equity"]),
        )
        account_state["current_drawdown"] = (
            0.0
            if account_state["equity_peak"] <= 0
            else (performance["equity"] / account_state["equity_peak"]) - 1.0
        )
        account_state["today_signal_count"] = int(account_state.get("today_signal_count", 0) or 0) + len(normalized_signals)
        account_state["today_order_count"] = int(account_state.get("today_order_count", 0) or 0) + len(new_orders)
        account_state["today_fill_count"] = int(account_state.get("today_fill_count", 0) or 0) + len(new_fills)
        account_state["last_scan_at"] = _now_iso()
        account_state["runtime_status"] = "running"
        report = write_report(
            run_id=cycle_id,
            report_type="trading_cycle",
            title="Trading Runtime Cycle Report",
            metadata={
                "cycle_id": cycle_id,
                "mode": settings_execution.get("mode", "paper"),
                "universe_id": settings.get("universe_id", "default"),
            },
            summary={
                "signal_count": len(normalized_signals),
                "order_count": len(new_orders),
                "fill_count": len(new_fills),
                "open_positions": len(positions),
                "total_pnl": performance["total_pnl"],
            },
            sections=[
                {"heading": "Signals", "body": normalized_signals[:25]},
                {"heading": "Orders", "body": new_orders[:25]},
                {"heading": "Performance", "body": performance},
            ],
            status="created",
        )
        account_state["report_urls"] = [report["report_path"]]
        save_account_state(account_state)
        upsert_trading_run(
            {
                "cycle_id": cycle_id,
                "status": "completed",
                "mode": settings_execution.get("mode", "paper"),
                "universe_id": settings.get("universe_id", "default"),
                "started_at_utc": started_at,
                "finished_at_utc": _now_iso(),
                "signal_count": len(normalized_signals),
                "order_count": len(new_orders),
                "fill_count": len(new_fills),
                "error": None,
            }
        )
        _sync_algorithm_stats(
            rows=list_algorithm_records(),
            signals=normalized_signals,
            orders=new_orders,
            fills=new_fills,
            performance=performance,
            last_error_map=last_error_map,
        )
        return {
            "cycle_id": cycle_id,
            "status": "completed",
            "signal_count": len(normalized_signals),
            "order_count": len(new_orders),
            "fill_count": len(new_fills),
            "skipped_symbols": skipped,
            "report_path": report["report_path"],
            "status_payload": get_trading_status_payload(),
        }
    except Exception as exc:  # noqa: BLE001
        account_state["runtime_status"] = "paused"
        account_state["error_count"] = int(account_state.get("error_count", 0) or 0) + 1
        save_account_state(account_state)
        upsert_trading_run(
            {
                "cycle_id": cycle_id,
                "status": "failed",
                "mode": settings_execution.get("mode", "paper"),
                "universe_id": settings.get("universe_id", "default"),
                "started_at_utc": started_at,
                "finished_at_utc": _now_iso(),
                "signal_count": 0,
                "order_count": 0,
                "fill_count": 0,
                "error": str(exc),
            }
        )
        log_trading_event(
            cycle_id=cycle_id,
            event_type="system_error",
            ticker=None,
            strategy=None,
            status="error",
            message=f"Trading cycle failed: {exc}",
            metadata={},
            notify=True,
            severity="critical",
        )
        raise


def get_trading_latest_scan_payload(limit: int = 200) -> dict[str, Any]:
    """Return latest scan payload."""
    records = _load_latest_signals()
    if limit > 0:
        records = records[:limit]
    meta = load_runtime_json(latest_scan_meta_path(), default={})
    if not isinstance(meta, dict):
        meta = {}
    return {
        "generated_at": meta.get("generated_at"),
        "cycle_id": meta.get("cycle_id"),
        "signal_count": int(meta.get("signal_count", len(records)) or len(records)),
        "items": records,
    }


def get_trading_scan_history_payload(limit: int = 250) -> dict[str, Any]:
    """Return historical scan rows."""
    frame = load_frame(signal_history_path())
    if frame.empty:
        return {"items": []}
    rows = (
        frame.sort_values("timestamp", ascending=False)
        .head(limit)
        .to_dict(orient="records")
    )
    return {"items": rows}


def get_trading_symbol_detail_payload(ticker: str) -> dict[str, Any]:
    """Return one symbol detail panel payload."""
    key = str(ticker or "").strip().upper()
    settings = get_trading_config(refresh=True)
    datasets, _skipped = load_trading_market_data(
        symbols=[key],
        lookback_days=int(settings.get("scan", {}).get("lookback_days", 320) or 320),
        provider=str(settings.get("scan", {}).get("provider", "yfinance") or "yfinance"),
        max_workers=1,
    )
    frame = datasets.get(key, pd.DataFrame())
    if frame.empty:
        return {"ticker": key, "series": [], "signals": [], "orders": [], "position": None}
    from openbb_quant_ml.service.trading.indicator_engine import compute_indicator_frame

    enriched = compute_indicator_frame(frame).tail(120).copy()
    latest_signals = [
        row for row in _load_latest_signals() if str(row.get("ticker", "")).upper() == key
    ][:20]
    orders = [
        row for row in _load_orders() if str(row.get("ticker", "")).upper() == key
    ][-20:]
    position = next(
        (row for row in load_open_positions() if str(row.get("ticker", "")).upper() == key),
        None,
    )
    explanation = str(latest_signals[0].get("reason", "")) if latest_signals else ""
    return {
        "ticker": key,
        "series": enriched.to_dict(orient="records"),
        "signals": latest_signals,
        "orders": orders,
        "position": position,
        "explanation": explanation,
    }


def get_trading_orders_payload(limit: int = 250) -> dict[str, Any]:
    rows = _load_orders()
    return {"items": rows[-limit:]}


def get_trading_fills_payload(limit: int = 250) -> dict[str, Any]:
    frame = _load_fills()
    if frame.empty:
        return {"items": []}
    rows = (
        frame.sort_values("filled_at", ascending=False)
        .head(limit)
        .to_dict(orient="records")
    )
    return {"items": rows}


def get_trading_positions_payload() -> dict[str, Any]:
    settings = get_trading_config(refresh=True)
    positions = update_positions_market_values(
        load_open_positions(),
        {
            str(row.get("ticker", "")).upper(): float(
                row.get("current_price", row.get("entry_price", 0.0)) or 0.0
            )
            for row in load_open_positions()
        },
    )
    return {
        "mode": settings.get("mode", "paper"),
        "items": positions,
    }


def get_trading_performance_payload() -> dict[str, Any]:
    payload = load_runtime_json(latest_performance_path(), default={})
    if not isinstance(payload, dict):
        payload = {}
    frame = load_frame(performance_history_path())
    if frame.empty:
        payload["equity_curve"] = []
        payload["drawdown_curve"] = []
        payload["daily_pnl"] = []
        return payload
    payload["equity_curve"] = [
        {"date": str(row.get("as_of_date")), "value": float(row.get("equity", 0.0) or 0.0)}
        for row in frame.tail(250).to_dict(orient="records")
    ]
    payload["drawdown_curve"] = [
        {"date": str(row.get("as_of_date")), "value": float(row.get("drawdown", 0.0) or 0.0)}
        for row in frame.tail(250).to_dict(orient="records")
    ]
    payload["daily_pnl"] = [
        {"date": str(row.get("as_of_date")), "value": float(row.get("total_pnl", 0.0) or 0.0)}
        for row in frame.tail(250).to_dict(orient="records")
    ]
    return payload


def get_trading_risk_payload() -> dict[str, Any]:
    settings = get_trading_config(refresh=True)
    latest = load_runtime_json(latest_risk_path(), default={})
    if not isinstance(latest, dict):
        latest = {}
    latest.setdefault("limits", settings.get("risk", {}))
    latest.setdefault("events", _load_risk_events()[-100:])
    return latest


def get_trading_events_payload(limit: int = 250) -> dict[str, Any]:
    return {"items": list_trading_events(limit=limit)}


def get_trading_algorithms_payload() -> dict[str, Any]:
    return {"items": sync_custom_algorithm_registry()}


def toggle_trading_algorithm_payload(
    *,
    name: str,
    version: str | None = None,
    active: bool | None = None,
    sandbox_mode: bool | None = None,
    signal_only: bool | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    items = update_algorithm_toggle(
        name=name,
        version=version,
        active=active,
        sandbox_mode=sandbox_mode,
        signal_only=signal_only,
        status=status,
    )
    return {"items": items}


def validate_trading_algorithm_payload(name: str, version: str | None = None) -> dict[str, Any]:
    registry = sync_custom_algorithm_registry()
    selected = next(
        (
            row
            for row in registry
            if row["name"] == name and (version is None or row["version"] == version)
        ),
        None,
    )
    if selected is None:
        raise ValueError(f"Unknown custom algorithm: {name}")
    algorithm = next(
        (
            item
            for item in discover_custom_algorithms()
            if item.name == selected["name"] and item.version == selected["version"]
        ),
        None,
    )
    if algorithm is None:
        raise ValueError(f"Algorithm module not available: {name}")
    settings = get_trading_config(refresh=True)
    symbols = load_trading_universe(str(settings.get("universe_id", "default") or "default"))
    sample_symbol = symbols[0] if symbols else None
    datasets, _skipped = load_trading_market_data(
        symbols=[sample_symbol] if sample_symbol else [],
        lookback_days=int(settings.get("scan", {}).get("lookback_days", 320) or 320),
        provider=str(settings.get("scan", {}).get("provider", "yfinance") or "yfinance"),
        max_workers=1,
    )
    sample_data = datasets.get(sample_symbol, pd.DataFrame())
    payload = validate_custom_algorithm(
        algorithm=algorithm,
        data=sample_data,
        symbol=sample_symbol,
    )
    new_row = dict(selected)
    new_row["validation_result"] = payload
    new_row["modified_at"] = _now_iso()
    upsert_algorithm_record(new_row)
    return payload


def get_trading_execution_mode_payload() -> dict[str, Any]:
    settings = get_trading_config(refresh=True)
    return {
        "mode": str(settings.get("execution", {}).get("mode", "paper") or "paper"),
        "live_adapter_enabled": False,
        "broker_ready": False,
        "kill_switch": False,
        "updated_at": _now_iso(),
    }


def set_trading_execution_mode_payload(mode: str) -> dict[str, Any]:
    update_trading_settings_payload({"execution": {"mode": mode}})
    return get_trading_execution_mode_payload()


def approve_trading_order_payload(order_id: str) -> dict[str, Any]:
    orders_frame = load_frame(order_history_path())
    if orders_frame.empty:
        raise ValueError("No trading orders available.")
    rows = orders_frame.to_dict(orient="records")
    target = next((row for row in rows if str(row.get("order_id", "")) == order_id), None)
    if target is None:
        raise ValueError(f"Unknown trading order: {order_id}")
    if str(target.get("status", "")).lower() != "pending":
        return target
    settings = get_trading_config(refresh=True)
    key = str(target.get("ticker", "")).upper()
    datasets, _skipped = load_trading_market_data(
        symbols=[key],
        lookback_days=int(settings.get("scan", {}).get("lookback_days", 320) or 320),
        provider=str(settings.get("scan", {}).get("provider", "yfinance") or "yfinance"),
        max_workers=1,
    )
    frame = datasets.get(key, pd.DataFrame())
    if frame.empty:
        raise ValueError("Market data unavailable for approval.")
    engine = PaperExecutionEngine(
        slippage_bps=float(settings.get("execution", {}).get("slippage_bps", 2.0) or 2.0),
        commission_bps=float(settings.get("execution", {}).get("commission_bps", 1.0) or 1.0),
        fill_policy=str(settings.get("execution", {}).get("fill_policy", "close") or "close"),
    )
    submitted = engine.submit_order(target, frame.iloc[-1].to_dict())
    updated_order = submitted["order"]
    fill = submitted.get("fill")
    rows = [updated_order if str(row.get("order_id", "")) == order_id else row for row in rows]
    save_frame(order_history_path(), pd.DataFrame(rows))
    account_state = load_account_state(
        float(settings.get("account", {}).get("initial_cash", 1_000_000.0) or 1_000_000.0)
    )
    positions = load_open_positions()
    if isinstance(fill, dict):
        append_frame(fill_history_path(), pd.DataFrame([fill]))
        account_state, positions, closed_row = apply_fill_to_portfolio(
            fill=fill,
            account_state=account_state,
            positions=positions,
            symbol_meta=load_symbol_metadata().get(key, {"symbol": key}),
        )
        if closed_row is not None:
            append_closed_position(closed_row)
        save_open_positions(
            update_positions_market_values(positions, {key: float(fill.get("price", 0.0) or 0.0)})
        )
        save_account_state(account_state)
    return updated_order


def cancel_trading_order_payload(order_id: str) -> dict[str, Any]:
    frame = load_frame(order_history_path())
    if frame.empty:
        raise ValueError("No trading orders available.")
    rows = frame.to_dict(orient="records")
    updated = None
    for row in rows:
        if str(row.get("order_id", "")) == order_id:
            row["status"] = "cancelled"
            row["updated_at"] = _now_iso()
            updated = row
    if updated is None:
        raise ValueError(f"Unknown trading order: {order_id}")
    save_frame(order_history_path(), pd.DataFrame(rows))
    return updated


def close_trading_position_payload(ticker: str) -> dict[str, Any]:
    key = str(ticker or "").strip().upper()
    settings = get_trading_config(refresh=True)
    positions = load_open_positions()
    existing = next((row for row in positions if str(row.get("ticker", "")).upper() == key), None)
    if existing is None:
        raise ValueError(f"No open position for {key}.")
    signal = {
        "ticker": key,
        "signal_type": "exit",
        "signal": "exit",
        "side": "sell",
        "strength": 1.0,
        "confidence": 1.0,
        "strategy_name": str(existing.get("strategy", "manual_exit")),
        "algorithm_version": "manual",
        "reason": "Manual force close",
    }
    order = build_order_intent(
        signal=signal,
        settings=settings,
        account_state=load_account_state(
            float(settings.get("account", {}).get("initial_cash", 1_000_000.0) or 1_000_000.0)
        ),
        existing_position=existing,
        price=float(existing.get("current_price", existing.get("entry_price", 0.0)) or 0.0),
    )
    if order is None:
        raise ValueError(f"Failed to build close order for {key}.")
    append_frame(order_history_path(), pd.DataFrame([order]))
    return approve_trading_order_payload(str(order["order_id"]))
