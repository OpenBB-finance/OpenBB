"""Shared Deribit options chain, as the core model the options charts draw from."""

from typing import Any

CHAIN_COLUMNS = {
    "contract_symbol": "contract_symbol",
    "expiration": "expiration",
    "dte": "dte",
    "strike": "strike",
    "option_type": "option_type",
    "contract_size": "contract_size",
    "open_interest": "open_interest",
    "volume": "volume",
    "last": "last_trade_price",
    "bid": "bid",
    "ask": "ask",
    "mark": "mark",
    "implied_volatility": "implied_volatility",
    "delta": "delta",
    "gamma": "gamma",
    "theta": "theta",
    "vega": "vega",
    "rho": "rho",
    "underlying_price": "underlying_price",
}


def chain_expirations(data: Any) -> list[str]:
    """Return the expirations that still have contracts in the chain.

    Parameters
    ----------
    data : Any
        The loaded ``OptionsChainsData``.

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


def to_chain(frame: Any, symbol: str) -> Any:
    """Return a loaded chain frame as the core ``OptionsChainsData``.

    Parameters
    ----------
    frame : DataFrame
        The chain, as ``load_chain`` returns it.
    symbol : str
        The underlying root, as it appears in the instrument name.

    Returns
    -------
    OptionsChainsData
        One entry per contract, with implied volatility as a decimal.
    """
    from numpy import nan
    from openbb_core.provider.standard_models.options_chains import OptionsChainsData

    columns = frame.reindex(columns=list(CHAIN_COLUMNS)).rename(columns=CHAIN_COLUMNS)
    spot = frame["underlying_spot_price"].astype(float)
    forward = columns["underlying_price"].astype(float)
    columns["underlying_price"] = forward.where(forward > 0, spot)
    columns["implied_volatility"] = columns["implied_volatility"].astype(float) / 100
    columns["underlying_symbol"] = symbol.upper()
    columns = columns.sort_values(["expiration", "strike", "option_type"])
    columns = columns.astype(object).replace({nan: None}).reset_index(drop=True)

    return OptionsChainsData.model_validate(columns.to_dict(orient="list"))


async def load_symbol(symbol: str) -> Any:
    """Return the chain of one underlying as the core ``OptionsChainsData``.

    Parameters
    ----------
    symbol : str
        The underlying root, as it appears in the instrument name.

    Returns
    -------
    OptionsChainsData
        The chain the options charts are drawn from.

    Raises
    ------
    OpenBBError
        If the exchange lists no options on the underlying.
    """
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.errors import EmptyDataError

    from openbb_deribit.utils.options import chain

    root = symbol.upper()

    try:
        frame = await chain.load_chain(root)
    except (OpenBBError, EmptyDataError) as exc:
        raise OpenBBError(f"No options available for {root}.") from exc

    return to_chain(frame, root)


def get_strikes(data: Any) -> list[dict]:
    """Return the strike choices of a chain for its dropdown.

    Parameters
    ----------
    data : OptionsChainsData
        The loaded chain.

    Returns
    -------
    list[dict]
        ``[{label, value}]`` strike choices, led by the nearest out of the money.
    """
    underlying = data.underlying_price[0] if data.underlying_price else None
    choices: list[dict] = [{"label": "Nearest OTM", "value": None}]

    for strike in data.strikes:
        extra = (
            {"rightOfDescription": f"Underlying: ${underlying}"} if underlying else {}
        )
        choices.append(
            {
                "label": f"${int(strike) if strike.is_integer() else strike}",
                "value": strike,
                "extraInfo": extra,
            }
        )

    return choices
