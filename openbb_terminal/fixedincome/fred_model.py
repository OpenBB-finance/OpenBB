""" FRED model """
__docformat__ = "numpy"

import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Tuple

import certifi
import pandas as pd
from fredapi import Fred
from requests import HTTPError

from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.rich_config import console

# pylint: disable=attribute-defined-outside-init

logger = logging.getLogger(__name__)

YIELD_CURVE_SERIES_NOMINAL = {
    "1Month": "DGS1MO",
    "3Month": "DGS3MO",
    "6Month": "DGS6MO",
    "1Year": "DGS1",
    "2Year": "DGS2",
    "3Year": "DGS3",
    "5Year": "DGS5",
    "7Year": "DGS7",
    "10Year": "DGS10",
    "20Year": "DGS20",
    "30Year": "DGS30",
}
YIELD_CURVE_SERIES_REAL = {
    "5Year": "DFII5",
    "7Year": "DFII7",
    "10Year": "DFII10",
    "20Year": "DFII20",
    "30Year": "DFII30",
}

YIELD_CURVE_SERIES_CORPORATE_SPOT = {
    "6Month": "HQMCB6MT",
    "1Year": "HQMCB1YR",
    "2Year": "HQMCB2YR",
    "3Year": "HQMCB3YR",
    "5Year": "HQMCB5YR",
    "7Year": "HQMCB7YR",
    "10Year": "HQMCB10YR",
    "20Year": "HQMCB20YR",
    "30Year": "HQMCB30YR",
    "50Year": "HQMCB50YR",
    "75Year": "HQMCB75YR",
    "100Year": "HQMCB100YR"
}
YIELD_CURVE_SERIES_CORPORATE_PAR = {
    "2Year": "HQMCB2YRP",
    "5Year": "HQMCB5YRP",
    "10Year": "HQMCB10YRP",
    "30Year": "HQMCB30YRP",
}

YIELD_CURVE_NOMINAL_RATES = [1 / 12, 0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30]
YIELD_CURVE_SPOT_RATES = [0.5, 1, 2, 3, 5, 7, 10, 20, 30, 50, 75, 100]
YIELD_CURVE_REAL_RATES = [5, 7, 10, 20, 30]
YIELD_CURVE_PAR_RATES = [2, 5, 10, 30]

@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def get_series_data(
    series_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None
) -> pd.DataFrame:
    """Get Series data. [Source: FRED]

    Parameters
    ----------
    series_id : str
        Series ID to get data from
    start_date : Optional[str]
        Start date to get data from, format yyyy-mm-dd
    end_date : Optional[str]
        End data to get from, format yyyy-mm-dd

    Returns
    -------
    pd.DataFrame
        Series data
    """
    try:
        # Necessary for installer so that it can locate the correct certificates for
        # API calls and https
        # https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error/73270162#73270162
        os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
        os.environ["SSL_CERT_FILE"] = certifi.where()
        fredapi_client = Fred(cfg.API_FRED_KEY)
        df = fredapi_client.get_series(series_id, start_date, end_date)
    # Series does not exist & invalid api keys
    except HTTPError as e:
        console.print(e)

    return df


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def get_yield_curve(
    date: str = "", return_date: bool = False, inflation_adjusted: bool = False, spot_or_par: str = None
) -> Tuple[pd.DataFrame, str]:
    """Gets yield curve data from FRED.

    The graphic depiction of the relationship between the yield on bonds of the same credit quality but different
    maturities is known as the yield curve. In the past, most market participants have constructed yield curves from
    the observations of prices and yields in the Treasury market. Two reasons account for this tendency. First,
    Treasury securities are viewed as free of default risk, and differences in creditworthiness do not affect yield
    estimates. Second, as the most active bond market, the Treasury market offers the fewest problems of illiquidity
    or infrequent trading. The key function of the Treasury yield curve is to serve as a benchmark for pricing bonds
    and setting yields in other sectors of the debt market.

    It is clear that the market’s expectations of future rate changes are one important determinant of the
    yield-curve shape. For example, a steeply upward-sloping curve may indicate market expectations of near-term Fed
    tightening or of rising inflation. However, it may be too restrictive to assume that the yield differences across
    bonds with different maturities only reflect the market’s rate expectations. The well-known pure expectations
    hypothesis has such an extreme implication. The pure expectations hypothesis asserts that all government bonds
    have the same near-term expected return (as the nominally riskless short-term bond) because the return-seeking
    activity of risk-neutral traders removes all expected return differentials across bonds.

    Parameters
    ----------
    date: str
        Date to get curve for. If empty, gets most recent date (format yyyy-mm-dd)
    return_date: bool
        If True, returns date of yield curve

    Returns
    -------
    Tuple[pd.DataFrame, str]
        Dataframe of yields and maturities,
        Date for which the yield curve is obtained

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> ycrv_df = openbb.fixedincome.ycrv()

    Since there is a delay with the data, the most recent date is returned and can be accessed with return_date=True
    >>> ycrv_df, ycrv_date = openbb.fixedincome.ycrv(return_date=True)
    """

    # Necessary for installer so that it can locate the correct certificates for
    # API calls and https
    # https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error/73270162#73270162
    # os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
    # os.environ["SSL_CERT_FILE"] = certifi.where()

    fredapi_client = Fred(cfg.API_FRED_KEY)

    df = pd.DataFrame()
    
    # Check that the date is in the past
    today = datetime.now().strftime("%Y-%m-%d")
    if date and date >= today:
        console.print("[red]Date cannot be today or in the future[/red]")
        if return_date:
            return pd.DataFrame(), date
        return pd.DataFrame()

    # Add in logic that will get the most recent date
    if date:
        get_last = False
        start_date = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=50)).strftime("%Y-%m-%d")
    else:
        date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=50)).strftime("%Y-%m-%d")
        get_last = True

    if inflation_adjusted:
        fred_series = YIELD_CURVE_SERIES_REAL
        years = YIELD_CURVE_REAL_RATES
    elif spot_or_par:
        if spot_or_par == "spot":
            years = YIELD_CURVE_SPOT_RATES
            fred_series = YIELD_CURVE_SERIES_CORPORATE_SPOT
        elif spot_or_par == "par":
            years = YIELD_CURVE_PAR_RATES
            fred_series = YIELD_CURVE_SERIES_CORPORATE_PAR
        else:
            console.print("Please select either 'spot' or 'par' rates.")
    else:
        fred_series = YIELD_CURVE_SERIES_NOMINAL
        years = YIELD_CURVE_NOMINAL_RATES

    for key, s_id in fred_series.items():
        df = pd.concat(
            [
                df,
                pd.DataFrame(fredapi_client.get_series(s_id, start_date), columns=[key]),
            ],
            axis=1,
        )
    if df.empty:
        if return_date:
            return pd.DataFrame(), date
        return pd.DataFrame()
    # Drop rows with NaN -- corresponding to weekends typically
    df = df.dropna()

    if date not in df.index or get_last:
        # If the get_last flag is true, we want the first date, otherwise we want the last date.
        idx = -1 if get_last else 0
        date_of_yield = df.index[idx].strftime("%Y-%m-%d")
        rates = pd.DataFrame(df.iloc[idx, :].values, columns=["Rate"])
        
        if spot_or_par:
            console.print(f"Because {spot_or_par.title()} rates are published monthly, "
                          f"the nearest date to {date} is used which is {date_of_yield}.")
    else:
        date_of_yield = date
        series = df[df.index == date]
        if series.empty:
            return pd.DataFrame(), date_of_yield
        rates = pd.DataFrame(series.values.T, columns=["Rate"])

    rates.insert(0, "Maturity", years)
    if return_date:
        return rates, date_of_yield
    return rates
