"""FMP Helpers Module."""

from datetime import date
from functools import lru_cache
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError
from openbb_core.provider.utils.helpers import get_querystring


async def response_callback(response, _):
    """Use callback for make_request."""
    if response.status != 200:
        msg = await response.text()
        code = response.status
        raise UnauthorizedError(f"Unauthorized FMP request -> {code} -> {msg}")

    data = await response.json()

    if isinstance(data, dict):
        error_message = data.get("Error Message", data.get("error"))

        if error_message is not None:
            conditions = (
                "upgrade" in error_message.lower()
                or "exclusive endpoint" in error_message.lower()
                or "special endpoint" in error_message.lower()
                or "premium query parameter" in error_message.lower()
                or "subscription" in error_message.lower()
                or "unauthorized" in error_message.lower()
                or "premium" in error_message.lower()
            )

            if conditions:
                raise UnauthorizedError(f"Unauthorized FMP request -> {error_message}")

            raise OpenBBError(
                f"FMP Error Message -> Status code: {response.status} -> {error_message}"
            )

    return data


async def get_data(url: str, **kwargs: Any) -> list | dict:
    """Get data from FMP endpoint."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import amake_request

    return await amake_request(url, response_callback=response_callback, **kwargs)


async def get_data_urls(urls: list[str], **kwargs: Any) -> list | dict:
    """Get data from FMP for several urls."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import amake_requests

    return await amake_requests(urls, response_callback=response_callback, **kwargs)


def create_url(
    version: int,
    endpoint: str,
    api_key: str | None,
    query: Any | None = None,
    exclude: list[str] | None = None,
) -> str:
    """Return a URL for the FMP API.

    Parameters
    ----------
    version: int
        The version of the API to use.
    endpoint: str
        The endpoint to use.
    api_key: str
        The API key to use.
    query: Optional[BaseModel]
        The dictionary to be turned into a querystring.
    exclude: list[str]
        The keys to be excluded from the querystring.

    Returns
    -------
    str
        The querystring.
    """
    # pylint: disable=import-outside-toplevel
    from pydantic import BaseModel

    the_dict = {}
    if query:
        the_dict = query.model_dump() if isinstance(query, BaseModel) else query
    query_string = get_querystring(the_dict, exclude or [])
    base_url = f"https://financialmodelingprep.com/api/v{version}/"
    return f"{base_url}{endpoint}?{query_string}&apikey={api_key}"


async def get_data_many(
    url: str, sub_dict: str | None = None, **kwargs: Any
) -> list[dict]:
    """Get data from FMP endpoint and convert to list of schemas.

    Parameters
    ----------
    url: str
        The URL to get the data from.
    sub_dict: Optional[str]
        The sub-dictionary to use.

    Returns
    -------
    list[dict]
        Dictionary of data.
    """
    data = await get_data(url, **kwargs)

    if sub_dict and isinstance(data, dict):
        data = data.get(sub_dict, [])
    if isinstance(data, dict):
        raise ValueError("Expected list of dicts, got dict")
    if len(data) == 0:
        raise EmptyDataError()

    return data


async def get_data_one(url: str, **kwargs: Any) -> dict:
    """Get data from FMP endpoint and convert to schema."""
    data = await get_data(url, **kwargs)
    if isinstance(data, list):
        if len(data) == 0:
            raise ValueError("Expected dict, got empty list")

        try:
            data = {i: data[i] for i in range(len(data))} if len(data) > 1 else data[0]
        except TypeError as e:
            raise ValueError("Expected dict, got list of dicts") from e

    return data


def most_recent_quarter(base: date | None = None) -> date:
    """Get the most recent quarter date."""
    if base is None:
        base = date.today()
    base = min(base, date.today())  # This prevents dates from being in the future
    exacts = [(3, 31), (6, 30), (9, 30), (12, 31)]
    for exact in exacts:
        if base.month == exact[0] and base.day == exact[1]:
            return base
    if base.month < 4:
        return date(base.year - 1, 12, 31)
    if base.month < 7:
        return date(base.year, 3, 31)
    if base.month < 10:
        return date(base.year, 6, 30)
    return date(base.year, 9, 30)


def get_interval(value: str) -> str:
    """Get the intervals for the FMP API."""
    intervals = {
        "m": "min",
        "h": "hour",
        "d": "day",
    }

    return f"{value[:-1]}{intervals[value[-1]]}"


async def get_historical_ohlc(query, credentials, **kwargs: Any) -> list[dict]:
    """Return the raw data from the FMP endpoint."""
    # pylint: disable=import-outside-toplevel
    import asyncio  # noqa
    from openbb_core.provider.utils.helpers import (
        amake_request,
    )
    from warnings import warn

    api_key = credentials.get("fmp_api_key") if credentials else ""

    base_url = "https://financialmodelingprep.com/stable/"

    if hasattr(query, "adjustment") and query.adjustment == "unadjusted":
        base_url += "historical-price-eod/non-split-adjusted?"
    elif hasattr(query, "adjustment") and query.adjustment == "splits_and_dividends":
        base_url += "historical-price-eod/dividend-adjusted?"
    elif query.interval == "1d":
        base_url += "historical-price-eod/full?"
    elif query.interval == "1m":
        base_url += "historical-chart/1min?"
    elif query.interval == "5m":
        base_url += "historical-chart/5min?"
    elif query.interval in ["60m", "1h"]:
        query.interval = "60m"
        base_url += "historical-chart/1hour?"

    query_str = get_querystring(
        query.model_dump(), ["symbol", "adjustment", "interval"]
    )
    symbols = query.symbol.split(",")

    results: list = []
    messages: list = []

    async def get_one(symbol):
        """Get data for one symbol."""
        url = f"{base_url}symbol={symbol}&{query_str}&apikey={api_key}"
        data: list = []
        response = await amake_request(
            url, response_callback=response_callback, **kwargs
        )

        if isinstance(response, dict) and response.get("Error Message"):
            message = (
                f"Error fetching data for {symbol}: {response.get('Error Message', '')}"
            )
            warn(message)
            messages.append(message)

        if isinstance(response, list) and len(response) > 0:
            data = response

        elif isinstance(response, dict) and response.get("historical"):
            data = response.get("historical", [])

        if not data:
            message = f"No data found for {symbol}."
            warn(message)
            messages.append(message)

        elif data:
            for d in data:
                d["symbol"] = symbol
                results.append(d)

    await asyncio.gather(*[get_one(symbol) for symbol in symbols])

    if not results:
        raise EmptyDataError(
            f"{str(','.join(messages)).replace(',', ' ') if messages else 'No data found'}"
        )

    return results


@lru_cache(maxsize=1)
def get_available_transcript_symbols(api_key) -> list:
    """Return the available symbols for earnings call transcripts."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import make_request

    url = f"https://financialmodelingprep.com/stable/earnings-transcript-list?apikey={api_key}"

    data = make_request(url)

    data.raise_for_status()

    return data.json()


@lru_cache(maxsize=64)
def get_transcript_dates_for_symbol(symbol: str, api_key: str) -> list:
    """Return the available dates for a given symbol's earnings call transcripts."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import make_request

    url = f"https://financialmodelingprep.com/stable/earning-call-transcript-dates?symbol={symbol}&apikey={api_key}"

    data = make_request(url)

    data.raise_for_status()

    return data.json()
