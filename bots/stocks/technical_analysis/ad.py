import logging
from datetime import datetime, timedelta

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import bots.config_discordbot as cfg
from bots import helpers
from gamestonk_terminal.common.technical_analysis import volume_model
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def ad_command(ticker="", is_open="False", start="", end=""):
    """Displays chart with accumulation/distribution line [Yahoo Finance]"""

    # Debug
    if cfg.DEBUG:
        logger.debug("ta ad %s %s %s %s", ticker, is_open, start, end)

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

    if is_open in ["false", "False", "FALSE", ""]:
        is_open = False

    if is_open in ["true", "True", "TRUE"]:
        is_open = True

    if is_open not in [True, False]:
        raise Exception("is_open argument has to be true or false")

    ticker = ticker.upper()
    df_stock = helpers.load(ticker, start)
    if df_stock.empty:
        raise Exception("Stock ticker is invalid")

    # Retrieve Data
    df_stock = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

    divisor = 1_000_000
    df_vol = df_stock["Volume"].dropna()
    df_vol = df_vol.values / divisor
    df_ta = volume_model.ad(df_stock, is_open)
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
            name="A/D [M]",
            x=df_ta.index,
            y=df_ta.iloc[:, 0].values,
            line=dict(width=2),
            opacity=1,
        ),
        row=3,
        col=1,
    )
    fig.add_hline(
        y=0,
        fillcolor="grey",
        opacity=1,
        layer="below",
        line_width=3,
        line=dict(color="grey", dash="dash"),
        row=3,
        col=1,
    )
    if cfg.PLT_WATERMARK:
        fig.add_layout_image(cfg.PLT_WATERMARK)
    fig.update_layout(
        margin=dict(l=10, r=0, t=40, b=20),
        template=cfg.PLT_TA_STYLE_TEMPLATE,
        colorway=cfg.PLT_TA_COLORWAY,
        title=f"{ticker} AD",
        title_x=0.4,
        yaxis_title="Stock Price ($)",
        yaxis2_title="Volume [M]",
        yaxis3_title="A/D [M]",
        font=cfg.PLT_FONT,
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

    imagefile = "ta_ad.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if cfg.INTERACTIVE:
        plt_link = helpers.inter_chart(fig, imagefile, callback=False)

    fig.update_layout(
        width=800,
        height=500,
    )

    imagefile = helpers.image_border(imagefile, fig=fig)

    return {
        "title": f"Stocks: Accumulation/Distribution Line {ticker}",
        "description": plt_link,
        "imagefile": imagefile,
    }
