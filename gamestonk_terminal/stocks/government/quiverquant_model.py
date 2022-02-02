"""Quiverquant Model"""
__docformat__ = "numpy"

# Provided by Quiverquant guys to GST users
import logging

import numpy as np
import pandas as pd
import requests
from sklearn.linear_model import LinearRegression

from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

API_QUIVERQUANT_KEY = (
    "5cd2a65e96d0486efbe926a7cdbc1e8d8ab6c7b3"  # pragma: allowlist secret
)


@log_start_end(log=logger)
def get_government_trading(gov_type: str, ticker: str = "") -> pd.DataFrame:
    """Returns the most recent transactions by members of government

    Parameters
    ----------
    gov_type: str
        Type of government data between:
        'congress', 'senate', 'house', 'contracts', 'quarter-contracts' and 'corporate-lobbying'
    ticker : str
        Ticker to get congress trading data from

    Returns
    -------
    pd.DataFrame
        Most recent transactions by members of U.S. Congress
    """
    if gov_type == "congress":
        if ticker:
            url = (
                f"https://api.quiverquant.com/beta/historical/congresstrading/{ticker}"
            )
        else:
            url = "https://api.quiverquant.com/beta/live/congresstrading"

    elif gov_type.lower() == "senate":
        if ticker:
            url = f"https://api.quiverquant.com/beta/historical/senatetrading/{ticker}"
        else:
            url = "https://api.quiverquant.com/beta/live/senatetrading"

    elif gov_type.lower() == "house":
        if ticker:
            url = f"https://api.quiverquant.com/beta/historical/housetrading/{ticker}"
        else:
            url = "https://api.quiverquant.com/beta/live/housetrading"

    elif gov_type.lower() == "contracts":
        if ticker:
            url = (
                f"https://api.quiverquant.com/beta/historical/govcontractsall/{ticker}"
            )
        else:
            url = "https://api.quiverquant.com/beta/live/govcontractsall"

    elif gov_type.lower() == "quarter-contracts":
        if ticker:
            url = f"https://api.quiverquant.com/beta/historical/govcontracts/{ticker}"
        else:
            url = "https://api.quiverquant.com/beta/live/govcontracts"

    elif gov_type.lower() == "corporate-lobbying":
        if ticker:
            url = f"https://api.quiverquant.com/beta/historical/lobbying/{ticker}"
        else:
            url = "https://api.quiverquant.com/beta/live/lobbying"

    else:
        return pd.DataFrame()

    headers = {
        "accept": "application/json",
        "X-CSRFToken": "TyTJwjuEC7VV7mOqZ622haRaaUr0x0Ng4nrwSRFKQs7vdoBcJlK9qjAS69ghzhFu",  # pragma: allowlist secret
        "Authorization": f"Token {API_QUIVERQUANT_KEY}",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        if gov_type in ["congress", "senate", "house"]:
            return pd.DataFrame(response.json()).rename(
                columns={"Date": "TransactionDate", "Senator": "Representative"}
            )
        return pd.DataFrame(response.json())

    return pd.DataFrame()


@log_start_end(log=logger)
def analyze_qtr_contracts(analysis: str, num: int = 5) -> pd.DataFrame:
    """Analyzes quarterly contracts by ticker

    Parameters
    ----------
    analysis : str
        How to analyze.  Either gives total amount or sorts by high/low momentum.
    num : int, optional
        Number to return, by default 5

    Returns
    -------
    pd.DataFrame
        Dataframe with tickers and total amount if total selected.
    """
    df_contracts = get_government_trading("quarter-contracts")

    if analysis == "total":
        df_groups = (
            df_contracts.groupby("Ticker")["Amount"].sum().sort_values(ascending=False)
        )
        return pd.DataFrame(df_groups[:num])

    if analysis in {"upmom", "downmom"}:
        df_coef = pd.DataFrame(columns=["Ticker", "Coef"])
        df_groups = df_contracts.groupby("Ticker")
        for tick, data in df_groups:
            regr = LinearRegression()

            amounts = data.sort_values(by=["Year", "Qtr"])["Amount"].values

            # Train the model using the training sets
            regr.fit(np.arange(0, len(amounts)).reshape(-1, 1), amounts)

            df_coef = df_coef.append(
                {"Ticker": tick, "Coef": regr.coef_[0]}, ignore_index=True
            )

        return df_coef.sort_values(by=["Coef"], ascending=analysis == "downmom")[
            "Ticker"
        ][:num]
    return pd.DataFrame()
