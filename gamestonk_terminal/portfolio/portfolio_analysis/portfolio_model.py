"""Portfolio Model"""
__docformat__ = "numpy"

import logging

import pandas as pd
import yfinance as yf

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import print_rich_table
from gamestonk_terminal.portfolio.portfolio_analysis import yfinance_model
from gamestonk_terminal.rich_config import console

# pylint: disable=no-member,unsupported-assignment-operation,unsubscriptable-object


logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def load_portfolio(
    full_path: str,
    sector: bool = False,
    country: bool = False,
    last_price: bool = False,
    show_nan: bool = True,
) -> pd.DataFrame:
    """Loads a portfolio file into a dataframe and adds sector and last price

    Parameters
    ----------
    full_path : str
        Path to portfolio file.
    sector : bool, optional
        Boolean to indicate getting sector from yfinance, by default False
    country : bool, optional
        Boolean to indicate getting country from yfinance, by default False
    last_price : bool, optional
        Boolean to indicate getting last price from yfinance, by default False
    show_nan : bool, optional
        Boolean to indicate dropping nan values, by default True

    Returns
    -------
    pd.DataFrame
        Dataframe containing portfolio
    """
    if full_path.endswith(".csv"):
        df = pd.read_csv(full_path)

    elif full_path.endswith(".json"):
        df = pd.read_json(full_path)

    elif full_path.endswith(".xlsx"):
        df = pd.read_excel(full_path, engine="openpyxl")

    if sector:
        df["sector"] = df.apply(
            lambda row: yf.Ticker(row.Ticker).info["sector"]
            if "sector" in yf.Ticker(row.Ticker).info.keys()
            else "yf Other",
            axis=1,
        )

    if country:
        country_dict = {
            tick: yfinance_model.get_country(tick) for tick in df.Ticker.unique()
        }
        df["Country"] = df["Ticker"].map(country_dict)

    if last_price:
        df["last_price"] = df.apply(
            lambda row: yf.Ticker(row.Ticker)
            .history(period="1d")["Close"][-1]
            .round(2),
            axis=1,
        )
        df["value"] = df["Shares"] * df["last_price"]

    if not show_nan:
        df = df.dropna(axis=1)

    print_rich_table(df, title="Portfolio", headers=list(df.columns))
    console.print("")
    return df
