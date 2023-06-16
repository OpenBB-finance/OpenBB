"""Quiverquant Model"""
__docformat__ = "numpy"

# Provided by Quiverquant guys to GST users
import logging
import textwrap
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

API_QUIVERQUANT_KEY = (
    "5cd2a65e96d0486efbe926a7cdbc1e8d8ab6c7b3"  # pragma: allowlist secret
)


@log_start_end(log=logger)
def get_government_trading(
    gov_type: str = "congress", symbol: str = ""
) -> pd.DataFrame:
    """Returns the most recent transactions by members of government

    Parameters
    ----------
    gov_type: str
        Type of government data between:
        'congress', 'senate', 'house', 'contracts', 'quarter-contracts' and 'corporate-lobbying'
    symbol : str
        Ticker symbol to get congress trading data from

    Returns
    -------
    pd.DataFrame
        Most recent transactions by members of U.S. Congress
    """
    if gov_type == "congress":
        if symbol:
            url = (
                f"https://api.quiverquant.com/beta/historical/congresstrading/{symbol}"
            )
        else:
            url = "https://api.quiverquant.com/beta/live/congresstrading"

    elif gov_type.lower() == "senate":
        if symbol:
            url = f"https://api.quiverquant.com/beta/historical/senatetrading/{symbol}"
        else:
            url = "https://api.quiverquant.com/beta/live/senatetrading"

    elif gov_type.lower() == "house":
        if symbol:
            url = f"https://api.quiverquant.com/beta/historical/housetrading/{symbol}"
        else:
            url = "https://api.quiverquant.com/beta/live/housetrading"

    elif gov_type.lower() == "contracts":
        if symbol:
            url = (
                f"https://api.quiverquant.com/beta/historical/govcontractsall/{symbol}"
            )
        else:
            url = "https://api.quiverquant.com/beta/live/govcontractsall"

    elif gov_type.lower() == "quarter-contracts":
        if symbol:
            url = f"https://api.quiverquant.com/beta/historical/govcontracts/{symbol}"
        else:
            url = "https://api.quiverquant.com/beta/live/govcontracts"

    elif gov_type.lower() == "corporate-lobbying":
        if symbol:
            url = f"https://api.quiverquant.com/beta/historical/lobbying/{symbol}"
        else:
            url = "https://api.quiverquant.com/beta/live/lobbying"

    else:
        return pd.DataFrame()
    headers = {
        "accept": "application/json",
        "X-CSRFToken": "TyTJwjuEC7VV7mOqZ622haRaaUr0x0Ng4nrwSRFKQs7vdoBcJlK9qjAS69ghzhFu",  # pragma: allowlist secret
        "Authorization": f"Token {API_QUIVERQUANT_KEY}",
    }
    response = request(url, headers=headers, timeout=10)  # Default timeout causes error
    if response.status_code == 200:
        if gov_type in ["congress", "senate", "house"]:
            return pd.DataFrame(response.json()).rename(
                columns={"Date": "TransactionDate", "Senator": "Representative"}
            )
        return pd.DataFrame(response.json())
    return pd.DataFrame()


@log_start_end(log=logger)
def get_contracts(
    symbol: str,
    past_transaction_days: int = 10,
) -> pd.DataFrame:
    """Get government contracts for ticker [Source: quiverquant.com]

    Parameters
    ----------
    symbol: str
        Ticker to get congress trading data from
    past_transaction_days: int
        Number of days to get transactions for

    Returns
    -------
    pd.DataFrame
        Most recent transactions by members of U.S. Congress
    """
    df_contracts = get_government_trading("contracts", symbol)

    if df_contracts.empty:
        console.print("No government contracts found\n")
        return pd.DataFrame()

    df_contracts["Date"] = pd.to_datetime(df_contracts["Date"]).dt.date

    df_contracts = df_contracts[
        df_contracts["Date"].isin(df_contracts["Date"].unique()[:past_transaction_days])
    ]

    df_contracts.drop_duplicates(inplace=True)

    return df_contracts


@log_start_end(log=logger)
def get_hist_contracts(
    symbol: str,
) -> pd.DataFrame:
    """Get historical quarterly government contracts [Source: quiverquant.com]

    Parameters
    ----------
    symbol: str
        Ticker symbol to get congress trading data from

    Returns
    -------
    pd.DataFrame
        Historical quarterly government contracts
    """
    df_contracts = get_government_trading("quarter-contracts", symbol=symbol)

    if df_contracts.empty:
        console.print("No quarterly government contracts found\n")
        return pd.DataFrame()

    return df_contracts


@log_start_end(log=logger)
def get_last_government(
    gov_type: str = "congress", limit: int = -1, representative: str = ""
) -> pd.DataFrame:
    """Get last government trading [Source: quiverquant.com]

    Parameters
    ----------
    gov_type: str
        Type of government data between: congress, senate and house
    limit: int
        Number of days to look back
    representative: str
        Specific representative to look at

    Returns
    -------
    pd.DataFrame
        Last government trading
    """
    df_gov = get_government_trading(gov_type)

    if df_gov.empty:
        return pd.DataFrame()

    df_gov = df_gov[
        df_gov["TransactionDate"].isin(df_gov["TransactionDate"].unique()[:limit])
    ]

    if gov_type == "congress":
        df_gov = df_gov[
            [
                "TransactionDate",
                "Ticker",
                "Representative",
                "Transaction",
                "Range",
                "House",
                "ReportDate",
            ]
        ].rename(
            columns={
                "TransactionDate": "Transaction Date",
                "ReportDate": "Report Date",
            }
        )
    else:
        df_gov = df_gov[
            [
                "TransactionDate",
                "Ticker",
                "Representative",
                "Transaction",
                "Range",
            ]
        ].rename(columns={"TransactionDate": "Transaction Date"})

    if representative:
        df_gov = df_gov[df_gov["Representative"].str.split().str[0] == representative]

    return df_gov


@log_start_end(log=logger)
def get_government_buys(
    gov_type: str = "congress",
    past_transactions_months: int = 6,
) -> pd.DataFrame:
    """Get top buy government trading [Source: quiverquant.com]

    Parameters
    ----------
    gov_type: str
        Type of government data between: congress, senate and house
    past_transactions_months: int
        Number of months to get trading for

    Returns
    -------
    pd.DataFrame
        DataFrame of top government buy trading
    """
    df_gov = get_government_trading(gov_type)
    if df_gov.empty:
        return pd.DataFrame()

    df_gov = df_gov.sort_values("TransactionDate", ascending=False)
    start_date = datetime.now() - timedelta(days=past_transactions_months * 30)

    df_gov["TransactionDate"] = pd.to_datetime(df_gov["TransactionDate"])

    df_gov = df_gov[df_gov["TransactionDate"] > start_date].dropna(axis=1)

    # Catch bug where error shown for purchase of >5,000,000
    df_gov["Range"] = df_gov["Range"].apply(
        lambda x: "$5,000,001-$5,000,001" if x == ">$5,000,000" else x
    )
    df_gov["min"] = df_gov["Range"].apply(
        lambda x: x.split("-")[0].strip("$").replace(",", "").strip()
    )
    df_gov["max"] = df_gov["Range"].apply(
        lambda x: x.split("-")[1].replace(",", "").strip().strip("$")
        if "-" in x
        else x.strip("$").replace(",", "")
    )
    df_gov["lower"] = df_gov[["min", "max", "Transaction"]].apply(
        lambda x: float(x["min"])
        if x["Transaction"] == "Purchase"
        else -float(x["max"]),
        axis=1,
    )
    df_gov["upper"] = df_gov[["min", "max", "Transaction"]].apply(
        lambda x: float(x["max"])
        if x["Transaction"] == "Purchase"
        else -float(x["min"]),
        axis=1,
    )

    df_gov = df_gov.sort_values("TransactionDate", ascending=True)

    return df_gov


@log_start_end(log=logger)
def get_government_sells(
    gov_type: str = "congress",
    past_transactions_months: int = 6,
) -> pd.DataFrame:
    """Get top sell government trading [Source: quiverquant.com]

    Parameters
    ----------
    gov_type: str
        Type of government data between: congress, senate and house
    past_transactions_months: int
        Number of months to get trading for

    Returns
    -------
    pd.DataFrame
        DataFrame of top government sell trading
    """
    df_gov = get_government_trading(gov_type)

    if df_gov.empty:
        return pd.DataFrame()

    df_gov = df_gov.sort_values("TransactionDate", ascending=False)

    start_date = datetime.now() - timedelta(days=past_transactions_months * 30)

    df_gov["TransactionDate"] = pd.to_datetime(df_gov["TransactionDate"])

    df_gov = df_gov[df_gov["TransactionDate"] > start_date].dropna()
    df_gov["Range"] = df_gov["Range"].apply(
        lambda x: "$5,000,001-$5,000,001" if x == ">$5,000,000" else x
    )
    df_gov["min"] = df_gov["Range"].apply(
        lambda x: x.split("-")[0]
        .strip("$")
        .replace(",", "")
        .strip()
        .replace(">$", "")
        .strip()
    )
    df_gov["max"] = df_gov["Range"].apply(
        lambda x: x.split("-")[1]
        .replace(",", "")
        .strip()
        .strip("$")
        .replace(">$", "")
        .strip()
        if "-" in x
        else x.strip("$").replace(",", "").replace(">$", "").strip()
    )

    df_gov["lower"] = df_gov[["min", "max", "Transaction"]].apply(
        lambda x: float(x["min"])
        if x["Transaction"] == "Purchase"
        else -float(x["max"]),
        axis=1,
    )
    df_gov["upper"] = df_gov[["min", "max", "Transaction"]].apply(
        lambda x: float(x["max"])
        if x["Transaction"] == "Purchase"
        else -float(x["min"]),
        axis=1,
    )

    df_gov = df_gov.sort_values("TransactionDate", ascending=True)

    return df_gov


@log_start_end(log=logger)
def get_top_lobbying() -> pd.DataFrame:
    """Corporate lobbying details

    Returns
    -------
    pd.DataFrame
        DataFrame of top corporate lobbying

    """
    df_lobbying = get_government_trading("corporate-lobbying")

    if df_lobbying.empty:
        console.print("No corporate lobbying found\n")
        return pd.DataFrame()

    return df_lobbying


@log_start_end(log=logger)
def get_last_contracts(
    past_transaction_days: int = 2,
) -> pd.DataFrame:
    """Get last government contracts [Source: quiverquant.com]

    Parameters
    ----------
    past_transaction_days: int
        Number of days to look back

    Returns
    -------
    pd.DataFrame
        DataFrame of government contracts
    """
    df_contracts = get_government_trading("contracts")

    if df_contracts.empty:
        console.print("No government contracts found\n")
        return pd.DataFrame()

    df_contracts.sort_values("Date", ascending=False)

    df_contracts["Date"] = pd.to_datetime(df_contracts["Date"])

    df_contracts.drop_duplicates(inplace=True)

    df_contracts = df_contracts[
        df_contracts["Date"].isin(df_contracts["Date"].unique()[:past_transaction_days])
    ]

    df_contracts = df_contracts[["Date", "Ticker", "Amount", "Description", "Agency"]]
    df_contracts["Description"] = df_contracts["Description"].apply(
        lambda x: "\n".join(textwrap.wrap(x, 50)) if x is not None else None
    )

    return df_contracts


def get_cleaned_government_trading(
    symbol: str,
    gov_type: str = "congress",
    past_transactions_months: int = 6,
) -> pd.DataFrame:
    """Government trading for specific ticker [Source: quiverquant.com]

    Parameters
    ----------
    symbol: str
        Ticker symbol to get congress trading data from
    gov_type: str
        Type of government data between: congress, senate and house
    past_transactions_months: int
        Number of months to get transactions for

    Returns
    -------
    pd.DataFrame
        DataFrame of tickers government trading
    """
    df_gov = get_government_trading(gov_type, symbol)

    if df_gov.empty:
        return pd.DataFrame()

    df_gov = df_gov.sort_values("TransactionDate", ascending=False)

    start_date = datetime.now() - timedelta(days=past_transactions_months * 30)

    df_gov["TransactionDate"] = pd.to_datetime(df_gov["TransactionDate"])

    df_gov = df_gov[df_gov["TransactionDate"] > start_date]

    if df_gov.empty:
        console.print(f"No recent {gov_type} trading data found\n")
        return pd.DataFrame()

    df_gov["min"] = df_gov["Range"].apply(
        lambda x: x.split("-")[0].strip("$").replace(",", "").strip()
    )
    df_gov["max"] = df_gov["Range"].apply(
        lambda x: x.split("-")[1].replace(",", "").strip().strip("$")
        if "-" in x
        else x.strip("$").replace(",", "").split("\n")[0]
    )

    df_gov["lower"] = df_gov[["min", "max", "Transaction"]].apply(
        lambda x: int(float(x["min"]))
        if x["Transaction"] == "Purchase"
        else -int(float(x["max"])),
        axis=1,
    )
    df_gov["upper"] = df_gov[["min", "max", "Transaction"]].apply(
        lambda x: int(float(x["max"]))
        if x["Transaction"] == "Purchase"
        else -1 * int(float(x["min"])),
        axis=1,
    )

    df_gov = df_gov.sort_values("TransactionDate", ascending=True)

    return df_gov


@log_start_end(log=logger)
def get_qtr_contracts(analysis: str = "total", limit: int = 5) -> pd.DataFrame:
    """Analyzes quarterly contracts by ticker

    Parameters
    ----------
    analysis : str
        How to analyze.  Either gives total amount or sorts by high/low momentum.
    limit : int, optional
        Number to return, by default 5

    Returns
    -------
    pd.DataFrame
        Dataframe with tickers and total amount if total selected.
    """
    df_contracts = get_government_trading("quarter-contracts")

    if df_contracts.empty:
        console.print("No quarterly government contracts found\n")
        return pd.DataFrame()

    if analysis == "total":
        df_groups = (
            df_contracts.groupby("Ticker")["Amount"].sum().sort_values(ascending=False)
        )
        return pd.DataFrame(df_groups[:limit])

    if analysis in {"upmom", "downmom"}:
        coef = []
        df_groups = df_contracts.groupby("Ticker")
        for tick, data in df_groups:
            regr = LinearRegression()

            amounts = data.sort_values(by=["Year", "Qtr"])["Amount"].values

            # Train the model using the training sets
            regr.fit(np.arange(0, len(amounts)).reshape(-1, 1), amounts)

            coef.append({"Ticker": tick, "Coef": regr.coef_[0]})

        return pd.DataFrame(coef).sort_values(
            by=["Coef"], ascending=analysis == "downmom"
        )["Ticker"][:limit]

    return pd.DataFrame()


@log_start_end(log=logger)
def get_lobbying(symbol: str, limit: int = 10) -> pd.DataFrame:
    """Corporate lobbying details

    Parameters
    ----------
    symbol: str
        Ticker symbol to get corporate lobbying data from
    limit: int
        Number of events to show

    Returns
    -------
    pd.DataFrame
        Dataframe with corporate lobbying data
    """
    df_lobbying = get_government_trading("corporate-lobbying", symbol=symbol)

    if df_lobbying.empty:
        console.print("No corporate lobbying found\n")
        return pd.DataFrame()

    df_lobbying.sort_values(by=["Date"], ascending=False)

    return df_lobbying.head(limit)
