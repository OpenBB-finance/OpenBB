""" ECB model """
__docformat__ = "numpy"

import logging
import sys
import time
from datetime import datetime, timedelta
from functools import partial
from multiprocessing import Pool, cpu_count
from typing import Tuple
from urllib.error import HTTPError

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console, optional_rich_track

logger = logging.getLogger(__name__)

# pylint: disable=too-many-return-statements


@log_start_end(log=logger)
def get_series_data(
    series_id: str = "EST.B.EU000A2X2A25.WT", start_date: str = "", end_date: str = ""
):
    """Get ECB data

    Parameters
    ----------
    series_id: str
        ECB ID of data
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    """
    start_date = start_date.replace("-", "")
    end_date = end_date.replace("-", "")
    url = (
        "https://sdw.ecb.europa.eu/quickviewexport.do?trans=N"
        f"&start={start_date}&end={end_date}&SERIES_KEY={series_id}&type=csv"
    )
    time.sleep(0.5)

    def _get_data(max_retries: int = 5):
        try:
            df = pd.read_csv(
                url, header=5, usecols=[0, 1], index_col=0, parse_dates=True
            )
            df = df.iloc[::-1]
            return df
        except KeyboardInterrupt as interrupt:
            raise interrupt
        except (HTTPError, Exception):
            max_retries -= 1
            if max_retries == 0:
                return pd.DataFrame()
            time.sleep(0.5)
            return _get_data(max_retries=max_retries)

    return _get_data()


@log_start_end(log=logger)
def get_ecb_yield_curve(
    date: str = "",
    yield_type: str = "spot_rate",
    return_date: bool = False,
    detailed: bool = False,
    any_rating: bool = True,
) -> Tuple[pd.DataFrame, str]:
    """Gets euro area yield curve data from ECB.

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
    yield_type: str
        What type of yield curve to get, options: ['spot_rate', 'instantaneous_forward', 'par_yield']
    return_date: bool
        If True, returns date of yield curve
    detailed: bool
        If True, returns detailed data. Note that this is very slow.
    aaa_only: bool
        If True, it only returns rates for AAA rated bonds. If False, it returns rates for all bonds

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
    if yield_type == "spot_rate":
        yield_type = f"YC.B.U2.EUR.4F.G_N_{'A' if any_rating else 'C'}.SV_C_YM.SR_"
    elif yield_type == "instantaneous_forward":
        yield_type = f"YC.B.U2.EUR.4F.G_N_{'A' if any_rating else 'C'}.SV_C_YM.IF_"
    elif yield_type == "par_yield":
        yield_type = f"YC.B.U2.EUR.4F.G_N_{'A' if any_rating else 'C'}.SV_C_YM.PY"
    else:
        console.print("[red]Incorrect input for parameter yield_type[/red]")
        if return_date:
            return pd.DataFrame(), date
        return pd.DataFrame()

    if detailed:
        console.print(
            "Note that due to the large amount of data, this may take a while. Use CTRL + C to cancel."
        )
        series_id = [
            f"{yield_type}{y}Y{m}M" if y != 0 else f"{yield_type}{m}M"
            for y in range(0, 30)
            for m in range(1, 12)
            if (y != 0 or m >= 3)
        ]
        series_id.append(f"{yield_type}30Y")
        labels = [
            f"{y}Year{m}Month" if y != 0 else f"{m}Month"
            for y in range(0, 30)
            for m in range(1, 12)
            if (y != 0 or m >= 3)
        ]
        labels.append("30Year")
        years = [
            y + m / 12 for y in range(0, 30) for m in range(1, 12) if (y != 0 or m >= 3)
        ]
        years.append(30)
    else:
        series_id = [f"{yield_type}{m}M" for m in [3, 6]]
        series_id += [f"{yield_type}{y}Y" for y in [1, 2, 3, 5, 7, 10, 20, 30]]
        labels = [f"{m}Month" for m in [3, 6]]
        labels += [f"{y}Year" for y in [1, 2, 3, 5, 7, 10, 20, 30]]
        years = [0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30]

    df = pd.DataFrame()
    # Check that the date is in the past
    today = datetime.now().strftime("%Y-%m-%d")
    if date and date >= today:
        console.print("[red]Date cannot be today or in the future[/red]")
        if return_date:
            return pd.DataFrame(), date
        return pd.DataFrame()

    # Add in logic that will get the most recent date.

    if not date:
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        if detailed and not hasattr(sys, "frozen"):
            with Pool(cpu_count() - 1) as pool:
                # To be able to use optional_rich_track with multiprocessing,
                # we need to use imap_unordered

                results = optional_rich_track(
                    pool.imap_unordered(
                        partial(get_series_data, start_date=date, end_date=date),
                        series_id,
                    ),
                    total=len(series_id),
                    desc="Obtaining yield curve data",
                )
                for i, result in enumerate(results):
                    if isinstance(result, pd.DataFrame) and result.empty:
                        console.print(f"\n[red]No data for {series_id[i]}[/red]")
                        # we remove the corresponding index from the list of years
                        years.pop(i)
                        continue

                    result.columns = [labels[i]]
                    df = pd.concat([df, result], axis=1)

        else:
            for i in optional_rich_track(
                range(len(series_id)), desc="Obtaining yield curve data"
            ):
                temp = get_series_data(series_id[i], date, date)
                temp.columns = [labels[i]]
                df = pd.concat([df, temp], axis=1)

    except (Exception, KeyboardInterrupt):
        console.print("\n[yellow]Data collection was canceled.[/yellow]")
        return pd.DataFrame(), date

    if df.empty:
        if return_date:
            return pd.DataFrame(), date
        return pd.DataFrame()

    # Drop rows with NaN -- corresponding to weekends typically
    df = df.dropna()
    if datetime.strptime(date, "%Y-%m-%d") not in df.index:
        nearest_value = df.index.get_indexer(
            [datetime.strptime(date, "%Y-%m-%d")], method="nearest"
        )
        date_of_yield = df.iloc[nearest_value].index[0].date()
        series = df[df.index == df.iloc[nearest_value].index[0]]
        if series.empty:
            return pd.DataFrame(), date_of_yield
        rates = pd.DataFrame(series.values.T, columns=["Rate"])
        console.print(
            f"{date} not available, therefore selecting the nearest date, {date_of_yield}."
        )
    else:
        date_of_yield = date
        series = df[df.index == datetime.strptime(date, "%Y-%m-%d")]
        if series.empty:
            return pd.DataFrame(), date_of_yield
        rates = pd.DataFrame(series.values.T, columns=["Rate"])

    rates.insert(0, "Maturity", years)

    if return_date:
        return rates, date_of_yield
    return rates
