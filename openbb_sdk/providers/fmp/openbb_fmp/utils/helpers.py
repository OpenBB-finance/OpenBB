"""FMP Helpers Module."""

import json
from datetime import datetime
from io import StringIO
from typing import Any, List, Optional, Type, TypeVar, Union

import requests
from openbb_provider import helpers
from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import QueryParamsType
from openbb_provider.helpers import (
    get_querystring,
)
from pydantic import BaseModel, PositiveFloat, validator
from requests.exceptions import SSLError

T = TypeVar("T", bound=BaseModel)


class BasicResponse:
    def __init__(self, response: StringIO):
        # Find a way to get the status code
        self.status_code = 200
        response.seek(0)
        self.text = response.read()

    def json(self) -> dict:
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
    from pyodide.http import open_url

    response = open_url(url)
    return BasicResponse(response)


def get_data(url: str, **kwargs: Any) -> Union[list, dict]:
    """Get data from FMP endpoint."""
    try:
        r: Union[requests.Response, BasicResponse] = helpers.make_request(url, **kwargs)
    except SSLError:
        r = request(url)
    if r.status_code == 404:
        raise RuntimeError("FMP endpoint doesn't exist")

    data = r.json()
    if r.status_code != 200:
        message = data.get("message", "unknown error")
        raise RuntimeError(f"Error in FMP request -> {message}")

    if "Error Message" in data:
        raise RuntimeError("FMP Error Message -> " + data["Error Message"])

    if len(data) == 0:
        raise RuntimeError("No results found. Try adjusting the query parameters.")

    return data


def create_url(
    version: int,
    endpoint: str,
    api_key: Optional[str],
    query: Optional[QueryParamsType] = None,
    exclude: Optional[List[str]] = None,
) -> str:
    """Creates a URL for the FMP API.

    Parameters:
    -----------
    version: int
        The version of the API to use.
    endpoint: str
        The endpoint to use.
    api_key: str
        The API key to use.
    query: Optional[QueryParamsType]
        The dictionary to be turned into a querystring.
    exclude: List[str]
        The keys to be excluded from the querystring.

    Returns:
    --------
    str
        The querystring.

    """
    the_dict = {} if not query else query.dict(by_alias=True)
    query_string = get_querystring(the_dict, exclude or [])
    base_url = f"https://financialmodelingprep.com/api/v{version}/"
    return f"{base_url}{endpoint}?{query_string}&apikey={api_key}"


def get_data_many(
    url: str, to_schema: Type[T], sub_dict: Optional[str] = None, **kwargs: Any
) -> List[T]:
    """Get data from FMP endpoint and convert to list of schemas.

    Parameters:
    -----------
    url: str
        The URL to get the data from.
    to_schema: T
        The schema to convert the data to.
    sub_dict: Optional[str]
        The sub-dictionary to use.

    Returns:
    --------
    List[T]
        The list of schemas.
    """
    data = get_data(url, **kwargs)
    if sub_dict and isinstance(data, dict):
        data = data.get(sub_dict, [])
    if isinstance(data, dict):
        raise ValueError("Expected list of dicts, got dict")
    return [to_schema.parse_obj(d) for d in data]  # type: ignore


def get_data_one(url: str, to_schema: Type[T], **kwargs: Any) -> T:
    """Get data from FMP endpoint and convert to schema."""
    data = get_data(url, **kwargs)
    if isinstance(data, list):
        if len(data) == 0:
            raise ValueError("Expected dict, got empty list")

        try:
            data = {i: data[i] for i in range(len(data))} if len(data) > 1 else data[0]
        except TypeError as e:
            raise ValueError("Expected dict, got list of dicts") from e

    return to_schema.parse_obj(data)  # type: ignore


class BaseStockPriceData(Data):
    """Base Stock Price Data."""

    date: datetime
    open: PositiveFloat
    high: PositiveFloat
    low: PositiveFloat
    close: PositiveFloat
    volume: float

    @validator("date", pre=True)
    def time_validate(cls, v: str) -> datetime:  # pylint: disable=E0213
        """Validate the date."""
        if len(v) < 12:
            return datetime.strptime(v, "%Y-%m-%d")
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
