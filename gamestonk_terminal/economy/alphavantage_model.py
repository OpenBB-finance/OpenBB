""" Alpha Vantage Model """
__docformat__ = "numpy"

import logging

import pandas as pd
import requests
from alpha_vantage.sectorperformance import SectorPerformances

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import get_user_agent

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
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


@log_start_end(log=logger)
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


@log_start_end(log=logger)
def get_gdp_capita() -> pd.DataFrame:
    """Real GDP per Capita for United States

    Returns
    -------
    pd.DataFrame
        DataFrame of GDP per Capita
    """
    url = f"https://www.alphavantage.co/query?function=REAL_GDP_PER_CAPITA&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    r = requests.get(url, headers={"User-Agent": get_user_agent()})
    if r.status_code != 200:
        return pd.DataFrame()
    data = pd.DataFrame(r.json()["data"])
    data["date"] = pd.to_datetime(data["date"])
    data["GDP"] = data["value"].astype(float)
    data = data.drop(columns=["value"])
    return data


@log_start_end(log=logger)
def get_inflation() -> pd.DataFrame:
    """Get historical Inflation for United States from AlphaVantage

    Returns
    -------
    pd.DataFrame
        DataFrame of inflation rates
    """
    url = f"https://www.alphavantage.co/query?function=INFLATION&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    r = requests.get(url, headers={"User-Agent": get_user_agent()})
    if r.status_code != 200:
        return pd.DataFrame()
    data = pd.DataFrame(r.json()["data"])
    data["date"] = pd.to_datetime(data["date"])
    data["Inflation"] = data["value"].astype(float)
    data = data.drop(columns=["value"])

    return data


@log_start_end(log=logger)
def get_cpi(interval: str) -> pd.DataFrame:
    """Get Consumer Price Index from Alpha Vantage

    Parameters
    ----------
    interval : str
        Interval for data.  Either "m" or "s" for monthly or semiannual

    Returns
    -------
    pd.DataFrame
        Dataframe of CPI
    """
    s_interval = "semiannual" if interval == "s" else "monthly"
    url = f"https://www.alphavantage.co/query?function=CPI&interval={s_interval}&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    r = requests.get(url, headers={"User-Agent": get_user_agent()})

    if r.status_code != 200:
        return pd.DataFrame()

    data = pd.DataFrame(r.json()["data"])
    data["date"] = pd.to_datetime(data["date"])
    data["CPI"] = data["value"].astype(float)
    data = data.drop(columns=["value"])

    return data


@log_start_end(log=logger)
def get_treasury_yield(interval: str, maturity: str) -> pd.DataFrame:
    """Get historical yield for a given maturity

    Parameters
    ----------
    interval : str
        Interval for data.  Can be "d","w","m" for daily, weekly or monthly
    maturity : str
        Maturity timeline.  Can be "3mo","5y","10y" or "30y"

    Returns
    -------
    pd.DataFrame
        Dataframe of historical yields
    """
    d_interval = {"d": "daily", "w": "weekly", "m": "monthly"}
    d_maturity = {"3m": "3month", "5y": "5year", "10y": "10year", "30y": "30year"}

    url = f"https://www.alphavantage.co/query?function=TREASURY_YIELD&interval={d_interval[interval]}&ma"
    url += f"turity={d_maturity[maturity]}&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    r = requests.get(url, headers={"User-Agent": get_user_agent()})
    if r.status_code != 200:
        return pd.DataFrame()

    data = pd.DataFrame(r.json()["data"])
    data["date"] = pd.to_datetime(data["date"])
    data["Yield"] = data["value"].astype(float)
    data = data.drop(columns=["value"])

    return data


@log_start_end(log=logger)
def get_unemployment() -> pd.DataFrame:
    """Get historical unemployment for United States

    Returns
    -------
    pd.DataFrame
        Dataframe of historical yields
    """
    url = f"https://www.alphavantage.co/query?function=UNEMPLOYMENT&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    r = requests.get(url, headers={"User-Agent": get_user_agent()})
    if r.status_code != 200:
        return pd.DataFrame()
    data = pd.DataFrame(r.json()["data"])
    data["date"] = pd.to_datetime(data["date"])
    data["unemp"] = data["value"].astype(float)
    data = data.drop(columns=["value"])
    return data
