from datetime import datetime, timedelta

import plotly.graph_objects as go

import bots.config_discordbot as cfg
from bots import helpers, load_candle
from bots.config_discordbot import logger
from gamestonk_terminal.common.technical_analysis import volatility_model


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
    news: bool = False,
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
        past_days += 30 if news else 0
        if start == "":
            ta_start = datetime.now() - timedelta(days=past_days)
        else:
            ta_start = datetime.strptime(start, cfg.DATE_FORMAT) - timedelta(
                days=past_days
            )
        past_days += 2 if news else 10
        ta_start = load_candle.local_tz(ta_start)

    if not length.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    length = float(length)
    n_std = float(n_std)

    if mamode not in possible_ma:
        raise Exception("Invalid ma entered")

    # Retrieve Data
    df_stock, start, end = load_candle.stock_data(
        ticker=ticker,
        interval=interval,
        past_days=past_days,
        extended_hours=extended_hours,
        start=start,
        end=end,
        heikin_candles=heikin_candles,
    )

    if df_stock.empty:
        return Exception("No Data Found")

    df_ta = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]
    df_ta = volatility_model.bbands(df_ta["Adj Close"], length, n_std, mamode)

    # Output Data
    if interval != 1440:
        ta_end = load_candle.local_tz(end)
        df_ta = df_ta.loc[(df_ta.index >= ta_start) & (df_ta.index < ta_end)]

    fig = load_candle.candle_fig(df_ta, ticker, interval, extended_hours, news)

    fig.add_trace(
        go.Scatter(
            name=f"{df_ta.columns[0].replace('_', ' ')}",
            x=df_ta.index,
            y=df_ta.iloc[:, 0].values,
            opacity=1,
            mode="lines",
            line_color="indigo",
        ),
        secondary_y=True,
    )
    fig.add_trace(
        go.Scatter(
            name=f"{df_ta.columns[2].replace('_', ' ')}",
            x=df_ta.index,
            y=df_ta.iloc[:, 2].values,
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
            name=f"{df_ta.columns[1].replace('_', ' ')}",
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
        title=f"{ticker.upper()} Bollinger Bands ({mamode.upper()})",
        title_x=0.1,
        dragmode="pan",
    )
    config = dict({"scrollZoom": True})
    imagefile = "ta_bbands.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if cfg.INTERACTIVE:
        html_ran = helpers.uuid_get()
        fig.write_html(f"in/bbands_{html_ran}.html", config=config)
        plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/bbands_{html_ran}.html)"

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
