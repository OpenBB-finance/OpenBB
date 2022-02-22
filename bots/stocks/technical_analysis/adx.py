from datetime import datetime, timedelta

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots import helpers
from gamestonk_terminal.common.technical_analysis import trend_indicators_model


def adx_command(ticker="", length="14", scalar="100", drift="1", start="", end=""):
    """Displays chart with average directional movement index [Yahoo Finance]"""

    # Debug
    if cfg.DEBUG:
        # pylint: disable=logging-too-many-args
        logger.debug(
            "ta-adx %s %s %s %s %s",
            ticker,
            length,
            scalar,
            drift,
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
    if not scalar.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    scalar = float(scalar)
    if not drift.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    drift = float(drift)

    ticker = ticker.upper()
    df_stock = helpers.load(ticker, start)
    if df_stock.empty:
        raise Exception("Stock ticker is invalid")

    # Retrieve Data
    df_stock = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

    df_ta = trend_indicators_model.adx(
        df_stock["High"],
        df_stock["Low"],
        df_stock["Adj Close"],
        length,
        scalar,
        drift,
    )

    # Output Data
    leg_adx = df_ta.columns[0].replace("_", " ")
    neg_di = df_ta.columns[1].replace("_", " ")
    pos_di = df_ta.columns[2].replace("_", " ")

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.07,
        row_width=[0.5, 0.5],
    )
    fig.add_trace(
        go.Scatter(
            name=ticker,
            x=df_stock.index,
            y=df_stock["Adj Close"].values,
            line=dict(color="#fdc708", width=2),
            opacity=1,
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            mode="lines",
            name=f"ADX ({leg_adx})",
            x=df_ta.index,
            y=df_ta.iloc[:, 0].values,
            opacity=1,
            line=dict(width=2),
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            mode="lines",
            name=f"+DI ({pos_di})",
            x=df_ta.index,
            y=df_ta.iloc[:, 1].values,
            opacity=1,
            line=dict(width=1),
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            mode="lines",
            name=f"- DI ({neg_di})",
            x=df_ta.index,
            y=df_ta.iloc[:, 2].values,
            opacity=1,
            line=dict(width=1),
        ),
        row=2,
        col=1,
    )
    fig.add_hline(
        y=25,
        fillcolor="grey",
        opacity=1,
        layer="below",
        line_width=3,
        line=dict(color="grey", dash="dash"),
        row=2,
        col=1,
    )
    fig.update_layout(
        margin=dict(l=0, r=20, t=30, b=20),
        template=cfg.PLT_TA_STYLE_TEMPLATE,
        colorway=cfg.PLT_TA_COLORWAY,
        title=f"Average Directional Movement Index (ADX) on {ticker}",
        title_x=0.3,
        yaxis_title="Stock Price ($)",
        yaxis=dict(
            fixedrange=False,
        ),
        xaxis=dict(
            rangeslider=dict(visible=False),
            type="date",
        ),
        dragmode="pan",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    config = dict({"scrollZoom": True})
    imagefile = "ta_adx.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if cfg.INTERACTIVE:
        html_ran = helpers.uuid_get()
        fig.write_html(f"in/adx_{html_ran}.html", config=config)
        plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/adx_{html_ran}.html)"

    fig.update_layout(
        width=800,
        height=500,
    )

    imagefile = helpers.image_border(imagefile, fig=fig)

    return {
        "title": f"Stocks: Average-Directional-Movement-Index {ticker}",
        "description": plt_link,
        "imagefile": imagefile,
    }
