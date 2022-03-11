import configparser
import random
from datetime import datetime, timedelta

import yfinance as yf
from finvizfinance.screener import ticker
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.helpers import image_border
from bots.stocks.screener import screener_options as so
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.screener import finviz_model

# pylint:disable=no-member


def historical_command(signal: str = "", start=""):
    """Displays historical price comparison between similar companies [Yahoo Finance]"""

    # Debug user input
    if cfg.DEBUG:
        logger.debug("scr-historical %s %s", signal, start)

    # Check for argument
    if signal not in so.d_signals_desc:
        raise Exception("Invalid preset selected!")

    register_matplotlib_converters()

    screen = ticker.Ticker()

    if signal in finviz_model.d_signals:
        screen.set_filter(signal=finviz_model.d_signals[signal])

    else:
        preset_filter = configparser.RawConfigParser()
        preset_filter.optionxform = str  # type: ignore
        preset_filter.read(so.presets_path + signal + ".ini")

        d_general = preset_filter["General"]
        d_filters = {
            **preset_filter["Descriptive"],
            **preset_filter["Fundamental"],
            **preset_filter["Technical"],
        }

        d_filters = {k: v for k, v in d_filters.items() if v}

        if d_general["Signal"]:
            screen.set_filter(filters_dict=d_filters, signal=d_general["Signal"])
        else:
            screen.set_filter(filters_dict=d_filters)

    if start == "":
        start = datetime.now() - timedelta(days=365)
    else:
        start = datetime.strptime(start, cfg.DATE_FORMAT)

    # Output Data
    l_min = []
    l_leg = []
    l_stocks = screen.screener_view(verbose=0)

    if len(l_stocks) > 10:
        description = (
            "\nThe limit of stocks to compare with are 10. Hence, 10 random similar stocks will be displayed."
            "\nThe selected list will be: "
        )
        random.shuffle(l_stocks)
        l_stocks = sorted(l_stocks[:10])
        description = description + (", ".join(l_stocks))
        logger.debug(description)

    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

    while l_stocks:
        l_parsed_stocks = []
        for symbol in l_stocks:
            try:
                df_similar_stock = yf.download(
                    symbol,
                    start=datetime.strftime(start, "%Y-%m-%d"),
                    progress=False,
                    threads=False,
                )
                if not df_similar_stock.empty:
                    plt.plot(
                        df_similar_stock.index,
                        df_similar_stock["Adj Close"].values,
                    )
                    l_min.append(df_similar_stock.index[0])
                    l_leg.append(symbol)

                l_parsed_stocks.append(symbol)
            except Exception as e:
                error = (
                    f"{e}\nDisregard previous error, which is due to API Rate limits from Yahoo Finance. "
                    f"Because we like '{symbol}', and we won't leave without getting data from it."
                )

                return {
                    "title": "ERROR Stocks: [Yahoo Finance] Historical Screener",
                    "description": error,
                }

        for parsed_stock in l_parsed_stocks:
            l_stocks.remove(parsed_stock)

    if signal:
        plt.title(
            f"Screener Historical Price using {finviz_model.d_signals[signal]} signal"
        )
    else:
        plt.title(f"Screener Historical Price using {signal} preset")

    plt.xlabel("Time")
    plt.ylabel("Share Price ($)")
    plt.legend(l_leg)
    plt.grid(b=True, which="major", color="#666666", linestyle="-")
    plt.minorticks_on()
    plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    # ensures that the historical data starts from same datapoint
    plt.xlim([max(l_min), df_similar_stock.index[-1]])

    imagefile = "scr_historical.png"
    plt.savefig(imagefile)
    imagefile = image_border(imagefile)

    return {
        "title": "Stocks: [Yahoo Finance] Historical Screener",
        "description": description,
        "imagefile": imagefile,
    }
