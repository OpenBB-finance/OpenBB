import logging
from datetime import datetime, timedelta

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from bots import imps
from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.dark_pool_shorts import sec_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def ftd_command(ticker: str = "", start="", end=""):
    """Fails-to-deliver data [SEC]"""

    # Debug user input
    if imps.DEBUG:
        logger.debug("dps ftd %s %s %s", ticker, start, end)

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

    ticker = ticker.upper()

    if start == "":
        start = datetime.now() - timedelta(days=365)
    else:
        start = datetime.strptime(start, imps.DATE_FORMAT)

    if end == "":
        end = datetime.now()
    else:
        end = datetime.strptime(end, imps.DATE_FORMAT)

    # Retrieve data
    ftds_data = sec_model.get_fails_to_deliver(ticker, start, end, 0)

    # Debug user output
    if imps.DEBUG:
        logger.debug(ftds_data.to_string())

    stock = imps.load(ticker, start)
    stock_ftd = stock[stock.index > start]
    stock_ftd = stock_ftd[stock_ftd.index < end]

    ftd_opacity = 0.4 if (start > (datetime.now() - timedelta(days=30))) else 0.6
    ftd_opacity = (
        ftd_opacity if (start > (datetime.now() - timedelta(days=120))) else 0.9
    )

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
        secondary_y=True,
    )
    fig.add_trace(
        go.Bar(
            name="FTDs",
            x=ftds_data["SETTLEMENT DATE"],
            y=ftds_data["QUANTITY (FAILS)"],
            yaxis="y2",
            opacity=ftd_opacity,
        ),
        secondary_y=False,
    )
    if imps.PLT_WATERMARK:
        fig.add_layout_image(imps.PLT_WATERMARK)

    ftds_scale = imps.chart_volume_scaling(ftds_data["QUANTITY (FAILS)"], 2)

    fig.update_layout(
        margin=dict(l=0, r=20, t=30, b=20),
        template=imps.PLT_TA_STYLE_TEMPLATE,
        colorway=imps.PLT_TA_COLORWAY,
        title=f"{ticker} Failed-to-deliver",
        title_x=0.5,
        yaxis2_title="<b>Stock Price</b>",
        font=imps.PLT_FONT,
        yaxis2=dict(
            side="left",
            fixedrange=False,
            layer="above traces",
            overlaying="y",
            titlefont=dict(color="#fdc708"),
            tickfont=dict(
                color="#fdc708",
                size=13,
            ),
            nticks=20,
        ),
        yaxis=dict(
            side="right",
            position=0.15,
            fixedrange=False,
            showgrid=False,
            title_text="",
            titlefont=dict(color="#d81aea"),
            tickfont=dict(
                color="#d81aea",
                size=13,
            ),
            nticks=20,
            range=ftds_scale["range"],
            tickvals=ftds_scale["ticks"],
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
        hovermode="x unified",
    )

    imagefile = "dps_ftd.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if imps.INTERACTIVE:
        plt_link = imps.inter_chart(fig, imagefile, callback=False)

    imagefile = imps.image_border(imagefile, fig=fig)

    return {
        "title": f"Stocks: [SEC] Failure-to-deliver {ticker}",
        "description": plt_link,
        "imagefile": imagefile,
    }
