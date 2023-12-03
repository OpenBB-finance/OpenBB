"""Nasdaq Helpers Module."""

import json
import re
from datetime import timedelta
from io import StringIO
from typing import Any, List, Optional, TypeVar, Union

import requests
from openbb_core.provider import helpers
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import BaseModel
from random_user_agent.user_agent import UserAgent
from requests.exceptions import SSLError

T = TypeVar("T", bound=BaseModel)


def remove_html_tags(text: str):
    """Remove HTML tags from a string."""
    clean = re.compile("<.*?>")
    return re.sub(clean, " ", text)


def get_random_agent() -> str:
    """Generate a random user agent for a request."""
    user_agent_rotator = UserAgent(limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()
    return user_agent


HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip",
    "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
    "Host": "api.nasdaq.com",
    "User-Agent": get_random_agent(),
    "Connection": "keep-alive",
}

IPO_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip",
    "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
    "Host": "api.nasdaq.com",
    "Origin": "https://www.nasdaq.com",
    "Referer": "https://www.nasdaq.com/",
    "User-Agent": get_random_agent(),
    "Connection": "keep-alive",
}


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
    """Get data from Nasdaq endpoint."""
    try:
        r: Union[requests.Response, BasicResponse] = helpers.make_request(url, **kwargs)
    except SSLError:
        r = request(url)
    if r.status_code == 404:
        raise RuntimeError("Nasdaq endpoint doesn't exist")

    data = r.json()
    if len(data) == 0:
        raise EmptyDataError()

    if data["data"] is None:
        message = data["status"]["bCodeMessage"]["errorMessage"]
        raise RuntimeError(f"Error in Nasdaq request -> {message}")

    return data


def get_data_many(
    url: str, sub_dict: Optional[str] = None, **kwargs: Any
) -> List[dict]:
    """Get data from Nasdaq endpoint and convert to list of schemas.

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

    return data


def get_data_one(url: str, **kwargs: Any) -> dict:
    """Get data from Nasdaq endpoint and convert to schema."""
    data = get_data(url, **kwargs)
    if isinstance(data, list):
        if len(data) == 0:
            raise ValueError("Expected dict, got empty list")

        try:
            data = {i: data[i] for i in range(len(data))} if len(data) > 1 else data[0]
        except TypeError as e:
            raise ValueError("Expected dict, got list of dicts") from e

    return data


def date_range(start_date, end_date):
    """Yield dates between start_date and end_date."""
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)
