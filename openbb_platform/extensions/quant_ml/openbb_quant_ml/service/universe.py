"""Universe config helpers."""

from __future__ import annotations

from typing import Any

import yaml

from openbb_quant_ml.service.constants import UNIVERSE_CONFIG_PATH


def load_universe_config() -> dict[str, Any]:
    """Load universe configuration YAML."""
    with UNIVERSE_CONFIG_PATH.open(encoding="utf-8") as file:
        payload = yaml.safe_load(file) or {}
    payload.setdefault("version", "v1")
    payload.setdefault("assets", [])
    return payload


def get_default_symbols() -> list[str]:
    """Return default universe symbols."""
    payload = load_universe_config()
    assets = payload.get("assets", [])
    return [asset["symbol"] for asset in assets if asset.get("symbol")]
