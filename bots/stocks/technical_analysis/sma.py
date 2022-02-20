from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots import helpers
from gamestonk_terminal.common.technical_analysis import overlap_model


def sma_command(ticker="", window="", offset="", start="", end=""):
    """Displays chart with simple moving average [Yahoo Finance]"""

    # Debug
    if cfg.DEBUG:
        logger.debug(
            "ta-sma %s %s %s %s %s",
            ticker,
            window,
            offset,
            start,
            end,
        )

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

    if start == "":
        start = datetime.now() - timedelta(days=365)
    else:
        start = datetime.strptime(start, cfg.DATE_FORMAT)

    if end == "":
        end = datetime.now()
    else:
        end = datetime.strptime(end, cfg.DATE_FORMAT)

    l_legend = [ticker]

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

    ticker = ticker.upper()
    stock = helpers.load(ticker, start)
    if stock.empty:
        raise Exception("Stock ticker is invalid")

    # Retrieve Data
    price_df = pd.DataFrame(
        stock["Adj Close"].values, columns=["Price"], index=stock.index
    )
    i = 1
    for win in window:
        sma_data = overlap_model.sma(
            values=stock["Adj Close"], length=win, offset=offset
        )
        price_df = price_df.join(sma_data)
        l_legend.append(f"SMA {win}")
        i += 1

    # Output Data
    start = start.strftime("%Y-%m-%d")
    end = end.strftime("%Y-%m-%d")
    price_df = price_df.loc[(price_df.index >= start) & (price_df.index < end)]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            name=f"{ticker}",
            x=price_df.index,
            y=price_df["Price"],
            line=dict(color="#fdc708", width=2),
            opacity=1,
        ),
    )
    for i in range(1, price_df.shape[1]):
        trace_name = price_df.columns[i].replace("_", " ")
        fig.add_trace(
            go.Scatter(
                name=trace_name,
                x=price_df.index,
                y=price_df.iloc[:, i],
                opacity=1,
            ),
        )
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=20),
        template=cfg.PLT_TA_STYLE_TEMPLATE,
        colorway=cfg.PLT_TA_COLORWAY,
        title=f"{ticker} SMA",
        title_x=0.5,
        yaxis_title="Stock Price ($)",
        xaxis_title="Time",
        yaxis=dict(
            fixedrange=False,
        ),
        xaxis=dict(
            rangeslider=dict(visible=False),
            type="date",
        ),
        dragmode="pan",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )
    config = dict({"scrollZoom": True})
    imagefile = "ta_sma.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if cfg.INTERACTIVE:
        html_ran = helpers.uuid_get()
        fig.write_html(f"in/sma_{html_ran}.html", config=config)
        plt_link = f"[Interactive]({cfg.INTERACTIVE_URL}/sma_{html_ran}.html)"

    fig.update_layout(
        width=800,
        height=500,
    )

    imagefile = helpers.image_border(imagefile, fig=fig)

    return {
        "title": f"Stocks: Simple-Moving-Average {ticker}",
        "description": plt_link,
        "imagefile": imagefile,
    }
