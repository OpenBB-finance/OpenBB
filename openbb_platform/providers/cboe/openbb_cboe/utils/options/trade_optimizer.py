"""Cboe trade optimizer transport."""

from typing import Any

SYMBOL_INFO = "https://ww2.cboe.com/education/tools/trade-optimizer/symbol-info/"
OPTIMIZER = "https://ww2.cboe.com/education/tools/trade-optimizer/trade-optimizer-data/"
REFERER = "https://ww2.cboe.com/optionsinstitute/tools/trade_optimizer/?iframe=1"


def _headers() -> dict:
    """Build the headers the optimizer answers to."""
    return {
        "Accept": "application/json",
        "Referer": REFERER,
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
            " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
        ),
    }


async def get_symbol_info(symbol: str, use_cache: bool = True) -> dict[str, Any]:
    """Get the quote and the expirations the optimizer offers for a symbol.

    Parameters
    ----------
    symbol : str
        The underlying ticker symbol.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    dict[str, Any]
        The quote under 'details' and the dates under 'expirations'.

    Raises
    ------
    OpenBBError
        If the optimizer does not cover the symbol.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_cboe.utils.helpers import get_cboe_data

    response = await get_cboe_data(
        f"{SYMBOL_INFO}?symbol={symbol.upper()}",
        use_cache=use_cache,
        headers=_headers(),
    )

    if not isinstance(response, dict) or not response.get("success"):
        raise OpenBBError(f"The trade optimizer does not cover {symbol}.")

    return response


async def get_strategies(
    symbol: str,
    target_date: str,
    target_price: float,
    use_cache: bool = True,
) -> list[dict]:
    """Get every strategy the optimizer ranks for a target price and date.

    Parameters
    ----------
    symbol : str
        The underlying ticker symbol.
    target_date : str
        The expiration to trade, as YYYY-MM-DD.
    target_price : float
        The price the underlying is expected to reach.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    list[dict]
        One record per strategy, ranked by return.

    Raises
    ------
    OpenBBError
        If the optimizer returns no strategies.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_cboe.utils.helpers import get_cboe_data

    url = (
        f"{OPTIMIZER}?symbol={symbol.upper()}"
        f"&targetDate={target_date}&targetPrice={target_price}"
    )
    response = await get_cboe_data(url, use_cache=use_cache, headers=_headers())
    results = (response or {}).get("results") if isinstance(response, dict) else None

    if not results:
        raise OpenBBError(f"No strategies were returned for {symbol}.")

    return results


SENTIMENTS = {
    "very_bearish": 0.175,
    "bearish": 0.325,
    "neutral": 0.5,
    "bullish": 0.675,
    "very_bullish": 0.825,
}


def target_price(spot: float, iv30: float, dte: int, sentiment: str) -> float:
    """Return the price a sentiment targets, as a quantile of the distribution.

    Parameters
    ----------
    spot : float
        The current price of the underlying.
    iv30 : float
        The 30-day implied volatility, in percentage points.
    dte : int
        Days until the expiration being traded.
    sentiment : str
        One of the keys of SENTIMENTS.

    Returns
    -------
    float
        The target price, rounded the way the tool presents it.
    """
    from math import exp, sqrt
    from statistics import NormalDist

    quantile = SENTIMENTS.get(sentiment, 0.5)
    sigma = (iv30 / 100) * sqrt(max(dte, 1) / 365)
    z = NormalDist().inv_cdf(quantile)

    return round(spot * exp(sigma * z - 0.5 * sigma**2), 2)


def probability_below(spot: float, iv30: float, dte: int, price: float) -> float:
    """Return the market-implied probability of finishing below a price."""
    from math import log, sqrt
    from statistics import NormalDist

    sigma = (iv30 / 100) * sqrt(max(dte, 1) / 365)

    if sigma <= 0 or spot <= 0 or price <= 0:
        return 0.5

    return NormalDist().cdf((log(price / spot) + 0.5 * sigma**2) / sigma)
