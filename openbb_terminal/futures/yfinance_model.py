"""Yahoo Finance model"""
__docformat__ = "numpy"

import logging
import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd
import yfinance as yf
from dateutil.relativedelta import relativedelta

from openbb_terminal.core.config.paths import MISCELLANEOUS_DIRECTORY
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

# pylint: disable=attribute-defined-outside-init

logger = logging.getLogger(__name__)

FUTURES_DATA = pd.read_csv(MISCELLANEOUS_DIRECTORY / "futures" / "futures.csv")

MONTHS = {
    1: "F",
    2: "G",
    3: "H",
    4: "J",
    5: "K",
    6: "M",
    7: "N",
    8: "Q",
    9: "U",
    10: "V",
    11: "X",
    12: "Z",
}


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")  # noqa: SIM115

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


@log_start_end(log=logger)
def get_search_futures(
    category: str = "",
    exchange: str = "",
    description: str = "",
):
    """Get search futures [Source: Yahoo Finance]

    Parameters
    ----------
    category: str
        Select the category where the future exists
    exchange: str
        Select the exchange where the future exists
    description: str
        Select the description where the future exists
    """
    df = FUTURES_DATA
    if category:
        df = df[df["Category"] == category]
    if exchange:
        df = df[df["Exchange"] == exchange]
    if description:
        df = df[
            [description.lower() in desc.lower() for desc in df["Description"].values]
        ]
    return df


@log_start_end(log=logger)
def get_historical_futures(
    symbols: List[str],
    expiry: str = "",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Get historical futures [Source: Yahoo Finance]

    Parameters
    ----------
    symbols: List[str]
        List of future timeseries symbols to display
    expiry: str
        Future expiry date with format YYYY-MM
    start_date: Optional[str]
        Start date of the historical data with format YYYY-MM-DD
    end_date: Optional[str]
        End date of the historical data with format YYYY-MM-DD

    Returns
    -------
    pd.DataFrame
        Historical futures data
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=3 * 365)).strftime("%Y-%m-%d")

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    if start_date >= end_date:
        console.print("[yellow]Start date must be before end date.[/yellow]")
        return pd.DataFrame()

    if expiry:
        symbols_with_expiry = list()

        for symbol in symbols:
            expiry_date = datetime.strptime(expiry, "%Y-%m")
            exchange = FUTURES_DATA[FUTURES_DATA["Ticker"] == symbol][
                "Exchange"
            ].values[0]

            symbols_with_expiry.append(
                f"{symbol}{MONTHS[expiry_date.month]}{str(expiry_date.year)[-2:]}.{exchange}"
            )

        return yf.download(
            symbols_with_expiry,
            start=start_date,
            end=end_date,
            progress=False,
            period="max",
            ignore_tz=True,
        )

    df = yf.download(
        [t + "=F" for t in symbols],
        start=start_date,
        end=end_date,
        progress=False,
        period="max",
        ignore_tz=True,
    )
    if len(symbols) > 1:
        df.columns = pd.MultiIndex.from_tuples(
            [(tup[0], tup[1].replace("=F", "")) for tup in df.columns]
        )

    return df


@log_start_end(log=logger)
def get_curve_futures(
    symbol: str = "",
    date: Optional[str] = "",
) -> pd.DataFrame:
    """Get curve futures [Source: Yahoo Finance]

    Parameters
    ----------
    symbol: str
        symbol to get forward curve
    date: str
        optionally include historical price for each contract

    Returns
    -------
    pd.DataFrame
        Dictionary with sector weightings allocation
    """
    if symbol not in FUTURES_DATA["Ticker"].unique().tolist():
        return pd.DataFrame()

    exchange = FUTURES_DATA[FUTURES_DATA["Ticker"] == symbol]["Exchange"].values[0]
    today = datetime.today()

    futures_index = list()
    futures_curve = list()
    historical_curve = list()
    i = 0
    empty_count = 0
    # Loop through until we find 12 consecutive empty months
    while empty_count < 12:
        future = today + relativedelta(months=i)
        future_symbol = (
            f"{symbol}{MONTHS[future.month]}{str(future.year)[-2:]}.{exchange}"
        )
        with HiddenPrints():
            data = yf.download(future_symbol, progress=False, ignore_tz=True)

        if data.empty:
            empty_count += 1

        else:
            empty_count = 0
            futures_index.append(future.strftime("%b-%Y"))
            futures_curve.append(data["Adj Close"].values[-1])
            if date != "":
                historical_curve.append(data["Adj Close"].get(date, None))

        i += 1

    if not futures_index:
        return pd.DataFrame()

    if historical_curve:
        if None in historical_curve:
            console.print("[yellow]No pricing data for selected date.[/yellow]")
        return pd.DataFrame(
            index=futures_index,
            data=zip(futures_curve, historical_curve),
            columns=["Last Price", date],
        )
    return pd.DataFrame(index=futures_index, data=futures_curve, columns=["Last Price"])
