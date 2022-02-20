from datetime import datetime, timedelta

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots import helpers
from gamestonk_terminal.stocks.dark_pool_shorts import sec_model


def ftd_command(ticker: str = "", start="", end=""):
    """Fails-to-deliver data [SEC]"""

    # Debug user input
    if cfg.DEBUG:
        logger.debug("dps-ftd %s %s %s", ticker, start, end)

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

    ticker = ticker.upper()

    if start == "":
        start = datetime.now() - timedelta(days=365)
    else:
        start = datetime.strptime(start, cfg.DATE_FORMAT)

    if end == "":
        end = datetime.now()
    else:
        end = datetime.strptime(end, cfg.DATE_FORMAT)

    # Retrieve data
    ftds_data = sec_model.get_fails_to_deliver(ticker, start, end, 0)

    # Debug user output
    if cfg.DEBUG:
        logger.debug(ftds_data.to_string())

    stock = helpers.load(ticker, start)
    stock_ftd = stock[stock.index > start]
    stock_ftd = stock_ftd[stock_ftd.index < end]

    # Output data
    fig = make_subplots(shared_xaxes=True, specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            name=ticker,
            x=stock_ftd.index,
            y=stock_ftd["Adj Close"],
            line=dict(color="#fdc708", width=2),
            opacity=1,
            showlegend=False,
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            name="FTDs",
            x=ftds_data["SETTLEMENT DATE"],
            y=ftds_data["QUANTITY (FAILS)"] / 1000,
            opacity=1,
        ),
        secondary_y=True,
    )
    # Set y-axes titles
    fig.update_yaxes(title_text="<b>Shares</b> [K]", secondary_y=True)
    fig.update_layout(
        margin=dict(l=0, r=20, t=30, b=20),
        template=cfg.PLT_TA_STYLE_TEMPLATE,
        colorway=cfg.PLT_TA_COLORWAY,
        title=f"{ticker}",
        title_x=0.5,
        yaxis_title="<b>Stock Price</b> ($)",
        yaxis=dict(
            side="right",
            fixedrange=False,
        ),
        xaxis=dict(
            rangeslider=dict(visible=False),
            type="date",
            fixedrange=False,
        ),
        xaxis2=dict(
            rangeslider=dict(visible=False),
            type="date",
            fixedrange=False,
        ),
        dragmode="pan",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis2=dict(
            side="left",
            position=0.15,
            fixedrange=False,
        ),
        hovermode="x unified",
    )
    config = dict({"scrollZoom": True})
    imagefile = "dps_ftd.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if cfg.INTERACTIVE:
        html_ran = helpers.uuid_get()
        fig.write_html(f"in/ftds_{html_ran}.html", config=config)
        plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/ftds_{html_ran}.html)"

    fig.update_layout(
        width=800,
        height=500,
    )

    imagefile = helpers.image_border(imagefile, fig=fig)

    return {
        "title": f"Stocks: [SEC] Failure-to-deliver {ticker}",
        "description": plt_link,
        "imagefile": imagefile,
    }
