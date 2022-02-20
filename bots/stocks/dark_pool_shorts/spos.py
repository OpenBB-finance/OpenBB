import plotly.graph_objects as go
import yfinance as yf
from plotly.subplots import make_subplots

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots import helpers
from gamestonk_terminal.stocks.dark_pool_shorts import stockgrid_model


def spos_command(ticker: str = ""):
    """Net short vs position [Stockgrid]"""

    # Debug user input
    if cfg.DEBUG:
        logger.debug("dps-spos %s", ticker)

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

    ticker = ticker.upper()

    stock = yf.download(ticker, progress=False)
    if stock.empty:
        raise Exception("Stock ticker is invalid")

    # Retrieve data
    df = stockgrid_model.get_net_short_position(ticker)

    # Debug user output
    if cfg.DEBUG:
        logger.debug(df.to_string())

    # Output data
    title = f"Stocks: [Stockgrid] Net Short vs Position {ticker}"

    fig = make_subplots(shared_xaxes=True, specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            name="Position ($)",
            x=df["dates"].values,
            y=df["dollar_dp_position"] * 1_000,
            line=dict(color="#fdc708", width=2),
            opacity=1,
            showlegend=False,
        ),
        secondary_y=True,
    )
    fig.add_trace(
        go.Bar(
            name="Net Short Vol. ($)",
            x=df["dates"],
            y=df["dollar_net_volume"],
            opacity=1,
            showlegend=False,
        ),
        secondary_y=False,
    )
    # Set y-axes titles
    fig.update_xaxes(dtick="M1", tickformat="%b %d\n%Y")
    fig.update_yaxes(title_text="<b>Position</b> ($)", secondary_y=True)
    fig.update_traces(hovertemplate="%{y:.2s}")
    fig.update_layout(
        margin=dict(l=0, r=10, t=40, b=20),
        template=cfg.PLT_TA_STYLE_TEMPLATE,
        colorway=cfg.PLT_TA_COLORWAY,
        title=f"Net Short Vol. vs Position for {ticker}",
        title_x=0.5,
        yaxis_title="<b>Net Short Vol.</b> ($)",
        yaxis=dict(
            side="left",
            showgrid=False,
            fixedrange=False,
            layer="above traces",
            titlefont=dict(color="#d81aea"),
            tickfont=dict(color="#d81aea"),
            nticks=10,
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
            side="right",
            position=0.15,
            fixedrange=False,
            titlefont=dict(color="#fdc708"),
            tickfont=dict(color="#fdc708"),
            nticks=10,
        ),
        hovermode="x unified",
    )
    config = dict({"scrollZoom": True})
    imagefile = "dps_spos.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if cfg.INTERACTIVE:
        html_ran = helpers.uuid_get()
        fig.write_html(f"in/spos_{html_ran}.html", config=config)
        plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/spos_{html_ran}.html)"

    fig.update_layout(
        width=800,
        height=500,
    )

    imagefile = helpers.image_border(imagefile, fig=fig)

    return {
        "title": title,
        "description": plt_link,
        "imagefile": imagefile,
    }
