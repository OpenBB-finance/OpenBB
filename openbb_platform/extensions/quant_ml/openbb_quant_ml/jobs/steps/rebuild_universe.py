"""Step: rebuild universe with filters."""

from __future__ import annotations

from typing import Any

from openbb_quant_ml.service.universe_builder import build_universe


def run(config: dict[str, Any]) -> dict[str, Any]:
    payload = build_universe(universe_id=config.get("universe_id"))
    return {
        "status": "ok",
        "universe_id": payload.get("universe_id"),
        "train_size": len(payload.get("train_universe", [])),
        "trade_size": len(payload.get("trade_universe", [])),
    }
