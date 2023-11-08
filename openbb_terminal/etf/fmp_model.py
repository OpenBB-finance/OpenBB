"""FinancialModelingPrep model"""
__docformat__ = "numpy"

import json
import logging
from typing import Any, Dict, List
from urllib.error import HTTPError
from urllib.request import urlopen

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console, optional_rich_track

logger = logging.getLogger(__name__)

# pylint: disable=consider-using-with


@log_start_end(log=logger)
def get_etf_sector_weightings(name: str) -> Dict:
    """Return sector weightings allocation of ETF. [Source: FinancialModelingPrep]

    Parameters
    ----------
    name: str
        ETF name

    Returns
    -------
    Dict[str, Any]
        Dictionary with sector weightings allocation
    """
    try:
        response = urlopen(  # noqa: S310
            "https://financialmodelingprep.com/api/v3/etf-sector-weightings/"
            f"{name}?apikey={get_current_user().credentials.API_KEY_FINANCIALMODELINGPREP}"
        )
        data = json.loads(response.read().decode("utf-8"))
    except HTTPError:
        console.print(
            "This endpoint is only for premium members. Please visit the subscription page to upgrade the "
            "plan (Starter or higher) at https://financialmodelingprep.com/developer/docs/pricing"
        )
        return dict()

    if "Error Message" in data:
        raise ValueError(data["Error Message"])

    return data


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_stock_price_change(
    tickers: List[str], start_date: str, end_date: str
) -> Dict[str, float]:
    """Get stock's price percent change over specified time period.

    Parameters
    ----------
    tickers : List[str]
        Ticker(s) to get information for.
    start: str
        Date from which data is fetched in format YYYY-MM-DD
    end: str
        Date from which data is fetched in format YYYY-MM-DD

    Returns
    -------
    Dict[str, float]
        Percent change of closing price over time period, or dictionary of ticker, change pairs.
    """
    tickers_tracker = optional_rich_track(
        tickers, False, "Gathering stock prices", len(tickers)
    )
    current_user = get_current_user()
    data_aggregate = dict()

    for tick in tickers_tracker:
        tickers_req = str(tick) + ","
        for _ in range(4):
            try:
                _tick = next(tickers_tracker)
                tickers_req += _tick + ","
            except StopIteration:
                break

        url = f"""https://financialmodelingprep.com/api/v3/historical-price-full/{tickers_req}?\
from={start_date}&to={end_date}&serietype=line\
&apikey={current_user.credentials.API_KEY_FINANCIALMODELINGPREP}"""

        response = request(url)
        if response.status_code != 200 or "Error Message" in response.json():
            message = f"Error, Status Code: {response.status_code}."
            message = (
                message
                if "Error Message" not in response.json()
                else message + "\n" + response.json()["Error Message"] + ".\n"
            )
            console.print(message)
            return dict()

        data = response.json()
        stock_list = data
        if "historicalStockList" in data:
            stock_list = data["historicalStockList"]

        for stock in stock_list:
            close_end = stock["historical"][0]["close"]
            close_start = stock["historical"][-1]["close"]
            pct_change = 100 * (close_end - close_start) / close_start
            data_aggregate[stock["symbol"]] = pct_change

    return data_aggregate


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_etf_holdings(ticker: str, limit: int = 10) -> List[Dict[str, Any]]:
    """This endpoint returns all stocks held by a specific ETF.

    Parameters
    ----------
    ticker : str
        ETF ticker.
    limit: int
        Limit amount of stocks to return. FMP returns data
        by descending weighting.

    Returns
    -------
    List[Dict[str,any]]
        Info for stock holdings in the ETF.
    """

    current_user = get_current_user()
    url = f"""https://financialmodelingprep.com/api/v3/etf-holder/{ticker}\
?apikey={current_user.credentials.API_KEY_FINANCIALMODELINGPREP}"""
    response = request(url)
    if response.status_code != 200 or "Error Message" in response.json():
        message = f"Error, Status Code: {response.status_code}."
        message = (
            message
            if "Error Message" not in response.json()
            else message + "\n" + response.json()["Error Message"] + ".\n"
        )
        console.print(message)
        return []

    return response.json()[0:limit]


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_holdings_pct_change(
    ticker: str,
    start_date: str,
    end_date: str,
    limit: int = 10,
) -> pd.DataFrame:
    """Calculate percent change for each holding in ETF.

    Parameters
    ----------
    ticker : str
        ETF ticker.
    limit: int
        Limit amount of stocks to return. FMP returns data
        by descending weighting.

    Returns
    -------
    pd.DataFrame
        Calculated percentage change for each stock in the ETF, in descending order.
    """

    df = pd.DataFrame(columns=["Ticker", "Name", "Percent Change"], data=[])
    holdings = get_etf_holdings(ticker, limit)
    tickers = []
    for stock in holdings:
        tickers.append(stock.get("asset", " "))

    pct_changes = get_stock_price_change(tickers, start_date, end_date)

    for stock in holdings:
        pct_change = pct_changes.get(stock["asset"], 0)
        if pct_change == 0:
            console.print(
                f"""Percent change not found for: {stock["asset"]}: {stock["name"]}"""
            )
        new_df = pd.DataFrame(
            {
                "Ticker": stock["asset"],
                "Name": stock["name"],
                "Percent Change": pct_changes.get(stock["asset"], 0),
            },
            index=[0],
        )

        df = pd.concat([df, new_df], ignore_index=True)

    sorted_df = df.sort_values(by="Percent Change", ascending=False, inplace=False)

    return sorted_df
