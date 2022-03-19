import logging

import plotly.graph_objects as go

import bots.config_discordbot as cfg
from bots import helpers, load_candle
from gamestonk_terminal.common.technical_analysis import volume_model
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def obv_command(
    ticker="",
    interval: int = 15,
    past_days: int = 0,
    start="",
    end="",
    extended_hours: bool = False,
    heikin_candles: bool = False,
    news: bool = False,
):
    """Displays chart with on balance volume [Yahoo Finance]"""

    # Debug
    if cfg.DEBUG:
        logger.debug(
            "ta obv %s %s %s %s %s %s %s",
            ticker,
            past_days,
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

    df_ta = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]
    df_ta = df_ta.join(volume_model.obv(df_ta))

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
        row_width=[0.5, 0.6],
        specs=[
            [{"secondary_y": True}],
            [{"secondary_y": False}],
        ],
    )
    title = f"{plot['plt_title']} OBV"
    fig = plot["fig"]

    fig.add_trace(
        go.Scatter(
            name="OBV",
            mode="lines",
            x=df_ta.index,
            y=df_ta["OBV"],
            line=dict(width=2),
            opacity=1,
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
        title_x=0.1,
        title_font_size=14,
        dragmode="pan",
        yaxis=dict(nticks=15),
        yaxis2=dict(nticks=15),
    )
    imagefile = "ta_obv.png"

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
        "title": f"Stocks: On-Balance-Volume {ticker.upper()}",
        "description": plt_link,
        "imagefile": imagefile,
    }
