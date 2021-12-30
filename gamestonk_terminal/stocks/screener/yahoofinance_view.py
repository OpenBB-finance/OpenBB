"""Yahoo Finance View"""
__docformat__ = "numpy"
import configparser
import datetime
import os
import random
from typing import List
import numpy as np
import pandas as pd

from pandas.plotting import register_matplotlib_converters
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import yfinance as yf
from finvizfinance.screener import ticker
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
)
from gamestonk_terminal.stocks.screener import finviz_model

register_matplotlib_converters()

presets_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "presets/")

d_candle_types = {
    "o": "Open",
    "h": "High",
    "l": "Low",
    "c": "Close",
    "a": "Adj Close",
}


def historical(
    preset_loaded: str,
    limit: int = 10,
    start: datetime.datetime = datetime.datetime.now()
    - datetime.timedelta(days=6 * 30),
    type_candle: str = "a",
    normalize: bool = True,
    export: str = "",
) -> List[str]:
    """View historical price of stocks that meet preset

    Parameters
    ----------
    preset_loaded: str
        Preset loaded to filter for tickers
    limit: int
        Number of stocks to display
    start: datetime
        Start datetime to display historical data
    type_candle: str
        Type of candle to display
    normalize : bool
        Boolean to normalize all stock prices using MinMax
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    screen = ticker.Ticker()
    if preset_loaded in finviz_model.d_signals:
        screen.set_filter(signal=finviz_model.d_signals[preset_loaded])

    else:
        preset_filter = configparser.RawConfigParser()
        preset_filter.optionxform = str  # type: ignore
        preset_filter.read(presets_path + preset_loaded + ".ini")

        d_general = preset_filter["General"]
        d_filters = {
            **preset_filter["Descriptive"],
            **preset_filter["Fundamental"],
            **preset_filter["Technical"],
        }

        d_filters = {k: v for k, v in d_filters.items() if v}

        if "Signal" in d_general and d_general["Signal"]:
            screen.set_filter(filters_dict=d_filters, signal=d_general["Signal"])
        else:
            screen.set_filter(filters_dict=d_filters)

    l_stocks = screen.ScreenerView(verbose=0)
    limit_random_stocks = False

    if l_stocks:
        if len(l_stocks) > limit:
            random.shuffle(l_stocks)
            l_stocks = sorted(l_stocks[:limit])
            print(
                "\nThe limit of stocks to compare with are 10. Hence, 10 random similar stocks will be displayed.",
                f"\nThe selected list will be: {', '.join(l_stocks)}",
            )
            limit_random_stocks = True

        df_screener = yf.download(l_stocks, start=start, progress=False, threads=False)[
            d_candle_types[type_candle]
        ][l_stocks]
        df_screener = df_screener[l_stocks]

        if np.any(df_screener.isna()):
            nan_tickers = df_screener.columns[df_screener.isna().sum() >= 1].to_list()
            print(
                f"NaN values found in: {', '.join(nan_tickers)}.  Replacing with zeros."
            )
            df_screener = df_screener.fillna(0)

        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        # This puts everything on 0-1 scale for visualizing
        if normalize:
            mm_scale = MinMaxScaler()
            df_screener = pd.DataFrame(
                mm_scale.fit_transform(df_screener),
                columns=df_screener.columns,
                index=df_screener.index,
            )
        df_screener.plot(ax=ax)
        if limit_random_stocks:
            ax.set_title(
                f"Screener Historical Price using {preset_loaded} on 10 of those stocks"
            )
        else:
            ax.set_title(f"Screener Historical Price using {preset_loaded}")
        ax.set_xlabel("Time")
        ax.set_ylabel(
            f"{['','Normalized'][normalize]} Share Price {['($)',''][normalize]}"
        )
        ax.grid(b=True, which="major", color="#666666", linestyle="-")
        ax.legend(l_stocks, bbox_to_anchor=(1.04, 1), loc="upper left")
        # ensures that the historical data starts from same datapoint
        ax.set_xlim([df_screener.index[0], df_screener.index[-1]])
        plt.gcf().autofmt_xdate()
        fig.tight_layout()
        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "historical",
            df_screener,
        )

        return l_stocks

    print("No screener stocks found with this preset", "\n")
    return []
