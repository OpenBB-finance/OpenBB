"""Shared TMX options-chain loader and cache for the options views."""

from __future__ import annotations

from typing import Any

LOADED_SYMBOLS: dict[str, Any] = {}


async def load_symbol(symbol: str, update: bool = False) -> Any:
    """Return the cached ``TmxOptionsChainsData`` for a symbol, loading it once.

    Parameters
    ----------
    symbol : str
        The underlying symbol.
    update : bool
        When True, bypass the cache and refetch.

    Returns
    -------
    Any
        The parsed ``TmxOptionsChainsData`` object.

    Raises
    ------
    OpenBBError
        If the symbol has no options chain published by TMX.
    """
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.errors import EmptyDataError

    symbol = symbol.upper()

    if symbol in LOADED_SYMBOLS and not update:
        return LOADED_SYMBOLS[symbol]

    from openbb_tmx.models.options_chains import TmxOptionsChainsFetcher

    try:
        data = await TmxOptionsChainsFetcher.fetch_data({"symbol": symbol}, {})
    except (OpenBBError, EmptyDataError) as exc:
        raise OpenBBError(f"No options available for {symbol}.") from exc

    results = data.result if hasattr(data, "result") else data

    if results is None or not getattr(results, "expirations", None):
        raise OpenBBError(f"No options available for {symbol}.")

    LOADED_SYMBOLS[symbol] = results

    return results


def get_expirations(symbol: str) -> list[dict]:
    """Return the cached expiration choices for a symbol's dropdown.

    Parameters
    ----------
    symbol : str
        The underlying symbol.

    Returns
    -------
    list[dict]
        ``[{label, value}]`` expiration choices, empty when not yet loaded.
    """
    results = LOADED_SYMBOLS.get(symbol.upper())

    if results is None:
        return []

    return [{"label": str(e), "value": str(e)} for e in results.expirations]


def get_strikes(symbol: str) -> list[dict]:
    """Return the cached strike choices for a symbol's dropdown.

    Parameters
    ----------
    symbol : str
        The underlying symbol.

    Returns
    -------
    list[dict]
        ``[{label, value}]`` strike choices, empty when not yet loaded.
    """
    results = LOADED_SYMBOLS.get(symbol.upper())

    if results is None:
        return []

    underlying = results.underlying_price[0] if results.underlying_price else None
    choices: list[dict] = [{"label": "Nearest OTM", "value": None}]

    for strike in results.strikes:
        extra = (
            {"rightOfDescription": f"Underlying: ${underlying}"} if underlying else {}
        )
        choices.append(
            {
                "label": f"${str(strike).replace('.0', '')}",
                "value": strike,
                "extraInfo": extra,
            }
        )

    return choices
