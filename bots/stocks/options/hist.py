import logging

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from bots import imps
from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.options import syncretism_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def hist_command(
    ticker: str = "",
    expiry: str = "",
    strike: float = 10,
    opt_type: str = "",
    greek: str = "",
):
    """Plot historical option prices

    Parameters
    ----------
    ticker: str
        Stock ticker
    expiry: str
        expiration date
    strike: float
        Option strike price
    put: bool
        Calls for call
        Puts for put
    """

    # Debug
    if imps.DEBUG:
        logger.info(
            "opt grhist %s %s %s %s %s", ticker, strike, opt_type, expiry, greek
        )

    # Check for argument
    if ticker is None:
        raise Exception("Stock ticker is required")

    if opt_type == "Puts":
        put = bool(True)
    if opt_type == "Calls":
        put = bool(False)
    chain_id = ""

    df_hist = syncretism_model.get_historical_greeks(
        ticker, expiry, chain_id, strike, put
    )
    title = f"\n{ticker.upper()} {strike} {opt_type} expiring {expiry} Historical {greek.upper()}"
    # Output data
    fig = make_subplots(shared_xaxes=True, specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            name=ticker.upper(),
            x=df_hist.index,
            y=df_hist.price,
            line=dict(color="#fdc708", width=2),
            opacity=1,
        ),
    )
    fig.add_trace(
        go.Scatter(
            name="Premium",
            x=df_hist.index,
            y=df_hist["premium"],
            opacity=1,
            yaxis="y2",
        ),
    )
    if greek:
        fig.add_trace(
            go.Scatter(
                name=f"{greek.upper()}",
                x=df_hist.index,
                y=df_hist[greek],
                opacity=1,
                yaxis="y3",
            ),
        )
    if imps.PLT_WATERMARK:
        fig.add_layout_image(imps.PLT_WATERMARK)
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=20),
        template=imps.PLT_TA_STYLE_TEMPLATE,
        colorway=imps.PLT_TA_COLORWAY,
        title=f"<b>{title}</b>",
        title_x=0.01,
        title_font_size=12,
        yaxis_title="<b>Stock Price</b>",
        font=imps.PLT_FONT,
        yaxis=dict(
            side="right",
            fixedrange=False,
            titlefont=dict(color="#fdc708"),
            tickfont=dict(color="#fdc708"),
            showgrid=False,
            position=0.02,
            nticks=20,
        ),
        xaxis=dict(
            rangeslider=dict(visible=False),
            type="date",
            fixedrange=False,
            domain=[0.037, 1],
        ),
        xaxis2=dict(
            rangeslider=dict(visible=False),
            type="date",
            fixedrange=False,
        ),
        xaxis3=dict(
            rangeslider=dict(visible=False),
            type="date",
            fixedrange=False,
        ),
        dragmode="pan",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, font_size=8, xanchor="right", x=1
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
            side="left",
            position=0,
            fixedrange=False,
            showgrid=False,
            overlaying="y",
            titlefont=dict(color="#00e6c3"),
            tickfont=dict(color="#00e6c3"),
            nticks=20,
        ),
        hovermode="x unified",
    )

    imagefile = "opt_hist.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if imps.INTERACTIVE:
        plt_link = imps.inter_chart(fig, imagefile, callback=False)

    imagefile = imps.image_border(imagefile, fig=fig)

    return {
        "title": f"{ticker.upper()} {strike} {opt_type} expiring {expiry} Historical",
        "description": plt_link,
        "imagefile": imagefile,
    }
