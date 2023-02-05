"""CoinGecko helpers"""
__docformat__ = "numpy"

import datetime as dt
import json
import logging
import math
import textwrap
from datetime import timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dateutil import parser
from requests.adapters import HTTPAdapter, RetryError
from urllib3.util.retry import Retry

from openbb_terminal.helper_funcs import get_user_agent, request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

GECKO_BASE_URL = "https://www.coingecko.com"

DENOMINATION = ("usd", "btc", "eth")


def millify(n: Union[float, int]) -> str:
    millnames = ["", "K", "M", "B", "T"]
    n = float(n)
    millidx = max(
        0,
        min(
            len(millnames) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))
        ),
    )

    return f"{n / 10 ** (3 * millidx):.0f}{millnames[millidx]}"


def calc_change(current: Union[float, int], previous: Union[float, int]):
    """Calculates change between two different values"""
    if current == previous:
        return 0
    try:
        return ((current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return float("inf")


def get_btc_price() -> float:
    """Get BTC/USD price from CoinGecko API

    Returns
    -------
    str
        latest bitcoin price in usd.
    """

    req = request(
        "https://api.coingecko.com/api/v3/simple/"
        "price?ids=bitcoin&vs_currencies=usd&include_market_cap"
        "=false&include_24hr_vol"
        "=false&include_24hr_change=false&include_last_updated_at=false"
    )
    return req.json()["bitcoin"]["usd"]


def _retry_session(
    url: str, retries: int = 3, backoff_factor: float = 1.0
) -> requests.Session:
    """Helper methods that retries to make request to CoinGecko


    Parameters
    ----------
    url: str
        Url to mount a session
    retries: int
        How many retries
    backoff_factor: float
        Backoff schema - time periods between retry

    Returns
    -------
    requests.Session
        Mounted session
    """

    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        status_forcelist=[500, 502, 503, 504],
        backoff_factor=backoff_factor,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount(url, adapter)
    return session


def scrape_gecko_data(url: str) -> BeautifulSoup:
    """Helper method that scrape Coin Gecko site.

    Parameters
    ----------
    url : str
        coin gecko url to scrape e.g: "https://www.coingecko.com/en/discover"

    Returns
    -------
        BeautifulSoup object
    """
    headers = {"User-Agent": get_user_agent()}
    session = _retry_session("https://www.coingecko.com")
    try:
        req = session.get(url, headers=headers)
    except Exception as error:
        logger.exception(error)
        console.print(error)
        raise RetryError(
            "Connection error. Couldn't connect to CoinGecko and scrape the data. "
            "Please visit CoinGecko site, and check if it's not under maintenance"
        ) from error

    if req.status_code >= 400:
        raise Exception(
            f"Couldn't connect to {url}. Status code: {req.status_code}. Reason: {req.reason}"
        )

    return BeautifulSoup(req.text, features="lxml")


def replace_underscores_to_newlines(cols: list, line: int = 13) -> list:
    """Helper method that replace underscores to white space and breaks it to new line

    Parameters
    ----------
    cols
        - list of columns names
    line
        - line length
    Returns
    -------
        list of column names with replaced underscores
    """

    return [
        textwrap.fill(c.replace("_", " "), line, break_long_words=False)
        for c in list(cols)
    ]


def find_discord(item: Optional[List[Any]]) -> Union[str, Any]:
    if isinstance(item, list) and len(item) > 0:
        discord = [chat for chat in item if "discord" in chat]
        if len(discord) > 0:
            return discord[0]
    return None


def join_list_elements(elem):
    if isinstance(elem, dict):
        return ", ".join(k for k, v in elem.items())
    if isinstance(elem, list):
        return ", ".join(k for k in elem)
    return None


def filter_list(lst: Optional[List[Any]]) -> Optional[List[Any]]:
    if isinstance(lst, list) and len(lst) > 0:
        return [i for i in lst if i != ""]
    return lst


def calculate_time_delta(date: dt.datetime) -> int:
    now = dt.datetime.now(timezone.utc)
    if not isinstance(date, dt.datetime):
        date = parser.parse(date)
    return (now - date).days


def get_eth_addresses_for_cg_coins(file) -> pd.DataFrame:  # pragma: no cover
    with open(file, encoding="utf8") as f:
        data = json.load(f)
        df = pd.DataFrame(data)
        df["ethereum"] = df["platforms"].apply(
            lambda x: x.get("ethereum") if "ethereum" in x else None
        )
        return df


def clean_question_marks(dct: dict) -> None:
    if isinstance(dct, dict):
        for k, v in dct.items():
            if v == "?":
                dct[k] = None


def replace_qm(df: pd.DataFrame) -> pd.DataFrame:
    df.replace({"?": None, " ?": None}, inplace=True)
    return df


def get_url(url: str, elem: BeautifulSoup):  # pragma: no cover
    return url + elem.find("a")["href"]


def clean_row(row: BeautifulSoup) -> list:
    """Helper method that cleans whitespaces and newlines in text returned from BeautifulSoup
    Parameters
    ----------
    row
        text returned from BeautifulSoup find method
    Returns
    -------
        list of elements
    """

    return [r for r in row.text.strip().split("\n") if r not in ["", " "]]


def convert(word: str) -> str:
    return "".join(x.capitalize() or "_" for x in word.split("_") if word.isalpha())


def collateral_auditors_parse(
    args: Any,
) -> Tuple[Any, Any]:  # pragma: no cover
    try:
        if args and args[0] == "N/A":
            collateral = args[1:]
            auditors = []
        else:
            n_elem = int(args[0])
            auditors = args[1 : n_elem + 1]  # noqa: E203
            collateral = args[n_elem + 1 :]  # noqa: E203

        return auditors, collateral
    except ValueError:
        return [], []


def swap_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = list(df.columns)
    cols = [cols[-1]] + cols[:-1]
    df = df[cols]
    return df


def changes_parser(changes: list) -> list:
    if isinstance(changes, list) and len(changes) < 3:
        for _ in range(3 - len(changes)):
            changes.append(None)
    else:
        changes = [None for _ in range(3)]
    return changes


def remove_keys(entries: tuple, the_dict: Dict[Any, Any]) -> None:
    for key in entries:
        if key in the_dict:
            del the_dict[key]


def rename_columns_in_dct(dct: dict, mapper: dict) -> dict:
    return {mapper.get(k, v): v for k, v in dct.items()}


def create_dictionary_with_prefixes(
    columns: Sequence[Any], dct: Dict[Any, Any], constrains: Optional[Tuple] = None
):  # type: ignore
    results = {}
    for column in columns:
        ath_data = dct.get(column, {})
        for element in ath_data:  # type: ignore
            if constrains:  # type: ignore
                if element in constrains:  # type: ignore
                    results[f"{column}_" + element] = ath_data.get(element)  # type: ignore
            else:
                results[f"{column}_" + element] = ath_data.get(element)  # type: ignore
    return results
