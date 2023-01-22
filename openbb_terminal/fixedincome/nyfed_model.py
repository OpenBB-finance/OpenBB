""" NYFED model """
__docformat__ = "numpy"

import logging
from datetime import datetime

import numpy
import pandas as pd
from requests import request

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_sofr_data(
    series: str = "overnight", start_date: str = "1980-01-01", end_date: str = ""
) -> pd.DataFrame:
    """Get Secured Overnight Financing Rate (SOFR) data

    Parameters
    ----------
    series: str
        Specific data to return, options: ['overnight', '30_day', '90_day', '180_day', 'index', 'all']
    start_date: str
        Start date, formatted YYYY-MM-DD
    end_date:
        End date, formatted YYYY-MM-DD

    Returns
    -------
    pd.DataFrame
        Dataframe with SOFR data
    """
    if isinstance(start_date, datetime):
        start_date = datetime.strftime(start_date, "%Y-%m-%d")
    if series.lower() == "overnight":
        data = request(
            "GET",
            url=f"https://markets.newyorkfed.org/api/rates/secured/sofr/search.json?startDate={start_date}&endDate={end_date}",
        ).json()
        df = pd.DataFrame.from_records(
            data["refRates"],
            index="effectiveDate",
            exclude=["type", "revisionIndicator", "footnoteId"],
        )
    else:
        data = request(
            "GET",
            url=f"https://markets.newyorkfed.org/api/rates/secured/sofrai/search.json?startDate={start_date}&endDate={end_date}",
        ).json()
        df = pd.DataFrame.from_records(
            data["refRates"],
            index="effectiveDate",
            exclude=["type", "revisionIndicator"],
        )
    df.index = pd.to_datetime(df.index)
    df = df.replace("NA", numpy.NaN)
    df = df.astype(float)
    if series == "index":
        df = df["index"]
    elif series != "overnight" and series != "all":
        df = df["average" + series.replace("_", "")]
    return df


@log_start_end(log=logger)
def get_effr_data(start_date: str = "1980-01-01", end_date: str = "") -> pd.DataFrame:
    """Get Effective Federal Funds Rate (EFFR) data

    Parameters
    ----------
    start_date: str
        Start date, formatted YYYY-MM-DD
    end_date:
        End date, formatted YYYY-MM-DD

    Returns
    -------
    pd.DataFrame
        Dataframe with EFFR data
    """
    if isinstance(start_date, datetime):
        start_date = datetime.strftime(start_date, "%Y-%m-%d")
    data = request(
        "GET",
        url=f"https://markets.newyorkfed.org/api/rates/unsecured/effr/search.json?startDate={start_date}&endDate={end_date}",
    ).json()
    df = pd.DataFrame.from_records(
        data["refRates"],
        index="effectiveDate",
        exclude=["type", "revisionIndicator"],
    )
    df.index = pd.to_datetime(df.index)
    df = df.replace("NA", numpy.NaN)
    df = df.astype(float)

    return df


@log_start_end(log=logger)
def get_obfr_data(start_date: str = "1980-01-01", end_date: str = "") -> pd.DataFrame:
    """Get Overnight Bank Funding Rate (OBFR) data

    Parameters
    ----------
    start_date: str
        Start date, formatted YYYY-MM-DD
    end_date:
        End date, formatted YYYY-MM-DD

    Returns
    -------
    pd.DataFrame
        Dataframe with OBFR data
    """
    if isinstance(start_date, datetime):
        start_date = datetime.strftime(start_date, "%Y-%m-%d")
    data = request(
        "GET",
        url=f"https://markets.newyorkfed.org/api/rates/unsecured/obfr/search.json?startDate={start_date}&endDate={end_date}",
    ).json()
    df = pd.DataFrame.from_records(
        data["refRates"],
        index="effectiveDate",
        exclude=["type", "revisionIndicator"],
    )
    df.index = pd.to_datetime(df.index)
    df = df.replace("NA", numpy.NaN)
    df = df.astype(float)

    return df
