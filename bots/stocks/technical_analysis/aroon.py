import logging

import plotly.graph_objects as go

import bots.config_discordbot as cfg
from bots import helpers, load_candle
from gamestonk_terminal.common.technical_analysis import trend_indicators_model
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def aroon_command(
    ticker="",
    interval: int = 15,
    past_days: int = 0,
    length="25",
    scalar="100",
    start="",
    end="",
    extended_hours: bool = False,
    heikin_candles: bool = False,
    news: bool = False,
):
    """Displays chart with aroon indicator [Yahoo Finance]"""

    # Debug
    if cfg.DEBUG:
        logger.debug(
            "ta aroon %s %s %s %s %s",
            ticker,
            interval,
            past_days,
            length,
            scalar,
            start,
            end,
            extended_hours,
            heikin_candles,
            news,
        )

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

    if not length.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    length = int(length)
    if not scalar.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    scalar = float(scalar)

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
    df_ta = df_ta.join(
        trend_indicators_model.aroon(df_ta["High"], df_ta["Low"], length, scalar)
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
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_width=[0.2, 0.2, 0.3],
        specs=[
            [{"secondary_y": True}],
            [{"secondary_y": False}],
            [{"secondary_y": False}],
        ],
    )
    title = f"{plot['plt_title']} Aroon ({length})"
    fig = plot["fig"]

    fig.add_trace(
        go.Scatter(
            name="Aroon DOWN",
            x=df_ta.index,
            y=df_ta[f"AROOND_{length}"],
            opacity=1,
        ),
        row=2,
        col=1,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            name="Aroon UP",
            x=df_ta.index,
            y=df_ta[f"AROONU_{length}"],
            opacity=1,
        ),
        row=2,
        col=1,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            name="Aroon OSC",
            x=df_ta.index,
            y=df_ta[f"AROONOSC_{length}"],
            opacity=1,
        ),
        row=3,
        col=1,
        secondary_y=False,
    )
    fig.add_hline(
        y=50,
        fillcolor="grey",
        opacity=1,
        layer="below",
        line_width=3,
        line=dict(color="grey", dash="dash"),
        row=2,
        col=1,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=20),
        template=cfg.PLT_TA_STYLE_TEMPLATE,
        colorway=cfg.PLT_TA_COLORWAY,
        title=title,
        title_x=0.1,
        title_font_size=14,
        dragmode="pan",
        yaxis=dict(nticks=10),
        yaxis2=dict(nticks=10),
    )
    imagefile = "ta_aroon.png"

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
        "title": f"Stocks: Aroon-Indicator {ticker.upper()}",
        "description": plt_link,
        "imagefile": imagefile,
    }
