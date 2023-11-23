"""Alpha Vantage Helpers Module."""

import json
import re
from io import StringIO
from typing import Any, List, Optional, TypeVar, Union

import requests
from openbb_core.provider import helpers
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import get_querystring
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
    """Request function for PyScript.

    Pass in Method and make sure to await!

    Parameters
    ----------
    url: str
        URL to make request to

    Return
    ------
    response: BasicRequest
        BasicRequest object with status_code and text attributes
    """
    # pylint: disable=import-outside-toplevel
    from pyodide.http import open_url  # type: ignore

    response = open_url(url)
    return BasicResponse(response)


def get_data(url: str, **kwargs: Any) -> Union[list, dict]:
    """Get data from Alpha Vantage endpoint."""
    try:
        r: Union[requests.Response, BasicResponse] = helpers.make_request(url, **kwargs)
    except SSLError:
        r = request(url)
    if r.status_code == 404:
        raise RuntimeError("Alpha Vantage endpoint doesn't exist")

    data = r.json()
    if "Information" in data:
        raise RuntimeError(f"Error in Alpha Vantage request -> {data['Information']}")

    if len(data) == 0:
        raise EmptyDataError()

    return data


def create_url(
    version: int,
    endpoint: str,
    api_key: Optional[str],
    query: Optional[BaseModel] = None,
    exclude: Optional[List[str]] = None,
) -> str:
    """Return a URL for the Alpha Vantage API.

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
    the_dict = {} if not query else query.model_dump()
    query_string = get_querystring(the_dict, exclude or [])
    base_url = f"https://financialmodelingprep.com/api/v{version}/"
    return f"{base_url}{endpoint}?{query_string}&apikey={api_key}"


def get_data_many(
    url: str, sub_dict: Optional[str] = None, **kwargs: Any
) -> List[dict]:
    """Get data from Alpha Vantage endpoint and convert to list of schemas.

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
    data = get_data(url, **kwargs)
    if sub_dict and isinstance(data, dict):
        data = data.get(sub_dict, [])
    if isinstance(data, dict):
        raise ValueError("Expected list of dicts, got dict")
    if len(data) == 0:
        raise EmptyDataError()

    return data


def get_data_one(url: str, **kwargs: Any) -> dict:
    """Get data from Alpha Vantage endpoint and convert to schema."""
    data = get_data(url, **kwargs)
    if isinstance(data, list):
        if len(data) == 0:
            raise ValueError("Expected dict, got empty list")

        try:
            data = {i: data[i] for i in range(len(data))} if len(data) > 1 else data[0]
        except TypeError as e:
            raise ValueError("Expected dict, got list of dicts") from e

    return data


def get_interval(value: str) -> str:
    """Get the intervals for the Alpha Vantage API."""

    intervals = {
        "m": "min",
        "d": "day",
        "W": "week",
        "M": "month",
    }

    return f"{value[:-1]}{intervals[value[-1]]}"


def extract_key_name(key):
    """Extract the alphabetical part of the key using regex."""
    match = re.search(r"\d+\.\s+([a-z]+)", key, re.I)
    return match.group(1) if match else key
