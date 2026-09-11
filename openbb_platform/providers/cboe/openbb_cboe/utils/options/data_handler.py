"""Shared Cboe options-chain loader and cache for the options views."""

from __future__ import annotations

from typing import Any

LOADED_SYMBOLS: dict[str, Any] = {}


def chain_expirations(data: Any) -> list[str]:
    """Return the expirations that still have contracts in the chain.

    ``OptionsChainsData.expirations`` lists every expiration in the payload,
    including ones whose contracts ``dataframe`` has already dropped for having
    expired. Driving a picker or a chart off that offers dates which resolve to
    no rows at all - a chain fetched the morning after an expiration would lead
    with a date whose quotes come back empty.

    Parameters
    ----------
    data : Any
        The parsed ``CboeOptionsChainsData``.

    Returns
    -------
    list[str]
        Sorted expirations that have rows, falling back to the model's own list
        if the frame cannot be built.
    """
    try:
        frame = data.dataframe
    except Exception:  # noqa: BLE001
        return list(data.expirations)

    if "expiration" not in frame.columns:
        return list(data.expirations)

    return sorted({str(value) for value in frame["expiration"]})


async def load_symbol(symbol: str, update: bool = False) -> Any:
    """Return the cached ``CboeOptionsChainsData`` for a symbol, loading it once.

    Parameters
    ----------
    symbol : str
        The underlying ticker symbol.
    update : bool
        When True, bypass the cache and refetch.

    Returns
    -------
    Any
        The parsed ``CboeOptionsChainsData`` object.

    Raises
    ------
    OpenBBError
        If the symbol has no options chain published by Cboe.
    """
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.errors import EmptyDataError

    symbol = symbol.upper()

    if symbol in LOADED_SYMBOLS and not update:
        return LOADED_SYMBOLS[symbol]

    from openbb_cboe.models.options_chains import CboeOptionsChainsFetcher

    try:
        data = await CboeOptionsChainsFetcher.fetch_data({"symbol": symbol}, {})
    except (OpenBBError, EmptyDataError) as exc:
        raise OpenBBError(f"No options available for {symbol}.") from exc

    results = data.result if hasattr(data, "result") else data

    if results is None or not getattr(results, "expirations", None):
        raise OpenBBError(f"No options available for {symbol}.")

    LOADED_SYMBOLS[symbol] = results

    return results


def _implied_forward(records: list[dict]) -> tuple[float, float]:
    """Return the forward price and discount factor a chain implies.

    Parameters
    ----------
    records : list[dict]
        The published contracts of one expiration.

    Returns
    -------
    tuple[float, float]
        The forward price and discount factor, ``(0.0, 1.0)`` when too few
        strikes carry both a call and a put.
    """
    paired: dict = {}

    for record in records:
        theoretical = record.get("theoretical_price")

        if theoretical is None:
            continue

        strike = float(record["strike"])
        side = str(record["option_type"])[0]
        paired.setdefault(strike, {})[side] = float(theoretical)

    points = [
        (strike, sides["c"] - sides["p"])
        for strike, sides in paired.items()
        if "c" in sides and "p" in sides
    ]

    if len(points) < 5:
        return 0.0, 1.0

    count = len(points)
    mean_strike = sum(strike for strike, _ in points) / count
    mean_gap = sum(gap for _, gap in points) / count
    covariance = sum(
        (strike - mean_strike) * (gap - mean_gap) for strike, gap in points
    )
    variance = sum((strike - mean_strike) ** 2 for strike, _ in points)
    discount = -covariance / variance

    if discount <= 0:
        return 0.0, 1.0

    return (mean_gap + discount * mean_strike) / discount, discount


async def get_chain_marks(symbol: str, expiration: str) -> dict:
    """Return what Cboe publishes for an expiration.

    Parameters
    ----------
    symbol : str
        The underlying ticker symbol.
    expiration : str
        The expiration to read.

    Returns
    -------
    dict
        The quote, implied volatility, and theoretical price of each
        ``(option_type, strike)`` under 'contracts', with the expiration's
        implied 'forward', 'discount', and 'dte'.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    empty: dict = {"contracts": {}, "forward": 0.0, "discount": 1.0, "dte": 0}

    try:
        data = await load_symbol(symbol)
    except OpenBBError:
        return empty

    frame = data.dataframe
    records = frame[frame["expiration"].astype(str) == expiration].to_dict("records")

    if not records:
        return empty

    contracts: dict = {}

    for record in records:
        volatility = record.get("implied_volatility")
        contracts[(str(record["option_type"])[0], float(record["strike"]))] = {
            "iv": (
                float(volatility)
                if volatility is not None and 0 < float(volatility) < 5
                else None
            ),
            "theoretical_price": record.get("theoretical_price"),
            "bid": record.get("bid"),
            "ask": record.get("ask"),
        }

    forward, discount = _implied_forward(records)

    return {
        "contracts": contracts,
        "forward": forward,
        "discount": discount,
        "dte": int(records[0]["dte"]),
    }


def get_expirations(symbol: str) -> list[dict]:
    """Return the cached expiration choices for a symbol's dropdown.

    Parameters
    ----------
    symbol : str
        The underlying ticker symbol.

    Returns
    -------
    list[dict]
        ``[{label, value}]`` expiration choices, empty when not yet loaded.
    """
    results = LOADED_SYMBOLS.get(symbol.upper())

    if results is None:
        return []

    return [{"label": e, "value": e} for e in chain_expirations(results)]


def get_strikes(symbol: str) -> list[dict]:
    """Return the cached strike choices for a symbol's dropdown.

    Parameters
    ----------
    symbol : str
        The underlying ticker symbol.

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
