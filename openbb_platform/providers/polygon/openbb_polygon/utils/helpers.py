"""Polygon Helpers Module."""

import json
from io import StringIO
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union

from openbb_core.provider.utils.errors import EmptyDataError
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
    """Request function for PyScript.

    Pass in Method and make sure to await.

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


async def response_callback(
    response: ClientResponse, _: ClientSession
) -> Union[dict, List[dict]]:
    """Use callback for make_request."""
    data: Dict = await response.json()  # type: ignore

    if response.status != 200:
        message = data.get("error", None) or data.get("message", None)
        raise RuntimeError(f"Error in Polygon request -> {message}")

    keys_in_data = "results" in data or "tickers" in data

    if not keys_in_data or len(data) == 0:
        raise EmptyDataError()

    return data


async def get_data(url: str, **kwargs: Any) -> Union[list, dict]:
    """Get data from Polygon endpoint."""
    return await amake_request(url, response_callback=response_callback, **kwargs)


async def get_data_many(
    url: str, sub_dict: Optional[str] = None, **kwargs: Any
) -> List[dict]:
    """Get data from Polygon endpoint and convert to list of schemas.

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


async def get_data_one(url: str, **kwargs: Any) -> dict:
    """Get data from Polygon endpoint and convert to schema."""
    data = await get_data(url, **kwargs)
    if isinstance(data, list):
        if len(data) == 0:
            raise ValueError("Expected dict, got empty list")

        try:
            data = {i: data[i] for i in range(len(data))} if len(data) > 1 else data[0]
        except TypeError as e:
            raise ValueError("Expected dict, got list of dicts") from e

    return data


def get_date_condition(date: str) -> Tuple:
    """Get the date condition for the querystring."""
    date_conditions = {
        "<": "lt",
        "<=": "lte",
        ">": "gt",
        ">=": "gte",
    }

    for key, value in date_conditions.items():
        if key in date:
            return date.split(key)[1], value

    return date, "eq"


def map_tape(tape: int) -> str:
    """Map the tape to a string."""
    STOCK_TAPE_MAP = {
        1: "Tape A: NYSE",
        2: "Tape B: NYSE ARCA",
        3: "Tape C: NASDAQ",
    }

    return STOCK_TAPE_MAP.get(tape, "") if tape else ""
