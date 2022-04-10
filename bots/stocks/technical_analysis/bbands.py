import logging

import plotly.graph_objects as go

from bots import imps, load_candle
from openbb_terminal.common.technical_analysis import volatility_model
from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


# pylint: disable=R0913
@log_start_end(log=logger)
def bbands_command(
    ticker="",
    interval: int = 15,
    past_days: int = 0,
    length="20",
    n_std: float = 2.0,
    ma_mode="sma",
    start="",
    end="",
    extended_hours: bool = False,
    heikin_candles: bool = False,
    trendline: bool = False,
    news: bool = False,
):
    """Displays chart with bollinger bands [Yahoo Finance]"""

    # Debug
    if imps.DEBUG:
        # pylint: disable=logging-too-many-args
        logger.debug(
            "ta bbands %s %s %s %s %s %s %s %s %s %s %s %s",
            ticker,
            interval,
            past_days,
            length,
            n_std,
            ma_mode,
            start,
            end,
            extended_hours,
            heikin_candles,
            trendline,
            news,
        )

    # Check for argument
    possible_ma = [
        "dema",
        "ema",
        "fwma",
        "hma",
        "linreg",
        "midpoint",
        "pwma",
        "rma",
        "sinwma",
        "sma",
        "swma",
        "t3",
        "tema",
        "trima",
        "vidya",
        "wma",
        "zlma",
    ]

    if ticker == "":
        raise Exception("Stock ticker is required")

    if not length.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    ta_length = int(length)
    n_std = float(n_std)

    if ma_mode not in possible_ma:
        raise Exception("Invalid ma entered")

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
        raise Exception("No Data Found")

    df_ta = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]
    df_ta = df_ta.join(
        volatility_model.bbands(df_ta["Adj Close"], ta_length, n_std, ma_mode)
    )

    # Output Data
    if interval != 1440:
        df_ta = df_ta.loc[(df_ta.index >= bar_start) & (df_ta.index < end)]
    df_ta = df_ta.fillna(0.0)

    plot = load_candle.candle_fig(
        df_ta, ticker, interval, extended_hours, news, trendline=trendline
    )
    title = f"<b>{plot['plt_title']} Bollinger Bands ({ma_mode.upper()})</b>"
    fig = plot["fig"]
    idx = 6 if (not trendline) and (interval != 1440) else 11

    fig.add_trace(
        go.Scatter(
            name=f"BBU_{length}_{n_std}",
            x=df_ta.index,
            y=df_ta.iloc[:, (idx + 2)].values,
            opacity=1,
            mode="lines",
            line_color="indigo",
        ),
        secondary_y=True,
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            name=f"BBL_{length}_{n_std}",
            x=df_ta.index,
            y=df_ta.iloc[:, idx].values,
            opacity=1,
            mode="lines",
            line_color="indigo",
            fill="tonexty",
            fillcolor="rgba(74, 0, 128, 0.2)",
        ),
        secondary_y=True,
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            name=f"BBM_{length}_{n_std}",
            x=df_ta.index,
            y=df_ta.iloc[:, (idx + 1)].values,
            opacity=1,
            line=dict(
                width=1.5,
                dash="dash",
            ),
        ),
        secondary_y=True,
        row=1,
        col=1,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=20),
        template=imps.PLT_TA_STYLE_TEMPLATE,
        colorway=imps.PLT_TA_COLORWAY,
        title=title,
        title_x=0.1,
        title_font_size=14,
        dragmode="pan",
    )
    imagefile = "ta_bbands.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if imps.INTERACTIVE:
        plt_link = imps.inter_chart(fig, imagefile, callback=False)

    imagefile = imps.image_border(imagefile, fig=fig)

    return {
        "title": f"Stocks: Bollinger-Bands {ticker.upper()}",
        "description": plt_link,
        "imagefile": imagefile,
    }
