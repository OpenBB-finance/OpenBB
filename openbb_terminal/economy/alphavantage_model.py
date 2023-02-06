""" Alpha Vantage Model """
__docformat__ = "numpy"

import logging

import pandas as pd
from alpha_vantage.sectorperformance import SectorPerformances

from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_sector_data() -> pd.DataFrame:
    """Get real-time performance sector data

    Returns
    -------
    df_sectors : pd.Dataframe
        Real-time performance data
    """
    sector_perf = SectorPerformances(
        key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas"
    )

    df_sectors, _ = sector_perf.get_sector()

    # pylint: disable=invalid-sequence-index
    df_rtp = df_sectors["Rank A: Real-Time Performance"]
    df_rtp = df_rtp.apply(lambda x: x * 100)
    df_rtp = df_rtp.to_frame().reset_index()

    df_rtp.columns = ["Sector", "% Chg"]

    return df_rtp


@log_start_end(log=logger)
def get_real_gdp(
    interval: str = "q",
    start_year: int = 2010,
) -> pd.DataFrame:
    """Get annual or quarterly Real GDP for US

    Parameters
    ----------
    interval : str, optional
        Interval for GDP, by default "a" for annual, by default "q"
    start_year : int, optional
        Start year for plot, by default 2010

    Returns
    -------
    pd.DataFrame
        Dataframe of GDP
    """
    s_interval = "quarterly" if interval == "q" else "annual"

    url = (
        "https://www.alphavantage.co/query?function=REAL_GDP"
        + f"&interval={s_interval}&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    )
    r = request(url, headers={"User-Agent": get_user_agent()})

    if r.status_code != 200:
        console.print(f"Request error. Response code: {str(r.status_code)}.\n")
        return pd.DataFrame()

    payload = r.json()

    # Successful requests
    if "data" in payload:
        if payload["data"]:
            data = pd.DataFrame(payload["data"])
            data["date"] = pd.to_datetime(data["date"])
            data["GDP"] = data["value"].astype(float)
            data = data.drop(columns=["value"])
            return data[data["date"] >= f"{start_year}-01-01"]
        console.print(f"No data found for {interval}.\n")
    # Invalid API Keys
    if "Error Message" in payload:
        console.print(payload["Error Message"])
    # Premium feature, API plan is not authorized
    if "Information" in payload:
        console.print(payload["Information"])

    return pd.DataFrame()


@log_start_end(log=logger)
def get_gdp_capita(start_year: int = 2010) -> pd.DataFrame:
    """Real GDP per Capita for United States

    Parameters
    ----------
    start_year : int, optional
        Start year for plot, by default 2010

    Returns
    -------
    pd.DataFrame
        DataFrame of GDP per Capita
    """
    url = (
        "https://www.alphavantage.co/query?function=REAL_GDP_PER_CAPITA"
        + f"&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    )
    r = request(url, headers={"User-Agent": get_user_agent()})
    if r.status_code != 200:
        console.print(f"Request error. Response code: {str(r.status_code)}.\n")
        return pd.DataFrame()

    payload = r.json()

    if "data" in payload:
        if payload["data"]:
            data = pd.DataFrame(payload["data"])
            data["date"] = pd.to_datetime(data["date"])
            data["GDP"] = data["value"].astype(float)
            data = data.drop(columns=["value"])
            return data[data["date"] >= f"{start_year}-01-01"]
        console.print("No data found.\n")
    # Invalid API Keys
    if "Error Message" in payload:
        console.print(payload["Error Message"])
    # Premium feature, API plan is not authorized
    if "Information" in payload:
        console.print(payload["Information"])

    return pd.DataFrame()


@log_start_end(log=logger)
def get_inflation(start_year: int = 2010) -> pd.DataFrame:
    """Get historical Inflation for United States from AlphaVantage

    Parameters
    ----------
    start_year : int, optional
        Start year for plot, by default 2010

    Returns
    -------
    pd.DataFrame
        DataFrame of inflation rates
    """
    url = (
        "https://www.alphavantage.co/query?function=INFLATION"
        + f"&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    )
    r = request(url, headers={"User-Agent": get_user_agent()})
    if r.status_code != 200:
        console.print(f"Request error. Response code: {str(r.status_code)}.\n")
        return pd.DataFrame()

    payload = r.json()

    if "data" in payload:
        if payload["data"]:
            data = pd.DataFrame(payload["data"])
            data["date"] = pd.to_datetime(data["date"])
            data["Inflation"] = data["value"].astype(float)
            data = data.drop(columns=["value"])
            return data[data["date"] >= f"{start_year}-01-01"]
        console.print("No data found.\n")
    # Invalid API Keys
    if "Error Message" in payload:
        console.print(payload["Error Message"])
    # Premium feature, API plan is not authorized
    if "Information" in payload:
        console.print(payload["Information"])

    return pd.DataFrame()


@log_start_end(log=logger)
def get_cpi(interval: str = "m", start_year: int = 2010) -> pd.DataFrame:
    """Get Consumer Price Index from Alpha Vantage

    Parameters
    ----------
    interval : str
        Interval for data.  Either "m" or "s" for monthly or semiannual
    start_year : int, optional
        Start year for plot, by default 2010

    Returns
    -------
    pd.DataFrame
        Dataframe of CPI
    """
    s_interval = "semiannual" if interval == "s" else "monthly"
    url = (
        f"https://www.alphavantage.co/query?function=CPI&interval={s_interval}"
        + f"&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    )
    r = request(url, headers={"User-Agent": get_user_agent()})

    if r.status_code != 200:
        console.print(f"Request error. Response code: {str(r.status_code)}.\n")
        return pd.DataFrame()

    payload = r.json()

    # Successful requests
    if "data" in payload:
        if payload["data"]:
            data = pd.DataFrame(payload["data"])
            data["date"] = pd.to_datetime(data["date"])
            data["CPI"] = data["value"].astype(float)
            data = data.drop(columns=["value"])
            return data[data["date"] >= f"{start_year}-01-01"]
        console.print(f"No data found for {interval}.\n")
    # Invalid API Keys
    if "Error Message" in payload:
        console.print(payload["Error Message"])
    # Premium feature, API plan is not authorized
    if "Information" in payload:
        console.print(payload["Information"])

    return pd.DataFrame()


@log_start_end(log=logger)
def get_treasury_yield(
    interval: str = "m", maturity: str = "10y", start_date: str = "2010-01-01"
) -> pd.DataFrame:
    """Get historical yield for a given maturity

    Parameters
    ----------
    interval : str
        Interval for data.  Can be "d","w","m" for daily, weekly or monthly, by default "m"
    start_date: str
        Start date for data.  Should be in YYYY-MM-DD format, by default "2010-01-01"
    maturity : str
        Maturity timeline.  Can be "3mo","5y","10y" or "30y", by default "10y"

    Returns
    -------
    pd.DataFrame
        Dataframe of historical yields
    """
    d_interval = {"d": "daily", "w": "weekly", "m": "monthly"}
    d_maturity = {"3m": "3month", "5y": "5year", "10y": "10year", "30y": "30year"}

    url = (
        "https://www.alphavantage.co/query?function=TREASURY_YIELD"
        + f"&interval={d_interval[interval]}"
        + f"&maturity={d_maturity[maturity]}&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    )
    r = request(url, headers={"User-Agent": get_user_agent()})
    if r.status_code != 200:
        console.print(f"Request error. Response code: {str(r.status_code)}.\n")
        return pd.DataFrame()

    payload = r.json()

    # Successful requests
    if "data" in payload:
        if payload["data"]:
            data = pd.DataFrame(payload["data"])
            data["date"] = pd.to_datetime(data["date"])
            data["Yield"] = data["value"].astype(float)
            data = data.drop(columns=["value"])
            return data[data["date"] >= start_date]
        console.print(f"No data found for {interval}.\n")
    # Invalid API Keys
    if "Error Message" in payload:
        console.print(payload["Error Message"])
    # Premium feature, API plan is not authorized
    if "Information" in payload:
        console.print(payload["Information"])

    return pd.DataFrame()


@log_start_end(log=logger)
def get_unemployment(start_year: int = 2010) -> pd.DataFrame:
    """Get historical unemployment for United States

    Parameters
    ----------
    start_year : int, optional
        Start year for plot, by default 2010

    Returns
    -------
    pd.DataFrame
        Dataframe of historical yields
    """
    url = f"https://www.alphavantage.co/query?function=UNEMPLOYMENT&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    r = request(url, headers={"User-Agent": get_user_agent()})
    if r.status_code != 200:
        return pd.DataFrame()

    payload = r.json()
    data = pd.DataFrame()

    # Successful requests
    if "data" in payload:
        if payload["data"]:
            data = pd.DataFrame(payload["data"])
            data["date"] = pd.to_datetime(data["date"])
            data["unemp"] = data["value"].astype(float)
            data = data.drop(columns=["value"])
            return data[data["date"] >= f"{start_year}-01-01"]
        console.print("No data found.\n")
    # Invalid API Keys
    if "Error Message" in payload:
        console.print(payload["Error Message"])
    # Premium feature, API plan is not authorized
    if "Information" in payload:
        console.print(payload["Information"])

    return pd.DataFrame()
