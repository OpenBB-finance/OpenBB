"""Intrinio Helpers Module."""

import json
from datetime import datetime, timedelta
from io import StringIO
from typing import Any, List, Optional, TypeVar, Union

import requests
import requests_cache
from openbb_provider import helpers
from openbb_provider.utils.helpers import make_request
from pydantic import BaseModel
from requests.exceptions import SSLError

T = TypeVar("T", bound=BaseModel)


# This will cache the symbol directory requests for 5 days.
intrinio_session = requests_cache.CachedSession(
    "OpenBB_Intrinio", expire_after=timedelta(days=5), use_cache_dir=True
)


def get_options_tickers(api_key: str = "") -> List[str]:
    """Returns all tickers that have existing options contracts.

    Parameters
    ----------
    api_key: str
        Intrinio API key.

    Returns
    -------
    List[str]
        List of tickers
    """
    url = f"https://api-v2.intrinio.com/options/tickers?api_key={api_key}"

    r = intrinio_session.get(url, timeout=10)

    return r.json()["tickers"]


def get_options_expirations(
    symbol: str,
    after: Optional[str] = datetime.now().date().strftime("%Y-%m-%d"),
    before: Optional[str] = "",
    api_key: str = "",
) -> list:
    """Returns a list of all current and upcoming option contract expiration dates for a particular symbol.

    Parameters
    ----------
    symbol: str
        The options symbol, corresponding to the underlying security.
    after: str
        Return option contract expiration dates after this date. Format: YYYY-MM-DD
    before: str
        Return option contract expiration dates before this date. Format: YYYY-MM-DD
    api_key: str
        Intrinio API key.
    """

    url = f"https://api-v2.intrinio.com/options/expirations/{symbol}/eod?before={before}&after={after}&api_key={api_key}"

    r = make_request(url)

    return sorted(list(r.json()["expirations"]))


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
    Request function for PyScript. Pass in Method and make sure to await!

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
        raise RuntimeError("Intrinio endpoint doesn't exist")

    data = r.json()
    if r.status_code != 200:
        message = data.get("message", "unknown error")
        raise RuntimeError(f"Error in Intrinio request -> {message}")

    if "Error Message" in data:
        raise RuntimeError("Intrinio Error Message -> " + data["Error Message"])

    if len(data) == 0:
        raise RuntimeError("No results found. Try adjusting the query parameters.")

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
