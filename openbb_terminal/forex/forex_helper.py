"""Forex helper."""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Iterable
import os
import argparse
import logging
import re

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import LogLocator, ScalarFormatter
import mplfinance as mpf
import yfinance as yf
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from openbb_terminal.stocks import stocks_helper
from openbb_terminal.forex import av_model, polygon_model
from openbb_terminal.rich_config import console
from openbb_terminal.decorators import log_start_end
import openbb_terminal.config_terminal as cfg
from openbb_terminal.helper_funcs import (
    is_valid_axes_count,
    plot_autoscale,
    lambda_long_number_format_y_axis,
)

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
    "Oanda": "Oanda",
    "Polygon": "Polygon",
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
    source : str, optional
        Where to get data from, by default "YahooFinance"
    verbose : bool, optional
        Display verbose information on what was the pair that was loaded, by default True

    Returns
    -------
    pd.DataFrame
        The loaded data
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

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
            )
            df.index.name = "date"
            return df

        if source == "YahooFinance":
            df = yf.download(
                f"{from_symbol}{to_symbol}=X",
                start=datetime.strptime(start_date, "%Y-%m-%d"),
                interval=clean_interval,
                progress=verbose,
            )
            df.index.name = "date"
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
        )
        df.index.name = "date"
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
    external_axes: Optional[List[plt.Axes]] = None,
    use_matplotlib: bool = True,
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
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list), by default None
    """
    # We check if there's Volume data to avoid errors and empty subplots
    has_volume = False
    if "Volume" in data.columns:
        has_volume = bool(data["Volume"].sum() > 0)

    if add_trend:
        if (data.index[1] - data.index[0]).total_seconds() >= 86400:
            data = stocks_helper.find_trendline(data, "OC_High", "high")
            data = stocks_helper.find_trendline(data, "OC_Low", "low")

    if use_matplotlib:
        ap0 = []
        if add_trend:
            if "OC_High_trend" in data.columns:
                ap0.append(
                    mpf.make_addplot(
                        data["OC_High_trend"],
                        color=cfg.theme.up_color,
                        secondary_y=False,
                    ),
                )

            if "OC_Low_trend" in data.columns:
                ap0.append(
                    mpf.make_addplot(
                        data["OC_Low_trend"],
                        color=cfg.theme.down_color,
                        secondary_y=False,
                    ),
                )

        candle_chart_kwargs = {
            "type": "candle",
            "style": cfg.theme.mpf_style,
            "volume": has_volume,
            "addplot": ap0,
            "xrotation": cfg.theme.xticks_rotation,
            "scale_padding": {"left": 0.3, "right": 1, "top": 0.8, "bottom": 0.8},
            "update_width_config": {
                "candle_linewidth": 0.6,
                "candle_width": 0.8,
                "volume_linewidth": 0.8,
                "volume_width": 0.8,
            },
            "warn_too_much_data": 10000,
            "yscale": yscale,
        }

        if ma:
            candle_chart_kwargs["mav"] = ma

        if external_axes is None:
            candle_chart_kwargs["returnfig"] = True
            candle_chart_kwargs["figratio"] = (10, 7)
            candle_chart_kwargs["figscale"] = 1.10
            candle_chart_kwargs["figsize"] = plot_autoscale()
            candle_chart_kwargs["warn_too_much_data"] = 100_000

            fig, ax = mpf.plot(data, **candle_chart_kwargs)

            if has_volume:
                lambda_long_number_format_y_axis(data, "Volume", ax)

            fig.suptitle(
                f"{from_symbol}/{to_symbol}",
                x=0.055,
                y=0.965,
                horizontalalignment="left",
            )

            if ma:
                # Manually construct the chart legend
                colors = [cfg.theme.get_colors()[i] for i, _ in enumerate(ma)]
                lines = [Line2D([0], [0], color=c) for c in colors]
                labels = ["MA " + str(label) for label in ma]
                ax[0].legend(lines, labels)

            if yscale == "log":
                ax[0].yaxis.set_major_formatter(ScalarFormatter())
                ax[0].yaxis.set_major_locator(
                    LogLocator(base=100, subs=[1.0, 2.0, 5.0, 10.0])
                )
                ax[0].ticklabel_format(style="plain", axis="y")

            cfg.theme.visualize_output(force_tight_layout=False)
        elif (has_volume and is_valid_axes_count(external_axes, 2)) or (
            not has_volume and is_valid_axes_count(external_axes, 1)
        ):
            candle_chart_kwargs["ax"] = external_axes[0]
            if has_volume:
                candle_chart_kwargs["volume"] = external_axes[1]
            mpf.plot(data, **candle_chart_kwargs)

    if not use_matplotlib:
        fig = make_subplots(
            rows=2 if has_volume else 1,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.06,
            subplot_titles=(
                f"{from_symbol}/{to_symbol}",
                "Volume" if has_volume else None,
            ),
            row_width=[0.2, 0.7] if has_volume else [1],
        )
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data.Open,
                high=data.High,
                low=data.Low,
                close=data.Close,
                name="OHLC",
            ),
            row=1,
            col=1,
        )
        if ma:
            plotly_colors = [
                "black",
                "teal",
                "blue",
                "purple",
                "orange",
                "gray",
                "deepskyblue",
            ]
            for idx, ma_val in enumerate(ma):
                temp = data["Adj Close"].copy()
                temp[f"ma{ma_val}"] = data["Adj Close"].rolling(ma_val).mean()
                temp = temp.dropna()
                fig.add_trace(
                    go.Scatter(
                        x=temp.index,
                        y=temp[f"ma{ma_val}"],
                        name=f"MA{ma_val}",
                        mode="lines",
                        line=go.scatter.Line(
                            color=plotly_colors[np.mod(idx, len(plotly_colors))]
                        ),
                    ),
                    row=1,
                    col=1,
                )

        if add_trend:
            if "OC_High_trend" in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data["OC_High_trend"],
                        name="High Trend",
                        mode="lines",
                        line=go.scatter.Line(color="green"),
                    ),
                    row=1,
                    col=1,
                )
            if "OC_Low_trend" in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data["OC_Low_trend"],
                        name="Low Trend",
                        mode="lines",
                        line=go.scatter.Line(color="red"),
                    ),
                    row=1,
                    col=1,
                )

        if has_volume:
            colors = [
                "red" if row.Open < row["Adj Close"] else "green"
                for _, row in data.iterrows()
            ]
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data.Volume,
                    name="Volume",
                    marker_color=colors,
                ),
                row=2,
                col=1,
            )
        fig.update_layout(
            yaxis_title="Stock Price ($)",
            xaxis=dict(
                rangeselector=dict(
                    buttons=list(
                        [
                            dict(
                                count=1,
                                label="1m",
                                step="month",
                                stepmode="backward",
                            ),
                            dict(
                                count=3,
                                label="3m",
                                step="month",
                                stepmode="backward",
                            ),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(
                                count=1,
                                label="1y",
                                step="year",
                                stepmode="backward",
                            ),
                            dict(step="all"),
                        ]
                    )
                ),
                rangeslider=dict(visible=False),
                type="date",
            ),
        )

        fig.update_layout(
            updatemenus=[
                dict(
                    buttons=[
                        dict(
                            label="linear",
                            method="relayout",
                            args=[{"yaxis.type": "linear"}],
                        ),
                        dict(
                            label="log",
                            method="relayout",
                            args=[{"yaxis.type": "log"}],
                        ),
                    ]
                )
            ]
        )

        fig.show(config=dict({"scrollZoom": True}))

    return


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
