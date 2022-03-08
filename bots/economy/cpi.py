from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go

import bots.config_discordbot as cfg
from bots import helpers
from bots.config_discordbot import logger
from gamestonk_terminal.economy.fred import fred_model


def cpi_command(start=""):
    """Displays Consumer Prices Index (CPI)"""

    # Debug
    if cfg.DEBUG:
        logger.debug(
            "econ cpi %s",
            start,
        )

    if start == "":
        start = datetime.now() - timedelta(days=900)
    else:
        start = datetime.strptime(start, cfg.DATE_FORMAT)

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
    if cfg.DEBUG:
        logger.debug(df.to_string())

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["CPI"],
        )
    )
    fig.update_layout(
        xaxis_range=[df.index[0], end],
    )
    fig.update_xaxes(dtick="M2", tickformat="%b\n%Y")
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=50),
        template=cfg.PLT_SCAT_STYLE_TEMPLATE,
        colorway=cfg.PLT_TA_COLORWAY,
        title="CPI Monthly",
        title_x=0.5,
        yaxis_title="Consumer Prices",
        legend_title="",
        font=cfg.PLT_FONT,
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
    config = dict({"scrollZoom": True})
    imagefile = "econ-cpi.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if cfg.INTERACTIVE:
        html_ran = helpers.uuid_get()
        fig.write_html(f"in/econ-cpi_{html_ran}.html", config=config)
        plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/econ-cpi_{html_ran}.html)"

    fig.update_layout(
        width=800,
        height=500,
    )

    imagefile = helpers.image_border(imagefile, fig=fig)

    return {
        "title": "Consumer Prices Index",
        "description": plt_link,
        "imagefile": imagefile,
    }
