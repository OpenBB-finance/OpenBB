import logging

import plotly.graph_objects as go

import bots.config_discordbot as cfg
from bots import helpers, load_candle
from gamestonk_terminal.common.technical_analysis import momentum_model
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


# pylint: disable=R0913
@log_start_end(log=logger)
def macd_command(
    ticker="",
    interval: int = 15,
    past_days: int = 0,
    fast="12",
    slow="26",
    signal="9",
    start="",
    end="",
    extended_hours: bool = False,
    heikin_candles: bool = False,
    news: bool = False,
):
    """Displays chart with moving average convergence/divergence [Yahoo Finance]"""

    # Debug
    if cfg.DEBUG:
        # pylint: disable=logging-too-many-args
        logger.debug(
            "ta macd %s %s %s %s %s %s %s %s %s %s %s",
            ticker,
            interval,
            past_days,
            fast,
            slow,
            signal,
            start,
            end,
            extended_hours,
            heikin_candles,
            news,
        )

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

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

    if df_stock.empty:
        return Exception("No Data Found")

    if not fast.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    fast = int(fast)
    if not slow.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    slow = int(slow)
    if not signal.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    signal = int(signal)

    df_ta = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

    if df_ta.empty:
        return Exception("No Data Found")

    ta_data = momentum_model.macd(df_stock["Adj Close"], fast, slow, signal)
    df_ta = df_ta.join(ta_data)

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
    title = f"{plot['plt_title']} MACD {fast} {slow} {signal}"
    fig = plot["fig"]

    fig.add_trace(
        go.Bar(
            name="MACD Histogram",
            x=df_ta.index,
            y=df_ta[f"MACDh_{fast}_{slow}_{signal}"],
            opacity=(plot["bar_opacity"] + 0.3),
            marker_color="#d81aea",
        ),
        row=2,
        col=1,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            name="MACD Line",
            mode="lines",
            x=df_ta.index,
            y=df_ta[f"MACD_{fast}_{slow}_{signal}"],
            opacity=0.8,
            line=dict(color="#00e6c3"),
        ),
        row=2,
        col=1,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            name="Signal Line",
            mode="lines",
            x=df_ta.index,
            y=df_ta[f"MACDs_{fast}_{slow}_{signal}"],
            opacity=1,
            line=dict(color="#9467bd"),
        ),
        row=2,
        col=1,
        secondary_y=False,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=20),
        template=cfg.PLT_TA_STYLE_TEMPLATE,
        colorway=cfg.PLT_TA_COLORWAY,
        title=title,
        title_x=0.02,
        title_font_size=14,
        dragmode="pan",
    )
    imagefile = "ta_macd.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if cfg.INTERACTIVE:
        plt_link = helpers.inter_chart(fig, imagefile, callback=False)

    fig.update_layout(
        width=800,
        height=500,
    )

    imagefile = helpers.image_border(imagefile, fig=fig)

    return {
        "title": f"Stocks: Moving-Average-Convergence-Divergence {ticker.upper()}",
        "description": plt_link,
        "imagefile": imagefile,
    }
