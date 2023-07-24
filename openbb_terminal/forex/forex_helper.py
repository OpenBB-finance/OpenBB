"""Forex helper."""
import argparse
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Optional

import pandas as pd
import yfinance as yf

from openbb_terminal.core.plots.plotly_ta.ta_class import PlotlyTA
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forex import av_model, polygon_model
from openbb_terminal.rich_config import console
from openbb_terminal.stocks import stocks_helper

CANDLE_SORT = [
    "adjclose",
    "open",
    "close",
    "high",
    "low",
    "volume",
    "logret",
]

FOREX_SOURCES: Dict = {
    "YahooFinance": "YahooFinance",
    "AlphaVantage": "AlphaAdvantage",
    "Polygon": "Polygon",
    "Oanda": "Oanda",
}

SOURCES_INTERVALS: Dict = {
    "YahooFinance": [
        "1min",
        "5min",
        "15min",
        "30min",
        "60min",
        "90min",
        "1hour",
        "1day",
        "5day",
        "1week",
        "1month",
        "3month",
    ],
    "AlphaVantage": ["1min", "5min", "15min", "30min", "60min"],
}

INTERVAL_MAPS: Dict = {
    "YahooFinance": {
        "1min": "1m",
        "2min": "2m",
        "5min": "5m",
        "15min": "15m",
        "30min": "30m",
        "60min": "60m",
        "90min": "90m",
        "1hour": "60m",
        "1day": "1d",
        "5day": "5d",
        "1week": "1wk",
        "1month": "1mo",
        "3month": "3mo",
    },
    "AlphaVantage": {
        "1min": 1,
        "5min": 5,
        "15min": 15,
        "30min": 30,
        "60min": 60,
        "1day": 1,
    },
}

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def load(
    to_symbol: str,
    from_symbol: str,
    resolution: str = "d",
    interval: str = "1day",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source: str = "YahooFinance",
    verbose: bool = False,
) -> pd.DataFrame:
    """Load forex for two given symbols.

    Parameters
    ----------
    to_symbol : str
        The from currency symbol. Ex: USD, EUR, GBP, YEN
    from_symbol : str
        The from currency symbol. Ex: USD, EUR, GBP, YEN
    resolution : str, optional
        The resolution for the data, by default "d"
    interval : str, optional
        What interval to get data for, by default "1day"
    start_date : Optional[str], optional
        When to begin loading in data, by default last_year.strftime("%Y-%m-%d")
    end_date : Optional[str], optional
        When to end loading in data, by default None
    source : str, optional
        Where to get data from, by default "YahooFinance"
    verbose : bool, optional
        Display verbose information on what was the pair that was loaded, by default True

    Returns
    -------
    pd.DataFrame
        The loaded data

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.forex.load(from_symbol="EUR", to_symbol="USD", start_date="2020-11-30", end_date="2022-12-01")
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    if end_date is None:
        end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        end_date = (
            datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        ).strftime("%Y-%m-%d")

    if source in ["YahooFinance", "AlphaVantage"]:
        interval_map = INTERVAL_MAPS[source]

        if interval not in interval_map.keys() and resolution != "d":
            if verbose:
                console.print(
                    f"Interval not supported by {FOREX_SOURCES[source]}."
                    " Need to be one of the following options",
                    list(interval_map.keys()),
                )
            return pd.DataFrame()

        # Check interval in multiple ways
        if interval in interval_map:
            clean_interval = interval_map[interval]
        elif interval in interval_map.values():
            clean_interval = interval
        else:
            console.print(f"[red]'{interval}' is an invalid interval[/red]\n")
            return pd.DataFrame()

        if source == "AlphaVantage":
            if "min" in interval:
                resolution = "i"
            df = av_model.get_historical(
                to_symbol=to_symbol,
                from_symbol=from_symbol,
                resolution=resolution,
                interval=clean_interval,
                start_date=start_date,
                end_date=end_date,
            )
            df.index.name = "date"
            df.name = f"{from_symbol}/{to_symbol}"
            return df

        if source == "YahooFinance":
            df = yf.download(
                f"{from_symbol}{to_symbol}=X",
                start=datetime.strptime(start_date, "%Y-%m-%d"),
                end=datetime.strptime(end_date, "%Y-%m-%d"),
                interval=clean_interval,
                progress=verbose,
            )
            df.index = pd.to_datetime(df.index).tz_localize(None)
            df.index.name = "date"
            df.name = f"{from_symbol}/{to_symbol}"
            return df

    if source == "Polygon":
        # Interval for polygon gets broken into multiplier and timeframe
        temp = re.split(r"(\d+)", interval)
        multiplier = int(temp[1])
        timeframe = temp[2]
        if timeframe == "min":
            timeframe = "minute"
        df = polygon_model.get_historical(
            f"{from_symbol}{to_symbol}",
            multiplier=multiplier,
            timespan=timeframe,
            start_date=start_date,
            end_date=end_date,
        )
        df.index.name = "date"
        df.name = f"{from_symbol}/{to_symbol}"
        return df

    console.print(f"Source {source} not supported")
    return pd.DataFrame()


@log_start_end(log=logger)
def get_yf_currency_list() -> List:
    """Load YF list of forex pair a local file."""
    path = os.path.join(os.path.dirname(__file__), "data/yahoofinance_forex.json")

    return sorted(list(set(pd.read_json(path)["from_symbol"])))


YF_CURRENCY_LIST = get_yf_currency_list()


@log_start_end(log=logger)
def check_valid_yf_forex_currency(fx_symbol: str) -> str:
    """Check if given symbol is supported on Yahoo Finance.

    Parameters
    ----------
    fx_symbol : str
        Symbol to check

    Returns
    -------
    str
        Currency symbol

    Raises
    ------
    argparse.ArgumentTypeError
        Symbol not valid on YahooFinance
    """
    if fx_symbol.upper() in get_yf_currency_list():
        return fx_symbol.upper()

    raise argparse.ArgumentTypeError(
        f"{fx_symbol.upper()} not found in YahooFinance supported currency codes. "
    )


@log_start_end(log=logger)
def display_candle(
    data: pd.DataFrame,
    to_symbol: str = "",
    from_symbol: str = "",
    ma: Optional[Iterable[int]] = None,
    external_axes: bool = False,
    add_trend: bool = False,
    yscale: str = "linear",
):
    """Show candle plot for fx data.

    Parameters
    ----------
    data : pd.DataFrame
        Loaded fx historical data
    to_symbol : str
        To forex symbol
    from_symbol : str
        From forex symbol
    ma : Optional[Iterable[int]]
        Moving averages
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    # We check if there's Volume data to avoid errors and empty subplots
    if not (has_volume := False) and "Volume" in data.columns:
        has_volume = bool(data["Volume"].sum() > 0)

    if add_trend and (data.index[1] - data.index[0]).total_seconds() >= 86400:
        if "date_id" not in data.columns:
            data = stocks_helper.process_candle(data)
        data = stocks_helper.find_trendline(data, "OC_High", "high")
        data = stocks_helper.find_trendline(data, "OC_Low", "low")

    indicators = {}
    if ma:
        indicators = dict(rma=dict(length=ma))

    data.name = f"{from_symbol}/{to_symbol}"
    fig = PlotlyTA.plot(data, indicators, volume=has_volume)
    if add_trend:
        fig.add_trend(data, secondary_y=False)

    fig.update_yaxes(type=yscale, row=1, col=1, nticks=20, secondary_y=False)

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def parse_forex_symbol(input_symbol):
    """Parse potential forex symbols."""
    for potential_split in ["-", "/"]:
        if potential_split in input_symbol:
            symbol = input_symbol.replace(potential_split, "")
            return symbol
    if len(input_symbol) != 6:
        raise argparse.ArgumentTypeError("Input symbol should be 6 characters.\n ")
    return input_symbol.upper()
