"""Paper execution and risk-control services for Quant ML."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4
from typing import Any

import numpy as np
import pandas as pd

from openbb_quant_ml.models import (
    ExecutionFillsResponse,
    ExecutionOrderItem,
    ExecutionOrderPreviewRequest,
    ExecutionOrdersResponse,
    ExecutionPnlResponse,
    ExecutionPositionsResponse,
    ExecutionPreviewResponse,
    ExecutionSubmitResponse,
    ModelName,
    RiskLimitsResponse,
    RiskPretradeRequest,
    RiskPretradeResponse,
    RiskViolationItem,
    RiskEventsResponse,
)
from openbb_quant_ml.service.pipeline import get_portfolio_current
from openbb_quant_ml.service.storage import get_run_dir, load_json, save_json

DEFAULT_MODEL: ModelName = "lgbm_ranker"
SUPPORTED_MODELS: tuple[ModelName, ...] = ("xgb_lstm", "lgbm_ranker")
DEFAULT_NAV = 1_000_000.0
DEFAULT_SLIPPAGE_BPS = 2.0
DEFAULT_RISK_LIMITS: dict[str, float] = {
    # Keep a pragmatic default that permits diversified long-only allocations,
    # while still blocking highly concentrated books.
    "max_weight": 0.60,
    "gross_exposure": 1.4,
    "net_exposure_abs": 1.0,
    "sector_concentration": 0.60,
    "turnover": 1.0,
}


def _normalize_model_name(model_name: str | None) -> ModelName:
    if model_name in SUPPORTED_MODELS:
        return model_name
    return DEFAULT_MODEL


def _run_exists(run_id: str) -> bool:
    return get_run_dir(run_id).exists()


def _execution_state_path(run_dir: Path, model_name: ModelName) -> Path:
    return run_dir / f"execution_{model_name}.json"


def _fills_path(run_dir: Path, model_name: ModelName) -> Path:
    return run_dir / f"fills_{model_name}.parquet"


def _positions_path(run_dir: Path, model_name: ModelName) -> Path:
    return run_dir / f"positions_{model_name}.json"


def _risk_events_path(run_dir: Path, model_name: ModelName) -> Path:
    return run_dir / f"risk_events_{model_name}.json"


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _default_execution_state(nav: float = DEFAULT_NAV) -> dict[str, Any]:
    return {
        "initial_nav": float(nav),
        "nav": float(nav),
        "cash": float(nav),
        "realized_pnl": 0.0,
        "orders": [],
        "kill_switch": False,
        "updated_at": _utc_now_iso(),
    }


def _load_execution_state(run_dir: Path, model_name: ModelName, nav: float | None = None) -> dict[str, Any]:
    default_nav = float(nav) if nav is not None else DEFAULT_NAV
    payload = load_json(_execution_state_path(run_dir, model_name), default={})
    if not isinstance(payload, dict) or not payload:
        return _default_execution_state(default_nav)
    payload.setdefault("initial_nav", default_nav)
    payload.setdefault("nav", payload.get("initial_nav", default_nav))
    payload.setdefault("cash", payload.get("nav", default_nav))
    payload.setdefault("realized_pnl", 0.0)
    payload.setdefault("orders", [])
    payload.setdefault("kill_switch", False)
    payload.setdefault("updated_at", _utc_now_iso())
    return payload


def _load_positions(run_dir: Path, model_name: ModelName) -> dict[str, dict[str, float]]:
    payload = load_json(_positions_path(run_dir, model_name), default={})
    if not isinstance(payload, dict):
        return {}
    out: dict[str, dict[str, float]] = {}
    for symbol, row in payload.items():
        if not isinstance(row, dict):
            continue
        out[str(symbol)] = {
            "quantity": float(row.get("quantity", 0.0)),
            "avg_cost": float(row.get("avg_cost", 0.0)),
        }
    return out


def _save_positions(run_dir: Path, model_name: ModelName, positions: dict[str, dict[str, float]]) -> None:
    clean = {
        symbol: {
            "quantity": float(row.get("quantity", 0.0)),
            "avg_cost": float(row.get("avg_cost", 0.0)),
        }
        for symbol, row in positions.items()
        if abs(float(row.get("quantity", 0.0))) > 1e-12
    }
    save_json(_positions_path(run_dir, model_name), clean)


def _save_execution_state(run_dir: Path, model_name: ModelName, state: dict[str, Any]) -> None:
    state["updated_at"] = _utc_now_iso()
    save_json(_execution_state_path(run_dir, model_name), state)


def _load_price_panel(run_dir: Path, field: str = "close") -> pd.DataFrame:
    market_path = run_dir / "market_data.parquet"
    if not market_path.exists():
        return pd.DataFrame()
    market = pd.read_parquet(market_path)
    if market.empty:
        return pd.DataFrame()
    if field not in market.columns:
        if field == "open" and "close" in market.columns:
            field = "close"
        else:
            return pd.DataFrame()
    return (
        market.assign(date=pd.to_datetime(market["date"]).dt.tz_localize(None))
        .pivot(index="date", columns="symbol", values=field)
        .sort_index()
    )


def _execution_price_field(run_dir: Path, model_name: ModelName) -> str:
    payload = load_json(run_dir / f"backtest_{model_name}.json", default={})
    if not payload:
        payload = load_json(run_dir / "backtest.json", default={})
    entry_price = str(payload.get("entry_price", "close"))
    return "open" if entry_price == "next_open" else "close"


def _latest_prices(
    run_dir: Path,
    as_of_date: str | None = None,
    price_field: str = "close",
) -> tuple[str | None, dict[str, float]]:
    panel = _load_price_panel(run_dir, field=price_field)
    if panel.empty:
        return None, {}
    if as_of_date:
        target = pd.Timestamp(as_of_date)
        series = panel.loc[panel.index <= target].tail(1)
        if series.empty:
            series = panel.tail(1)
    else:
        series = panel.tail(1)
    if series.empty:
        return None, {}
    date_iso = pd.Timestamp(series.index[-1]).date().isoformat()
    row = series.iloc[-1].dropna()
    prices = {str(sym): float(px) for sym, px in row.items() if float(px) > 0}
    return date_iso, prices


def _append_fills(run_dir: Path, model_name: ModelName, fills: list[dict[str, Any]]) -> None:
    if not fills:
        return
    path = _fills_path(run_dir, model_name)
    incoming = pd.DataFrame(fills)
    if path.exists():
        existing = pd.read_parquet(path)
        incoming = pd.concat([existing, incoming], ignore_index=True)
    incoming.to_parquet(path, index=False)


def _append_risk_events(run_dir: Path, model_name: ModelName, events: list[dict[str, Any]]) -> None:
    if not events:
        return
    path = _risk_events_path(run_dir, model_name)
    payload = load_json(path, default={"events": []})
    rows = payload.get("events", []) if isinstance(payload, dict) else []
    if not isinstance(rows, list):
        rows = []
    rows.extend(events)
    payload = {"events": rows[-2000:]}
    save_json(path, payload)


def _portfolio_snapshot(run_id: str, model_name: ModelName) -> tuple[str | None, dict[str, float], dict[str, float]]:
    portfolio = get_portfolio_current(run_id=run_id, model_name=model_name)
    target_weights = {item.symbol: float(item.weight) for item in portfolio.symbol_weights}
    category_weights = {item.category: float(item.weight) for item in portfolio.asset_class_weights}
    return portfolio.as_of_date, target_weights, category_weights


def _calc_weights_from_positions(
    positions: dict[str, dict[str, float]],
    prices: dict[str, float],
    nav: float,
) -> dict[str, float]:
    if nav <= 0:
        return {}
    out: dict[str, float] = {}
    for symbol, row in positions.items():
        px = prices.get(symbol)
        if px is None or px <= 0:
            continue
        value = float(row.get("quantity", 0.0)) * px
        out[symbol] = value / nav
    return out


def _preview_orders(
    run_id: str,
    model_name: ModelName,
    slippage_bps: float,
    cost_bps: float | None,
    nav: float | None,
) -> tuple[ExecutionPreviewResponse, dict[str, Any]]:
    if not _run_exists(run_id):
        return (
            ExecutionPreviewResponse(
                run_id=run_id,
                model_name=model_name,
                status="not_found",
                message="Run not found",
            ),
            {},
        )

    run_dir = get_run_dir(run_id)
    as_of_date, target_weights, category_weights = _portfolio_snapshot(run_id, model_name)
    if not target_weights:
        return (
            ExecutionPreviewResponse(
                run_id=run_id,
                model_name=model_name,
                status="insufficient_data",
                message="Run backtest first",
            ),
            {},
        )

    state = _load_execution_state(run_dir, model_name, nav=nav)
    nav_value = float(nav) if nav is not None else float(state.get("nav", state.get("initial_nav", DEFAULT_NAV)))
    if nav_value <= 0:
        nav_value = float(state.get("initial_nav", DEFAULT_NAV))

    current_positions = _load_positions(run_dir, model_name)
    entry_field = _execution_price_field(run_dir, model_name)
    latest_market_date, prices = _latest_prices(run_dir, as_of_date, price_field=entry_field)
    if not prices:
        return (
            ExecutionPreviewResponse(
                run_id=run_id,
                model_name=model_name,
                status="insufficient_data",
                message="Market prices are unavailable",
            ),
            {},
        )

    current_weights = _calc_weights_from_positions(current_positions, prices, nav_value)
    symbols = sorted(set(target_weights).union(set(current_weights)))
    orders: list[ExecutionOrderItem] = []
    turnover_notional = 0.0

    for symbol in symbols:
        px = prices.get(symbol)
        if px is None or px <= 0:
            continue
        target_w = float(target_weights.get(symbol, 0.0))
        current_w = float(current_weights.get(symbol, 0.0))
        diff_value = (target_w - current_w) * nav_value
        qty = diff_value / px
        if abs(qty) < 1e-8:
            continue
        side = "buy" if qty > 0 else "sell"
        est_notional = abs(qty * px)
        turnover_notional += est_notional
        orders.append(
            ExecutionOrderItem(
                order_id=f"ord-{uuid4().hex[:10]}",
                symbol=symbol,
                side=side,
                quantity=float(qty),
                current_weight=current_w,
                target_weight=target_w,
                est_price=float(px),
                est_notional=float(est_notional),
                status="preview",
            )
        )

    preview = ExecutionPreviewResponse(
        run_id=run_id,
        model_name=model_name,
        status="ok",
        as_of_date=latest_market_date,
        nav=nav_value,
        orders=orders,
        estimated_turnover=float(turnover_notional / max(nav_value, 1e-12)),
        message=None if orders else "No rebalance orders required.",
    )

    context = {
        "run_dir": run_dir,
        "state": state,
        "positions": current_positions,
        "prices": prices,
        "price_field": entry_field,
        "cost_bps": float(cost_bps) if cost_bps is not None else float(state.get("cost_bps", 10.0)),
        "slippage_bps": float(slippage_bps),
        "target_category_weights": category_weights,
    }
    return preview, context


def _risk_violations_from_preview(
    preview: ExecutionPreviewResponse,
    category_weights: dict[str, float],
    limits: dict[str, float],
    turnover_limit: float | None = None,
) -> list[RiskViolationItem]:
    violations: list[RiskViolationItem] = []
    if preview.status != "ok":
        return violations

    max_weight = 0.0
    gross_exposure = 0.0
    net_exposure = 0.0
    for order in preview.orders:
        max_weight = max(max_weight, abs(float(order.target_weight)))
        gross_exposure += abs(float(order.target_weight))
        net_exposure += float(order.target_weight)

    max_weight_limit = float(limits.get("max_weight", DEFAULT_RISK_LIMITS["max_weight"]))
    if max_weight > max_weight_limit + 1e-12:
        violations.append(
            RiskViolationItem(
                rule_id="max_weight",
                severity="critical",
                value=max_weight,
                limit=max_weight_limit,
                message="Maximum position weight exceeded.",
            )
        )

    gross_limit = float(limits.get("gross_exposure", DEFAULT_RISK_LIMITS["gross_exposure"]))
    if gross_exposure > gross_limit + 1e-12:
        violations.append(
            RiskViolationItem(
                rule_id="gross_exposure",
                severity="critical",
                value=gross_exposure,
                limit=gross_limit,
                message="Gross exposure limit exceeded.",
            )
        )

    net_limit = float(limits.get("net_exposure_abs", DEFAULT_RISK_LIMITS["net_exposure_abs"]))
    if abs(net_exposure) > net_limit + 1e-12:
        violations.append(
            RiskViolationItem(
                rule_id="net_exposure",
                severity="warning",
                value=abs(net_exposure),
                limit=net_limit,
                message="Net exposure absolute limit exceeded.",
            )
        )

    sector_concentration = max(category_weights.values()) if category_weights else 0.0
    sector_limit = float(limits.get("sector_concentration", DEFAULT_RISK_LIMITS["sector_concentration"]))
    if sector_concentration > sector_limit + 1e-12:
        violations.append(
            RiskViolationItem(
                rule_id="sector_concentration",
                severity="warning",
                value=float(sector_concentration),
                limit=sector_limit,
                message="Sector concentration limit exceeded.",
            )
        )

    turnover = float(preview.estimated_turnover)
    turnover_limit_value = float(turnover_limit) if turnover_limit is not None else float(
        limits.get("turnover", DEFAULT_RISK_LIMITS["turnover"])
    )
    if turnover > turnover_limit_value + 1e-12:
        violations.append(
            RiskViolationItem(
                rule_id="turnover",
                severity="warning",
                value=turnover,
                limit=turnover_limit_value,
                message="Turnover limit exceeded.",
            )
        )

    return violations


def _risk_limits(run_dir: Path, model_name: ModelName) -> dict[str, float]:
    state = _load_execution_state(run_dir, model_name)
    limits = state.get("risk_limits")
    if isinstance(limits, dict) and limits:
        out: dict[str, float] = {}
        for key, value in limits.items():
            try:
                out[str(key)] = float(value)
            except (TypeError, ValueError):
                continue
        if out:
            return out
    return DEFAULT_RISK_LIMITS.copy()


def preview_execution_orders(request: ExecutionOrderPreviewRequest) -> ExecutionPreviewResponse:
    """Preview paper execution orders from latest target portfolio."""
    model_name = _normalize_model_name(request.model_name)
    preview, _ = _preview_orders(
        run_id=request.run_id,
        model_name=model_name,
        slippage_bps=request.slippage_bps,
        cost_bps=request.cost_bps,
        nav=request.nav,
    )
    return preview


def submit_execution_orders(request: ExecutionOrderPreviewRequest) -> ExecutionSubmitResponse:
    """Submit paper execution orders and mark immediate fills."""
    model_name = _normalize_model_name(request.model_name)
    preview, context = _preview_orders(
        run_id=request.run_id,
        model_name=model_name,
        slippage_bps=request.slippage_bps,
        cost_bps=request.cost_bps,
        nav=request.nav,
    )
    if preview.status != "ok":
        return ExecutionSubmitResponse(
            run_id=request.run_id,
            model_name=model_name,
            status=preview.status,
            message=preview.message,
            orders=[],
            kill_switch=False,
        )

    run_dir: Path = context["run_dir"]
    state: dict[str, Any] = context["state"]
    positions: dict[str, dict[str, float]] = context["positions"]
    prices: dict[str, float] = context["prices"]
    cost_bps = float(context["cost_bps"])
    slippage_bps = float(context["slippage_bps"])
    target_category_weights: dict[str, float] = context["target_category_weights"]

    limits = _risk_limits(run_dir, model_name)
    violations = _risk_violations_from_preview(preview, target_category_weights, limits)
    critical = [item for item in violations if item.severity == "critical"]
    if critical or bool(state.get("kill_switch", False)):
        state["kill_switch"] = True
        _save_execution_state(run_dir, model_name, state)
        events = [
            {
                "triggered_at": _utc_now_iso(),
                "rule_id": item.rule_id,
                "severity": item.severity,
                "message": item.message,
                "value": float(item.value),
                "limit": float(item.limit),
            }
            for item in violations
        ]
        _append_risk_events(run_dir, model_name, events)
        return ExecutionSubmitResponse(
            run_id=request.run_id,
            model_name=model_name,
            status="insufficient_data",
            message="Kill switch active. Orders are blocked by risk limits.",
            orders=[],
            kill_switch=True,
        )

    cash = float(state.get("cash", preview.nav))
    realized = float(state.get("realized_pnl", 0.0))
    fills: list[dict[str, Any]] = []
    submitted_orders: list[ExecutionOrderItem] = []

    for order in preview.orders:
        symbol = str(order.symbol)
        px = float(prices.get(symbol, order.est_price))
        if px <= 0:
            continue
        qty = float(order.quantity)
        slip = slippage_bps / 10000.0
        fill_price = px * (1.0 + slip if qty > 0 else 1.0 - slip)
        notional = qty * fill_price
        fee = abs(notional) * (cost_bps / 10000.0)

        prev = positions.get(symbol, {"quantity": 0.0, "avg_cost": 0.0})
        prev_qty = float(prev.get("quantity", 0.0))
        prev_avg = float(prev.get("avg_cost", 0.0))
        new_qty = prev_qty + qty

        if prev_qty != 0.0 and np.sign(prev_qty) != np.sign(qty):
            closing_qty = min(abs(prev_qty), abs(qty))
            if prev_qty > 0:
                realized += closing_qty * (fill_price - prev_avg)
            else:
                realized += closing_qty * (prev_avg - fill_price)

        if abs(new_qty) < 1e-12:
            new_avg = 0.0
            new_qty = 0.0
        elif prev_qty == 0.0 or np.sign(prev_qty) == np.sign(qty):
            new_avg = (prev_qty * prev_avg + qty * fill_price) / (new_qty + 1e-12)
        elif np.sign(prev_qty) == np.sign(new_qty):
            new_avg = prev_avg
        else:
            new_avg = fill_price

        positions[symbol] = {"quantity": float(new_qty), "avg_cost": float(new_avg)}
        cash -= notional + fee

        submitted = order.model_copy(update={"status": "filled", "est_price": float(fill_price)})
        submitted_orders.append(submitted)
        fills.append(
            {
                "filled_at": _utc_now_iso(),
                "order_id": submitted.order_id,
                "symbol": symbol,
                "side": submitted.side,
                "quantity": float(qty),
                "fill_price": float(fill_price),
                "notional": float(abs(notional)),
                "fee": float(fee),
            }
        )

    _save_positions(run_dir, model_name, positions)
    _append_fills(run_dir, model_name, fills)

    latest_date, latest_prices = _latest_prices(run_dir)
    if not latest_prices:
        latest_prices = prices
    market_value = 0.0
    for symbol, row in positions.items():
        qty = float(row.get("quantity", 0.0))
        px = float(latest_prices.get(symbol, 0.0))
        market_value += qty * px
    nav_after = float(cash + market_value)

    state["cash"] = float(cash)
    state["nav"] = nav_after
    state["realized_pnl"] = float(realized)
    state["orders"] = [item.model_dump(mode="json") for item in submitted_orders]
    state["cost_bps"] = float(cost_bps)
    state["slippage_bps"] = float(slippage_bps)
    _save_execution_state(run_dir, model_name, state)

    return ExecutionSubmitResponse(
        run_id=request.run_id,
        model_name=model_name,
        status="ok",
        submitted_at=_utc_now_iso(),
        orders=submitted_orders,
        fills_count=len(fills),
        cash_after=float(cash),
        nav_after=nav_after,
        kill_switch=bool(state.get("kill_switch", False)),
        message=None if fills else "No fills were generated.",
    )


def get_execution_orders_current(run_id: str, model_name: str | None = None) -> ExecutionOrdersResponse:
    """Return latest order snapshot for paper execution."""
    normalized_model = _normalize_model_name(model_name)
    if not _run_exists(run_id):
        return ExecutionOrdersResponse(run_id=run_id, model_name=normalized_model, status="not_found", message="Run not found")
    run_dir = get_run_dir(run_id)
    state = _load_execution_state(run_dir, normalized_model)
    orders = [ExecutionOrderItem(**row) for row in state.get("orders", []) if isinstance(row, dict)]
    return ExecutionOrdersResponse(
        run_id=run_id,
        model_name=normalized_model,
        status="ok",
        orders=orders,
    )


def get_execution_fills_history(run_id: str, model_name: str | None = None, limit: int = 200) -> ExecutionFillsResponse:
    """Return paper execution fills history."""
    normalized_model = _normalize_model_name(model_name)
    if not _run_exists(run_id):
        return ExecutionFillsResponse(run_id=run_id, model_name=normalized_model, status="not_found", message="Run not found")
    run_dir = get_run_dir(run_id)
    path = _fills_path(run_dir, normalized_model)
    if not path.exists():
        return ExecutionFillsResponse(
            run_id=run_id,
            model_name=normalized_model,
            status="insufficient_data",
            message="No fills history",
            fills=[],
        )
    frame = pd.read_parquet(path)
    if frame.empty:
        return ExecutionFillsResponse(
            run_id=run_id,
            model_name=normalized_model,
            status="insufficient_data",
            message="No fills history",
            fills=[],
        )
    rows = frame.tail(max(int(limit), 1)).to_dict(orient="records")
    return ExecutionFillsResponse(run_id=run_id, model_name=normalized_model, status="ok", fills=rows)


def get_execution_positions_current(run_id: str, model_name: str | None = None) -> ExecutionPositionsResponse:
    """Return current paper execution positions and exposures."""
    normalized_model = _normalize_model_name(model_name)
    if not _run_exists(run_id):
        return ExecutionPositionsResponse(run_id=run_id, model_name=normalized_model, status="not_found", message="Run not found")

    run_dir = get_run_dir(run_id)
    state = _load_execution_state(run_dir, normalized_model)
    positions = _load_positions(run_dir, normalized_model)
    as_of_date, prices = _latest_prices(run_dir)
    nav = float(state.get("nav", state.get("initial_nav", DEFAULT_NAV)))
    cash = float(state.get("cash", nav))

    rows: list[dict[str, float | str]] = []
    gross = 0.0
    net = 0.0
    for symbol, row in positions.items():
        qty = float(row.get("quantity", 0.0))
        if abs(qty) < 1e-12:
            continue
        px = float(prices.get(symbol, 0.0))
        avg_cost = float(row.get("avg_cost", 0.0))
        market_value = qty * px
        gross += abs(market_value)
        net += market_value
        unrealized = qty * (px - avg_cost)
        rows.append(
            {
                "symbol": symbol,
                "quantity": qty,
                "avg_cost": avg_cost,
                "market_price": px,
                "market_value": market_value,
                "weight": market_value / (nav + 1e-12),
                "unrealized_pnl": unrealized,
            }
        )

    rows.sort(key=lambda item: abs(float(item.get("market_value", 0.0))), reverse=True)
    gross_exp = gross / (nav + 1e-12)
    net_exp = net / (nav + 1e-12)
    return ExecutionPositionsResponse(
        run_id=run_id,
        model_name=normalized_model,
        status="ok",
        as_of_date=as_of_date,
        positions=rows,
        cash=cash,
        gross_exposure=float(gross_exp),
        net_exposure=float(net_exp),
    )


def get_execution_pnl(run_id: str, model_name: str | None = None) -> ExecutionPnlResponse:
    """Return paper execution realized/unrealized PnL."""
    normalized_model = _normalize_model_name(model_name)
    if not _run_exists(run_id):
        return ExecutionPnlResponse(run_id=run_id, model_name=normalized_model, status="not_found", message="Run not found")

    run_dir = get_run_dir(run_id)
    state = _load_execution_state(run_dir, normalized_model)
    positions_payload = get_execution_positions_current(run_id=run_id, model_name=normalized_model)
    if positions_payload.status == "not_found":
        return ExecutionPnlResponse(run_id=run_id, model_name=normalized_model, status="not_found", message="Run not found")

    realized = float(state.get("realized_pnl", 0.0))
    unrealized = float(sum(float(row.get("unrealized_pnl", 0.0)) for row in positions_payload.positions))
    total = realized + unrealized
    initial_nav = float(state.get("initial_nav", DEFAULT_NAV))

    return ExecutionPnlResponse(
        run_id=run_id,
        model_name=normalized_model,
        status="ok",
        as_of_date=positions_payload.as_of_date,
        realized_pnl=realized,
        unrealized_pnl=unrealized,
        total_pnl=total,
        return_pct=float(total / (initial_nav + 1e-12)),
    )


def get_risk_limits(run_id: str, model_name: str | None = None) -> RiskLimitsResponse:
    """Return current risk limits and kill-switch status."""
    normalized_model = _normalize_model_name(model_name)
    if not _run_exists(run_id):
        return RiskLimitsResponse(run_id=run_id, model_name=normalized_model, status="not_found", limits={})
    run_dir = get_run_dir(run_id)
    limits = _risk_limits(run_dir, normalized_model)
    state = _load_execution_state(run_dir, normalized_model)
    return RiskLimitsResponse(
        run_id=run_id,
        model_name=normalized_model,
        status="ok",
        limits=limits,
        kill_switch=bool(state.get("kill_switch", False)),
    )


def risk_check_pretrade(request: RiskPretradeRequest) -> RiskPretradeResponse:
    """Run pre-trade risk checks against latest target orders."""
    normalized_model = _normalize_model_name(request.model_name)
    if not _run_exists(request.run_id):
        return RiskPretradeResponse(
            run_id=request.run_id,
            model_name=normalized_model,
            status="not_found",
            passed=False,
            violations=[],
        )

    run_dir = get_run_dir(request.run_id)
    preview, context = _preview_orders(
        run_id=request.run_id,
        model_name=normalized_model,
        slippage_bps=DEFAULT_SLIPPAGE_BPS,
        cost_bps=None,
        nav=None,
    )
    if preview.status != "ok":
        return RiskPretradeResponse(
            run_id=request.run_id,
            model_name=normalized_model,
            status=preview.status,
            passed=False,
            violations=[],
        )

    limits = _risk_limits(run_dir, normalized_model)
    category_weights = context.get("target_category_weights", {})
    violations = _risk_violations_from_preview(
        preview,
        category_weights,
        limits,
        turnover_limit=request.turnover_limit,
    )

    kill_switch = any(item.severity == "critical" for item in violations)
    if kill_switch:
        state = _load_execution_state(run_dir, normalized_model)
        state["kill_switch"] = True
        _save_execution_state(run_dir, normalized_model, state)

    events = [
        {
            "triggered_at": _utc_now_iso(),
            "rule_id": item.rule_id,
            "severity": item.severity,
            "message": item.message,
            "value": float(item.value),
            "limit": float(item.limit),
        }
        for item in violations
    ]
    _append_risk_events(run_dir, normalized_model, events)

    return RiskPretradeResponse(
        run_id=request.run_id,
        model_name=normalized_model,
        status="ok",
        passed=len(violations) == 0,
        kill_switch=kill_switch,
        violations=violations,
    )


def get_risk_events(run_id: str, model_name: str | None = None, limit: int = 200) -> RiskEventsResponse:
    """Return risk events history."""
    normalized_model = _normalize_model_name(model_name)
    if not _run_exists(run_id):
        return RiskEventsResponse(run_id=run_id, model_name=normalized_model, status="not_found", message="Run not found")
    run_dir = get_run_dir(run_id)
    payload = load_json(_risk_events_path(run_dir, normalized_model), default={"events": []})
    rows = payload.get("events", []) if isinstance(payload, dict) else []
    if not isinstance(rows, list):
        rows = []
    return RiskEventsResponse(
        run_id=run_id,
        model_name=normalized_model,
        status="ok",
        events=[row for row in rows[-max(int(limit), 1) :] if isinstance(row, dict)],
    )
