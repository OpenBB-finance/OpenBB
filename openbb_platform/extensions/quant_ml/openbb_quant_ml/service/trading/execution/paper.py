"""Paper execution engine for the trading runtime."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from openbb_quant_ml.service.trading.execution.base import ExecutionEngine


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


class PaperExecutionEngine(ExecutionEngine):
    """Basic paper execution engine with slippage and fees."""

    def __init__(self, *, slippage_bps: float, commission_bps: float, fill_policy: str) -> None:
        self.slippage_bps = float(slippage_bps)
        self.commission_bps = float(commission_bps)
        self.fill_policy = str(fill_policy or "close")

    def submit_order(self, order: dict[str, Any], latest_bar: dict[str, Any]) -> dict[str, Any]:
        price_field = "open" if self.fill_policy == "next_open" else "close"
        reference_price = float(latest_bar.get(price_field, latest_bar.get("close", 0.0)) or 0.0)
        if reference_price <= 0.0:
            return {
                "order": {**order, "status": "rejected", "updated_at": _now_iso()},
                "fill": None,
                "error": "invalid_fill_price",
            }
        side = str(order.get("side", "buy")).lower()
        slip_multiplier = 1.0 + (self.slippage_bps / 10_000.0 if side == "buy" else -(self.slippage_bps / 10_000.0))
        fill_price = reference_price * slip_multiplier
        quantity = float(order.get("quantity", 0.0) or 0.0)
        notional = abs(quantity * fill_price)
        fee = notional * (self.commission_bps / 10_000.0)
        filled = {
            "fill_id": f"fill-{str(order.get('order_id', 'unknown'))}",
            "order_id": order.get("order_id"),
            "ticker": order.get("ticker"),
            "strategy_name": order.get("strategy_name"),
            "side": side,
            "quantity": quantity,
            "price": fill_price,
            "notional": notional,
            "fee": fee,
            "slippage_bps": self.slippage_bps,
            "filled_at": _now_iso(),
            "metadata": {"fill_policy": self.fill_policy},
        }
        updated = {
            **order,
            "status": "filled",
            "filled_price": fill_price,
            "updated_at": _now_iso(),
        }
        return {"order": updated, "fill": filled, "error": None}

    def cancel_order(self, order: dict[str, Any]) -> dict[str, Any]:
        return {**order, "status": "cancelled", "updated_at": _now_iso()}

    def get_order_status(self, order: dict[str, Any]) -> dict[str, Any]:
        return dict(order)

    def get_positions(self) -> list[dict[str, Any]]:
        return []

    def get_account_state(self) -> dict[str, Any]:
        return {}
