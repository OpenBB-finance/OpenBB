import logging

import plotly.graph_objects as go
import yfinance as yf
from plotly.subplots import make_subplots

import bots.config_discordbot as cfg
from bots import helpers
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.stocks.dark_pool_shorts import stockgrid_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def psi_command(ticker: str = ""):
    """Price vs short interest volume [Stockgrid]"""

    # Debug user input
    if cfg.DEBUG:
        logger.debug("dps psi %s", ticker)

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

    ticker = ticker.upper()

    stock = yf.download(ticker, progress=False)
    if stock.empty:
        raise Exception("Stock ticker is invalid")

    # Retrieve data
    df, prices = stockgrid_model.get_short_interest_volume(ticker)

    # Debug user output
    if cfg.DEBUG:
        logger.debug(df.to_string())

    # Output data
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_width=[0.3, 0.6],
        specs=[[{"secondary_y": True}], [{"secondary_y": False}]],
    )
    fig.add_trace(
        go.Scatter(
            name=ticker,
            x=df["date"].values,
            y=prices[len(prices) - len(df) :],
            line=dict(color="#fdc708", width=2),
            opacity=1,
            showlegend=False,
        ),
        row=1,
        col=1,
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            x=df["date"],
            y=df["total_volume"] / 1_000_000,
            name="Total Volume",
            yaxis="y2",
        ),
        row=1,
        col=1,
        secondary_y=True,
    )
    fig.add_trace(
        go.Bar(
            x=df["date"],
            y=df["short_volume"] / 1_000_000,
            name="Short Volume",
            yaxis="y2",
        ),
        row=1,
        col=1,
        secondary_y=True,
    )
    fig.add_trace(
        go.Scatter(
            name="Short Vol. %",
            x=df["date"].values,
            y=100 * df["short_volume%"],
            line=dict(width=2),
            opacity=1,
            showlegend=False,
        ),
        row=2,
        col=1,
        secondary_y=False,
    )
    if cfg.PLT_WATERMARK:
        fig.add_layout_image(cfg.PLT_WATERMARK)
    fig.update_traces(hovertemplate="%{y:.2f}")
    fig.update_xaxes(showspikes=True, spikesnap="cursor", spikemode="across")
    fig.update_yaxes(showspikes=True, spikethickness=2)
    fig.update_layout(
        margin=dict(l=10, r=0, t=40, b=20),
        template=cfg.PLT_TA_STYLE_TEMPLATE,
        colorway=cfg.PLT_TA_COLORWAY,
        title=f"Price vs Short Volume Interest for {ticker}",
        title_x=0.45,
        yaxis_title="Stock Price ($)",
        yaxis2_title="FINRA Volume [M]",
        yaxis3_title="Short Vol. %",
        font=cfg.PLT_FONT,
        yaxis=dict(
            side="right",
            fixedrange=False,
            titlefont=dict(color="#fdc708"),
            tickfont=dict(color="#fdc708"),
            nticks=20,
        ),
        yaxis2=dict(
            side="left",
            fixedrange=False,
            anchor="x",
            overlaying="y",
            titlefont=dict(color="#d81aea"),
            tickfont=dict(color="#d81aea"),
            nticks=20,
        ),
        yaxis3=dict(
            fixedrange=False,
            titlefont=dict(color="#9467bd"),
            tickfont=dict(color="#9467bd"),
            nticks=20,
        ),
        xaxis=dict(
            rangeslider=dict(visible=False),
            type="date",
        ),
        dragmode="pan",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        spikedistance=1000,
        hoverdistance=100,
    )

    imagefile = "dps_psi.png"

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
        "title": f"Stocks: [Stockgrid] Price vs Short Interest Volume {ticker}",
        "description": plt_link,
        "imagefile": imagefile,
    }
