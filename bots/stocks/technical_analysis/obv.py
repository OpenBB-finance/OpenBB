from datetime import datetime, timedelta

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots import helpers
from gamestonk_terminal.common.technical_analysis import volume_model


def obv_command(ticker="", start="", end=""):
    """Displays chart with on balance volume [Yahoo Finance]"""

    # Debug
    if cfg.DEBUG:
        logger.debug(
            "ta-obv %s %s %s",
            ticker,
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

    ticker = ticker.upper()
    df_stock = helpers.load(ticker, start)
    if df_stock.empty:
        raise Exception("Stock ticker is invalid")

    # Retrieve Data
    df_stock = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

    # Output Data
    divisor = 1_000_000
    df_vol = df_stock["Volume"].dropna()
    df_vol = df_vol.values / divisor
    df_ta = volume_model.obv(df_stock)
    df_cal = df_ta.values
    df_cal = df_cal / divisor

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_width=[0.2, 0.2, 0.2],
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
    colors = [
        "green" if row.Open < row["Adj Close"] else "red"
        for _, row in df_stock.iterrows()
    ]
    fig.add_trace(
        go.Bar(
            x=df_stock.index,
            y=df_vol,
            name="Volume [M]",
            marker_color=colors,
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            name="OBC [M]",
            x=df_ta.index,
            y=df_ta.iloc[:, 0].values,
            line=dict(width=2),
            opacity=1,
        ),
        row=3,
        col=1,
    )
    fig.update_layout(
        margin=dict(l=10, r=0, t=40, b=20),
        template=cfg.PLT_TA_STYLE_TEMPLATE,
        colorway=cfg.PLT_TA_COLORWAY,
        title=f"{ticker} OBV",
        title_x=0.4,
        yaxis_title="Stock Price ($)",
        yaxis2_title="Volume [M]",
        yaxis3_title="OBV [M]",
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
    imagefile = "ta_obv.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if cfg.INTERACTIVE:
        html_ran = helpers.uuid_get()
        fig.write_html(f"in/obv_{html_ran}.html", config=config)
        plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/obv_{html_ran}.html)"

    fig.update_layout(
        width=800,
        height=500,
    )
    imagefile = helpers.image_border(imagefile, fig=fig)

    return {
        "title": f"Stocks: On-Balance-Volume {ticker}",
        "description": plt_link,
        "imagefile": imagefile,
    }
