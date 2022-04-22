import logging
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go

from bots import imps
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import fred_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def cpi_command(start=""):
    """Displays Consumer Prices Index (CPI)"""

    # Debug
    if imps.DEBUG:
        logger.debug(
            "econ cpi %s",
            start,
        )

    if start == "":
        start = datetime.now() - timedelta(days=900)
    else:
        start = datetime.strptime(start, imps.DATE_FORMAT)

    # Retrieve data
    df_d = ("date", "CPI")
    series_ids = list(df_d)
    data = pd.DataFrame()

    for s_id in series_ids:
        data = pd.concat(
            [
                data,
                pd.DataFrame(
                    fred_model.get_series_data("CPIAUCSL", start), columns=[s_id]
                ),
            ],
            axis=1,
        )

    df = data.dropna()

    # Check for argument
    if df.empty:
        raise Exception("No available data found")

    data["date"] = pd.to_datetime(data["date"])
    data["CPI"] = data["CPI"].astype(float)
    data = data.drop(columns=["CPI"])
    end = datetime.now() + timedelta(days=30)

    # Debug user output
    if imps.DEBUG:
        logger.debug(df.to_string())

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["CPI"],
        )
    )

    if imps.PLT_WATERMARK:
        fig.add_layout_image(imps.PLT_WATERMARK)

    fig.update_xaxes(dtick="M2", tickformat="%b\n%Y")
    fig.update_layout(
        xaxis_range=[df.index[0], end],
        margin=dict(l=0, r=0, t=40, b=50),
        template=imps.PLT_SCAT_STYLE_TEMPLATE,
        colorway=imps.PLT_TA_COLORWAY,
        title="CPI Monthly",
        title_x=0.5,
        yaxis_title="Consumer Prices",
        legend_title="",
        font=imps.PLT_FONT,
        yaxis=dict(
            fixedrange=False,
            nticks=20,
        ),
        xaxis=dict(
            rangeslider=dict(visible=False),
            type="date",
        ),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        dragmode="pan",
    )

    imagefile = "econ-cpi.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if imps.INTERACTIVE:
        plt_link = imps.inter_chart(fig, imagefile, callback=False)

    imagefile = imps.image_border(imagefile, fig=fig)

    return {
        "title": "Consumer Prices Index",
        "description": plt_link,
        "imagefile": imagefile,
    }
