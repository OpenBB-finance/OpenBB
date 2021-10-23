"""Portfolio Model"""
__docformat__ = "numpy"

import os

import pandas as pd

from gamestonk_terminal.portfolio import portfolio_view

# pylint: disable=E1136
# pylint: disable=unsupported-assignment-operation


def save_df(df: pd.DataFrame, name: str) -> None:
    """
    Saves the portfolio as a csv

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to be saved
    name : str
        The name of the string
    """
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.abspath(os.path.join(path, "portfolios", name))
    if ".csv" in name:
        df.to_csv(path, index=False)
    elif ".json" in name:
        df.to_json(path, index=False)
    elif ".xlsx" in name:
        df = df.to_excel(path, index=False, engine="openpyxl")


def load_df(name: str) -> pd.DataFrame:
    """
    Saves the portfolio as a csv

    Parameters
    ----------
    name : str
        The name of the string

    Returns
    ----------
    data : pd.DataFrame
        A DataFrame with historical trading information
    """
    if ".csv" not in name and ".xlsx" not in name and ".json" not in name:
        print(
            "Please submit as 'filename.filetype' with filetype being csv, xlsx, or json\n"
        )
        return pd.DataFrame()

    try:
        if ".csv" in name:
            df = pd.read_csv(f"gamestonk_terminal/portfolio/portfolios/{name}")
        elif ".json" in name:
            df = pd.read_json(f"gamestonk_terminal/portfolio/portfolios/{name}")
        elif ".xlsx" in name:
            df = pd.read_excel(
                f"gamestonk_terminal/portfolio/portfolios/{name}", engine="openpyxl"
            )

        df.index = list(range(0, len(df.values)))
        df["Name"] = df["Name"].str.lower()
        df["Type"] = df["Type"].str.lower()
        df["Date"] = pd.to_datetime(df["Date"], format="%Y/%m/%d")
        return df
    except FileNotFoundError:
        portfolio_view.load_info()
        return pd.DataFrame()
