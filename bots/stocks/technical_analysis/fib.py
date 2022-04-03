import logging

import plotly.graph_objects as go

from bots import imps, load_candle
from openbb_terminal.common.technical_analysis import custom_indicators_model
from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def fib_command(
    ticker="",
    interval: int = 15,
    past_days: int = 0,
    start: str = "",
    end: str = "",
    extended_hours: bool = False,
    heikin_candles: bool = False,
    news: bool = False,
):
    """Displays chart with fibonacci retracement [Yahoo Finance]"""

    # Debug
    if imps.DEBUG:
        # pylint: disable=logging-too-many-args
        logger.debug(
            "ta fib %s %s %s %s %s %s %s %s",
            ticker,
            interval,
            past_days,
            start,
            end,
            extended_hours,
            heikin_candles,
            news,
        )

    past_days = (past_days + 1) if (interval != 1440) or (start != "") else 365

    # Retrieve Data
    (df_stock, start, end, bar_start,) = load_candle.stock_data(
        ticker=ticker,
        interval=interval,
        past_days=past_days,
        extended_hours=extended_hours,
        start=start,
        end=end,
        heikin_candles=heikin_candles,
    )

    if df_stock.empty:
        raise Exception(f"No data found for {ticker.upper()}.")

    df_ta = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

    # Output Data
    if interval != 1440:
        df_ta = df_ta.loc[(df_ta.index >= bar_start) & (df_ta.index < end)]

    (
        df_fib,
        min_date,
        max_date,
        min_pr,
        max_pr,
    ) = custom_indicators_model.calculate_fib_levels(df_ta, 12, bar_start, None)

    levels = df_fib.Price

    # Output Data
    fibs = [
        "<b>0</b>",
        "<b>0.235</b>",
        "<b>0.382</b>",
        "<b>0.5</b>",
        "<b>0.618</b>",
        "<b>0.65</b>",
        "<b>1</b>",
    ]
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
    title = f"<b>{plot['plt_title']} Fibonacci-Retracement-Levels</b>"
    lvl_text: str = "right" if min_date > max_date else "left"
    fig = plot["fig"]

    fig.add_trace(
        go.Scatter(
            x=[min_date, max_date],
            y=[min_pr, max_pr],
            opacity=1,
            mode="lines",
            line=imps.PLT_FIB_COLORWAY[8],
            showlegend=False,
        ),
        row=1,
        col=1,
        secondary_y=True,
    )

    for i in range(6):
        fig.add_trace(
            go.Scatter(
                name=fibs[i],
                x=[min_date, max_date],
                y=[levels[i], levels[i]],
                opacity=0.2,
                mode="lines",
                line_color=imps.PLT_FIB_COLORWAY[i],
                showlegend=False,
            ),
            row=1,
            col=1,
            secondary_y=True,
        )
        fig.add_trace(
            go.Scatter(
                name=fibs[i + 1],
                x=[min_date, max_date],
                y=[levels[i + 1], levels[i + 1]],
                opacity=0.2,
                mode="lines",
                fill="tonexty",
                line_color=imps.PLT_FIB_COLORWAY[i + 1],
                showlegend=False,
            ),
            row=1,
            col=1,
            secondary_y=True,
        )

    for i in range(7):
        fig.add_trace(
            go.Scatter(
                name=fibs[i],
                x=[min_date],
                y=[levels[i]],
                opacity=0.9,
                mode="text",
                text=fibs[i],
                textposition=f"middle {lvl_text}" if i != 5 else f"bottom {lvl_text}",
                textfont=dict(imps.PLT_FIB_COLORWAY[7], color=imps.PLT_FIB_COLORWAY[i]),
                showlegend=False,
            ),
            row=1,
            col=1,
            secondary_y=True,
        )
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=20),
        template=imps.PLT_TA_STYLE_TEMPLATE,
        title=title,
        title_x=0.02,
        title_font_size=14,
        dragmode="pan",
    )
    imagefile = "ta_fib.png"

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
        "title": f"Stocks: Fibonacci-Retracement-Levels {ticker.upper()}",
        "description": plt_link,
        "imagefile": imagefile,
    }
