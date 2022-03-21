import logging

import plotly.graph_objects as go

from bots import imps, load_candle
from gamestonk_terminal.common.technical_analysis import overlap_model
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


# pylint: disable=R0912
# pylint: disable=R0913
@log_start_end(log=logger)
def candle_command(
    ticker: str = "",
    interval: int = 15,
    past_days: int = 0,
    extended_hours: bool = False,
    start="",
    end="",
    news: bool = False,
    heikin_candles: bool = False,
    vwap: bool = False,
):
    """Shows candle plot of loaded ticker or crypto. [Source: Yahoo Finance or Binance API]

    Parameters
    ----------
    ticker : Stock Ticker
    interval : Chart Minute Interval, 1440 for Daily
    past_days: Past Days to Display. Default: 0(Not for Daily)
    extended_hours: Display Pre/After Market Hours. Default: False
    start: YYYY-MM-DD format
    end: YYYY-MM-DD format
    news: Display clickable news markers on interactive chart. Default: False
    heikin_candles: Heikin Ashi candles. Default: False
    """

    logger.info(
        "candle %s %s %s %s %s %s %s %s",
        ticker,
        interval,
        past_days,
        extended_hours,
        start,
        end,
        news,
        heikin_candles,
    )

    # Retrieve Data
    df_stock, start, end, bar_start = load_candle.stock_data(
        ticker=ticker,
        interval=interval,
        past_days=past_days,
        extended_hours=extended_hours,
        start=start,
        end=end,
        news=news,
        heikin_candles=heikin_candles,
    )

    df_stock = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]
    df_stock = df_stock.join(overlap_model.vwap(df_stock, 0))

    # Check that loading a stock was not successful
    if df_stock.empty:
        raise Exception(f"No data found for {ticker.upper()}.")

    # Output Data
    if interval != 1440:
        df_stock = df_stock.loc[(df_stock.index >= bar_start) & (df_stock.index < end)]

    plot = load_candle.candle_fig(
        df_stock,
        ticker,
        interval,
        extended_hours,
        news,
        bar=bar_start,
        int_bar=interval,
    )
    title = f"{plot['plt_title']} Chart"
    fig = plot["fig"]

    if interval != 1440 and vwap:
        fig.add_trace(
            go.Scatter(
                name="VWAP",
                x=df_stock.index,
                y=df_stock["VWAP_D"],
                opacity=0.65,
                line=dict(color="#00e6c3", width=2),
                showlegend=True,
            ),
            secondary_y=True,
        )

    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=20),
        template=imps.PLT_CANDLE_STYLE_TEMPLATE,
        title=title,
        title_x=0.5,
        title_font_size=14,
    )
    imagefile = "candle.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if imps.INTERACTIVE:
        plt_link = imps.inter_chart(fig, imagefile, callback=True)

    fig.update_layout(
        width=800,
        height=500,
    )
    imagefile = imps.image_border(imagefile, fig=fig)

    return {
        "title": title,
        "description": plt_link,
        "imagefile": imagefile,
    }
