"""Intrinio Helpers Module."""

import asyncio
import json
from datetime import (
    date as dateType,
    timedelta,
)
from io import StringIO
from typing import Any, Dict, List, Optional, TypeVar, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    ClientSession,
    amake_request,
)
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BasicResponse:
    """Basic Response class."""

    def __init__(self, response: StringIO):
        """Initialize the BasicResponse class."""
        # Find a way to get the status code
        self.status_code = 200
        response.seek(0)
        self.text = response.read()

    def json(self) -> dict:
        """Return the response as a dictionary."""
        return json.loads(self.text)


def request(url: str) -> BasicResponse:
    """
    Request function for PyScript. Pass in Method and make sure to await.

    Parameters
    ----------
    url: str
        URL to make request to

    Return:
    -------
    response: BasicRequest
        BasicRequest object with status_code and text attributes
    """
    # pylint: disable=import-outside-toplevel
    from pyodide.http import open_url  # type: ignore

    response = open_url(url)
    return BasicResponse(response)


async def response_callback(
    response: ClientResponse, _: ClientSession
) -> Union[dict, List[dict]]:
    """Use callback for async_request."""
    data = await response.json()

    if isinstance(data, dict) and "error" in data:
        message = data.get("message", "")
        error = data.get("error", "")
        if "api key" in message.lower() or error.startswith(
            "You do not have sufficient access to view this data"
        ):
            raise UnauthorizedError(
                f"Unauthorized Intrinio request -> {message} -> {error}"
            )

        raise OpenBBError(f"Error in Intrinio request -> {message} -> {error}")

    if isinstance(data, (str, float)):
        data = {"value": data}

    if isinstance(data, list) and len(data) == 0:
        raise EmptyDataError()

    return data


async def get_data(url: str, **kwargs: Any) -> Union[list, dict]:
    """Get data from Intrinio endpoint."""
    return await amake_request(url, response_callback=response_callback, **kwargs)


async def get_data_many(
    url: str, sub_dict: Optional[str] = None, **kwargs: Any
) -> List[dict]:
    """Get data from Intrinio endpoint and convert to list of schemas.

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
    return data


async def get_data_one(url: str, **kwargs: Any) -> Dict[str, Any]:
    """Get data from Intrinio endpoint and convert to schema."""
    data = await get_data(url, **kwargs)
    if isinstance(data, list):
        if len(data) == 0:
            raise ValueError("Expected dict, got empty list")

        try:
            data = {i: data[i] for i in range(len(data))} if len(data) > 1 else data[0]
        except TypeError as e:
            raise ValueError("Expected dict, got list of dicts") from e

    return data


def get_weekday(date: dateType) -> dateType:
    """Return the weekday date."""
    if date.weekday() in [5, 6]:
        return date - timedelta(days=date.weekday() - 4)
    return date


async def async_get_data_one(
    url: str, limit: int = 1, sleep: float = 1, **kwargs: Any
) -> Union[list, dict]:
    """Get data from Intrinio endpoint and convert to schema."""
    if limit > 100:
        await asyncio.sleep(sleep)

    try:
        data = await get_data(url, **kwargs)
    except Exception as e:
        if "limit" not in str(e):
            raise e
        return await async_get_data_one(url, limit, sleep, **kwargs)

    return data
