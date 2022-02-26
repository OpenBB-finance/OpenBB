from datetime import datetime, timedelta

from matplotlib import pyplot as plt

import bots.config_discordbot as cfg
import bots.helpers
from bots.config_discordbot import logger
from bots.helpers import image_border
from gamestonk_terminal import config_plot as cfp
from gamestonk_terminal.common.technical_analysis import custom_indicators_model
from gamestonk_terminal.helper_funcs import plot_autoscale


def fib_command(ticker="", start="", end=""):
    """Displays chart with fibonacci retracement [Yahoo Finance]"""

    # Debug
    if cfg.DEBUG:
        logger.debug(
            "ta-fib %s %s %s",
            ticker,
            start,
            end,
        )

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

    if start == "":
        start = datetime.now() - timedelta(days=365)
        f_start = None
    else:
        start = datetime.strptime(start, cfg.DATE_FORMAT)
        f_start = start

    if end == "":
        end = datetime.now()
        f_end = None
    else:
        end = datetime.strptime(end, cfg.DATE_FORMAT)
        f_end = None

    ticker = ticker.upper()
    df_stock = bots.helpers.load(ticker, start)
    if df_stock.empty:
        raise Exception("Stock ticker is invalid")

    # Retrieve Data
    df_stock = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

    start = start.strftime("%Y-%m-%d")
    end = end.strftime("%Y-%m-%d")
    (
        df_fib,
        min_date,
        max_date,
        min_pr,
        max_pr,
    ) = custom_indicators_model.calculate_fib_levels(df_stock, 120, f_start, f_end)

    levels = df_fib.Price
    fig, ax = plt.subplots(figsize=(plot_autoscale()), dpi=cfp.PLOT_DPI)

    ax.plot(df_stock["Adj Close"], "b")
    ax.plot([min_date, max_date], [min_pr, max_pr], c="k")

    for i in levels:
        ax.axhline(y=i, c="g", alpha=0.5)

    for i in range(5):
        ax.fill_between(df_stock.index, levels[i], levels[i + 1], alpha=0.6)

    ax.set_ylabel("Price")
    ax.set_title(f"Fibonacci Support for {ticker.upper()}")
    ax.set_xlim(df_stock.index[0], df_stock.index[-1])

    ax1 = ax.twinx()
    ax1.set_ylim(ax.get_ylim())
    ax1.set_yticks(levels)
    ax1.set_yticklabels([0, 0.235, 0.382, 0.5, 0.618, 1])

    plt.gcf().autofmt_xdate()
    fig.tight_layout(pad=1)
    imagefile = "ta_fib.png"
    plt.savefig(imagefile)

    imagefile = image_border(imagefile)

    return {
        "title": f"Stocks: Fibonacci-Retracement-Levels {ticker}",
        "imagefile": imagefile,
    }
