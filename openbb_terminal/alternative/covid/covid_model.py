"""Covid Model"""
__docformat__ = "numpy"

import logging
import warnings

import numpy as np
import pandas as pd

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

global_cases_time_series = (
    "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_"
    "covid_19_time_series/time_series_covid19_confirmed_global.csv"
)
global_deaths_time_series = (
    "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_"
    "covid_19_time_series/time_series_covid19_deaths_global.csv"
)


@log_start_end(log=logger)
def get_global_cases(country: str) -> pd.DataFrame:
    """Get historical cases for given country

    Parameters
    ----------
    country: str
        Country to search for

    Returns
    -------
    pd.DataFrame
        Dataframe of historical cases
    """
    cases = pd.read_csv(global_cases_time_series)
    cases = cases.rename(columns={"Country/Region": "Country"})
    cases = (
        cases.drop(columns=["Province/State", "Lat", "Long"])
        .groupby("Country")
        .agg("sum")
        .T
    )
    cases.index = pd.to_datetime(cases.index)
    cases = pd.DataFrame(cases[country]).diff().dropna()
    if cases.shape[1] > 1:
        return pd.DataFrame(cases.sum(axis=1))
    return cases


@log_start_end(log=logger)
def get_global_deaths(country: str) -> pd.DataFrame:
    """Get historical deaths for given country

    Parameters
    ----------
    country: str
        Country to search for

    Returns
    -------
    pd.DataFrame
        Dataframe of historical deaths
    """
    deaths = pd.read_csv(global_deaths_time_series)
    deaths = deaths.rename(columns={"Country/Region": "Country"})
    deaths = (
        deaths.drop(columns=["Province/State", "Lat", "Long"])
        .groupby("Country")
        .agg("sum")
        .T
    )
    deaths.index = pd.to_datetime(deaths.index)
    deaths = pd.DataFrame(deaths[country]).diff().dropna()
    if deaths.shape[1] > 1:
        return pd.DataFrame(deaths.sum(axis=1))
    return deaths


@log_start_end(log=logger)
def get_case_slopes(days_back: int = 30, threshold: int = 10000) -> pd.DataFrame:
    """Load cases and find slope over period

    Parameters
    ----------
    days_back: int
        Number of historical days to consider
    threshold: int
        Threshold for total number of cases
    Returns
    -------
    pd.DataFrame
        Dataframe containing slopes
    """
    # Ignore the pandas warning for setting a slace with a value
    warnings.filterwarnings("ignore")
    cases = pd.read_csv(global_cases_time_series)
    cases = cases.rename(columns={"Country/Region": "Country"})
    cases = (
        (
            cases.drop(columns=["Province/State", "Lat", "Long"])
            .groupby("Country")
            .agg("sum")
        )
        .diff()
        .dropna()
    )
    hist = cases.iloc[:, -days_back:]
    hist["Sum"] = hist.sum(axis=1)
    hist = hist[hist.Sum > threshold].drop(columns="Sum")
    hist["Slope"] = hist.apply(
        lambda x: np.polyfit(np.arange(days_back), x, 1)[0], axis=1
    )
    return pd.DataFrame(hist["Slope"])
