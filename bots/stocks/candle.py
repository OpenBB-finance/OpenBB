import logging
from datetime import datetime, timedelta

import plotly.graph_objects as go

import bots.config_discordbot as cfg
from bots import helpers, load_candle
from gamestonk_terminal.common.technical_analysis import overlap_model
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


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
):
    """Display Candlestick Chart

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

    if interval != 1440:
        past_days += 30 if news else 1
        if start == "":
            ta_start = datetime.now() - timedelta(days=past_days)
        else:
            ta_start = datetime.strptime(start, cfg.DATE_FORMAT) - timedelta(
                days=past_days
            )
        past_days += 2 if news else 10
        ta_start = load_candle.local_tz(ta_start)

    # Retrieve Data
    df_stock, start, end = load_candle.stock_data(
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
        return Exception(f"No data found for {ticker.upper()}.")

    # Output Data
    if interval != 1440:
        ta_end = load_candle.local_tz(end)
        df_stock = df_stock.loc[
            (df_stock.index >= ta_start) & (df_stock.index < ta_end)
        ]

    fig = load_candle.candle_fig(df_stock, ticker, interval, extended_hours, news)

    plt_title = f"{ticker.upper()} Intraday {interval}min"
    title = f"Intraday {interval}min Chart for {ticker.upper()}"
    if interval == 1440:
        plt_title = f"{ticker.upper()} Daily"
        title = f"Daily Chart for {ticker.upper()}"

    if interval != 1440:
        fig.add_trace(
            go.Scatter(
                name="VWAP",
                x=df_stock.index,
                y=df_stock["VWAP_D"],
                opacity=0.65,
                line=dict(color="#fdc708", width=2),
                showlegend=True,
            ),
            secondary_y=True,
        )

    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=20),
        template=cfg.PLT_CANDLE_STYLE_TEMPLATE,
        title=plt_title,
    )

    imagefile = "candle.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if cfg.INTERACTIVE:
        plt_link = helpers.inter_chart(fig, imagefile, callback=True)

    fig.update_layout(
        width=800,
        height=500,
    )
    imagefile = helpers.image_border(imagefile, fig=fig)

    return {
        "title": title,
        "description": plt_link,
        "imagefile": imagefile,
    }
