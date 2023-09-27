"""FinancialModelingPrep model"""
__docformat__ = "numpy"

import json
import logging
from typing import Any, Dict, List, Union
from urllib.error import HTTPError
from urllib.request import urlopen

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

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
    ticker: str, start_date: str, end_date: str
) -> Union[None, float]:
    """Get stock's price percent change over specified time period.

    Parameters
    ----------
    ticker : str
        Ticker to get information from.
    start: str
        Date from which data is fetched in format YYYY-MM-DD
    end: str
        Date from which data is fetched in format YYYY-MM-DD

    Returns
    -------
    Union[None, float]
        Percent change of closing price over time period
    """
    current_user = get_current_user()
    url = f"""https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?
        from={start_date}&to={end_date}&serietype=line
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
        return None
    data = response.json()

    close_end = data["historical"][0]["close"]
    close_start = data["historical"][-1]["close"]
    pct_change = 100 * (close_end - close_start) / close_start

    return pct_change


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_etf_holdings(ticker: str) -> List[Dict[str, Any]]:
    """This endpoint returns all stocks held by a specific ETF.

    Parameters
    ----------
    ticker : str
        ETF ticker.

    Returns
    -------
    List[Dict[str,any]]
        Info for stock holdings in the ETF.
    """

    current_user = get_current_user()
    url = f"""https://financialmodelingprep.com/api/v3/etf-holder/{ticker}?
        apikey={current_user.credentials.API_KEY_FINANCIALMODELINGPREP}"""
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

    return response.json()


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_holdings_pct_change(
    ticker: str, start_date: str, end_date: str
) -> pd.DataFrame:
    """Calculate percent change for each holding in ETF.

    Parameters
    ----------
    ticker : str
        ETF ticker.

    Returns
    -------
    pd.DataFrame
        Calculated percentage change for each stock in the ETF, in descending order.
    """
    holdings = get_etf_holdings(ticker=ticker)
    if len(holdings) == 0:
        return pd.DataFrame()
    data_list = []
    for stock in holdings:
        if stock["asset"]:
            pct_change = get_stock_price_change(
                ticker=stock["asset"], start_date=start_date, end_date=end_date
            )
            data_list.append(
                {
                    "Ticker": stock["asset"],
                    "Name": stock["name"],
                    "Percent Change": pct_change,
                }
            )
        else:
            data_list.append({"Ticker": "", "Name": stock["name"], "Percent Change": 0})

    df = pd.DataFrame(data_list)
    df.sort_values(by="Percent Change", ascending=False, inplace=True)

    return df
