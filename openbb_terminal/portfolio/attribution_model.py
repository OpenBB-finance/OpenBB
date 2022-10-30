import os
import json
from datetime import datetime
from datetime import date
import logging

import yfinance as yf
import pandas as pd
from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


SPY_SECTORS_MAP = {
    "S&P 500 Materials (Sector)": "basic_materials",
    "S&P 500 Industrials (Sector)": "industrials",
    "S&P 500 Consumer Discretionary (Sector)": "consumer_cyclical",
    "S&P 500 Consumer Staples (Sector)": "consumer_defensive",
    "S&P 500 Health Care (Sector)": "healthcare",
    "S&P 500 Financials (Sector)": "financial_services",
    "S&P 500 Information Technology (Sector)": "technology",
    "S&P 500 Telecommunication Services (Sector)": "communication_services",
    "S&P 500 Utilities (Sector)": "utilities",
    "S&P 500 Real Estate (Sector)": "realestate",
    "S&P 500 Energy (Sector)": "energy",
}

PF_SECTORS_MAP = {
    "Basic Materials": "S&P 500 Materials (Sector)",
    "Industrials": "S&P 500 Industrials (Sector)",
    "Consumer Cyclical": "S&P 500 Consumer Discretionary (Sector)",
    "Consumer Defensive": "S&P 500 Consumer Staples (Sector)",
    "Healthcare": "S&P 500 Health Care (Sector)",
    "Financial Services": "S&P 500 Financials (Sector)",
    "Technology": "S&P 500 Information Technology (Sector)",
    "Communication Services": "S&P 500 Telecommunication Services (Sector)",
    "Utilities": "S&P 500 Utilities (Sector)",
    "Real Estate": "S&P 500 Real Estate (Sector)",
    "Energy": "S&P 500 Energy (Sector)",
}


@log_start_end(log=logger)
def get_spy_sector_contributions(
    start_date, end_date=date.today()
):  # format like 2015-01-15 (YYYY-MM-DD)
    """
    Fetches sector contributions for the SPY for a fixed period

    Parameters
    ----------
    start_date : str ('yyyy-mm-dd') or datetime.date
        start date for fetching data
    end_date : str ('yyyy-mm-dd') or datetime.date
        end date for fetching data

    Returns
    -------
    contributions : pd.DataFrame
        dataframe with SPY raw contributions
    """

    # Sector Map

    sectors_ticker = "SPY"

    # Load in info
    sp500_tickers_data = get_daily_sector_prices(start_date, end_date)
    weight_data = yf.Ticker("SPY").info["sectorWeightings"]

    # reformat Data
    weights = {"SPY":{}}
    for sector in weight_data:
        weights["SPY"].update(sector)

    # add the sectors + dates + adj close to the dataframe
    records = []
    for sector, data in sp500_tickers_data.items():
        for x in range(0, len(data["sector_data"])):
            record = {
                "sector": sector,
                "date": data["sector_data"].index[x],
                "adj_close": data["sector_data"][x],
                "sector_weight": weights[sectors_ticker][SPY_SECTORS_MAP[sector]],
            }
            records.append(record)

    df = pd.DataFrame(records)

    df["pct_change"] = df.groupby("sector")["adj_close"].pct_change()
    df["contribution"] = df["pct_change"] * df["sector_weight"]

    contributions = df.groupby("sector").agg({"contribution": "sum"})
    contributions["contribution_as_pct"] = (
        contributions["contribution"] / abs(df["contribution"].sum())
    ) * 100

    return contributions


@log_start_end(log=logger)
def get_portfolio_sector_contributions(start_date, portfolio_trades: pd.DataFrame):

    """
    Calculates sector contributions for the loaded portfolio for a fixed period. This is done
    by calculating the daily attribution of each asset (% change in adj_close * Weight in PF)
    then grouping by sector and summing the contribution.

    Parameters
    ----------
    start_data : str ('yyyy-mm-dd') or datetime.date
        start date for calculating contributions from
    portfolio_trades : dataframe
        dataframe of trades in the loaded portfolio

    Returns
    -------
    contributions : pd.DataFrame
        dataframe with portfolio raw contributions
    """

    # Cast portfolio_trades "Date" to datetime64[ns]
    portfolio_trades["Date"] = pd.to_datetime(portfolio_trades["Date"])

    contrib_df = pd.DataFrame()
    asset_tickers = list(portfolio_trades["Ticker"].unique())
    first_price = portfolio_trades["Date"].min()

    price_data = pd.DataFrame(
        yf.download(asset_tickers, start=first_price, progress=False)["Adj Close"]
    )  # returns series when one ticker, hence cast to df

    # if there is only one ticker the column name is "Adj Close" instead of the ticker,
    # if so it needs to be renamed to allow the df multiplication to work
    if len(asset_tickers) == 1:
        price_data = price_data.rename(columns={"Adj Close": asset_tickers[0]})

    price_change = price_data.pct_change()

    # Create a wide dataframe of shares owned on each day
    cumulative_positions = portfolio_trades.copy()
    cumulative_positions["Quantity"] = cumulative_positions.groupby("Ticker")[
        "Quantity"
    ].cumsum()

    cumulative_positions_wide = pd.pivot(
        cumulative_positions, index="Date", columns="Ticker", values="Quantity"
    )
    index = pd.date_range(start=first_price, end=datetime.now(), freq="1D")
    contrib_df = cumulative_positions_wide.reindex(index).ffill(axis=0)

    # Multiply shares by price to get market cap of holdings on day
    contrib_df = contrib_df * price_data

    # turn daily market caps market caps into portfolio weights
    contrib_df = contrib_df.div(contrib_df.sum(axis=1), axis=0)

    # multiply by pct change in price to get daily attribution
    contrib_df = contrib_df * price_change

    # Wide to Long for aggregation
    contrib_df = contrib_df.reset_index()
    contrib_df = contrib_df.rename(columns={"index": "date"})

    # filter passed off desired date here
    contrib_df["date"] = contrib_df["date"].dt.date
    contrib_df = contrib_df[~(contrib_df["date"] < start_date)]

    # melt on datetime field
    contrib_df = pd.melt(contrib_df, id_vars="date")

    # # Get Sectors
    sector_df = (
        portfolio_trades[["Ticker", "Sector"]]
        .groupby("Ticker")
        .agg({"Sector": "min"})
        .reset_index()
    )

    contrib_df = pd.merge(contrib_df, sector_df)
    contrib_df = contrib_df.rename(columns={"value": "contribution"})

    contrib_df = contrib_df.groupby("Sector").agg({"contribution": "sum"})
    contrib_df["contribution_as_pct"] = (
        contrib_df["contribution"] / abs(contrib_df["contribution"].sum())
    ) * 100

    contrib_df = contrib_df.rename(index=PF_SECTORS_MAP)
    contrib_df = contrib_df.reindex(PF_SECTORS_MAP.values())
    contrib_df = contrib_df.fillna(0)

    return contrib_df


@log_start_end(log=logger)
def percentage_attrib_categorizer(bench_df: pd.DataFrame, pf_df: pd.DataFrame):
    """
    Merges S&P500 benchmark attribution and portfolio attribution dataframes and calculates
    excess attribution, attribution ratio, attribution direction and attribution sensitivity.
    Returns attribution results as a proportion of the portfolio.

    for example if a PF returns 1% and the raw attribution of a sector is 0.5% the result for the
    sector is 50%.

    Parameters
    ----------
    bench_df : pd.DataFrame
        S&P500 attribution dataframe
    pf_df : pd.DataFrame
        portfolio attribution dataframe

    Returns
    -------
    result : pd.DataFrame
        dataframe of S&P500 and PF attribution as a proportion
    """

    # rename columns
    bench_df.rename(columns={"contribution_as_pct": "S&P500 [%]"}, inplace=True)
    pf_df.rename(columns={"contribution_as_pct": "Portfolio [%]"}, inplace=True)
    result = bench_df.join(pf_df)

    # 1. Excess Attribution

    result["Excess Attribution"] = result["Portfolio [%]"] - result["S&P500 [%]"]

    # 2. Attribution Ratio

    result["Attribution Ratio"] = result["Portfolio [%]"] / result["S&P500 [%]"]

    # 3. Attribution Direction

    direction = []

    for ratio in result["Attribution Ratio"]:
        if ratio >= 0:
            direction.append("Correlated (+)")
        elif ratio < 0:
            direction.append("Uncorrelated (-)")

    result["Attribution Direction [+/-]"] = direction

    # 4. Attribution Sensetivity

    sensitivity = []

    for ratio in result["Attribution Ratio"]:
        if abs(ratio) > 1.25:
            sensitivity.append("High")
        elif 0.75 <= abs(ratio) <= 1.25:
            sensitivity.append("Normal")
        elif abs(ratio) < 0.75:
            sensitivity.append("Low")

    result["Attribution Sensitivity"] = sensitivity

    return result


@log_start_end(log=logger)
def raw_attrib_categorizer(bench_df, pf_df):
    """
    Merges S&P500 benchmark attribution and portfolio attribution dataframes and calculates
    excess attribution, attribution ratio, attribution direction and attribution sensitivity.
    Returns attribution results as raw values

    for example if a PF returns 1% and the raw attribution of a sector is 0.5% the result for the
    sector is 0.5

    Parameters
    ----------
    bench_df : pd.DataFrame
        S&P500 attribution dataframe
    pf_df : pd.DataFrame
        portfolio attribution dataframe

    Returns
    -------
    result : pd.DataFrame
        dataframe of S&P500 and PF attribution as raw values.
    """

    # rename columns
    bench_df.rename(columns={"contribution": "S&P500"}, inplace=True)
    pf_df.rename(columns={"contribution": "Portfolio"}, inplace=True)
    result = bench_df.join(pf_df)

    # 1. Excess Attribution

    result["Excess Attribution"] = result["Portfolio"] - result["S&P500"]

    # 2. Attribution Ratio

    result["Attribution Ratio"] = result["Portfolio"] / result["S&P500"]

    # 3. Attribution Direction

    direction = []

    for ratio in result["Attribution Ratio"]:
        if ratio >= 0:
            direction.append("Correlated (+)")
        elif ratio < 0:
            direction.append("Uncorrelated (-)")

    result["Attribution Direction [+/-]"] = direction

    # 4. Attribution Sensetivity

    sensitivity = []

    for ratio in result["Attribution Ratio"]:
        if abs(ratio) > 1.25:
            sensitivity.append("High")
        elif 0.75 <= abs(ratio) <= 1.25:
            sensitivity.append("Normal")
        elif abs(ratio) < 0.75:
            sensitivity.append("Low")

    result["Attribution Sensitivity"] = sensitivity

    return result


@log_start_end(log=logger)
def get_daily_sector_prices(start_date, end_date):
    """
    fetches daily sector prices for S&P500 for a fixed time period

    Parameters
    ----------
    start_date : str ('yyyy-mm-dd') or datetime.date
        start date for fetching data
    end_date : str ('yyyy-mm-dd') or datetime.date
        end date for fetching data

    Returns
    -------
    sp500_tickers_data : Dictionary
        dictionary of dataframes with SPY daily sector prices
    """
    # Load tickers from json file
    ticker_json_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "sp500_sectors_and_industries.json"
    )
    sp500_tickers = json.load(open(ticker_json_path))

    sp500_tickers_data = {}  # to store data

    for (
        sector,
        industry_groups,
    ) in sp500_tickers.items():  # iterate thru the sectors in the json file
        # load the data required
        sp500_tickers_data[sector] = {  # builds a dictionary for the sector
            "sector_data": yf.download(
                industry_groups["sector_ticker"],
                start=start_date,
                end=end_date,
                progress=False,
            )["Adj Close"]
        }  # stores the data here

    return sp500_tickers_data
