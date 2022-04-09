import io
import logging
from datetime import datetime, timedelta

import numpy as np
from matplotlib import pyplot as plt

from bots import config_discordbot as cfg
from bots.helpers import image_border, load
from openbb_terminal.common.technical_analysis import momentum_model
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import plot_autoscale

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def cg_command(ticker="", length="14", start="", end=""):
    """Displays chart with centre of gravity [Yahoo Finance]"""

    # Debug
    if cfg.DEBUG:
        logger.debug(
            "ta-cg %s %s %s %s",
            ticker,
            length,
            start,
            end,
        )

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

    if start == "":
        start = datetime.now() - timedelta(days=365)
    else:
        start = datetime.strptime(start, cfg.DATE_FORMAT)

    if end == "":
        end = datetime.now()
    else:
        end = datetime.strptime(end, cfg.DATE_FORMAT)

    if not length.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    length = float(length)

    ticker = ticker.upper()
    df_stock = load(ticker, start)
    if df_stock.empty:
        raise Exception("Stock ticker is invalid")

    # Retrieve Data
    df_stock = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]
    df_close = df_stock["Adj Close"]
    df_close.columns = ["values"]
    df_ta = momentum_model.cg(df_close, length)
    df_ta = df_ta.fillna(0.0)

    # Output Data
    fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax = axes[0]
    ax.set_title(f"{ticker} Centre of Gravity")
    ax.plot(df_stock.index, df_stock["Adj Close"].values, lw=1)
    ax.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax.set_ylabel("Share Price ($)")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")

    ax2 = axes[1]
    ax2.plot(df_ta.index, df_ta.values, lw=2, label="CG")
    # shift cg 1 bar forward for signal
    signal = df_ta.values
    signal = np.roll(signal, 1)
    ax2.plot(df_ta.index, signal, lw=1, label="Signal")
    ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax2.grid(b=True, which="major", color="#666666", linestyle="-")

    plt.gcf().autofmt_xdate()
    fig.tight_layout(pad=1)
    plt.legend()
    imagefile = "ta_cg.png"
    dataBytesIO = io.BytesIO()
    plt.savefig(dataBytesIO)
    plt.close("all")

    dataBytesIO.seek(0)
    imagefile = image_border(imagefile, base64=dataBytesIO)

    return {
        "title": f"Stocks: Center-of-Gravity {ticker}",
        "imagefile": imagefile,
    }
