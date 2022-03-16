import logging

import plotly.graph_objects as go

import bots.config_discordbot as cfg
from bots import helpers, load_candle
from gamestonk_terminal.common.technical_analysis import volatility_model
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def kc_command(
    ticker="",
    interval: int = 15,
    past_days: int = 0,
    length="20",
    scalar="2",
    ma_mode="sma",
    offset="0",
    start="",
    end="",
    extended_hours: bool = False,
    heikin_candles: bool = False,
    news: bool = False,
):
    """Displays chart with keltner channel [Yahoo Finance]"""

    # Debug
    if cfg.DEBUG:
        # pylint: disable=logging-too-many-args
        logger.debug(
            "ta kc %s %s %s %s %s %s %s %s %s %s %s %s",
            ticker,
            interval,
            past_days,
            length,
            scalar,
            ma_mode,
            offset,
            start,
            end,
            extended_hours,
            heikin_candles,
            news,
        )

    # Check for argument
    if not length.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    length = int(length)
    if not scalar.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    scalar = float(scalar)
    if not offset.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    offset = float(offset)

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

    df_ta = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

    if df_ta.empty:
        return Exception("No Data Found")

    ta_data = volatility_model.kc(
        df_stock["High"],
        df_stock["Low"],
        df_stock["Adj Close"],
        length,
        scalar,
        ma_mode,
        offset,
    )
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
        shared_xaxes=True,
        vertical_spacing=0.07,
    )
    title = f"{plot['plt_title']} Keltner Channels ({ma_mode.upper()})"
    fig = plot["fig"]

    fig.add_trace(
        go.Scatter(
            name="upper",
            x=df_ta.index,
            y=df_ta[f"KCUs_{length}_{scalar}"],
            opacity=1,
            mode="lines",
            line_color="indigo",
            showlegend=False,
        ),
        row=1,
        col=1,
        secondary_y=True,
    )
    fig.add_trace(
        go.Scatter(
            name="lower",
            x=df_ta.index,
            y=df_ta[f"KCLs_{length}_{scalar}"],
            opacity=1,
            mode="lines",
            line_color="indigo",
            fill="tonexty",
            fillcolor="rgba(74, 0, 128, 0.2)",
            showlegend=False,
        ),
        row=1,
        col=1,
        secondary_y=True,
    )
    fig.add_trace(
        go.Scatter(
            name="mid",
            x=df_ta.index,
            y=df_ta[f"KCBs_{length}_{scalar}"],
            opacity=1,
            line=dict(
                width=1.5,
                dash="dash",
            ),
            showlegend=False,
        ),
        row=1,
        col=1,
        secondary_y=True,
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
    imagefile = "ta_kc.png"

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
        "title": f"Stocks: Keltner-Channel {ticker.upper()}",
        "description": plt_link,
        "imagefile": imagefile,
    }
