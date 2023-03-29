"""eodhd Model"""
__docformat__ = "numpy"

import logging

import numpy as np
import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_EODHD_KEY"])
def get_financials(
    symbol: str, statement: str, quarterly: bool = False, ratios: bool = False
) -> pd.DataFrame:
    """Get ticker financial statements from eodhd

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    statement: str
        Financial statement data to retrieve, can be balance, income or cash
    quarterly:bool
        Flag to get quarterly reports, by default False
    ratios: bool
        Shows percentage change, by default False

    Returns
    -------
    pd.DataFrame
        Balance Sheets or Income Statements or cashflow
    """

    # Note the filing date is over 30 years so will always get as many as allowed
    request_url = (
        "https://eodhistoricaldata.com/api/fundamentals/"
        f"{symbol}?"
        f"api_token={get_current_user().credentials.API_EODHD_KEY}"
        f"&filter=Financials::{statement}"
        f"::{['yearly', 'quarterly'][quarterly]}"
    )

    r = request(request_url)
    if r.status_code != 200:
        console.print(
            "[red]Invalid API Key for EODHD. Please note that for Fundamental Data, a paid plan is required.\n[/red]"
            "Get your API key here: https://eodhistoricaldata.com/r/?ref=869U7F4J and select either the "
            "'Fundamentals Data Feed' or 'ALL-IN-ONE Package'.\n"
        )
        return pd.DataFrame()

    r_json = r.json()

    df_financials = pd.DataFrame(r_json)
    df_financials.drop("date", inplace=True)
    df_financials.drop("filing_date", inplace=True)
    df_financials.drop("currency_symbol", inplace=True)

    df_financials = df_financials.fillna(value=np.nan)
    df_financials = df_financials.dropna(how="all")

    if ratios:
        df_financials = df_financials.iloc[:, :5]
        df_financials = df_financials.replace("-", "0")
        df_financials = df_financials.astype(float)
        df_financials = df_financials.pct_change(axis="columns", periods=-1).fillna(0)
    return df_financials
