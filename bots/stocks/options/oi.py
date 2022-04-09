import logging

import pandas as pd
import plotly.graph_objects as go

from bots import imps
from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.options import op_helpers, yfinance_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def oi_command(
    ticker: str = None,
    expiry: str = "",
    min_sp: float = None,
    max_sp: float = None,
):
    """Options OI"""

    # Debug
    if imps.DEBUG:
        logger.debug("opt oi %s %s %s %s", ticker, expiry, min_sp, max_sp)

    # Check for argument
    if not ticker:
        raise Exception("Stock ticker is required")

    dates = yfinance_model.option_expirations(ticker)

    if not dates:
        raise Exception("Stock ticker is invalid")

    options = yfinance_model.get_option_chain(ticker, expiry)
    calls = options.calls
    puts = options.puts
    current_price = yfinance_model.get_price(ticker)

    min_strike = 0.75 * current_price
    max_strike = 1.95 * current_price

    if len(calls) > 40:
        min_strike = 0.75 * current_price
        max_strike = 1.25 * current_price

    if min_sp:
        min_strike = min_sp
    if max_sp:
        max_strike = max_sp

    call_oi = calls.set_index("strike")["openInterest"] / 1000
    put_oi = puts.set_index("strike")["openInterest"] / 1000
    call_oi = call_oi.fillna(0.0)
    put_oi = put_oi.fillna(0.0)

    df_opt = pd.merge(call_oi, put_oi, left_index=True, right_index=True)
    df_opt = df_opt.rename(
        columns={"openInterest_x": "OI_call", "openInterest_y": "OI_put"}
    )

    max_pain = op_helpers.calculate_max_pain(df_opt)
    fig = go.Figure()

    dmax = df_opt[["OI_call", "OI_put"]].values.max()
    dmin = df_opt[["OI_call", "OI_put"]].values.min()
    fig.add_trace(
        go.Scatter(
            x=df_opt.index,
            y=df_opt["OI_call"],
            name="Calls",
            mode="lines+markers",
            line=dict(color="#00ACFF", width=3),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_opt.index,
            y=df_opt["OI_put"],
            name="Puts",
            mode="lines+markers",
            line=dict(color="#e4003a", width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[current_price, current_price],
            y=[dmin, dmax],
            mode="lines",
            line=dict(color="gold", width=2),
            name="Current Price",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[max_pain, max_pain],
            y=[dmin, dmax],
            mode="lines",
            line=dict(color="grey", width=3, dash="dash"),
            name=f"Max Pain: {max_pain}",
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
        title=f"Open Interest for {ticker.upper()} expiring {expiry}",
        title_x=0.5,
        legend_title="",
        xaxis_title="Strike",
        yaxis_title="Open Interest (1k)",
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

    imagefile = "opt_oi.png"

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
        "title": f"Open Interest for {ticker.upper()} expiring {expiry}",
        "description": plt_link,
        "imagefile": imagefile,
    }
