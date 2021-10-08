"""Portfolio Model"""
__docformat__ = "numpy"

from tabulate import tabulate
import pandas as pd
import yfinance as yf
import gamestonk_terminal.feature_flags as gtff

# pylint: disable=no-member,unsupported-assignment-operation,unsubscriptable-object


def load_portfolio(
    full_path: str,
    sector: bool = False,
    last_price: bool = False,
    show_nan: bool = True,
) -> pd.DataFrame:
    """Loads a portfolio file into a dataframe and adds sector and last price

    Parameters
    ----------
    full_path : str
        Path to portfolio file.
    sector : bool, optional
        Boolean to indicate getting sector from yfinance , by default False
    last_price : bool, optional
        Boolean to indicate getting last price from yfinance, by default False
    show_nan : bool, optional
        Boolean to indicate dropping nan values, by default True

    Returns
    -------
    pd.DataFrame
        Dataframe conataining portfolio
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

    if gtff.USE_TABULATE_DF:
        print(tabulate(df, tablefmt="fancy_grid", headers=df.columns), "\n")
    else:
        print(df.to_string(), "\n")
    return df
