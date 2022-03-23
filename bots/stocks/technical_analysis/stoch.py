import logging

import plotly.graph_objects as go

from bots import imps, load_candle
from gamestonk_terminal.common.technical_analysis import momentum_model
from gamestonk_terminal.decorators import log_start_end

# pylint: disable=R0913
logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def stoch_command(
    ticker: str = "",
    interval: int = 15,
    past_days: int = 0,
    fast_k="14",
    slow_d="3",
    slow_k="4",
    start="",
    end="",
    extended_hours: bool = False,
    heikin_candles: bool = False,
    news: bool = False,
):
    """Displays chart with stochastic relative strength average [Yahoo Finance]"""

    # Debug
    if imps.DEBUG:
        logger.debug(
            "ta stoch %s %s %s %s %s %s %s %s %s %s %s",
            ticker,
            interval,
            past_days,
            fast_k,
            slow_k,
            slow_d,
            start,
            end,
            extended_hours,
            heikin_candles,
            news,
        )

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

    if not fast_k.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    fast_k = int(fast_k)
    if not slow_k.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    slow_k = int(slow_k)
    if not slow_d.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    slow_d = int(slow_d)

    # Retrieve Data
    df_stock, start, end, bar_start = load_candle.stock_data(
        ticker=ticker,
        interval=interval,
        past_days=past_days,
        extended_hours=extended_hours,
        start=start,
        end=end,
        heikin_candles=heikin_candles,
    )

    df_ta = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

    if df_ta.empty:
        raise Exception("No Data Found")

    df_ta = df_ta.join(
        momentum_model.stoch(
            df_stock["High"],
            df_stock["Low"],
            df_stock["Adj Close"],
            fast_k,
            slow_d,
            slow_k,
        )
    )

    # Output Data
    if interval != 1440:
        df_ta = df_ta.loc[(df_ta.index >= bar_start) & (df_ta.index < end)]

    plot = load_candle.candle_fig(
        df_ta,
        ticker,
        interval,
        extended_hours,
        news,
        bar=bar_start,
        int_bar=interval,
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.07,
        row_width=[0.4, 0.6],
        specs=[[{"secondary_y": True}], [{"secondary_y": False}]],
    )
    title = f"<b>{plot['plt_title']} STOCH RSI</b>"
    fig = plot["fig"]

    fig.add_trace(
        go.Scatter(
            name=f"%K {fast_k}, {slow_d}, {slow_k}",
            x=df_ta.index,
            y=df_ta.iloc[:, 6].values,
            line=dict(width=1.8),
            mode="lines",
            opacity=1,
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            name=f"%D {fast_k}, {slow_d}, {slow_k}",
            x=df_ta.index,
            y=df_ta.iloc[:, 7].values,
            line=dict(width=1.8, dash="dash"),
            opacity=1,
        ),
        row=2,
        col=1,
    )
    fig.add_hrect(
        y0=80,
        y1=100,
        fillcolor="red",
        opacity=0.2,
        layer="below",
        line_width=0,
        row=2,
        col=1,
    )
    fig.add_hrect(
        y0=0,
        y1=20,
        fillcolor="green",
        opacity=0.2,
        layer="below",
        line_width=0,
        row=2,
        col=1,
    )
    fig.add_hline(
        y=80,
        fillcolor="green",
        opacity=1,
        layer="below",
        line_width=3,
        line=dict(color="red", dash="dash"),
        row=2,
        col=1,
    )
    fig.add_hline(
        y=20,
        fillcolor="green",
        opacity=1,
        layer="below",
        line_width=3,
        line=dict(color="green", dash="dash"),
        row=2,
        col=1,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=20),
        template=imps.PLT_TA_STYLE_TEMPLATE,
        colorway=imps.PLT_TA_COLORWAY,
        title=title,
        title_x=0.01,
        title_font_size=14,
        dragmode="pan",
    )
    imagefile = "ta_stoch.png"

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
        "title": f"Stocks: Stochastic-Relative-Strength-Index {ticker.upper()}",
        "description": plt_link,
        "imagefile": imagefile,
    }
