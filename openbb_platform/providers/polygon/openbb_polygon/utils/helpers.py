"""Polygon Helpers Module."""

import json
from io import StringIO
from typing import Any, List, Optional, TypeVar, Union

import requests
from openbb_provider import helpers
from openbb_provider.utils.errors import EmptyDataError
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
    """Get data from Polygon endpoint."""

    try:
        r: Union[requests.Response, BasicResponse] = helpers.make_request(url, **kwargs)
    except SSLError:
        r = request(url)
    if r.status_code == 404:
        raise RuntimeError("Polygon endpoint doesn't exist")

    data = r.json()
    if r.status_code != 200:
        message = data.get("message")
        error = data.get("error")
        value = error or message

        raise RuntimeError(f"Error in Polygon request -> {value}")

    if "results" not in data or len(data) == 0:
        raise EmptyDataError()

    return data


def get_data_many(
    url: str, sub_dict: Optional[str] = None, **kwargs: Any
) -> List[dict]:
    """Get data from Polygon endpoint and convert to list of schemas.

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
    """Get data from Polygon endpoint and convert to schema."""

    data = get_data(url, **kwargs)
    if isinstance(data, list):
        if len(data) == 0:
            raise ValueError("Expected dict, got empty list")

        try:
            data = {i: data[i] for i in range(len(data))} if len(data) > 1 else data[0]
        except TypeError as e:
            raise ValueError("Expected dict, got list of dicts") from e

    return data


def get_date_condition(date: str) -> str:
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


STOCK_TAPE_MAP = {
    1: "Tape A: NYSE",
    2: "Tape B: NYSE ARCA",
    3: "Tape C: NASDAQ",
}

EXCHANGE_ID_MAP = [
    {
        "id": 1,
        "type": "exchange",
        "asset_class": "stocks",
        "locale": "us",
        "name": "NYSE American, LLC",
        "acronym": "AMEX",
        "mic": "XASE",
        "operating_mic": "XNYS",
        "participant_id": "A",
        "url": "https://www.nyse.com/markets/nyse-american",
    },
    {
        "id": 2,
        "type": "exchange",
        "asset_class": "stocks",
        "locale": "us",
        "name": "Nasdaq OMX BX, Inc.",
        "mic": "XBOS",
        "operating_mic": "XNAS",
        "participant_id": "B",
        "url": "https://www.nasdaq.com/solutions/nasdaq-bx-stock-market",
    },
    {
        "id": 3,
        "type": "exchange",
        "asset_class": "stocks",
        "locale": "us",
        "name": "NYSE National, Inc.",
        "acronym": "NSX",
        "mic": "XCIS",
        "operating_mic": "XNYS",
        "participant_id": "C",
        "url": "https://www.nyse.com/markets/nyse-national",
    },
    {
        "id": 4,
        "type": "TRF",
        "asset_class": "stocks",
        "locale": "us",
        "name": "FINRA NYSE TRF",
        "mic": "FINY",
        "operating_mic": "XNYS",
        "participant_id": "D",
        "url": "https://www.finra.org",
    },
    {
        "id": 4,
        "type": "TRF",
        "asset_class": "stocks",
        "locale": "us",
        "name": "FINRA Nasdaq TRF Carteret",
        "mic": "FINN",
        "operating_mic": "FINR",
        "participant_id": "D",
        "url": "https://www.finra.org",
    },
    {
        "id": 4,
        "type": "TRF",
        "asset_class": "stocks",
        "locale": "us",
        "name": "FINRA Nasdaq TRF Chicago",
        "mic": "FINC",
        "operating_mic": "FINR",
        "participant_id": "D",
        "url": "https://www.finra.org",
    },
    {
        "id": 4,
        "type": "TRF",
        "asset_class": "stocks",
        "locale": "us",
        "name": "FINRA Alternative Display Facility",
        "mic": "XADF",
        "operating_mic": "FINR",
        "participant_id": "D",
        "url": "https://www.finra.org",
    },
    {
        "id": 5,
        "type": "SIP",
        "asset_class": "stocks",
        "locale": "us",
        "name": "Unlisted Trading Privileges",
        "operating_mic": "XNAS",
        "participant_id": "E",
        "url": "https://www.utpplan.com",
    },
    {
        "id": 6,
        "type": "TRF",
        "asset_class": "stocks",
        "locale": "us",
        "name": "International Securities Exchange, LLC - Stocks",
        "mic": "XISE",
        "operating_mic": "XNAS",
        "participant_id": "I",
        "url": "https://nasdaq.com/solutions/nasdaq-ise",
    },
    {
        "id": 7,
        "type": "exchange",
        "asset_class": "stocks",
        "locale": "us",
        "name": "Cboe EDGA",
        "mic": "EDGA",
        "operating_mic": "XCBO",
        "participant_id": "J",
        "url": "https://www.cboe.com/us/equities",
    },
    {
        "id": 8,
        "type": "exchange",
        "asset_class": "stocks",
        "locale": "us",
        "name": "Cboe EDGX",
        "mic": "EDGX",
        "operating_mic": "XCBO",
        "participant_id": "K",
        "url": "https://www.cboe.com/us/equities",
    },
    {
        "id": 9,
        "type": "exchange",
        "asset_class": "stocks",
        "locale": "us",
        "name": "NYSE Chicago, Inc.",
        "mic": "XCHI",
        "operating_mic": "XNYS",
        "participant_id": "M",
        "url": "https://www.nyse.com/markets/nyse-chicago",
    },
    {
        "id": 10,
        "type": "exchange",
        "asset_class": "stocks",
        "locale": "us",
        "name": "New York Stock Exchange",
        "mic": "XNYS",
        "operating_mic": "XNYS",
        "participant_id": "N",
        "url": "https://www.nyse.com",
    },
    {
        "id": 11,
        "type": "exchange",
        "asset_class": "stocks",
        "locale": "us",
        "name": "NYSE Arca, Inc.",
        "mic": "ARCX",
        "operating_mic": "XNYS",
        "participant_id": "P",
        "url": "https://www.nyse.com/markets/nyse-arca",
    },
    {
        "id": 12,
        "type": "exchange",
        "asset_class": "stocks",
        "locale": "us",
        "name": "Nasdaq",
        "mic": "XNAS",
        "operating_mic": "XNAS",
        "participant_id": "T",
        "url": "https://www.nasdaq.com",
    },
    {
        "id": 13,
        "type": "SIP",
        "asset_class": "stocks",
        "locale": "us",
        "name": "Consolidated Tape Association",
        "operating_mic": "XNYS",
        "participant_id": "S",
        "url": "https://www.nyse.com/data/cta",
    },
    {
        "id": 14,
        "type": "exchange",
        "asset_class": "stocks",
        "locale": "us",
        "name": "Long-Term Stock Exchange",
        "mic": "LTSE",
        "operating_mic": "LTSE",
        "participant_id": "L",
        "url": "https://www.ltse.com",
    },
    {
        "id": 15,
        "type": "exchange",
        "asset_class": "stocks",
        "locale": "us",
        "name": "Investors Exchange",
        "mic": "IEXG",
        "operating_mic": "IEXG",
        "participant_id": "V",
        "url": "https://www.iextrading.com",
    },
    {
        "id": 16,
        "type": "TRF",
        "asset_class": "stocks",
        "locale": "us",
        "name": "Cboe Stock Exchange",
        "mic": "CBSX",
        "operating_mic": "XCBO",
        "participant_id": "W",
        "url": "https://www.cboe.com",
    },
    {
        "id": 17,
        "type": "exchange",
        "asset_class": "stocks",
        "locale": "us",
        "name": "Nasdaq Philadelphia Exchange LLC",
        "mic": "XPHL",
        "operating_mic": "XNAS",
        "participant_id": "X",
        "url": "https://www.nasdaq.com/solutions/nasdaq-phlx",
    },
    {
        "id": 18,
        "type": "exchange",
        "asset_class": "stocks",
        "locale": "us",
        "name": "Cboe BYX",
        "mic": "BATY",
        "operating_mic": "XCBO",
        "participant_id": "Y",
        "url": "https://www.cboe.com/us/equities",
    },
    {
        "id": 19,
        "type": "exchange",
        "asset_class": "stocks",
        "locale": "us",
        "name": "Cboe BZX",
        "mic": "BATS",
        "operating_mic": "XCBO",
        "participant_id": "Z",
        "url": "https://www.cboe.com/us/equities",
    },
    {
        "id": 20,
        "type": "exchange",
        "asset_class": "stocks",
        "locale": "us",
        "name": "MIAX Pearl",
        "mic": "EPRL",
        "operating_mic": "MIHI",
        "participant_id": "H",
        "url": "https://www.miaxoptions.com/alerts/pearl-equities",
    },
    {
        "id": 21,
        "type": "exchange",
        "asset_class": "stocks",
        "locale": "us",
        "name": "Members Exchange",
        "mic": "MEMX",
        "operating_mic": "MEMX",
        "participant_id": "U",
        "url": "https://www.memx.com",
    },
    {
        "id": 62,
        "type": "ORF",
        "asset_class": "stocks",
        "locale": "us",
        "name": "OTC Equity Security",
        "mic": "OOTC",
        "operating_mic": "FINR",
        "url": "https://www.finra.org/filing-reporting/over-the-counter-reporting-facility-orf",
    },
]


def map_exchanges(results):
    to_map = ["ask_exchange", "bid_exchange"]
    for result in results:
        for map in to_map:
            mapped_exchange_id = result.get(map)
            for exchange in EXCHANGE_ID_MAP:
                if exchange.get("id") == mapped_exchange_id:
                    result[map] = (
                        exchange.get("name")
                        .replace(",", "")
                        .replace("Inc.", "")
                        .strip()
                    )
                    break

    return results


def map_tape(results):
    for result in results:
        if "tape" in result:
            mapped_result = STOCK_TAPE_MAP[result["tape"]]
            result["tape"] = mapped_result
    return results
