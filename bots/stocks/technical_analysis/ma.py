from datetime import datetime, timedelta

import plotly.graph_objects as go

import bots.config_discordbot as cfg
from bots import helpers, load_candle
from bots.config_discordbot import logger
from gamestonk_terminal.common.technical_analysis import overlap_model


def ma_command(
    ticker="",
    interval: int = 15,
    past_days: int = 0,
    mamode="ema",
    window="",
    offset: int = 0,
    start="",
    end="",
    extended_hours: bool = False,
    heikin_candles: bool = False,
    news: bool = False,
):
    """Displays chart with selected Moving Average  [Yahoo Finance]"""
    # Debug
    if cfg.DEBUG:
        # pylint: disable=logging-too-many-args
        logger.debug(
            "ta ma %s %s %s %s %s %s",
            ticker,
            mamode,
            start,
            end,
        )

    # Check for argument
    overlap_ma = {
        "ema": overlap_model.ema,
        "hma": overlap_model.hma,
        "sma": overlap_model.sma,
        "wma": overlap_model.wma,
        "zlma": overlap_model.zlma,
    }

    if ticker == "":
        raise Exception("Stock ticker is required")

    if datetime.today().strftime("%A") == "Saturday" and past_days <= 1:
        past_days = 1
    if datetime.today().strftime("%A") == "Sunday" and past_days <= 2:
        past_days = 2

    if interval != 1440:
        past_days += 30 if news else 0
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
        heikin_candles=heikin_candles,
    )

    if df_stock.empty:
        return Exception("No Data Found")

    if window == "":
        window = [20, 50]
    else:
        window_temp = list()
        for wind in window.split(","):
            try:
                window_temp.append(float(wind))
            except Exception as e:
                raise Exception("Window needs to be a float") from e
        window = window_temp

    df_ta = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

    if df_ta.empty:
        return Exception("No Data Found")

    for win in window:
        ema_data = overlap_ma[mamode](
            values=df_ta["Adj Close"], length=win, offset=offset
        )
        df_ta = df_ta.join(ema_data)
    if mamode == "zlma":
        mamode = "ZL_EMA"

    if interval != 1440:
        ta_end = load_candle.local_tz(end)
        df_ta = df_ta.loc[(df_ta.index >= ta_start) & (df_ta.index < ta_end)]

    fig = load_candle.candle_fig(df_ta, ticker, interval, extended_hours, news)

    for win in window:
        fig.add_trace(
            go.Scatter(
                name=f"{mamode.upper()} {win}",
                x=df_ta.index,
                y=df_ta[f"{mamode.upper()}_{win}"],
                opacity=1,
            ),
            secondary_y=True,
        )

    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=20),
        template=cfg.PLT_TA_STYLE_TEMPLATE,
        colorway=cfg.PLT_TA_COLORWAY,
        title=f"{ticker.upper()} Moving Average ({mamode.upper()})",
        title_x=0.3,
        dragmode="pan",
    )
    config = dict({"scrollZoom": True})
    imagefile = "ta_ma.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if cfg.INTERACTIVE:
        html_ran = helpers.uuid_get()
        fig.write_html(f"in/ma_{html_ran}.html", config=config)
        plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/ma_{html_ran}.html)"

    fig.update_layout(
        width=800,
        height=500,
    )

    imagefile = helpers.image_border(imagefile, fig=fig)

    return {
        "title": f"Stocks: Moving Average {mamode.upper()}",
        "description": plt_link,
        "imagefile": imagefile,
    }
