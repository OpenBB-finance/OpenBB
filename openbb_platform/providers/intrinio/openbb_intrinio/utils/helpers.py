"""Intrinio Helpers Module."""

import asyncio
import json
from datetime import (
    date as dateType,
    timedelta,
)
from io import StringIO
from typing import Any, List, Optional, TypeVar, Union

import aiohttp
import requests
from openbb_core.provider import helpers
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import async_make_request
from pydantic import BaseModel
from requests.exceptions import SSLError

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

    Parameters:
    -----------
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


def get_data(url: str, **kwargs: Any) -> Union[list, dict]:
    """Get data from Intrinio endpoint."""
    try:
        r: Union[requests.Response, BasicResponse] = helpers.make_request(url, **kwargs)
    except SSLError:
        r = request(url)
    if r.status_code == 404:
        raise RuntimeError("Intrinio endpoint doesn't exist.")

    data = r.json()
    if r.status_code != 200:
        error = data.get("error")
        message = data.get("message")
        value = error or message
        raise RuntimeError(f"Error in Intrinio request -> {value}")

    if isinstance(data, (str, float)):
        data = {"value": data}

    if len(data) == 0:
        raise EmptyDataError()

    return data


def get_data_many(
    url: str, sub_dict: Optional[str] = None, **kwargs: Any
) -> List[dict]:
    """Get data from Intrinio endpoint and convert to list of schemas.

    Parameters:
    -----------
    url: str
        The URL to get the data from.
    sub_dict: Optional[str]
        The sub-dictionary to use.

    Returns:
    --------
    List[dict]
        Dictionary of data.
    """
    data = get_data(url, **kwargs)
    if sub_dict and isinstance(data, dict):
        data = data.get(sub_dict, [])
    if isinstance(data, dict):
        raise ValueError("Expected list of dicts, got dict")
    return data


def get_data_one(url: str, **kwargs: Any) -> dict:
    """Get data from Intrinio endpoint and convert to schema."""
    data = get_data(url, **kwargs)
    if isinstance(data, list):
        if len(data) == 0:
            raise ValueError("Expected dict, got empty list")

        try:
            data = {i: data[i] for i in range(len(data))} if len(data) > 1 else data[0]
        except TypeError as e:
            raise ValueError("Expected dict, got list of dicts") from e

    return data


def get_weekday(date: dateType) -> str:
    """Return the weekday date."""
    if date.weekday() in [5, 6]:
        return (date - timedelta(days=date.weekday() - 4)).strftime("%Y-%m-%d")
    return date.strftime("%Y-%m-%d")


async def response_callback(response: aiohttp.ClientResponse) -> dict:
    """Return the response."""
    data: dict = await response.json()

    if message := data.get("error", None) or data.get("message", None):
        raise RuntimeError(f"Error in Intrinio request -> {message}")

    if error := data.get("Error Message", None):
        raise RuntimeError(f"Intrinio Error Message -> {error}")

    return data


async def async_get_data_one(
    url: str, limit: int = 1, sleep: float = 1, **kwargs: Any
) -> dict:
    if limit > 100:
        await asyncio.sleep(sleep)

    try:
        data: dict = await async_make_request(
            url, response_callback=response_callback, **kwargs
        )
    except Exception as e:
        if "limit" not in str(e):
            raise e
        return await async_get_data_one(url, limit, sleep, **kwargs)

    return data
