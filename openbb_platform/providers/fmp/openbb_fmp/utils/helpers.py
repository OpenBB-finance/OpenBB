"""FMP Helpers Module."""

from datetime import date as dateType
from typing import Any, Dict, List, Optional, Union

from openbb_core.provider.utils.client import ClientSession
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    amake_request,
    amake_requests,
    get_querystring,
)
from pydantic import BaseModel


async def response_callback(
    response: ClientResponse, _: ClientSession
) -> Union[Dict, List[Dict]]:
    """Use callback for make_request."""
    data = await response.json()
    if isinstance(data, dict) and "Error Message" in data:
        raise RuntimeError(f"FMP Error Message -> {data['Error Message']}")

    if isinstance(data, dict) and "error" in data:
        raise RuntimeError(
            f"FMP Error Message -> {data['error']}. Status code: {response.status}"
        )

    return data


async def get_data(url: str, **kwargs: Any) -> Union[list, dict]:
    """Get data from FMP endpoint."""
    return await amake_request(url, response_callback=response_callback, **kwargs)


async def get_data_urls(urls: str, **kwargs: Any) -> Union[list, dict]:
    """Get data from FMP for several urls."""
    return await amake_requests(urls, response_callback=response_callback, **kwargs)


def create_url(
    version: int,
    endpoint: str,
    api_key: Optional[str],
    query: Optional[Union[BaseModel, Dict]] = None,
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


def most_recent_quarter(base: dateType = dateType.today()) -> dateType:
    """Get the most recent quarter date."""
    base = min(base, dateType.today())  # This prevents dates from being in the future
    exacts = [(3, 31), (6, 30), (9, 30), (12, 31)]
    for exact in exacts:
        if base.month == exact[0] and base.day == exact[1]:
            return base
    if base.month < 4:
        return dateType(base.year - 1, 12, 31)
    if base.month < 7:
        return dateType(base.year, 3, 31)
    if base.month < 10:
        return dateType(base.year, 6, 30)
    return dateType(base.year, 9, 30)


def get_interval(value: str) -> str:
    """Get the intervals for the FMP API."""
    intervals = {
        "m": "min",
        "h": "hour",
        "d": "day",
    }

    return f"{value[:-1]}{intervals[value[-1]]}"
