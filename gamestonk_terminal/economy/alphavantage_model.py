""" Alpha Vantage Model """
__docformat__ = "numpy"

import pandas as pd
from alpha_vantage.sectorperformance import SectorPerformances
import requests

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import get_user_agent


def get_sector_data() -> pd.DataFrame:
    """Get real-time performance sector data

    Returns
    ----------
    df_sectors : pd.Dataframe
        Real-time performance data
    """
    sector_perf = SectorPerformances(
        key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas"
    )
    # pylint: disable=unbalanced-tuple-unpacking
    df_sectors, _ = sector_perf.get_sector()
    return df_sectors


def get_real_gdp(interval: str = "a") -> pd.DataFrame:
    """Get annual or quarterly Real GDP for US

    Parameters
    ----------
    interval : str, optional
        Interval for GDP, by default "a" for annual
    Returns
    -------
    pd.DataFrame
        Dataframe of GDP
    """
    s_interval = "quarterly" if interval == "q" else "annual"
    url = f"https://www.alphavantage.co/query?function=REAL_GDP&interval={s_interval}&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    r = requests.get(url, headers={"User-Agent": get_user_agent()})

    if r.status_code != 200:
        return pd.DataFrame()

    data = pd.DataFrame(r.json()["data"])
    data["date"] = pd.to_datetime(data["date"])
    data["GDP"] = data["value"].astype(float)
    data = data.drop(columns=["value"])
    return data
