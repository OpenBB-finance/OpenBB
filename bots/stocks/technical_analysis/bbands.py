from datetime import datetime, timedelta

import plotly.graph_objects as go
from gamestonk_terminal.common.technical_analysis import volatility_model

import bots.config_discordbot as cfg
from bots import helpers, load
from bots.config_discordbot import logger


def bbands_command(
    ticker="",
    interval: int = 15,
    past_days: int = 0,
    length="20",
    n_std: float = 2.0,
    mamode="sma",
    start="",
    end="",
    extended_hours: bool = False,
    heikin_candles: bool = False,
):
    """Displays chart with bollinger bands [Yahoo Finance]"""
    # Debug
    if cfg.DEBUG:
        # pylint: disable=logging-too-many-args
        logger.debug(
            "ta bbands %s %s %s %s %s %s",
            ticker,
            length,
            n_std,
            mamode,
            start,
            end,
        )

    # Check for argument
    possible_ma = [
        "dema",
        "ema",
        "fwma",
        "hma",
        "linreg",
        "midpoint",
        "pwma",
        "rma",
        "sinwma",
        "sma",
        "swma",
        "t3",
        "tema",
        "trima",
        "vidya",
        "wma",
        "zlma",
    ]

    if ticker == "":
        raise Exception("Stock ticker is required")

    if datetime.today().strftime("%A") == "Saturday" and past_days <= 1:
        past_days = 1
    if datetime.today().strftime("%A") == "Sunday" and past_days <= 2:
        past_days = 2

    if interval != 1440:
        if start == "":
            bb_start = datetime.now() - timedelta(days=past_days)
        else:
            bb_start = datetime.strptime(start, cfg.DATE_FORMAT) - timedelta(
                days=past_days
            )
        past_days += 1
        bb_start = load.local_tz(bb_start).strftime("%Y-%m-%d")

    if not length.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    length = float(length)
    n_std = float(n_std)

    if mamode not in possible_ma:
        raise Exception("Invalid ma entered")

    ticker = ticker.upper()

    df_stock, start, end = load.candle_load(
        ticker=ticker,
        interval=interval,
        past_days=past_days,
        extended_hours=extended_hours,
        start=start,
        end=end,
        heikin_candles=heikin_candles,
    )

    if df_stock.empty:
        raise Exception("Stock ticker is invalid")

    # Retrieve Data
    bb_end = load.local_tz(end).strftime("%Y-%m-%d")
    df_ta = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]
    df_ta = volatility_model.bbands(df_ta["Adj Close"], length, n_std, mamode)

    # Output Data
    bbu = df_ta.columns[2].replace("_", " ")
    bbm = df_ta.columns[1].replace("_", " ")
    bbl = df_ta.columns[0].replace("_", " ")
    df_stock = df_stock.loc[bb_start:bb_end]
    fig = load.candle_fig(df_stock, ticker, interval, extended_hours)

    fig.add_trace(
        go.Scatter(
            name=f"{bbu}",
            x=df_ta.index,
            y=df_ta.iloc[:, 2].values,
            opacity=1,
            mode="lines",
            line_color="indigo",
        ),
        secondary_y=True,
    )
    fig.add_trace(
        go.Scatter(
            name=f"{bbl}",
            x=df_ta.index,
            y=df_ta.iloc[:, 0].values,
            opacity=1,
            mode="lines",
            line_color="indigo",
            fill="tonexty",
            fillcolor="rgba(74, 0, 128, 0.2)",
        ),
        secondary_y=True,
    )
    fig.add_trace(
        go.Scatter(
            name=f"{bbm}",
            x=df_ta.index,
            y=df_ta.iloc[:, 1].values,
            opacity=1,
            line=dict(
                width=1.5,
                dash="dash",
            ),
        ),
        secondary_y=True,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=20),
        template=cfg.PLT_TA_STYLE_TEMPLATE,
        colorway=cfg.PLT_TA_COLORWAY,
        title=f"{ticker} Bollinger Bands ({mamode.upper()})",
        title_x=0.1,
        yaxis_title="Stock Price ($)",
        dragmode="pan",
    )
    config = dict({"scrollZoom": True})
    imagefile = "ta_bbands.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if cfg.INTERACTIVE:
        html_ran = helpers.uuid_get()
        fig.write_html(f"in/cci_{html_ran}.html", config=config)
        plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/cci_{html_ran}.html)"

    fig.update_layout(
        width=800,
        height=500,
    )

    imagefile = helpers.image_border(imagefile, fig=fig)

    return {
        "title": f"Stocks: Bollinger-Bands {ticker}",
        "description": plt_link,
        "imagefile": imagefile,
    }
