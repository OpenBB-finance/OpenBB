import logging

import plotly.graph_objects as go
import yfinance as yf
from plotly.subplots import make_subplots

from bots import imps
from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def cc_hist_command(
    ticker: str = None, expiry: str = "", strike: float = 10, opt_type: str = ""
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
    opt_type: str
        Calls for call
        Puts for put
    """

    # Debug
    if imps.DEBUG:
        logger.info("opt hist %s, %s, %s, %s", ticker, strike, opt_type, expiry)

    # Check for argument
    if ticker is None:
        raise Exception("Stock ticker is required")
    yf_ticker = yf.Ticker(ticker)
    dates = list(yf_ticker.options)

    if not dates:
        raise Exception("Stock ticker is invalid")

    options = yf.Ticker(ticker).option_chain(expiry)

    if opt_type == "Calls":
        options = options.calls
    if opt_type == "Puts":
        options = options.puts

    chain_id = options.loc[options.strike == strike, "contractSymbol"].values[0]
    df_hist = yf.download(chain_id)
    df_hist.index.name = "date"

    title = f"{ticker.upper()} {strike} {opt_type} expiring {expiry} Historical"

    fig = make_subplots(
        shared_xaxes=True,
        specs=[[{"secondary_y": True}]],
    )
    fig.add_trace(
        go.Candlestick(
            x=df_hist.index,
            open=df_hist.Open,
            high=df_hist.High,
            low=df_hist.Low,
            close=df_hist.Close,
            name="OHLC",
            increasing_line_color=imps.PLT_CANDLE_INCREASING,
            decreasing_line_color=imps.PLT_CANDLE_DECREASING,
            showlegend=False,
        ),
        secondary_y=True,
    )
    fig.add_trace(
        go.Bar(
            x=df_hist.index,
            y=df_hist.Volume,
            name="Volume",
            yaxis="y2",
            marker_color=imps.PLT_CANDLE_VOLUME,
            opacity=0.3,
            showlegend=False,
        ),
        secondary_y=False,
    )
    if imps.PLT_WATERMARK:
        fig.add_layout_image(imps.PLT_WATERMARK)
    fig.update_layout(
        margin=dict(l=0, r=0, t=25, b=5),
        template=imps.PLT_CANDLE_STYLE_TEMPLATE,
        showlegend=False,
        title=title,
        title_x=0.1,
        title_font_size=14,
        yaxis2_title="Premium",
        yaxis_title="Volume",
        font=imps.PLT_FONT,
        yaxis=dict(
            showgrid=False,
            fixedrange=False,
            side="left",
            titlefont=dict(color=imps.PLT_CANDLE_YAXIS_TEXT_COLOR, size=12),
            tickfont=dict(
                color=imps.PLT_CANDLE_YAXIS_TEXT_COLOR,
                size=14,
            ),
            nticks=20,
        ),
        yaxis2=dict(
            side="right",
            fixedrange=False,
            anchor="x",
            layer="above traces",
            overlaying="y",
            nticks=20,
            tickfont=dict(
                size=14,
            ),
            showline=False,
        ),
        xaxis=dict(
            rangeslider=dict(visible=False),
            type="date",
        ),
        dragmode="pan",
    )
    fig.update_xaxes(
        rangebreaks=[
            dict(bounds=["sat", "mon"]),
        ],
    )

    imagefile = "opt_hist.png"

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
