"""Step: selective backfill placeholder."""

from __future__ import annotations

from typing import Any

from openbb_quant_ml.jobs.steps.update_market_data import run as run_market_update


def run(config: dict[str, Any]) -> dict[str, Any]:
    return run_market_update(config)
