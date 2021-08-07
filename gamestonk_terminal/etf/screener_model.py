"""Screener model"""
__docformat__ = "numpy"

import configparser
import pandas as pd


def etf_screener():
    """Screens the etfs pulled from my repo, which is updated hourly through the market day

    Returns
    ----------
    df : pd.DataFrame
        Screened dataframe
    """

    # pylint: disable=no-member

    df = pd.read_csv(
        "https://raw.githubusercontent.com/jmaslek/etf_scraper/main/etf_overviews.csv",
        index_col=0,
    )
    print("ETFs downloaded\n")

    cf = configparser.ConfigParser()
    cf.read("gamestonk_terminal/etf/etf_config.ini")
    cols = cf.sections()

    for col in cols:
        if cf[col]["Min"] != "None":
            query = f"{col} > {cf[col]['Min']} "
            df = df.query(query)
        if cf[col]["Max"] != "None":
            query = f"{col} < {cf[col]['Max']} "
            df = df.query(query)

    return df
