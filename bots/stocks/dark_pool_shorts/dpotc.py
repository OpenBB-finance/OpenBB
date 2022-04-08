import logging

import plotly.graph_objects as go
import yfinance as yf
from plotly.subplots import make_subplots

from bots import imps
from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.dark_pool_shorts import finra_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def dpotc_command(ticker: str = ""):
    """Dark pools (ATS) vs OTC data [FINRA]"""

    # Debug user input
    if imps.DEBUG:
        logger.debug("dps dpotc %s", ticker)

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

    ticker = ticker.upper()

    stock = yf.download(ticker, progress=False)
    if stock.empty:
        raise Exception("Stock ticker is invalid")

    # Retrieve data
    ats, otc = finra_model.getTickerFINRAdata(ticker)

    # Debug user output
    if imps.DEBUG:
        logger.debug(ats.to_string())
        logger.debug(otc.to_string())

    # Output data
    title = f"Stocks: [FINRA] Dark Pools (ATS) vs OTC {ticker}"

    if ats.empty and otc.empty:
        raise Exception("Stock ticker is invalid")

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_width=[0.4, 0.6],
        specs=[[{"secondary_y": True}], [{"secondary_y": False}]],
    )

    if not ats.empty and not otc.empty:
        fig.add_trace(
            go.Bar(
                x=ats.index,
                y=(ats["totalWeeklyShareQuantity"] + otc["totalWeeklyShareQuantity"]),
                name="ATS",
                opacity=0.8,
            ),
            row=1,
            col=1,
            secondary_y=False,
        )
        fig.add_trace(
            go.Bar(
                x=otc.index,
                y=otc["totalWeeklyShareQuantity"],
                name="OTC",
                opacity=0.8,
                yaxis="y2",
                offset=0.0001,
            ),
            row=1,
            col=1,
        )

    elif not ats.empty:
        fig.add_trace(
            go.Bar(
                x=ats.index,
                y=(ats["totalWeeklyShareQuantity"] + otc["totalWeeklyShareQuantity"]),
                name="ATS",
                opacity=0.8,
            ),
            row=1,
            col=1,
            secondary_y=False,
        )

    elif not otc.empty:
        fig.add_trace(
            go.Bar(
                x=otc.index,
                y=otc["totalWeeklyShareQuantity"],
                name="OTC",
                opacity=0.8,
                yaxis="y2",
                secondary_y=False,
            ),
            row=1,
            col=1,
        )

    if not ats.empty:
        fig.add_trace(
            go.Scatter(
                name="ATS",
                x=ats.index,
                y=ats["totalWeeklyShareQuantity"] / ats["totalWeeklyTradeCount"],
                line=dict(color="#fdc708", width=2),
                opacity=1,
                showlegend=False,
                yaxis="y2",
            ),
            row=2,
            col=1,
        )

        if not otc.empty:
            fig.add_trace(
                go.Scatter(
                    name="OTC",
                    x=otc.index,
                    y=otc["totalWeeklyShareQuantity"] / otc["totalWeeklyTradeCount"],
                    line=dict(color="#d81aea", width=2),
                    opacity=1,
                    showlegend=False,
                ),
                row=2,
                col=1,
            )
    else:
        fig.add_trace(
            go.Scatter(
                name="OTC",
                x=otc.index,
                y=otc["totalWeeklyShareQuantity"] / otc["totalWeeklyTradeCount"],
                line=dict(color="#d81aea", width=2),
                opacity=1,
                showlegend=False,
            ),
            row=2,
            col=1,
        )
    if imps.PLT_WATERMARK:
        fig.add_layout_image(imps.PLT_WATERMARK)
    fig.update_layout(
        margin=dict(l=20, r=0, t=10, b=20),
        template=imps.PLT_CANDLE_STYLE_TEMPLATE,
        colorway=imps.PLT_TA_COLORWAY,
        title=f"<b>Dark Pools (ATS) vs OTC (Non-ATS) Data for {ticker}</b>",
        title_x=0.025,
        title_font_size=14,
        yaxis3_title="Shares per Trade",
        yaxis_title="Total Weekly Shares",
        xaxis2_title="Weeks",
        font=imps.PLT_FONT,
        yaxis=dict(
            fixedrange=False,
            side="left",
            nticks=20,
        ),
        yaxis2=dict(
            fixedrange=False,
            showgrid=False,
            overlaying="y",
            anchor="x",
            layer="above traces",
        ),
        yaxis3=dict(
            fixedrange=False,
            nticks=10,
        ),
        xaxis=dict(
            rangeslider=dict(visible=False),
            type="date",
            showspikes=True,
            nticks=20,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode="group",
        bargap=0.5,
        bargroupgap=0,
        dragmode="pan",
        hovermode="x unified",
        spikedistance=1,
        hoverdistance=1,
    )

    imagefile = "dps_dpotc.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if imps.INTERACTIVE:
        plt_link = imps.inter_chart(fig, imagefile, callback=False)

    imagefile = imps.image_border(imagefile, fig=fig)

    return {
        "title": title,
        "description": plt_link,
        "imagefile": imagefile,
    }
