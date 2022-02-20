import pandas as pd
import plotly.graph_objects as go

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots import helpers
from gamestonk_terminal.stocks.options import yfinance_model


def vol_command(
    ticker: str = None,
    expiry: str = "",
    min_sp: float = None,
    max_sp: float = None,
):
    """Options VOL"""

    # Debug
    if cfg.DEBUG:
        logger.debug("opt-vol %s %s %s %s", ticker, expiry, min_sp, max_sp)

    # Check for argument
    if ticker is None:
        raise Exception("Stock ticker is required")

    dates = yfinance_model.option_expirations(ticker)

    if not dates:
        raise Exception("Stock ticker is invalid")

    options = yfinance_model.get_option_chain(ticker, expiry)
    current_price = yfinance_model.get_price(ticker)

    if min_sp is None:
        min_strike = 0.75 * current_price
    else:
        min_strike = min_sp

    if max_sp is None:
        max_strike = 1.25 * current_price
    else:
        max_strike = max_sp

    calls = options.calls
    puts = options.puts
    call_v = calls.set_index("strike")["volume"] / 1000
    put_v = puts.set_index("strike")["volume"] / 1000

    df_opt = pd.merge(put_v, call_v, left_index=True, right_index=True)
    dmax = df_opt.values.max()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=call_v.index,
            y=call_v.values,
            name="Calls",
            mode="lines+markers",
            line=dict(color="green", width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=put_v.index,
            y=put_v.values,
            name="Puts",
            mode="lines+markers",
            line=dict(color="red", width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[current_price, current_price],
            y=[0, dmax],
            mode="lines",
            line=dict(color="gold", width=2),
            name="Current Price",
        )
    )
    fig.update_xaxes(
        range=[min_strike, max_strike],
        constrain="domain",
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=60, b=20),
        template=cfg.PLT_SCAT_STYLE_TEMPLATE,
        title=f"Volume for {ticker.upper()} expiring {expiry}",
        title_x=0.5,
        legend_title="",
        xaxis_title="Strike",
        yaxis_title="Volume (1k)",
        xaxis=dict(
            rangeslider=dict(visible=False),
        ),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        dragmode="pan",
    )
    config = dict({"scrollZoom": True})
    imagefile = "opt_vol.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if cfg.INTERACTIVE:
        html_ran = helpers.uuid_get()
        fig.write_html(f"in/vol_{html_ran}.html", config=config)
        plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/vol_{html_ran}.html)"

    fig.update_layout(
        width=800,
        height=500,
    )

    imagefile = helpers.image_border(imagefile, fig=fig)

    return {
        "title": f"Volume for {ticker.upper()} expiring {expiry}",
        "description": plt_link,
        "imagefile": imagefile,
    }
