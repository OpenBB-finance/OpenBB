"""Trading universe service wrappers."""

from __future__ import annotations

from typing import Any

from openbb_quant_ml.service.universe import (
    get_default_symbols,
    get_symbol_metadata_map,
    get_symbols_for_universe,
)


def load_trading_universe(universe_id: str | None) -> list[str]:
    """Return the resolved trading universe."""
    symbols = get_symbols_for_universe(universe_id)
    return symbols or get_default_symbols()


def load_symbol_metadata() -> dict[str, dict[str, Any]]:
    """Return metadata map for the current universe set."""
    return get_symbol_metadata_map()
