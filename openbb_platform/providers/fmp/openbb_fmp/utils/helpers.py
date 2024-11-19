"""FMP Helpers Module."""

from datetime import date
from typing import Any, List, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError
from openbb_core.provider.utils.helpers import get_querystring


async def response_callback(response, _):
    """Use callback for make_request."""
    data = await response.json()
    if isinstance(data, dict):
        error_message = data.get("Error Message", data.get("error"))
        if error_message is not None:
            conditions = (
                "upgrade" in error_message.lower()
                or "exclusive endpoint" in error_message.lower()
                or "subscription" in error_message.lower()
                or "unauthorized" in error_message.lower()
            )
            if conditions:
                raise UnauthorizedError(f"Unauthorized FMP request -> {error_message}")
            raise OpenBBError(
                f"FMP Error Message -> Status code: {response.status} -> {error_message}"
            )

    return data


async def get_data(url: str, **kwargs: Any) -> Union[list, dict]:
    """Get data from FMP endpoint."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import amake_request

    return await amake_request(url, response_callback=response_callback, **kwargs)


async def get_data_urls(urls: str, **kwargs: Any) -> Union[list, dict]:
    """Get data from FMP for several urls."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import amake_requests

    return await amake_requests(urls, response_callback=response_callback, **kwargs)


def create_url(
    version: int,
    endpoint: str,
    api_key: Optional[str],
    query: Optional[Any] = None,
    exclude: Optional[List[str]] = None,
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
    exclude: List[str]
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
    url: str, sub_dict: Optional[str] = None, **kwargs: Any
) -> List[dict]:
    """Get data from FMP endpoint and convert to list of schemas.

    Parameters
    ----------
    url: str
        The URL to get the data from.
    sub_dict: Optional[str]
        The sub-dictionary to use.

    Returns
    -------
    List[dict]
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


def most_recent_quarter(base: Optional[date] = None) -> date:
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
