from datetime import datetime, timedelta

import plotly.graph_objects as go

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots import helpers
from gamestonk_terminal.common.technical_analysis import volatility_model


def bbands_command(ticker="", length="5", n_std="2", mamode="sma", start="", end=""):
    """Displays chart with bollinger bands [Yahoo Finance]"""

    # Debug
    if cfg.DEBUG:
        # pylint: disable=logging-too-many-args
        logger.debug(
            "ta-bbands %s %s %s %s %s %s",
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
    if not n_std.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    n_std = float(n_std)

    if mamode not in possible_ma:
        raise Exception("Invalid ma entered")

    ticker = ticker.upper()
    df_stock = helpers.load(ticker, start)
    if df_stock.empty:
        raise Exception("Stock ticker is invalid")

    # Retrieve Data
    df_stock = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

    df_ta = volatility_model.bbands(df_stock["Adj Close"], length, n_std, mamode)

    # Output Data
    bbu = df_ta.columns[2].replace("_", " ")
    bbm = df_ta.columns[1].replace("_", " ")
    bbl = df_ta.columns[0].replace("_", " ")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            name=f"{bbu}",
            x=df_ta.index,
            y=df_ta.iloc[:, 2].values,
            opacity=1,
            mode="lines",
            line_color="indigo",
        ),
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
    )
    fig.add_trace(
        go.Scatter(
            name=f"{ticker}",
            x=df_stock.index,
            y=df_stock["Adj Close"],
            line=dict(color="#fdc708", width=2),
            opacity=1,
        ),
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=20),
        template=cfg.PLT_TA_STYLE_TEMPLATE,
        colorway=cfg.PLT_TA_COLORWAY,
        title=f"{ticker} Bollinger Bands ({mamode.upper()})",
        title_x=0.5,
        yaxis_title="Stock Price ($)",
        xaxis_title="Time",
        yaxis=dict(
            fixedrange=False,
        ),
        xaxis=dict(
            rangeslider=dict(visible=False),
            type="date",
        ),
        dragmode="pan",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
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
