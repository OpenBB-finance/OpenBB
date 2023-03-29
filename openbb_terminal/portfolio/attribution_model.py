"""Attribution Model"""
__docformat__ = "numpy"

import logging
from datetime import date, datetime
from typing import Dict

import pandas as pd
import yfinance as yf

from openbb_terminal.decorators import log_start_end
from openbb_terminal.etf import fmp_model

logger = logging.getLogger(__name__)


SPY_SECTORS_MAP = {
    "S&P 500 Materials (Sector)": "Basic Materials",
    "S&P 500 Industrials (Sector)": "Industrials",
    "S&P 500 Consumer Discretionary (Sector)": "Consumer Cyclical",
    "S&P 500 Consumer Staples (Sector)": "Consumer Defensive",
    "S&P 500 Health Care (Sector)": "Healthcare",
    "S&P 500 Financials (Sector)": "Financial Services",
    "S&P 500 Information Technology (Sector)": "Technology",
    "S&P 500 Telecommunication Services (Sector)": "Communication Services",
    "S&P 500 Utilities (Sector)": "Utilities",
    "S&P 500 Real Estate (Sector)": "Real Estate",
    "S&P 500 Energy (Sector)": "Energy",
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
) -> pd.DataFrame:  # format like 2015-01-15 (YYYY-MM-DD)
    """
    Fetch sector contributions for the SPY for a fixed period

    Parameters
    ----------
    start_date : str ('yyyy-mm-dd') or datetime.date
        start date for fetching data
    end_date : str ('yyyy-mm-dd') or datetime.date
        end date for fetching data

    Returns
    -------
    contributions : pd.DataFrame
        DataFrame with contributions for each sector
    """

    # Sector Map
    sectors_ticker = "SPY"

    # Load in info
    sp500_tickers_data = get_daily_sector_prices(start_date, end_date)
    weight_data = fmp_model.get_etf_sector_weightings(sectors_ticker)

    # reformat Data
    weights: Dict[str, dict] = {"SPY": {}}

    for sector in weight_data:
        weight_formatted = float(sector["weightPercentage"].strip("%")) / 100
        weights[sectors_ticker][sector["sector"]] = weight_formatted

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
def get_portfolio_sector_contributions(
    start_date, portfolio_trades: pd.DataFrame
) -> pd.DataFrame:
    """Calculate sector contributions for the loaded portfolio for a fixed period. This is done
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
        yf.download(asset_tickers, start=first_price, progress=False, ignore_tz=True)[
            "Adj Close"
        ]
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
    contrib_df = contrib_df[~(contrib_df["date"] < start_date.date())]

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
def percentage_attrib_categorizer(
    bench_df: pd.DataFrame, pf_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge S&P500 benchmark attribution and portfolio attribution dataframes and calculates
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

    # using percentage contributions
    bench_df = bench_df.iloc[:, [1]]
    pf_df = pf_df.iloc[:, [1]]

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

    # 4. Attribution Sensitivity

    sensitivity = []

    for ratio in result["Attribution Ratio"]:
        if abs(ratio) > 1.25:
            sensitivity.append("High")
        elif 0.75 <= abs(ratio) <= 1.25:
            sensitivity.append("Normal")
        elif abs(ratio) < 0.75:
            sensitivity.append("Low")

    result["Attribution Sensitivity"] = sensitivity

    # 5. round values before output
    result["S&P500 [%]"] = result["S&P500 [%]"].astype(float).round(2)
    result["Portfolio [%]"] = result["Portfolio [%]"].astype(float).round(2)

    return result


@log_start_end(log=logger)
def raw_attrib_categorizer(bench_df, pf_df) -> pd.DataFrame:
    """Merge S&P500 benchmark attribution and portfolio attribution dataframes and calculates
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

    bench_df = bench_df.iloc[:, [0]]
    pf_df = pf_df.iloc[:, [0]]

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

    # 4. Attribution Sensitivity

    sensitivity = []

    for ratio in result["Attribution Ratio"]:
        if abs(ratio) > 1.25:
            sensitivity.append("High")
        elif 0.75 <= abs(ratio) <= 1.25:
            sensitivity.append("Normal")
        elif abs(ratio) < 0.75:
            sensitivity.append("Low")

    result["Attribution Sensitivity"] = sensitivity

    # 5. round values before output
    result["S&P500"] = result["S&P500"].astype(float).round(4)
    result["Portfolio"] = result["Portfolio"].astype(float).round(4)

    return result


@log_start_end(log=logger)
def get_daily_sector_prices(start_date, end_date) -> dict:
    """Fetch daily sector prices for S&P500 for a fixed time period

    Parameters
    ----------
    start_date : str ('yyyy-mm-dd') or datetime.date
        start date for fetching data
    end_date : str ('yyyy-mm-dd') or datetime.date
        end date for fetching data

    Returns
    -------
    sp500_tickers_data : dict
        dictionary of dataframes with SPY daily sector prices
    """
    # sector ticker information
    sp500_tickers = {
        "S&P 500 Materials (Sector)": "^SP500-15",
        "S&P 500 Industrials (Sector)": "^SP500-20",
        "S&P 500 Consumer Discretionary (Sector)": "^SP500-25",
        "S&P 500 Consumer Staples (Sector)": "^SP500-30",
        "S&P 500 Health Care (Sector)": "^SP500-35",
        "S&P 500 Financials (Sector)": "^SP500-40",
        "S&P 500 Information Technology (Sector)": "^SP500-45",
        "S&P 500 Telecommunication Services (Sector)": "^SP500-50",
        "S&P 500 Utilities (Sector)": "^SP500-55",
        "S&P 500 Real Estate (Sector)": "^SP500-60",
        "S&P 500 Energy (Sector)": "^GSPE",
    }

    sp500_tickers_data = {}  # to store data

    for (
        sector,
        sector_ticker,
    ) in sp500_tickers.items():  # iterate thru the sectors
        # load the data required from yfinance
        sp500_tickers_data[
            sector
        ] = {  # builds a dictionary entry for the sector with adj close data
            "sector_data": yf.download(
                sector_ticker,
                start=start_date,
                end=end_date,
                progress=False,
                ignore_tz=True,
            )["Adj Close"]
        }  # stores the data here

    return sp500_tickers_data
