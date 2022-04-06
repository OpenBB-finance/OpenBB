import logging

import pandas as pd
import plotly.graph_objects as go

from bots import imps
from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.options import yfinance_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def vol_command(
    ticker: str = None,
    expiry: str = "",
    min_sp: float = None,
    max_sp: float = None,
):
    """Options VOL"""

    # Debug
    if imps.DEBUG:
        logger.debug("opt-vol %s %s %s %s", ticker, expiry, min_sp, max_sp)

    # Check for argument
    if not ticker:
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
    call_v = call_v.fillna(0.0)
    put_v = put_v.fillna(0.0)

    df_opt = pd.merge(put_v, call_v, left_index=True, right_index=True)
    dmax = df_opt.values.max()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=call_v.index,
            y=call_v.values,
            name="Calls",
            mode="lines+markers",
            line=dict(color="#00ACFF", width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=put_v.index,
            y=put_v.values,
            name="Puts",
            mode="lines+markers",
            line=dict(color="#e4003a", width=3),
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
    if imps.PLT_WATERMARK:
        fig.add_layout_image(imps.PLT_WATERMARK)
    fig.update_xaxes(
        range=[min_strike, max_strike],
        constrain="domain",
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=60, b=20),
        template=imps.PLT_SCAT_STYLE_TEMPLATE,
        title=f"Volume for {ticker.upper()} expiring {expiry}",
        title_x=0.5,
        legend_title="",
        xaxis_title="Strike",
        yaxis_title="Volume (1k)",
        yaxis=dict(
            fixedrange=False,
            nticks=20,
        ),
        xaxis=dict(
            rangeslider=dict(visible=False),
        ),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        dragmode="pan",
    )

    imagefile = "opt_vol.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if imps.INTERACTIVE:
        plt_link = imps.inter_chart(fig, imagefile, callback=False)

    fig.update_layout(
        width=800,
        height=500,
    )

    imagefile = imps.image_border(imagefile, fig=fig)

    return {
        "title": f"Volume for {ticker.upper()} expiring {expiry}",
        "description": plt_link,
        "imagefile": imagefile,
    }
