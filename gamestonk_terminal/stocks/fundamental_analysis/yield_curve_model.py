""" Fundamental Analysis Yield Curve Model """
__docformat__ = "numpy"

import logging
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pandas.core.frame import DataFrame

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import get_user_agent

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_yield_curve(start: datetime, end: datetime) -> DataFrame:
    """Returns a US Treasury Yield Curve from start date to end date

    Parameters
    ----------
    start : datetime
        Start date
    end : datetime
        End date

    Returns
    -------
    DataFrame
        US Treasury Yield Curve data frame with the following columns
        Date,1 mo,2 mo,3 mo,6 mo,1 yr,2 yr,3 yr,5 yr,7 yr,10 yr,20 yr,30 yr
    """

    if start.year == end.year:
        df_yield_curve = get_yield_curve_year(str(start.year))
        return df_yield_curve[start:end]  # type: ignore

    df_yield_curve = get_yield_curve_year(str(start.year))

    a_year = start.year + 1

    while a_year <= end.year:
        df_temp_curve = get_yield_curve_year(str(a_year))
        df_yield_curve = df_yield_curve.append(df_temp_curve)
        a_year += 1

    return df_yield_curve[start:end]  # type: ignore


@log_start_end(log=logger)
def get_yield_curve_year(year: str) -> DataFrame:
    """Returns a US Treasury Yield Curve for a given year

    Parameters
    ----------
    year : str
        Yield curve year

    Returns
    -------
    DataFrame
        US Treasury Yield Curve data frame with the following columns
        Date,1 mo,2 mo,3 mo,6 mo,1 yr,2 yr,3 yr,5 yr,7 yr,10 yr,20 yr,30 yr
    """

    # pylint: disable=line-too-long
    yield_curve_url = "https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yieldYear&year={}"  # noqa: E501
    text_soup_yield_curve = BeautifulSoup(
        requests.get(
            yield_curve_url.format(year),
            headers={"User-Agent": get_user_agent()},
        ).text,
        "lxml",
    )

    yield_table = text_soup_yield_curve.find_all("table", {"class": "t-chart"})[0]

    a_yield_table_header = []
    for yield_table_header_col in yield_table.find("tr", {"class": None}).find_all(
        "th"
    ):
        a_yield_table_header.append(yield_table_header_col.text)

    df_yield_curve = pd.DataFrame(columns=a_yield_table_header)

    for yield_table_row in yield_table.find_all("tr", {"class": ["oddrow", "evenrow"]}):
        a_yield_row = []
        for idx, yield_table_col in enumerate(yield_table_row.find_all("td")):
            if idx == 0:
                a_yield_row.append(datetime.strptime(yield_table_col.text, "%m/%d/%y"))
            else:
                a_yield_row.append(float(yield_table_col.text))  # type: ignore

        df_yield_curve.loc[len(df_yield_curve)] = a_yield_row

    df_yield_curve = df_yield_curve.set_index(["Date"])

    return df_yield_curve
