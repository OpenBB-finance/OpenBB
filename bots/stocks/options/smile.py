import logging

import plotly.graph_objects as go

from bots import imps
from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.options import yfinance_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def smile_command(
    ticker: str = None,
    expiry: str = "",
    min_sp: float = None,
    max_sp: float = None,
):
    """Options Smile"""

    # Debug
    if imps.DEBUG:
        logger.debug("opt smile %s %s %s %s", ticker, expiry, min_sp, max_sp)

    # Check for argument
    if ticker is None:
        raise Exception("Stock ticker is required")

    dates = yfinance_model.option_expirations(ticker)

    if not dates:
        raise Exception("Stock ticker is invalid")

    options = yfinance_model.get_option_chain(ticker, expiry)
    calls = options.calls.fillna(0.0)
    puts = options.puts.fillna(0.0)
    current_price = yfinance_model.get_price(ticker)

    min_strike = 0.60 * current_price
    max_strike = 1.95 * current_price

    if len(calls) > 40:
        min_strike = 0.60 * current_price
        max_strike = 1.50 * current_price

    if min_sp:
        min_strike = min_sp
    if max_sp:
        max_strike = max_sp

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=calls["strike"],
            y=calls["impliedVolatility"].interpolate(method="nearest"),
            name="Calls",
            mode="lines+markers",
            marker=dict(
                color="#00ACFF",
                size=4.5,
            ),
            line=dict(color="#00ACFF", width=2, dash="dash"),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=puts["strike"],
            y=puts["impliedVolatility"].interpolate(method="nearest"),
            name="Puts",
            mode="lines+markers",
            marker=dict(
                color="#e4003a",
                size=4.5,
            ),
            line=dict(color="#e4003a", width=2, dash="dash"),
        )
    )

    if imps.PLT_WATERMARK:
        fig.add_layout_image(imps.PLT_WATERMARK)
    fig.update_xaxes(
        range=[min_strike, max_strike],
        constrain="domain",
    )
    fig.update_layout(
        margin=dict(l=20, r=0, t=60, b=20),
        template=imps.PLT_SCAT_STYLE_TEMPLATE,
        font=imps.PLT_FONT,
        title=f"<b>Implied Volatility vs. Strike for {ticker.upper()} expiring {expiry}</b>",
        title_x=0.5,
        legend_title="",
        xaxis_title="Strike",
        yaxis_title="Implied Volatility",
        yaxis=dict(
            side="right",
            fixedrange=False,
            nticks=20,
        ),
        xaxis=dict(
            rangeslider=dict(visible=False),
            nticks=20,
        ),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        dragmode="pan",
    )

    imagefile = "opt_smile.png"

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
        "title": f"Implied Volatility vs. Stirke for {ticker.upper()} expiring {expiry}",
        "description": plt_link,
        "imagefile": imagefile,
    }
