"""Finviz Model"""
__docformat__ = "numpy"

import pandas as pd

from openbb_terminal.helper_funcs import get_user_agent, request
from openbb_terminal.rich_config import console

timeframe_map = {
    "day": "",
    "week": "w1",
    "month": "w4",
    "3month": "w13",
    "6month": "w26",
    "year": "w52",
    "ytd": "ytd",
}


def get_heatmap_data(timeframe: str) -> pd.DataFrame:
    """Get heatmap data from finviz

    Parameters
    ----------
    timeframe: str
        Timeframe to get performance for

    Returns
    -------
    pd.DataFrame
        Dataframe of tickers, changes and sectors
    """
    if timeframe not in timeframe_map:
        console.print(f"[red]{timeframe} is an invalid timeframe[/red]")
        return pd.DataFrame()
    r = request(
        f"https://finviz.com/api/map_perf.ashx?t=sec&st={timeframe_map[timeframe]}",
        headers={"User-Agent": get_user_agent()},
    )
    r2_json = request(
        "https://finviz.com/maps/sec.json?rev=316",
        headers={"User-Agent": get_user_agent()},
    ).json()
    df_change = pd.DataFrame.from_dict(r.json()["nodes"], orient="index")
    df_change.columns = ["Change"]
    df_change["Change"] = df_change.Change
    changes_dict = df_change.to_dict()

    dfs = pd.DataFrame()
    for sector_dict in r2_json["children"]:
        for industry_dict in sector_dict["children"]:
            temp = pd.DataFrame(industry_dict["children"])
            temp["Sector"] = sector_dict["name"]
            temp["Industry"] = industry_dict["name"]
            dfs = pd.concat([dfs, temp], axis=0).reset_index(drop=True)

    dfs["Change"] = dfs["name"].copy().map(changes_dict["Change"])
    dfs = dfs.rename(columns={"name": "Ticker"})
    return dfs
